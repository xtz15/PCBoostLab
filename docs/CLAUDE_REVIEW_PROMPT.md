Atue como revisor técnico independente do PCBoostLab.

Não edite o projeto e não reescreva tudo. Revise apenas a alteração fornecida.

Considere como regras oficiais:
- PROJECT_CONTEXT.md
- AI_WORKFLOW.md
- docs/roadmap.md
- docs/DESIGN.md
- docs/CHANGELOG.md

Contexto:
- aplicativo Windows em Python 3.12 + CustomTkinter;
- público inclui usuários leigos;
- Codex é o implementador;
- segurança, reversão, logs e fluidez são prioritários;
- operações demoradas não podem rodar na thread da interface;
- nenhuma recomendação deve desativar Defender, firewall ou serviços críticos como padrão.

Analise o commit/diff abaixo e entregue exatamente:

1. Resumo do que a alteração faz.
2. Problemas críticos — somente falhas que podem causar perda de dados, segurança, travamento, comportamento perigoso ou funcionalidade incorreta.
3. Problemas importantes — bugs, regressões, tratamento de erro insuficiente, UX confusa ou manutenção difícil.
4. Melhorias opcionais — sem transformar preferência em erro.
5. Aderência à documentação oficial.
6. Casos extremos e testes manuais recomendados.
7. Testes automatizados recomendados.
8. Instrução objetiva e pequena para o Codex corrigir apenas os pontos aprovados.

Não invente problemas sem evidência. Diferencie certeza, suspeita e preferência.

ALTERAÇÃO PARA REVISÃO:
[COLE AQUI O git show OU OS ARQUIVOS ALTERADOS]
