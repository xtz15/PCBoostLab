# PCBoostLab - Diretrizes de Design e Experiência

## Objetivo

Este documento define os princípios de interface, experiência do usuário e comportamento visual do PCBoostLab.

O aplicativo deve parecer confiável, rápido, simples e profissional.

---

## Princípios gerais

- A interface deve ser clara e organizada.
- O usuário deve entender o que cada função faz antes de executá-la.
- O aplicativo não deve parecer um “booster milagroso”.
- O foco deve ser diagnóstico, transparência, segurança e orientação.
- O visual deve ser moderno, mas sem excesso de animações.
- Informações técnicas devem ser traduzidas para linguagem simples.

---

## Fluidez

A interface nunca deve congelar durante operações demoradas.

Se uma ação puder levar mais de alguns instantes:

- mostrar loading;
- mostrar mensagem de status;
- executar a tarefa em segundo plano;
- impedir cliques duplicados;
- manter a janela responsiva;
- informar quando a ação terminar;
- informar erro de forma amigável.

Exemplos de mensagens:

- `Carregando diagnóstico...`
- `Analisando arquivos temporários...`
- `Isso pode levar alguns segundos.`
- `Operação concluída com sucesso.`
- `Não foi possível concluir a operação.`

---

## Hierarquia visual

Cada tela deve ter:

1. Título principal.
2. Subtítulo explicativo.
3. Conteúdo organizado em cards ou seções.
4. Ações principais claramente destacadas.
5. Avisos visíveis antes de operações sensíveis.

---

## Cores de status

Usar cores com significado consistente:

- Verde: normal, seguro ou concluído.
- Amarelo: atenção ou recomendação.
- Vermelho: risco, erro ou situação crítica.
- Azul: informação ou ação neutra.
- Cinza: informação secundária ou indisponível.

Nunca depender apenas de cor. Sempre incluir texto explicativo.

---

## Tipografia e leitura

- Usar fontes legíveis.
- Evitar textos pequenos.
- Evitar blocos longos sem espaçamento.
- Usar linguagem simples para usuários iniciantes.
- Permitir explicações mais técnicas em áreas avançadas.
- Priorizar conforto visual para leitura prolongada.

---

## Botões e ações

Todo botão deve indicar claramente o que fará.

Exemplos adequados:

- `Analisar`
- `Atualizar diagnóstico`
- `Gerar relatório`
- `Abrir ferramenta do Windows`
- `Aplicar`
- `Desfazer`
- `Cancelar`

Evitar textos vagos como:

- `Boost`
- `Otimizar tudo`
- `Acelerar PC`
- `Corrigir geral`

Ações sensíveis devem exigir confirmação.

---

## Explicação das funcionalidades

Toda otimização deve exibir:

- o que ela faz;
- benefício esperado;
- risco;
- necessidade de administrador;
- possibilidade de reversão;
- quando é recomendado usar;
- quando não é recomendado usar.

---

## Loading e progresso

Quando possível, mostrar:

- estado atual;
- percentual;
- etapa em execução;
- tempo estimado apenas quando houver estimativa confiável.

Não mostrar tempo fictício.

Se não houver estimativa confiável, usar indicador de progresso indeterminado.

---

## Erros

O usuário nunca deve receber traceback ou mensagem técnica bruta.

A interface deve mostrar:

- mensagem simples;
- possível causa;
- orientação do que fazer;
- opção de tentar novamente, quando aplicável.

O erro técnico completo deve ser registrado no log.

---

## Acessibilidade

- Manter contraste adequado.
- Não usar apenas cores para transmitir informação.
- Permitir redimensionar a janela.
- Evitar animações rápidas ou excessivas.
- Manter espaçamento confortável.
- Considerar futuramente suporte a escala de interface.

---

## Consistência

Todos os módulos devem seguir o mesmo padrão visual:

- títulos;
- subtítulos;
- cards;
- avisos;
- botões;
- mensagens de sucesso;
- mensagens de erro;
- loading.

---

## Desempenho da interface

- Evitar consultas repetidas sem necessidade.
- Reaproveitar dados recentes quando possível.
- Não atualizar sensores em frequência excessiva.
- Cancelar ou ignorar resultados antigos se o usuário mudar de tela.
- Evitar consumo desnecessário de CPU e RAM.
- Não criar múltiplas threads para a mesma tarefa.

---

## Direção visual

O PCBoostLab deve transmitir:

- confiança;
- clareza;
- controle;
- segurança;
- profissionalismo.

O aplicativo não deve copiar identidade visual, textos, layout ou marca de softwares de terceiros.