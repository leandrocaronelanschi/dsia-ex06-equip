# Fronteira de segurança

## Conta e permissões
Em operação, usar conta dedicada `lavra-bot`, separada de Davi e Marina, sem acesso
a banco, redes ou segredos de produção. Checkout descartável do repositório com
leitura dos arquivos públicos selecionados. Escrita restrita a rastros e propostas
em diretório de trabalho isolado. A implementação presente não tem ferramentas
para shell, edição de origem, GitHub, merge, fechamento de issue ou deploy.

A chave do modelo deve ser exclusiva do experimento, com limite de gastos e sem
permissão administrativa; deve ficar apenas em .env local ou cofre do servidor.
O modelo recebe somente o recorte aprovado. Não usar a conta de Marina que acessa
produção. Não colocar token de GitHub no processo de inferência. A publicação
acadêmica deve ser feita pelo operador autenticado, após inspeção do pacote.

## Onde fica a pessoa
No fluxo sequencial e hierárquico, a execução termina com proposta aguardando
revisão humana. No grafo, o revisor desfavorável encaminha à devolução; parecer
favorável alcança interrupt. Marina inspeciona diff, critérios, lacunas e prova
de testes antes de aceitar a proposta. A aprovação permite somente aceitar a
proposta; não libera nenhuma ferramenta nem concede permissão para merge.

Merge, deploy, encerramento de issue e escrita em produção são sempre decisões
e ações humanas fora deste programa. Run concluída não significa issue resolvida.
A pessoa precisa verificar os testes e o comportamento observado.

## Registro e proteção
Cada rastro tem versão do fluxo, thread quando aplicável, hash da entrada, seed,
modelo configurado e retornado, eventos ordenados, duração, tentativas, respostas,
uso de tokens quando fornecido, primeira falha e saída. Gerente usa o mesmo
adaptador; suas chamadas também são contadas. Só campos explícitos são gravados.
Não se serializam ambiente, chave ou headers. Ainda assim código, issue e resposta
podem conter segredos: selecionar entrada pública, executar scanner e revisar
manualmente antes de publicar. Checkpoints de produção também devem ser privados.

Issue e código são dados não confiáveis; prompts orientam ignorar instruções
embutidas. Essa orientação não é barreira suficiente: a proteção principal é a
ausência de ferramentas e credenciais perigosas. Saídas nunca são executadas.
Há teto de chamadas e timeout, mas custos ainda dependem do provedor e gerente.

## Limitações da demonstração
O checkpointer é InMemorySaver e perde estado ao encerrar o processo. O nome no
terminal é autodeclarado. Um serviço real precisa de checkpointer durável,
autenticação do revisor, autorização no endpoint de retomada, isolamento de rede,
limites de recursos e proteção de branch. Não alegamos que esses controles de
infraestrutura foram implantados. Não há ações irreversíveis feitas pelo agente.
