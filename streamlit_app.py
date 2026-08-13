"""
CXPack Radar - Aplicação Principal Streamlit (Visão Geral & Dashboard no Estilo Lumin).
Sistema B2B de prospecção de fornecedores e fabricantes industriais.
"""

import streamlit as st
from database.connection import init_db, test_db_connection, get_db_session
from database.repositories.companies import CompanyRepository
from database.repositories.decision_makers import DecisionMakerRepository
from database.repositories.usage import UsageRepository
from services.quota_service import QuotaService
from ui.layout import apply_app_shell
from ui.components.bento_cards import render_dark_hero_card, render_lime_card, render_history_feed

# 1. Configuração da página do Streamlit
st.set_page_config(
    page_title="CXPack Radar - Dashboard SaaS B2B",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Aplicar App Shell Global (Topbar do Lumin + Sidebar Categorizada + Tema)
apply_app_shell(current_page="home")

# 3. Inicializar Banco de Dados
try:
    init_db()
except Exception as e:
    st.error(f"Erro ao inicializar banco de dados: {e}")

session = next(get_db_session())
company_repo = CompanyRepository(session)
dm_repo = DecisionMakerRepository(session)
usage_repo = UsageRepository(session)
quota_service = QuotaService(session)

user = st.session_state.get("user", {})
user_name = user.get("name", "Michael").split()[0]

# 4. Saudação Hero no Estilo Lumin (Hello, Michael)
st.markdown(f'<div style="font-size: 34px; font-weight: 800; color: #111111; letter-spacing: -1px; margin-bottom: 20px;">Olá, {user_name}</div>', unsafe_allow_html=True)

# 5. Carregar Dados Reais do Banco
companies = company_repo.list_companies(min_score=0)
total_companies = len(companies)
manufacturers_count = sum(1 for c in companies if c.company_type == "FABRICANTE")
quota_info = quota_service.get_quota_dashboard_data()

# 6. Grid Principal Replicando o Layout da Imagem Lumin
col_hero, col_center, col_right = st.columns([1.1, 1.2, 1.3])

# Coluna 1: Dark Hero Card (Estilo 'Total Balance' em Preto)
with col_hero:
    render_dark_hero_card(
        total_companies=total_companies,
        manufacturers_count=manufacturers_count,
        quota_used=quota_info["today_total"],
        safety_limit=quota_info["safety_limit"]
    )
    
    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    if st.button("🚀 NOVA PESQUISA WEB", use_container_width=True):
        st.switch_page("pages/1_new_search.py")

# Coluna 2: Módulos Centrais de Prospecção
with col_center:
    st.markdown("#### ⚡ Ações do Radar")
    if st.button("🏢 ABRIR BANCO & QSA", use_container_width=True):
        st.switch_page("pages/2_results.py")
    if st.button("💼 ABRIR MINI CRM INDUSTRIAL", use_container_width=True):
        st.switch_page("pages/5_crm.py")
    if st.button("📈 ANALYTICS EXECUTIVO", use_container_width=True):
        st.switch_page("pages/6_dashboard.py")

    st.divider()

    st.markdown("#### 📊 Cobertura da Base")
    st.markdown(f"• **Fabricantes Confirmados:** `{manufacturers_count}`")
    st.markdown(f"• **Decisores Mapeados:** `{len(dm_repo.list_all_decision_makers(limit=500))}`")
    st.markdown(f"• **Buscas Web Hoje (DDGS):** `{quota_info['today_total']}`")

# Coluna 3: Cards com Destaque Lime + Feed de Histórico
with col_right:
    # 3 Lime Cards no Topo (Estilo Cards PRO/Referral em Lime do Lumin)
    col_l1, col_l2, col_l3 = st.columns(3)
    with col_l1:
        render_lime_card("DDGS", "Busca R$ 0", "R$ 0")
    with col_l2:
        render_lime_card("Gemini", "Ia 3.1", "IA")
    with col_l3:
        render_lime_card("QSA", "Dados CNPJ", "QSA")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Feed de Histórico de Empresas Prospectadas (Estilo History List do Lumin)
    history_data = []
    for c in companies[:5]:
        history_data.append({
            "name": c.name,
            "domain": c.domain,
            "score": c.score,
            "company_type": c.company_type,
            "time_str": c.updated_at.strftime("%H:%M")
        })

    render_history_feed(history_data)
