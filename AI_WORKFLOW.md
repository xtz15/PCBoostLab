# PCBoostLab — AI Workflow

## Objetivo deste documento

Este arquivo define como o projeto deve usar ChatGPT, Codex, Claude, Git e GitHub sem gerar conflitos, alterações não rastreadas ou decisões contraditórias.

Ele deve ser lido junto com:

- `PROJECT_CONTEXT.md`
- `docs/roadmap.md`
- `docs/DESIGN.md`
- `docs/CHANGELOG.md`
- `docs/ideias.md`

Em caso de conflito, prevalece esta ordem:

1. regras de segurança do `PROJECT_CONTEXT.md`;
2. diretrizes de UX e engenharia do `docs/DESIGN.md`;
3. fluxo de agentes deste `AI_WORKFLOW.md`;
4. prioridades do `docs/roadmap.md`;
5. histórico do `docs/CHANGELOG.md`;
6. ideias não aprovadas do `docs/ideias.md`.

---

## Estrutura atual de trabalho

### Projeto no ChatGPT: `PCBoostLab`

O Projeto do ChatGPT reúne três chats:

#### `XX - PCBoostLab`

Chat oficial de arquitetura e desenvolvimento.

Responsabilidades:

- definir requisitos;
- organizar o roadmap;
- transformar ideias em tarefas pequenas;
- criar prompts objetivos para o Codex;
- revisar riscos, UX e comportamento esperado;
- orientar testes;
- lembrar o fluxo de commit e `git push`;
- explicar tudo de forma gradual para um desenvolvedor iniciante.

Este chat não deve editar diretamente o código local.

#### `XX - OVERCLOCK atual`

Chat oficial de suporte técnico do computador do usuário.

Responsabilidades:

- BIOS, Windows, drivers e hardware;
- diagnóstico de travamentos;
- temperaturas, voltagens e estabilidade;
- CPU, RAM, GPU, discos e periféricos;
- overclock e undervolt com cautela;
- avaliação de upgrades e compatibilidade;
- análise de prints de HWiNFO, CrystalDiskInfo, BIOS e Gerenciador de Tarefas.

Ele também funciona como fonte de conhecimento prático para as regras de diagnóstico do PCBoostLab, mas não deve comandar diretamente a implementação do software.

#### `XX - OVERCLOCK histórico`

Arquivo histórico da conversa original.

Finalidade:

- consultar decisões antigas;
- recuperar contexto;
- verificar prints, configurações e raciocínios anteriores.

Não deve ser usado como chat principal para novas tarefas.

---

## Papéis das ferramentas e agentes

### Usuário — proprietário do produto e aprovador final

O usuário:

- define prioridades;
- aprova o escopo;
- executa testes;
- informa o comportamento real do programa;
- autoriza ações sensíveis;
- decide se uma recomendação será implementada;
- confirma quando uma etapa está concluída.

Como o usuário é iniciante em programação, toda instrução deve indicar exatamente onde clicar ou qual comando executar.

### ChatGPT — arquiteto, coordenador e revisor funcional

ChatGPT deve:

- consultar a documentação oficial;
- propor uma tarefa pequena por vez;
- explicar riscos antes da implementação;
- criar o prompt para o Codex;
- revisar a resposta do Codex;
- orientar testes manuais;
- verificar se a documentação precisa ser atualizada;
- lembrar do commit e do `git push`.

ChatGPT não deve presumir que consegue acessar automaticamente `D:\PCBoostLab`. Quando necessário, deve pedir um arquivo, um print, a saída de um comando ou usar uma conexão real com o repositório.

### Codex — único implementador principal

Codex trabalha no projeto local:

`D:\PCBoostLab`

Configuração esperada:

- aprovação: a pedido;
- sandbox: gravação no workspace;
- rede: desligada, salvo autorização específica;
- acesso completo ao computador: desligado;
- branch principal atual: `master`;
- uma tarefa pequena por execução.

Codex deve:

- ler a documentação oficial antes de alterar arquivos;
- apresentar plano curto;
- alterar apenas o escopo autorizado;
- manter o aplicativo executável por `python app\main.py`;
- tratar erros;
- não introduzir dependências sem aprovação;
- explicar arquivos criados ou alterados;
- não executar ações administrativas do Windows sem autorização explícita.

Somente o Codex deve editar o código em uma etapa normal. Claude e ChatGPT atuam como revisores e coordenadores.

### Claude — revisor independente

Projeto no Claude:

