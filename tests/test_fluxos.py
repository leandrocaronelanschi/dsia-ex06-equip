import json
import tempfile
import unittest
from pathlib import Path
from langgraph.types import Command
from comum import Trace, read_input, ROOT
from crew.main import build as build_crew
from grafo.main import build

class Stub:
    """Test double only. Never counted as a model execution."""
    def __init__(self, directory, verdict='aprovar_proposta', malformed=False):
        self.trace=Trace('teste_sem_modelo',read_input(ROOT/'entradas/fixture_sintetica.json'),directory)
        self.calls=0
        self.outputs=['{"causa":"peso negativo aceito","criterios":["rejeitar negativos"]}',
                      '{"diff":"proposta sintética"}',
                      'INVALID' if malformed else json.dumps(dict(parecer=verdict,problemas=[],evidencias=['teste sintético'],testes_executados=False))]
    def call(self, messages):
        value=self.outputs[self.calls]
        self.calls+=1
        return value

class Tests(unittest.TestCase):
    def execute(self, verdict='aprovar_proposta', malformed=False):
        tmp=tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        adapter=Stub(tmp.name,verdict,malformed)
        graph=build(adapter)
        config={'configurable':{'thread_id':'teste'}}
        output=graph.invoke({'entrada':read_input(ROOT/'entradas/fixture_sintetica.json')},config)
        return adapter,graph,config,output
    def test_interrupt_and_resume_approval(self):
        adapter,graph,config,output=self.execute()
        self.assertIn('__interrupt__',output)
        self.assertEqual(graph.get_state(config).next,('aprovacao_humana',))
        result=graph.invoke(Command(resume={'pessoa':'revisor-de-teste','aprovar':True}),config)
        self.assertEqual(result['status'],'proposta_aceita')
        self.assertEqual(adapter.calls,3)  # Approval cannot rerun LLM nodes.
    def test_human_rejection(self):
        adapter,graph,config,_=self.execute()
        result=graph.invoke(Command(resume={'pessoa':'revisor-de-teste','aprovar':False}),config)
        self.assertEqual(result['status'],'rejeitado')
        self.assertEqual(adapter.calls,3)
    def test_no_identity_fails_closed(self):
        _,graph,config,_=self.execute()
        result=graph.invoke(Command(resume={'aprovar':True}),config)
        self.assertEqual(result['status'],'rejeitado')
    def test_conditional_return(self):
        _,graph,_,output=self.execute('devolver')
        self.assertNotIn('__interrupt__',output)
        self.assertEqual(output['status'],'devolvido_para_humano')
    def test_invalid_verdict_fails_closed(self):
        adapter,_,_,output=self.execute(malformed=True)
        self.assertEqual(output['status'],'devolvido_para_humano')
        self.assertIn('ParecerInvalido',adapter.trace.data['primeira_falha'])
    def test_both_crews_construct(self):
        with tempfile.TemporaryDirectory() as d:
            for version in ['sequencial','hierarquica']:
                crew=build_crew('entrada sintética',Stub(d),version)
                self.assertEqual(len(crew.agents),3)
                self.assertEqual(len(crew.tasks),3)
                self.assertTrue(all(a.role and a.goal and a.backstory for a in crew.agents))
                self.assertTrue(all(t.expected_output for t in crew.tasks))
    def test_input_hash_equal(self):
        entrada=read_input(ROOT/'entradas/fixture_sintetica.json')
        with tempfile.TemporaryDirectory() as d:
            hashes={Trace(v,entrada,d).data['entrada_sha256'] for v in ['sequencial','hierarquica','grafo']}
            self.assertEqual(len(hashes),1)

if __name__=='__main__':
    unittest.main()
