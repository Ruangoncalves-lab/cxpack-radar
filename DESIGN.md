# CXPack Radar — sistema visual

## Direção

Interface operacional inspirada em uma **ordem de fabricação**: folhas técnicas, divisórias, campos densos e sinalização de chão de fábrica. O produto deve parecer uma ferramenta de investigação industrial, não um painel SaaS genérico.

## Princípios

- Mostrar dados reais antes de decoração.
- Preservar a relação entre filtro, empresa e fonte.
- Usar uma superfície contínua por tarefa; evitar uma página feita de cartões soltos.
- Não usar gradientes, vidro, halos, depoimentos inventados ou métricas promocionais.
- Não preencher ausência de dados com conteúdo plausível. Exibir “Não informado” ou a ação necessária.

## Tokens

| Papel | Valor |
| --- | --- |
| Fundo de bancada | `#dcd8cd` |
| Papel | `#f7f4ec` |
| Papel secundário | `#ece8dd` |
| Tinta | `#171914` |
| Sinalização | `#e55332` |
| Sucesso | `#287a4d` |
| Erro | `#b83d32` |
| Raio padrão | `10–14px` |

Tipografia principal: **IBM Plex Sans**. Dados, CNPJ, score, datas e contadores: **IBM Plex Mono**. Ambas são servidas localmente pelo bundle.

## Estrutura

- Navegação lateral preta no desktop, menu Sheet no mobile.
- Cabeçalho fixo com o nome da área e estado do sistema.
- Conteúdo limitado a `1520px`, com margens responsivas.
- Listagens em linhas e colunas, com detalhe persistente da empresa à direita em telas largas.
- Formulário de busca como uma única ordem de pesquisa, dividido por seções numeradas.

## Componentes

- Componentes de interface seguem o padrão de código-fonte do shadcn e primitivas Radix.
- Botão primário usa tinta escura; ação de investigação usa laranja de sinalização.
- Campos têm altura mínima de `44px`, rótulos visíveis e foco de alto contraste.
- Estados vazios explicam a próxima ação. Erros aparecem junto da tarefa que falhou.
- Ícones são exclusivamente Lucide e sempre acompanham rótulo em ações não triviais.

## Movimento

Motion é reservado para entrada de página, seleção da navegação, painel de detalhe e progresso da busca. Duração normal entre `350–460ms`, easing suave e suporte obrigatório a `prefers-reduced-motion`.

## Responsividade

- Abaixo de `lg`, a barra lateral vira menu lateral acionado por botão.
- Tabelas priorizam empresa, score e ação; metadados secundários são ocultados progressivamente.
- O detalhe da empresa desce para o fluxo e mantém ações de telefone, WhatsApp, e-mail e site acessíveis.
