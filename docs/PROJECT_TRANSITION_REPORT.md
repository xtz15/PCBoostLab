# PCBoostLab — Relatório Global de Transição

## Finalidade

Este relatório registra a origem do projeto, o que foi feito na conversa histórica, como os chats e agentes foram organizados e qual é o estado conhecido no momento da transição.

Ele evita depender de uma conversa muito longa para recuperar contexto.

---

## 1. Origem

A conversa original começou como suporte técnico do computador do usuário.

Foram analisados:

- CPU, RAM, GPU, discos e temperaturas;
- BIOS ASUS;
- pagefile;
- Windows Search;
- inicialização;
- navegadores;
- NVIDIA;
- Autoruns;
- serviços e processos;
- uso de dois monitores;
- comportamento do Microsoft Defender;
- CS2 e otimizações.

A partir dessa experiência surgiu a ideia de desenvolver um aplicativo comercial próprio para diagnóstico e otimização assistida de PCs.

O conceito deixou de ser um “booster milagroso” e passou a ser:

**diagnóstico + explicação + otimização reversível + recomendação técnica.**

---

## 2. Objetivo do produto

O PCBoostLab pretende ser um aplicativo desktop Windows para usuários comuns e gamers.

Diferenciais pretendidos:

- diagnosticar antes de alterar;
- explicar cada função;
- informar benefício e risco;
- indicar quando uma ação não é necessária;
- oferecer reversão quando possível;
- gerar relatórios;
- orientar o usuário leigo;
- separar otimizações seguras de avançadas;
- não prometer ganho mágico de FPS.

Há intenção futura de comercialização. Por isso, segurança, licenças, transparência, termos de uso e privacidade são requisitos do produto.

---

## 3. Estrutura de chats no ChatGPT

Foi criado um Projeto no ChatGPT chamado:

`PCBoostLab`

Foram movidos para ele três chats:

### `XX - PCBoostLab`

Chat oficial de desenvolvimento.

Usado para:

- arquitetura;
- roadmap;
- prompts para Codex;
- testes;
- Git/GitHub;
- segurança;
- UX;
- planejamento dos módulos.

### `XX - OVERCLOCK atual`

Chat oficial de suporte do computador.

Usado para:

- hardware;
- BIOS;
- Windows;
- drivers;
- temperaturas;
- estabilidade;
- overclock/undervolt;
- upgrades;
- diagnóstico real do PC.

### `XX - OVERCLOCK histórico`

Conversa original extensa.

Deve ser tratada como arquivo histórico e fonte de consulta, não como chat operacional.

---

## 4. Projeto de revisão no Claude

Foi criado no Claude o projeto:

`PCBoostLab — Revisão`

Foram adicionados:

- `PROJECT_CONTEXT.md`;
- `docs/roadmap.md`;
- `docs/ideias.md`;
- `docs/DESIGN.md`;
- `docs/CHANGELOG.md`.

Claude recebeu instruções para atuar somente como revisor independente.

Ele não deve ser o implementador principal nem editar simultaneamente com o Codex.

---

## 5. Codex e VS Code

Ferramentas configuradas:

- Visual Studio Code;
- extensão oficial do Codex;
- Python 3.12;
- Git;
- ambiente virtual;
- PowerShell;
- GitHub.

Projeto local:

`D:\PCBoostLab`

Ambiente virtual:

`D:\PCBoostLab\.venv`

Repositório remoto:

`https://github.com/xtz15/PCBoostLab`

Branch:

`master`

Configuração de segurança esperada do Codex:

- aprovação a pedido;
- gravação somente no workspace;
- rede desligada;
- acesso completo desligado;
- implementação em tarefas pequenas.

---

## 6. Stack conhecida

- Python 3.12;
- CustomTkinter;
- psutil;
- py-cpuinfo;
- WMI;
- pywin32;
- GPUtil;
- Git;
- GitHub.

Antes de distribuição comercial, todas as dependências precisam passar por auditoria de licença e manutenção.

---

## 7. Estrutura conhecida do repositório

Arquivos e pastas relevantes:

```text
PCBoostLab/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── logger.py
│   │   └── models.py
│   ├── diagnostics/
│   │   ├── system_info.py
│   │   ├── processes.py
│   │   └── disks.py
│   ├── reports/
│   │   └── report_builder.py
│   ├── cleaning/
│   │   └── módulo iniciado; confirmar conteúdo atual antes de continuar
│   └── ui/
├── data/
│   ├── logs/
│   ├── reports/
│   └── backups/
├── docs/
│   ├── roadmap.md
│   ├── ideias.md
│   ├── DESIGN.md
│   └── CHANGELOG.md
├── PROJECT_CONTEXT.md
├── AI_WORKFLOW.md
├── requirements.txt
└── .gitignore
```

A estrutura exata deve sempre ser confirmada no repositório antes de propor alterações.

---

## 8. Funcionalidades implementadas

### Interface

