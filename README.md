# Exercício 6 — Uma equipe de agentes: crew e grafo

**Estado: preparação técnica testada, ainda NÃO pronta para envio.**
Não há repositório público publicado nem execuções com modelo. As três tentativas
registradas foram bloqueadas por falta de configuração. Zero chamadas ao provedor.
Os sete testes locais usam doubles, sem inferência. Não são resultados empíricos.

## Problema e vínculo com o curso
O fluxo noturno de Davi prevê triagem, correção e revisão das issues do Colheita.
Marina precisa saber quem decide e impedir que a equipe faça merge com credenciais
que também acessam produção. Esta implementação organiza analista, engenheiro e
revisor para produzir uma proposta de correção e encaminhá-la à pessoa.
Nenhuma execução deste programa altera o repositório de origem.

O colheita-mini oficial não foi disponibilizado neste ambiente. A entrada
`entradas/fixture_sintetica.json` é um pequeno caso artificial de pagamento agrícola,
criado exclusivamente para verificar o harness. Não se apresenta como o material
oficial do curso. Antes da coleta, substitua-o por um recorte real do colheita-mini
ou de seu repositório de pesquisa. O script preparar_entrada.py ajuda nessa tarefa.

## Estrutura e responsabilidades
- crew/config: três papéis específicos e tarefas com saídas verificáveis.
- crew/main.py: processos sequencial e hierárquico. O segundo acrescenta um gerente
  de coordenação aos três especialistas; suas chamadas também entram na medição.
- grafo/main.py: estado tipado, análise, proposta, revisão, decisão condicional,
  interrupt de aprovação e checkpointer em memória.
- comum.py: adaptador compartilhado, contagem de chamadas, orçamento e rastros JSON.
- rastros: testes locais e tentativas bloqueadas, com status explícito.

## Ambiente e instalação
Python 3.12.14. CrewAI 1.15.40, LangGraph 1.2.20 e langchain-openai 1.7.4.
As versões completas instaladas estão em requirements.lock.txt.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.lock.txt
cp .env.example .env
```
No Windows, pode copiar o arquivo pelo explorador. Edite .env localmente:
OPENAI_API_KEY é sua chave; MODEL deve ser um identificador de modelo disponível
na conta; SEED deve ser 42. Nenhuma chave é necessária para os testes unitários.
**Modelo real usado: nenhum.** A temperatura configurada é 0 e a seed padrão é 42.
Seed não garante determinismo do serviço; confirme que o modelo aceita temperatura,
seed e max_tokens. O código não troca de modelo nem remove parâmetros silenciosamente.
A assinatura do ChatGPT não configura automaticamente uma chave de API neste projeto.

## Preparar a entrada real
Escolha uma issue pequena e pública e seu commit de origem. Salve a descrição num
arquivo de texto e selecione o código e testes pertinentes. Não inclua .env, dados
pessoais ou registros reais da cooperativa.

```bash
python preparar_entrada.py --repo ../colheita-mini --issue issue.txt --arquivo src/pagamento.py --arquivo tests/test_pagamento.py --criterio "Peso negativo gera ValueError" --saida entradas/caso.json
```
Os caminhos acima são exemplos: substitua pelos arquivos existentes. Acrescente ao
JSON a URL e o commit efetivos. As três versões devem usar exatamente esse mesmo
arquivo, sem incorporar a saída de outra versão. O SHA-256 canônico fica no rastro.

## Executar e guardar as três versões
```bash
python -m crew.main sequencial --entrada entradas/caso.json
python -m crew.main hierarquica --entrada entradas/caso.json
python -m grafo.main --entrada entradas/caso.json
python comparar.py
```
Não há ferramenta de shell, aplicação de patch ou acesso ao GitHub no agente.
A saída é um diff proposto e um parecer. Testes propostos não são testes executados:
antes de aceitar a correção, uma pessoa aplica o diff em checkout descartável,
confere o patch e executa a reprodução e a suíte numa sandbox, guardando a evidência.

No grafo, parecer favorável pausa em interrupt; o terminal mostra proposta e revisão.
Identifique-se e digite APROVAR para aceitar somente a proposta. Qualquer outra
resposta rejeita. Parecer desfavorável ou inválido vai à devolução. Checkpointer e
thread_id mantêm a pausa e a retomada dentro do processo vivo. **O checkpointer em
memória não sobrevive ao encerramento do programa**; para rodar à noite num servidor,
substitua-o por armazenamento persistente e proteja a API de retomada com autenticação.
O nome digitado no terminal é autodeclaração, não autenticação de produção.

## Protocolo de medição
Mesma entrada, modelo, temperatura, seed, teto de 40 chamadas, timeout de 60 s por
requisição e limite de 2.500 tokens de saída por chamada. Sem cache, memória de
conversas anteriores ou retries de transporte. A coordenação hierárquica pode gerar
mais chamadas; isso é parte do tratamento. CrewAI tem limites de iteração próprios.
O limite do adaptador é de 40 chamadas remotas, incluindo as do gerente.

O tempo total usa perf_counter e inclui espera humana no grafo; o rastro também
separa tempo até a primeira saída e duração de cada chamada. Compare tempo de
processamento com tempo de processamento, e descreva a espera humana separadamente.
O script mostra o tempo até a primeira saída para o grafo quando disponível.
Primeira falha é a primeira exceção/configuração inválida observada pelo harness;
uma proposta tecnicamente errada exige inspeção humana e anotação adicional.
Não confunda ausência de exceção com correção da issue. Uma execução por condição
não permite generalizações sobre eficiência ou qualidade dos frameworks.

## Verificação e entrega
```bash
python -m unittest discover -s tests -v
python verificar_publicacao.py
```
Sete testes passaram na preparação. Após a coleta, registre primeiro erro semântico,
saídas, tempos e contagens; mantenha tentativas malsucedidas. Atualize COMPARACAO.md.
O scanner é auxiliar e não substitui revisão manual de segredos nos rastros.

Somente quando o material real e a coleta estiverem completos:
```bash
git init -b main
git add .
git commit -m "Implementa equipe e comparação do exercício 6"
gh repo create dsia-ex06-equipe --public --source=. --remote=origin --push
```
O gh precisa estar autenticado na sua conta. Abra o endereço retornado em janela
anônima e confira main, arquivos e rastros. Então cole a URL na atividade 3533.
Não envie o link antes dessa revisão: o enunciado permite um envio sem reabertura.