`PCBoostLab — Revisão`

Claude deve:

- revisar arquitetura, segurança, UX e legibilidade;
- identificar bugs, regressões e casos extremos;
- verificar aderência à documentação;
- separar problemas críticos, importantes e opcionais;
- recomendar testes;
- produzir instruções objetivas para o Codex.

Claude não deve editar a mesma pasta nem atuar simultaneamente com o Codex.

### Git — histórico local

Git registra versões no computador.

Um `commit` salva a versão no repositório local. Ele não envia nada sozinho ao GitHub.

### GitHub — backup e fonte remota oficial

Repositório:

`https://github.com/xtz15/PCBoostLab`

Branch:

`master`

O `git push` envia os commits locais para o GitHub.

---

## Regra principal: um agente editando por vez

Fluxo proibido:

1. Codex altera arquivos;
2. Claude altera os mesmos arquivos;
3. outra IA altera novamente sem commit;
4. o usuário não sabe qual mudança criou o erro.

Fluxo obrigatório:

1. planejar;
2. Codex implementar;
3. usuário testar;
4. Git registrar e enviar;
5. Claude revisar;
6. Codex corrigir, se a correção for aprovada;
7. testar, commitar e enviar novamente.

---

## Ciclo oficial de cada funcionalidade

### 0. Verificar estado

Antes de começar:

```powershell
cd D:\PCBoostLab
git status
```

O ideal é:

```text
nothing to commit, working tree clean
```

Também consultar:

- `PROJECT_CONTEXT.md`;
- `AI_WORKFLOW.md`;
- `docs/roadmap.md`;
- `docs/DESIGN.md`;
- `docs/CHANGELOG.md`.

Se houver alteração pendente, ela deve ser entendida, testada e salva ou descartada antes de iniciar outra tarefa.

### 1. Planejar no `XX - PCBoostLab`

A tarefa deve ser pequena e ter:

- objetivo;
- escopo permitido;
- comportamento esperado;
- arquivos que podem ser alterados;
- proibições;
- testes;
- critério de conclusão.

### 2. Implementar no Codex

O prompt deve exigir:

- plano curto;
- alteração mínima;
- tratamento de erros;
- respeito à documentação;
- nenhuma ação fora do workspace;
- relatório final dos arquivos alterados.

### 3. Testar localmente

Com o ambiente virtual ativo:

```powershell
cd D:\PCBoostLab
.\.venv\Scripts\Activate.ps1
python -m compileall app
python app\main.py
```

Testar também:

- navegação entre telas;
- loading;
- responsividade;
- mensagens de erro;
- repetição da ação;
- fechamento e reabertura;
- ausência de traceback para o usuário.

### 4. Atualizar documentação

Conforme a alteração, atualizar:

- `docs/CHANGELOG.md`;
- `docs/roadmap.md`;
- `PROJECT_CONTEXT.md`;
- `docs/DESIGN.md`, se houver nova regra de UX;
- `docs/ideias.md`, apenas para ideias ainda não aprovadas.

### 5. Salvar no Git e GitHub

```powershell
git status
git add .
git commit -m "tipo: descrição curta"
git push
git status
```

O resultado final deve ser:

```text
nothing to commit, working tree clean
```

### 6. Revisar no Claude

Enviar ao Claude:

```powershell
git show --stat HEAD
```

Para revisão detalhada, enviar também:

```powershell
git show --no-ext-diff HEAD
```

Se a saída for muito grande, enviar somente:

- o resumo do commit;
- os arquivos alterados;
- o código dos arquivos relevantes;
- prints do comportamento.

### 7. Corrigir apenas o que for aprovado

A resposta do Claude não vira código automaticamente.

O chat `XX - PCBoostLab` deve:

- avaliar as recomendações;
- rejeitar sugestões fora do roadmap;
- priorizar problemas reais;
- criar um novo prompt pequeno para o Codex.

---

## Padrão de commits

Usar mensagens em português:

- `feat: adiciona diagnóstico de GPU`
- `fix: corrige travamento da tela de limpeza`
- `docs: atualiza fluxo de revisão`
- `refactor: separa coleta de discos da interface`
- `test: adiciona testes do scanner de temporários`
- `chore: atualiza dependências aprovadas`

Evitar commits vagos:

- `mudanças`
- `teste`
- `arrumei`
- `versão nova`

Preferência: uma tarefa lógica por commit.

---

## Classificação de alterações

### Somente leitura

Exemplos:

