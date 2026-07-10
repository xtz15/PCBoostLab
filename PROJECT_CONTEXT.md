# PCBoostLab - Project Context

## Objetivo

O PCBoostLab é um aplicativo desktop para Windows desenvolvido em Python com CustomTkinter.

O objetivo é centralizar diagnóstico, manutenção, limpeza segura, recomendações e relatórios técnicos em uma interface simples.

O projeto não deve aplicar overclock automático.

Toda alteração no computador deve ser explicada, controlada e reversível quando possível.

---

## Público-alvo

Usuários Windows que desejam:

- diagnosticar problemas;
- entender o estado do computador;
- realizar limpezas seguras;
- receber recomendações;
- gerar relatórios.

O usuário não precisa ter conhecimento técnico avançado.

---

## Tecnologias

- Python 3.12
- CustomTkinter
- psutil
- WMI
- py-cpuinfo
- pywin32
- GPUtil
- Git
- GitHub

---

## Funcionalidades implementadas

### Painel

- Resumo do computador.
- Carregamento em segundo plano.
- Interface responsiva.

### Diagnóstico

- CPU.
- RAM.
- Sistema operacional.
- Processos.
- Discos.

### Processos

- Top 10 por uso de RAM.
- Top 10 por uso de CPU.
- Somente leitura.
- Não encerra processos.
- Ignora PID 0 e processos Idle.

### Discos

- Unidade.
- Sistema de arquivos.
- Espaço total.
- Espaço usado.
- Espaço livre.
- Percentual de uso.

### Relatórios

- Geração de relatório TXT.

### Logs

- Erros registrados em arquivo.
- O usuário nunca deve receber traceback na interface.

---

## Regras de segurança

- Nunca desativar Defender automaticamente.
- Nunca desativar Firewall automaticamente.
- Nunca alterar serviços críticos automaticamente.
- Nunca alterar Registro do Windows sem explicação e confirmação.
- Nunca apagar arquivos automaticamente sem mostrar o que será removido.
- Nunca prometer ganho de desempenho sem evidências.
- Toda alteração deve informar:
  - benefício;
  - risco;
  - como desfazer.

---

## Regras de interface

O aplicativo deve sempre parecer fluido.

Se alguma operação puder demorar:

- Mostrar loading.
- Executar em segundo plano.
- Manter a interface responsiva.
- Mostrar mensagem amigável.
- Evitar travamentos.
- Evitar cliques duplicados.

---

## Próxima funcionalidade

Desenvolver o módulo **Limpeza Segura**.

Objetivos:

- Informar frequência recomendada.
- Avisar que limpeza diária não é recomendada.
- Analisar arquivos temporários.
- Limpar Prefetch com aviso.
- Limpar cache de miniaturas.
- Integrar a Limpeza de Disco do Windows.
- Exibir prévia antes da limpeza.
- Mostrar espaço estimado.
- Registrar resultado em log.
- Gerar relatório.

---

## Documentação oficial

Antes de implementar qualquer funcionalidade, consultar:

- `PROJECT_CONTEXT.md`
- `docs/roadmap.md`
- `docs/ideias.md`
- `docs/DESIGN.md`
- `docs/CHANGELOG.md`

Em caso de conflito:

1. PROJECT_CONTEXT.md
2. DESIGN.md
3. roadmap.md
4. CHANGELOG.md

O arquivo `ideias.md` contém apenas ideias futuras e não representa funcionalidades aprovadas.

---

## Fluxo obrigatório após cada alteração

Sempre seguir esta sequência:

1. Testar o aplicativo.
2. Atualizar a documentação necessária.
3. Executar:

```powershell
git status
git add .
git commit -m "descrição da alteração"
git push
git status
```

Somente iniciar uma nova funcionalidade quando o Git retornar:

```text
nothing to commit, working tree clean
```