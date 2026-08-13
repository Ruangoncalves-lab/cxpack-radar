# 📡 CXPack Radar - Prospecção B2B Industrial

O **CXPack Radar** é uma plataforma inteligente para prospecção de fabricantes e fornecedores industriais B2B, desenvolvida com Python 3.12, Streamlit, Google Gemini Developer API (com Search Grounding) e SQLAlchemy.

## 🌟 Principais Recursos

- 💰 **Custo R$ 0 de API**: Opera no Free Tier do Google Gemini com Search Grounding.
- 🗄️ **Banco Proprietário Híbrido**: Opera localmente em SQLite e transiciona suavemente para PostgreSQL/Supabase em produção apenas alterando a `DATABASE_URL`.
- ⚡ **Cache Inteligente**: Reutiliza dados de buscas dos últimos 30 dias por hash determinístico (`search_hash`), economizando chamadas de API.
- 🚫 **Anti-Desperdício & Proteção de Cotas**:
  - Teto de segurança diário configurável (`DAILY_GROUNDED_SAFETY_LIMIT = 450`).
  - Gerador local de variação de queries industriais sem consumo de IA.
  - Normalizador de domínios raiz com blacklist configurável de marketplaces (Mercado Livre, Shopee, Amazon, etc.).
- 🛑 **Proteção Idempotente**: Uso de `st.form` e estados de busca (`CREATED`, `RUNNING`, `COMPLETED`) impedindo execuções duplicadas acidentais no Streamlit.

## 🛠️ Stack Tecnológica

- **Interface**: Streamlit
- **Linguagem**: Python 3.12
- **IA Provider**: Google Gemini (`google-genai` SDK) - Modelo `gemini-2.5-flash-lite`
- **Search Provider**: Gemini + Grounding with Google Search
- **ORM & Banco**: SQLAlchemy 2.x (SQLite / PostgreSQL)
- **Validação**: Pydantic

## 🚀 Como Executar

Consulte o guia detalhado em [SETUP_INICIANTE.md](file:///c:/Users/Administrator/.gemini/antigravity-ide/scratch/plastic-prospector-saas/SETUP_INICIANTE.md).

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar segredos (.streamlit/secrets.toml)
# Adicione sua GEMINI_API_KEY no arquivo .streamlit/secrets.toml

# 3. Iniciar a aplicação
streamlit run streamlit_app.py
```
