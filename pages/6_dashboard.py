"""
Dashboard Executivo Completo do CXPack Radar (pages/6_dashboard.py).
"""

import streamlit as st
import pandas as pd
from database.connection import get_db_session
from database.repositories.companies import CompanyRepository
from database.repositories.contacts import ContactRepository
from database.repositories.decision_makers import DecisionMakerRepository
from database.repositories.searches import SearchRepository
from services.quota_service import QuotaService
from ui.layout import apply_app_shell
from ui.components.metric_card import render_metric_card

st.set_page_config(page_title="Dashboard - CXPack Radar", page_icon="📈", layout="wide")
apply_app_shell(current_page="dashboard")

st.markdown('<div class="cx-hero-title">Dashboard Executivo & Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="cx-hero-subtitle">Métricas consolidadas de prospecção, taxa de economia por cache e distribuição dos fornecedores.</div>', unsafe_allow_html=True)

session = next(get_db_session())
company_repo = CompanyRepository(session)
contact_repo = ContactRepository(session)
dm_repo = DecisionMakerRepository(session)
search_repo = SearchRepository(session)
quota_service = QuotaService(session)

companies = company_repo.list_companies(min_score=0)
total_companies = len(companies)
manufacturers_count = sum(1 for c in companies if c.company_type == "FABRICANTE")
distributors_count = sum(1 for c in companies if c.company_type == "DISTRIBUIDOR")

all_dms = dm_repo.list_all_decision_makers(limit=1000)
total_dms = len(all_dms)

searches = search_repo.list_searches(limit=500)
total_searches = len(searches)
total_companies_found = sum(s.companies_found for s in searches)
total_new_companies = sum(s.new_companies_found for s in searches)
reused_companies = max(0, total_companies_found - total_new_companies)

reuse_rate = (reused_companies / total_companies_found * 100.0) if total_companies_found > 0 else 0.0

quota_info = quota_service.get_quota_dashboard_data()

st.markdown("### 📌 Indicadores Globais da Plataforma")

col1, col2, col3, col4 = st.columns(4)
with col1:
    render_metric_card("Empresas Cadastradas", f"{total_companies}")
with col2:
    render_metric_card("Fabricantes Confirmados", f"{manufacturers_count}")
with col3:
    render_metric_card("Decisores Mapeados", f"{total_dms}")
with col4:
    render_metric_card("Economia por Cache", f"{reused_companies}", delta=f"{reuse_rate:.1f}% de reuso")

st.divider()

col5, col6, col7, col8 = st.columns(4)
with col5:
    render_metric_card("Pesquisas Realizadas", f"{total_searches}")
with col6:
    render_metric_card("Buscas Web Hoje", f"{quota_info['today_total']}", delta="Provider: DDGS (R$ 0)")
with col7:
    render_metric_card("Limite Interno", f"{quota_info['safety_limit']} buscas")
with col8:
    render_metric_card("Distribuidoras/Revendas", f"{distributors_count}")

st.divider()

st.markdown("### 📊 Distribuição de Empresas & Funil do CRM")

col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("#### 🏢 Empresas por Tipo")
    if companies:
        type_counts = pd.Series([c.company_type for c in companies]).value_counts().reset_index()
        type_counts.columns = ["Tipo de Empresa", "Quantidade"]
        st.dataframe(type_counts, use_container_width=True, hide_index=True)
        st.bar_chart(type_counts.set_index("Tipo de Empresa"))
    else:
        st.info("Nenhuma empresa cadastrada.")

with col_g2:
    st.markdown("#### 💼 Leads por Estágio do CRM")
    if companies:
        crm_counts = pd.Series([c.crm_status or "NOVO" for c in companies]).value_counts().reset_index()
        crm_counts.columns = ["Estágio CRM", "Quantidade"]
        st.dataframe(crm_counts, use_container_width=True, hide_index=True)
        st.bar_chart(crm_counts.set_index("Estágio CRM"))
    else:
        st.info("Nenhum lead no CRM.")
