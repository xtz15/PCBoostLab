# PCBoostLab — Onde colocar cada arquivo e informação

## 1. Repositório local e GitHub

Pasta local:

`D:\PCBoostLab`

Devem ficar no repositório:

- `PROJECT_CONTEXT.md`
- `AI_WORKFLOW.md`
- `docs/roadmap.md`
- `docs/ideias.md`
- `docs/DESIGN.md`
- `docs/CHANGELOG.md`
- `docs/PROJECT_TRANSITION_REPORT.md`
- código em `app/`
- `requirements.txt`
- `.gitignore`
- arquivos `.gitkeep` necessários

Não devem ser enviados ao GitHub:

- `.venv/`
- `__pycache__/`
- `.env`
- senhas e tokens
- certificados
- logs gerados
- relatórios gerados
- backups gerados
- builds temporários
- dados de clientes

## 2. Projeto no ChatGPT `PCBoostLab`

Chats já incluídos:

- `XX - PCBoostLab`
- `XX - OVERCLOCK atual`
- `XX - OVERCLOCK histórico`

Arquivos recomendados na área de arquivos/conhecimento do Projeto:

- `PROJECT_CONTEXT.md`
- `AI_WORKFLOW.md`
- `docs/roadmap.md`
- `docs/DESIGN.md`
- `docs/CHANGELOG.md`
- `docs/ideias.md`
- `docs/PROJECT_TRANSITION_REPORT.md`
- opcional: `requirements.txt`

Importante:

O ChatGPT comum não lê automaticamente `D:\PCBoostLab`. Os arquivos do Projeto são cópias. Quando a documentação mudar de forma relevante, substitua/atualize os arquivos enviados ao Projeto, salvo se estiver usando uma conexão real com o GitHub.

Não é necessário subir:

- `.venv`
- logs
- relatórios gerados
- backups
- todos os arquivos de código a cada pequena alteração

Para analisar um bug específico, envie apenas:

- print;
- erro;
- arquivo relevante;
- saída de `git show`;
- comportamento esperado e observado.

## 3. Codex

Não é necessário fazer upload manual.

Codex trabalha diretamente em:

`D:\PCBoostLab`

Ele deve receber acesso apenas ao workspace e ler os documentos locais.

Antes de uma tarefa, peça:

- leitura da documentação;
- plano curto;
- escopo limitado;
- nenhuma alteração fora do workspace.

## 4. Projeto no Claude `PCBoostLab — Revisão`

Manter como conhecimento permanente:

- `PROJECT_CONTEXT.md`
- `AI_WORKFLOW.md`
- `docs/roadmap.md`
- `docs/DESIGN.md`
- `docs/CHANGELOG.md`
- `docs/ideias.md`
- `docs/PROJECT_TRANSITION_REPORT.md`
- opcional: `requirements.txt`

Para cada revisão, fornecer:

- `git show --stat HEAD`;
- `git show --no-ext-diff HEAD`, se couber;
- ou somente os arquivos alterados;
- prints do comportamento;
- erros observados.

Não enviar:

- `.venv`
- logs pessoais
- relatórios com dados privados
- repositório inteiro em toda revisão
- segredos

## 5. Chat `XX - OVERCLOCK atual`

Não precisa receber o código do PCBoostLab.

Ele deve receber:

- prints do PC;
- HWiNFO;
- CrystalDiskInfo;
- BIOS;
- Gerenciador de Tarefas;
- sintomas;
- resultados de testes.

As conclusões técnicas úteis ao produto podem depois ser transformadas em requisitos no `XX - PCBoostLab`.

## 6. Chat `XX - OVERCLOCK histórico`

Não adicionar arquivos novos, salvo para preservar algo exclusivamente histórico.

Use apenas como consulta.

## 7. Sincronização dos documentos

Ao alterar documentação:

1. salvar com `Ctrl + S`;
2. testar se aplicável;
3. fazer commit;
4. fazer `git push`;
5. atualizar as cópias nos Projetos do ChatGPT e Claude quando a mudança for relevante.

## 8. Arquivos novos a criar agora

Na raiz:

- `AI_WORKFLOW.md`

Em `docs/`:

- `PROJECT_TRANSITION_REPORT.md`

Opcional em `docs/`:

- `CLAUDE_REVIEW_PROMPT.md`
- `CHATGPT_HANDOFF_PROMPT.md`
- `FILE_PLACEMENT_CHECKLIST.md`

Depois:

```powershell
git status
git add .
git commit -m "docs: adiciona fluxo de IA e relatorio de transicao"
git push
git status
```
