import argparse
import json
from typing import TypedDict
import yaml
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt, Command
from comum import ROOT, Model, Trace, parse_json, read_input

class Estado(TypedDict, total=False):
    entrada: str
    analise: str
    proposta: str
    revisao: str
    parecer: str
    decisao: dict
    status: str

def build(adapter):
    tasks = yaml.safe_load((ROOT/'crew/config/tasks.yaml').read_text())
    agents = yaml.safe_load((ROOT/'crew/config/agents.yaml').read_text())
    def step(role, field, previous):
        def invoke(state):
            context = {key: state.get(key, '') for key in previous}
            text = adapter.call([
                {'role':'system','content':json.dumps(agents[role], ensure_ascii=False)},
                {'role':'user','content':tasks[role]['description'].replace('{entrada}',state['entrada'])
                 + '\nFormato obrigatório: ' + tasks[role]['expected_output']
                 + '\nContexto anterior: ' + json.dumps(context, ensure_ascii=False)}])
            result = {field:text}
            if field=='revisao':
                try:
                    review = parse_json(text)
                    verdict = review['parecer']
                    if verdict not in ('aprovar_proposta','devolver'):
                        raise ValueError('parecer inválido')
                    if review.get('testes_executados') is not False:
                        raise ValueError('não há ferramenta de testes neste fluxo')
                except (ValueError, KeyError, TypeError):
                    adapter.trace.fail('ParecerInvalido: encaminhado para devolucao')
                    verdict = 'devolver'
                result['parecer'] = verdict
            adapter.trace.event('no', nome=role, saida=text)
            return result
        return invoke
    def approval(state):
        # No side effects before interrupt: node restarts when resumed.
        answer = interrupt({'proposta':state['proposta'], 'revisao':state['revisao'],
                            'acao':'Aceitar somente a proposta para revisão posterior; nenhum merge/deploy'})
        valid = isinstance(answer, dict) and answer.get('aprovar') is True and bool(answer.get('pessoa'))
        adapter.trace.event('decisao_humana', decisao=answer)
        return {'decisao':answer, 'status':'proposta_aceita' if valid else 'rejeitado'}
    def returned(state):
        return {'status':'devolvido_para_humano'}
    graph = StateGraph(Estado)
    graph.add_node('analista',step('analista','analise',[]))
    graph.add_node('engenheiro',step('engenheiro','proposta',['analise']))
    graph.add_node('revisor',step('revisor','revisao',['analise','proposta']))
    graph.add_node('aprovacao_humana',approval)
    graph.add_node('devolucao',returned)
    graph.add_edge(START,'analista')
    graph.add_edge('analista','engenheiro')
    graph.add_edge('engenheiro','revisor')
    graph.add_conditional_edges('revisor',lambda s:s['parecer'],
                               {'aprovar_proposta':'aprovacao_humana','devolver':'devolucao'})
    graph.add_edge('aprovacao_humana',END)
    graph.add_edge('devolucao',END)
    return graph.compile(checkpointer=InMemorySaver())

def run(path, directory=None):
    import uuid
    entrada = read_input(path)
    trace = Trace('grafo',entrada,directory)
    config = {'configurable':{'thread_id':str(uuid.uuid4())}, 'recursion_limit':12}
    trace.event('thread',id=config['configurable']['thread_id'])
    try:
        graph = build(Model(trace))
        output = graph.invoke({'entrada':entrada},config)
        compute_s = __import__('time').perf_counter()-trace.started
        if '__interrupt__' in output:
            trace.event('interrupt',payload=[i.value for i in output['__interrupt__']])
            trace.save('aguardando_humano',graph.get_state(config).values)
            print('PROPOSTA:',graph.get_state(config).values.get('proposta'))
            print('REVISÃO:',graph.get_state(config).values.get('revisao'))
            person = input('Identificação do revisor humano (ou vazio para rejeitar): ').strip()
            decision = input('Digite APROVAR para aceitar a proposta; outra resposta rejeita: ')
            wait_start = __import__('time').perf_counter()
            output = graph.invoke(Command(resume={'pessoa':person,'aprovar':decision=='APROVAR'}),config)
            trace.event('retomada',tempo_s=__import__('time').perf_counter()-wait_start)
        trace.data['tempo_ate_primeira_saida_s'] = compute_s
        trace.save(output.get('status','concluido'),output)
    except Exception as exc:
        trace.fail('ExecucaoInterrompida:' + type(exc).__name__)
        trace.save('bloqueado')
    return trace

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--entrada',required=True)
    a=p.parse_args()
    trace=run(a.entrada)
    print(trace.path)
    raise SystemExit(1 if trace.data['status']=='bloqueado' else 0)