- diagnóstico de CPU, RAM, GPU e discos;
- leitura de processos;
- geração de relatório;
- consulta de configurações.

Podem ser implementadas sem privilégio administrativo, salvo limitações do Windows.

### Seguras e reversíveis

Exemplos:

- abrir ferramentas nativas;
- limpar apenas categorias previamente analisadas e confirmadas;
- alterar opção com estado anterior salvo;
- criar relatório e log.

Exigem prévia, confirmação e tratamento de erro.

### Avançadas

Exemplos:

- Registro;
- serviços;
- plano de energia;
- inicialização rápida;
- HAGS;
- indexação;
- configurações administrativas.

Exigem:

- benefício;
- risco;
- estado anterior;
- forma de reversão;
- confirmação explícita;
- log;
- privilégio administrativo quando necessário.

### Proibidas como padrão

- desativar Defender;
- desativar Firewall;
- desativar isolamento do núcleo;
- desativar serviços críticos em massa;
- alterar BCD/timers sem pesquisa e justificativa;
- aplicar overclock automático;
- alterar BIOS automaticamente;
- burlar anti-cheat;
- prometer ganho fixo de FPS;
- apagar arquivos pessoais;
- esconder alterações do usuário.

---

## Regras de UX e desempenho

- nenhuma operação pesada na thread principal;
- loading imediato;
- mensagens de status reais;
- não inventar percentual ou tempo restante;
- impedir cliques duplicados;
- ignorar resultado antigo se o usuário trocar de tela;
- não iniciar múltiplas coletas iguais;
- registrar erro técnico no log;
- mostrar mensagem simples ao usuário;
- reaproveitar dados recentes quando apropriado;
- evitar leituras excessivas de sensores.

---

## Limpeza Segura

A limpeza não deve ser vendida como aumento garantido de FPS.

Regras:

- limpeza geral recomendada no máximo semanalmente;
- mostrar data da última execução;
- avisar contra repetição desnecessária;
- analisar antes de apagar;
- mostrar categorias e tamanho estimado;
- pedir confirmação;
- registrar o resultado;
- nunca apagar Documentos, Downloads, Área de Trabalho, Google Drive, OneDrive ou arquivos pessoais sem seleção explícita.

Prefetch:

- deve existir como opção separada;
- não deve ser selecionado silenciosamente;
- explicar que a limpeza frequente não traz ganho consistente;
- avisar que o Windows reconstruirá o cache;
- recomendar uso apenas ocasional ou para diagnóstico de cache corrompido.

Limpeza de Disco:

- preferir ferramenta/API nativa;
- não automatizar cegamente todas as categorias;
- categorias potencialmente sensíveis devem ter explicação;
- downloads nunca devem ser selecionados automaticamente;
- a ação administrativa deve ser explícita.

---

## Segurança comercial e licenças

Antes de vender ou distribuir:

- revisar licença de todas as dependências;
- não embutir ferramentas de terceiros sem licença compatível;
- não distribuir a edição gratuita do HWiNFO como parte comercial sem autorização/licença apropriada;
- manter avisos de licença exigidos;
- criar termos de uso e política de privacidade;
- não coletar telemetria sem consentimento;
- não enviar diagnóstico para servidor sem autorização explícita;
- assinar o executável quando o produto estiver maduro;
- evitar promessas absolutas de desempenho ou segurança.

---

## Segredos e dados privados

Nunca enviar ao GitHub:

- senhas;
- tokens;
- chaves de API;
- certificados;
- cookies;
- dados de clientes;
- logs com informações sensíveis;
- relatórios pessoais gerados;
- arquivos `.env`.

Manter no `.gitignore`:

- `.venv/`;
- `__pycache__/`;
- logs;
- relatórios gerados;
- backups gerados;
- builds;
- arquivos temporários;
- segredos.

---

## Recuperação rápida

Ver estado:

```powershell
git status
```

Ver últimos commits:

```powershell
git log --oneline -10
```

Ver última alteração:

```powershell
git show --stat HEAD
```

Descartar alteração não commitada de um arquivo somente após confirmação:

```powershell
git restore caminho\do\arquivo
```

Não usar `git reset --hard`, `git clean -fd` ou force push sem revisão e confirmação expressas.

---

## Regra de encerramento

Uma tarefa só termina quando:

- o app foi testado;
- a documentação necessária foi atualizada;
- o commit foi criado;
- o `git push` foi concluído;
- `git status` retorna árvore limpa;
- o próximo passo está registrado no roadmap ou no contexto.
