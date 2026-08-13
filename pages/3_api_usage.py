"""
Dashboard de Uso da API e Buscas Web (pages/3_api_usage.py).
"""

import streamlit as st
import pandas as pd
from database.connection import get_db_session
from services.quota_service import QuotaService
from database.repositories.usage import UsageRepository
from database.repositories.searches import SearchRepository
from core.config import DEFAULT_GEMINI_MODEL, SEARCH_PROVIDER
from ui.layout import apply_app_shell
from ui.components.metric_card import render_metric_card

st.set_page_config(page_title="Uso da API - CXPack Radar", page_icon="📊", layout="wide")
apply_app_shell(current_page="quota")

st.markdown('<div class="cx-hero-title">Painel de Operações: Busca Web & Inteligência IA</div>', unsafe_allow_html=True)
st.markdown('<div class="cx-hero-subtitle">Monitoramento das buscas web públicas gratuitas (DDGS) e das operações de análise semântica (Google Gemini).</div>', unsafe_allow_html=True)

session = next(get_db_session())
quota_service = QuotaService(session)
usage_repo = UsageRepository(session)
search_repo = SearchRepository(session)

quota_info = quota_service.get_quota_dashboard_data()
searches = search_repo.list_searches(limit=500)
total_companies_found = sum(s.companies_found for s in searches)
total_new_companies = sum(s.new_companies_found for s in searches)
reused_companies = max(0, total_companies_found - total_new_companies)

tab_web, tab_ai = st.tabs(["🌐 BUSCA WEB (DDGS - R$ 0)", "🤖 INTELIGÊNCIA ARTIFICIAL (GEMINI)"])

with tab_web:
    st.markdown("### 🌐 Operações de Busca Web Pública (DDGS)")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("Provider Ativo", "DDGS", delta="Custo por API: R$ 0")
    with col2:
        render_metric_card("Buscas Web Hoje", f"{quota_info['today_total']}")
    with col3:
        render_metric_card("Empresas Encontradas", f"{total_companies_found}")
    with col4:
        render_metric_card("Economizadas por Cache", f"{reused_companies}")

    st.divider()
    st.info("💡 **Busca Gratuita Sem Cobrança por API:** O CXPack Radar aplica limites internos de segurança para evitar rate limiting e garantir o uso responsável.")

with tab_ai:
    st.markdown("### 🤖 Operações de Inteligência Artificial (Google Gemini)")

    col5, col6, col7 = st.columns(3)
    with col5:
        render_metric_card("Modelo Configurado", "Gemini 3.1", delta=DEFAULT_GEMINI_MODEL)
    with col6:
        render_metric_card("Função Principal", "Classificação & Extração")
    with col7:
        render_metric_card("Status da API", "🟢 Conectado")

st.divider()

st.markdown("### 📜 Registros de Requisições de Operações")
usage_logs = usage_repo.get_today_usage()

if not usage_logs:
    st.info("Nenhuma operação registrada hoje.")
else:
    log_data = []
    for u in usage_logs:
        log_data.append({
            "Horário": u.created_at.strftime("%H:%M:%S"),
            "Provedor": "DDGS" if "ddgs" in u.operation.lower() else "Gemini",
            "Operação": u.operation,
            "Operador": u.user_or_operator,
            "Quantidade": u.request_count,
            "Status": "🟢 Sucesso" if u.success else "🔴 Erro"
        })

    df = pd.DataFrame(log_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
