# CXPack Radar

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack

Frontend solicitado: React com Vite, Tailwind CSS, shadcn/ui e Motion. O backend Python existente continua responsável pela pesquisa, enriquecimento e persistência.

## Users

Equipes comerciais e de compras que prospectam fabricantes e fornecedores industriais no Brasil e precisam localizar empresas compatíveis com especificações concretas de produto.

## Product Purpose

Pesquisar fabricantes por produto, capacidade, material e localização; registrar cada busca; consolidar dados cadastrais públicos, telefones, e-mails, WhatsApp, QSA e tomadores de decisão; permitir que a equipe inspecione e contate empresas encontradas.

## Positioning

O sistema combina descoberta comercial na web com candidatos oficiais da base pública de CNPJ, mantendo candidatos por CNAE separados de fabricantes comprovados até existir evidência compatível com os filtros da busca.

## Operating Context

O uso é recorrente e operacional: iniciar uma busca técnica, acompanhar sua execução, comparar empresas, enriquecer um registro, abrir o WhatsApp e voltar ao histórico para consultar o que já foi coletado.

## Capabilities and Constraints

- A busca precisa respeitar produto, capacidade, material, localização e tipo de empresa.
- A cobertura principal é Brasil, com dados públicos de CNPJ/Receita por BrasilAPI e Minha Receita.
- Telefones e e-mails dependem de publicação em fontes públicas; um telefone não garante conta ativa no WhatsApp.
- DDGS é o provedor gratuito de descoberta web. Gemini é opcional e não pode ser apresentado como requisito para o fluxo principal.
- SQLite funciona localmente; PostgreSQL/Supabase é usado quando `DATABASE_URL` está configurada.
- O sistema não deve inventar empresas, contatos, métricas ou provas comerciais.

## Brand Commitments

Nome do produto: CXPack Radar. Idioma principal: português do Brasil. A interface deve evitar estética genérica de SaaS e privilegiar precisão, rastreabilidade e operação industrial.

## Evidence on Hand

O repositório contém buscas, empresas, contatos, páginas rastreadas, evidências, QSA, decisores, score e histórico persistidos no banco. Não há depoimentos, clientes, benchmarks comerciais ou métricas de velocidade aprovadas para divulgação.

## Product Principles

- Dados reais antes de decoração.
- Filtro técnico é contrato, não sugestão.
- Toda informação relevante mantém sua fonte.
- Contato deve estar a uma ação de distância.
- Candidato oficial e fabricante comprovado são estados distintos.

## Accessibility & Inclusion

Controles devem funcionar por teclado, preservar foco visível, ter alvos de toque adequados e respeitar preferência por movimento reduzido.
