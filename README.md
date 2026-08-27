# CXPack Radar

Plataforma de prospecção industrial para pesquisar fabricantes por produto, capacidade, material e localização; consolidar dados públicos de CNPJ; encontrar telefones, e-mails, WhatsApp, QSA e tomadores de decisão; e consultar o histórico de cada busca.

## Stack principal

- Frontend: React, Vite, Tailwind CSS, shadcn/ui e Motion.
- API: FastAPI.
- Pipeline: serviços Python existentes com DDGS, BrasilAPI, Minha Receita e crawler próprio.
- Banco: SQLAlchemy com SQLite local ou PostgreSQL/Supabase via `DATABASE_URL`.

Gemini é opcional. A descoberta principal e a consulta cadastral não dependem de IA generativa.

## Desenvolvimento

Requer Node.js 20.19+ e Python 3.12+.

```bash
pip install -r requirements.txt
npm install
```

Em dois terminais:

```bash
npm run api
npm run dev
```

A interface fica em `http://localhost:5173` e a API em `http://localhost:8000`.

## Produção

O FastAPI serve o build do Vite pela mesma porta:

```bash
npm run build
npm run serve
```

Configure `DATABASE_URL` para usar PostgreSQL/Supabase. Sem essa variável, o sistema usa `data/cxpack_radar.db`.

## Fluxos disponíveis

- Visão geral com métricas reais do banco.
- Busca técnica acompanhada em tempo real por polling.
- Lista de empresas filtrável por execução.
- Perfil completo com origem dos contatos e ação de WhatsApp.
- Histórico de pesquisas persistidas.
