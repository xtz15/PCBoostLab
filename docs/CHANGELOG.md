# PCBoostLab - Changelog

Todas as alterações relevantes do projeto devem ser registradas neste arquivo.

O formato segue uma adaptação simples do padrão Keep a Changelog.

---

## [Não lançado]

### Em desenvolvimento

- Módulo de Limpeza Segura.

### Alterado

- Prévia da Limpeza Segura agora exibe resumo da análise com total estimado, contagem de categorias disponíveis e categorias sem acesso, sem executar exclusão de arquivos.
- Prévia da Limpeza Segura agora mostra explicações específicas para cada categoria, incluindo o que é, benefício, risco, necessidade de administrador, possibilidade de desfazer e recomendação de uso.
- Prévia da Limpeza Segura agora mostra a quantidade de arquivos encontrados em cada categoria após a análise.

### Corrigido

- Corrigido o resumo da Limpeza Segura para não aparecer com valores zerados quando a lista de categorias estiver vazia.
- Categorias indisponíveis agora não exibem mais a contagem de arquivos com valor zero de forma enganosa.

### Adicionado

- Adicionados testes automatizados para a análise e resumo da Limpeza Segura usando unittest.
- Adicionada seleção visual das categorias na prévia da Limpeza Segura, com resumo separado e sem executar qualquer exclusão de arquivos.

---

## [0.1.0]

### Adicionado

- Estrutura modular inicial.
- Interface principal com CustomTkinter.
- Painel com resumo do computador.
- Diagnóstico de CPU.
- Diagnóstico de memória RAM.
- Diagnóstico do sistema operacional.
- Diagnóstico de processos por uso de CPU.
- Diagnóstico de processos por uso de RAM.
- Diagnóstico de discos e partições.
- Alertas visuais para uso elevado de CPU, RAM e armazenamento.
- Geração de relatórios em TXT.
- Sistema de logs.
- Carregamento em segundo plano.
- Indicadores de loading.
- Tratamento de erros sem exibir traceback ao usuário.
- Integração com Git.
- Integração com GitHub.
- Documentação inicial do projeto.

### Corrigido

- Processos Idle removidos da lista de maior consumo.
- Valores irreais de uso de CPU corrigidos.
- Travamento da interface ao abrir o Diagnóstico.
- Travamento da interface ao abrir o Painel.

### Segurança

- Diagnósticos implementados apenas em modo de leitura.
- Nenhum processo é encerrado automaticamente.
- Nenhuma configuração do Windows é alterada.
- Nenhuma ação administrativa é executada automaticamente.

---

## Convenções

Usar as categorias abaixo quando aplicável:

- `Adicionado`
- `Alterado`
- `Corrigido`
- `Removido`
- `Segurança`

Novas funcionalidades devem ser registradas inicialmente em `[Não lançado]`.

Quando uma versão for concluída, o conteúdo correspondente deve ser movido para uma nova seção numerada.