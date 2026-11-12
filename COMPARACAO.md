# Comparação — protocolo e situação atual

**Coleta empírica pendente.** As tentativas disponíveis pararam sem chamar o
modelo; não medem desempenho, qualidade ou custo das três versões. A fixture é
sintética. Não há alegação de que as duas crews tenham concluído uma execução.

| Versão | Tempo com modelo | Chamadas ao modelo | Primeira falha | Situação |
|---|---|---|---|---|
| crew_sequencial | Pendente | 0 nas tentativas bloqueadas | Configuração ausente | Não executada com modelo |
| crew_hierarquica | Pendente | 0 nas tentativas bloqueadas | Configuração ausente | Não executada com modelo |
| grafo | Pendente | 0 nas tentativas bloqueadas | Configuração ausente | Não executada com modelo |

## Entrada e medidas
As tentativas bloqueadas usam o mesmo JSON canônico, com o mesmo hash SHA-256:

`08416469935a410e2cc97f774a160d6d0e9b6e1bdcb03e47e35ccca6be4fba3c`

A mesma entrada deve ser repetida na coleta real. A contagem é feita no único
adaptador compartilhado, incluindo gerente e delegações; tentativas são contadas
antes de invocar o serviço, conclusões após a resposta. A validação sem chave para
antes da invocação: zero chamadas não é uma execução bem-sucedida.
Tempo total usa relógio monotônico. No grafo, tempo até primeira saída separa a
espera humana do processamento. Registre também erro semântico observado pela
pessoa, em adição à primeira falha técnica registrada automaticamente.

## O que foi preciso declarar
| Versão | Declarado no projeto | Gerenciado pela ferramenta | Limitação |
|---|---|---|---|
| Crew sequencial | Três papéis, ordem, agente por tarefa, contexto anterior e expected_output | Laço do agente e transmissão dos resultados | Esperado não garante correto; falta validação humana do diff |
| Crew hierárquica | Mesmos especialistas e tarefas, gerente, contexto, orçamento | Delegação e coordenação mediadas pelo gerente | Pode delegar mal ou consumir chamadas extras; medir em vez de presumir |
| Grafo | Estado tipado, nós, arestas, roteamento por parecer, interrupt, thread_id e checkpointer | Agendamento dos nós e pausa/retomada | Checkpointer em memória não é persistência durável |

A crew declara uma expectativa de saída, mas não torna prova de teste automática.
O grafo explicita no código a devolução e o portão humano; isso tampouco verifica
sozinho se o código proposto resolve a issue. Em todas as versões a pessoa decide.

## Como concluir a análise
Após rodar as três condições com modelo e uma issue real, mantenha os rastros,
execute comparar.py e substitua este aviso por uma análise dos resultados obtidos.
Informe patch proposto, teste reproduzido, suíte, aceitação humana, modelo retornado,
ordem de execução e limitações. Uma issue e uma rodada não sustentam generalizações.
Não concluir que a ferramenta é mais rápida ou melhor com base nos testes locais.
