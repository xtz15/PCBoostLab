# PCBoostLab - Project Context

## Objetivo

O PCBoostLab é um aplicativo desktop para Windows desenvolvido em Python com CustomTkinter.

O objetivo é centralizar diagnóstico, manutenção, limpeza segura, recomendações e relatórios técnicos em uma interface simples.

O projeto não deve aplicar overclock automático.

Toda alteração no computador deve ser explicada, controlada e reversível quando possível.

## Público-alvo

Usuários Windows que desejam:

- diagnosticar problemas;
- entender o estado do computador;
- realizar limpezas seguras;
- receber recomendações;
- gerar relatórios.

O usuário não precisa ter conhecimento técnico avançado.

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

## Funcionalidades implementadas

### Painel

- resumo do computador;
- carregamento em segundo plano;
- interface responsiva.

### Diagnóstico

- CPU;
- RAM;
- sistema operacional;
- processos;
- discos.

### Processos

- top 10 por uso de RAM;
- top 10 por uso de CPU;
- somente leitura;
- não encerra processos;
- ignora PID 0 e processos Idle.

### Discos

- unidade;
- sistema de arquivos;
- espaço total;
- espaço usado;
- espaço livre;
- percentual de uso.

### Relatórios

- geração de relatório em TXT.

### Logs

- erros são registrados em arquivo;
- o usuário não deve receber traceback na interface.

## Regras de segurança

- não desativar Defender;
- não desativar firewall;
- não alterar serviços críticos automaticamente;
- não aplicar ajustes de Registro sem explicação e reversão;
- não executar ações administrativas sem confirmação;
- não apagar arquivos sem prévia;
- não prometer ganho de FPS sem medição;
- toda ação avançada deve informar benefício, risco e como desfazer.

## Regras de interface

O aplicativo deve parecer fluido.

Se uma operação puder demorar:

- mostrar loading;
- executar em segundo plano;
- manter a janela responsiva;
- mostrar mensagem amigável;
- impedir cliques duplicados durante a execução.

## Próxima etapa

Desenvolver o módulo de Limpeza Segura.

Requisitos:

- mostrar frequência recomendada;
- avisar que limpeza diária não é recomendada;
- incluir análise de temporários;
- incluir Prefetch com aviso de uso ocasional;
- incluir limpeza de miniaturas;
- abrir a Limpeza de Disco do Windows;
- mostrar prévia antes de apagar;
- mostrar espaço estimado;
- registrar resultado em log;
- gerar relatório.

## Fluxo obrigatório após cada alteração

Sempre seguir esta ordem:

1. Testar o aplicativo.
2. Rodar:

```powershell
git status