- janela principal em CustomTkinter;
- menu lateral;
- Painel;
- Diagnóstico;
- Otimizações Seguras;
- Otimizações Avançadas;
- Limpeza;
- Restauração;
- Relatórios.

Algumas páginas ainda são estrutura visual e não executam otimizações reais.

### Painel

- resumo da CPU;
- RAM total;
- uso atual de RAM;
- sistema operacional;
- carregamento em segundo plano;
- interface corrigida para não congelar.

### Diagnóstico

- CPU;
- RAM;
- sistema;
- processos;
- discos;
- loading;
- botão para atualizar;
- alertas visuais;
- rolagem.

### Processos

- top 10 por RAM;
- top 10 por CPU;
- PID;
- tratamento de acesso negado;
- exclusão de PID 0 e Idle;
- normalização para evitar valores irreais;
- somente leitura;
- nenhum processo é encerrado.

### Discos

- unidades e partições;
- sistema de arquivos;
- total, usado e livre;
- percentual de uso;
- alertas por ocupação/espaço;
- somente leitura.

### Relatórios

- geração de relatório TXT;
- diretório local de relatórios;
- arquivos gerados excluídos do Git.

### Logs

- logger local;
- erros técnicos registrados;
- objetivo de não mostrar traceback ao usuário.

### Limpeza Segura

O módulo foi iniciado.

Antes de implementar algo novo, é obrigatório:

1. verificar `git status`;
2. ler o código existente em `app/cleaning/`;
3. executar o app;
4. confirmar o que já funciona;
5. continuar a partir do estado real, sem recriar do zero.

---

## 9. Problemas encontrados e corrigidos

- `.venv` foi adicionada acidentalmente ao staging do Git e depois excluída pelo `.gitignore`;
- Git foi configurado com nome/e-mail local;
- warnings LF/CRLF foram identificados como normais no Windows;
- travamento ao abrir Diagnóstico foi corrigido com thread/loading;
- travamento ao voltar ao Painel foi corrigido;
- `System Idle Process` deixou de aparecer como grande consumidor;
- uso de CPU de processos foi normalizado;
- pagefile do PC do usuário foi ajustado, mas isso pertence ao suporte técnico, não ao app;
- consumo alto do Defender durante desenvolvimento foi associado à varredura da `.venv`;
- ficou definido que não se deve desativar Defender como solução padrão.

---

## 10. Documentação criada e padronizada

### `PROJECT_CONTEXT.md`

Constituição do projeto:

- objetivo;
- público;
- stack;
- funcionalidades;
- segurança;
- UX;
- próxima etapa;
- fluxo Git;
- fontes oficiais.

### `docs/roadmap.md`

Ordem oficial das versões.

### `docs/ideias.md`

Banco de ideias não aprovadas.

### `docs/DESIGN.md`

Diretrizes de UX, fluidez, cores, mensagens e desempenho da interface.

### `docs/CHANGELOG.md`

Histórico do que foi adicionado, corrigido e protegido.

### `AI_WORKFLOW.md`

Coordenação de ChatGPT, Codex, Claude, Git e GitHub.

---

## 11. Fluxo obrigatório de desenvolvimento

1. Verificar `git status`.
2. Ler documentação.
3. Planejar no `XX - PCBoostLab`.
4. Codex implementar uma tarefa pequena.
5. Testar localmente.
6. Atualizar documentação aplicável.
7. Commitar.
8. Fazer `git push`.
9. Confirmar árvore limpa.
10. Claude revisar commits relevantes.
11. Codex corrigir somente recomendações aprovadas.

---

## 12. Próxima etapa conhecida

Retomar o módulo de Limpeza Segura.

Comportamento pretendido:

- análise antes da exclusão;
- loading e thread;
- frequência recomendada;
- aviso contra uso diário;
- tamanhos estimados;
- categorias;
- confirmação;
- log;
- relatório;
- comparação antes/depois.

Prefetch deve existir como opção com aviso técnico e não como “boost” garantido.

A Limpeza de Disco do Windows pode ser integrada, mas não deve selecionar cegamente categorias sensíveis nem Downloads.

---

## 13. Pontos futuros importantes

- auditoria de dependências e licenças;
- não depender comercialmente do HWiNFO gratuito;
- diagnóstico de GPU e sensores;
- SMART e saúde de SSD;
- restauração e rollback;
- otimizações seguras;
- separação entre interface sem admin e helper elevado;
- testes automatizados;
- instalador;
- assinatura de código;
- termos de uso;
- política de privacidade;
- eventual licença gratuita/Pro.

---

## 14. Regra de confiança

O estado do Git e o conteúdo do repositório são mais confiáveis que indicadores visuais desatualizados do VS Code ou GitLens.

Sempre confirmar com:

```powershell
git status
git log --oneline -10
```

Uma IA nunca deve afirmar que um arquivo existe ou que uma funcionalidade está concluída sem conferir evidência atual.
