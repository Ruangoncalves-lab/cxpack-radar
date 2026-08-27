"""CXPack Radar — central operacional de prospecção industrial."""

import html

import streamlit as st

from database.connection import get_db_session, init_db
from database.repositories.companies import CompanyRepository
from database.repositories.decision_makers import DecisionMakerRepository
from database.repositories.searches import SearchRepository
from services.quota_service import QuotaService
from ui.layout import apply_app_shell


st.set_page_config(
    page_title="CXPack Radar | Inteligência comercial industrial",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed",
)
apply_app_shell(current_page="home")

try:
    init_db()
except Exception as exc:
    st.error(f"Não foi possível iniciar o banco de dados: {exc}")

session = next(get_db_session())
company_repo = CompanyRepository(session)
dm_repo = DecisionMakerRepository(session)
search_repo = SearchRepository(session)
quota_service = QuotaService(session)

companies = company_repo.list_companies(min_score=0)
decision_makers = dm_repo.list_all_decision_makers(limit=1000)
searches = search_repo.list_searches(limit=100)
quota = quota_service.get_quota_dashboard_data()

manufacturers = [company for company in companies if company.company_type == "FABRICANTE"]
candidates = [company for company in companies if company.company_type == "CANDIDATO_CNAE"]
companies_with_contact = [company for company in companies if company.contacts or company.department_contacts]
actionable_rate = round(len(companies_with_contact) / len(companies) * 100) if companies else 0
quota_limit = max(quota.get("safety_limit", 1), 1)
quota_progress = min(100, round(quota.get("today_total", 0) / quota_limit * 100))

metric_data = [
    ("Base mapeada", len(companies), "empresas cadastradas", "DB"),
    ("Fabricantes", len(manufacturers), "com evidência comercial", "OK"),
    ("Leads acionáveis", f"{actionable_rate}%", "com contato publicado", "@"),
    ("Decisores", len(decision_makers), "pessoas e setores", "DM"),
]
cards = "".join(
    f'<article class="cx-stat-card"><div class="cx-stat-top"><span>{icon}</span></div>'
    f'<strong>{value}</strong><p>{label}</p><small>{note}</small></article>'
    for label, value, note, icon in metric_data
)
st.markdown(f'<section class="cx-stat-grid">{cards}</section>', unsafe_allow_html=True)

main, aside = st.columns([2.15, 1], gap="large")
with main:
    st.markdown('<section class="cx-panel-head"><div><h2>Empresas para investigar</h2><p>Prioridade por score e disponibilidade de contato</p></div></section>', unsafe_allow_html=True)
    shortlist = companies[:6]
    if shortlist:
        rows = ""
        for company in shortlist:
            safe_name = html.escape(company.name or company.domain)
            place = html.escape(" / ".join(filter(None, [company.city, company.state])) or "Brasil")
            has_contact = bool(company.contacts or company.department_contacts)
            status = "Contato disponível" if has_contact else "Enriquecer dados"
            rows += (
                f'<div class="cx-data-row"><span class="cx-data-avatar">{safe_name[:1].upper()}</span>'
                f'<div class="cx-data-main"><strong>{safe_name}</strong><span>{place} · {company.company_type.replace("_", " ").title()}</span></div>'
                f'<span class="cx-data-status {"ready" if has_contact else "pending"}">{status}</span>'
                f'<b>{company.score}<small>/100</small></b></div>'
            )
        st.markdown(f'<div class="cx-data-panel">{rows}</div>', unsafe_allow_html=True)
    else:
        st.info("Sua base ainda está vazia. Inicie uma busca para encontrar os primeiros fabricantes.")

    action_a, action_b, action_space = st.columns([1, 1, 2])
    with action_a:
        if st.button("Nova prospecção", type="primary", width="stretch"):
            st.switch_page("pages/1_new_search.py")
    with action_b:
        if st.button("Abrir empresas", width="stretch"):
            st.switch_page("pages/2_results.py")

    st.markdown('<section class="cx-panel-head cx-panel-space"><div><h2>Buscas recentes</h2><p>Últimas execuções registradas no radar</p></div></section>', unsafe_allow_html=True)
    if searches:
        search_rows = ""
        for search in searches[:5]:
            query = html.escape(" · ".join(filter(None, [search.product, search.capacity, search.material])))
            search_rows += (
                f'<div class="cx-search-row"><span>{search.created_at:%d/%m}</span><div><strong>{query}</strong>'
                f'<small>{html.escape(search.location or "Brasil")} · {search.status}</small></div>'
                f'<b>{search.companies_found or 0}<small> empresas</small></b></div>'
            )
        st.markdown(f'<div class="cx-data-panel">{search_rows}</div>', unsafe_allow_html=True)
    else:
        st.info("Nenhuma busca registrada.")

with aside:
    st.markdown(
        f"""
        <section class="cx-ops-card">
            <span class="cx-ops-state">RADAR OPERACIONAL</span>
            <h2>Busca gratuita ativa</h2>
            <p>{quota.get('today_total', 0)} de {quota_limit} consultas usadas hoje</p>
            <div class="cx-ops-progress" role="progressbar" aria-label="Uso do limite diário" aria-valuemin="0" aria-valuemax="100" aria-valuenow="{quota_progress}"><span style="width:{quota_progress}%"></span></div>
            <div class="cx-ops-summary"><strong>{quota_progress}%</strong><span>do limite diário interno</span></div>
            <a href="/api_usage?auth_token=active" target="_self">Ver uso detalhado</a>
        </section>
        """,
        unsafe_allow_html=True,
    )

    tasks = [
        ("Validar candidatos CNAE", len(candidates), "Confirmar produto no site oficial"),
        ("Completar contatos", max(0, len(companies) - len(companies_with_contact)), "Buscar telefone, e-mail ou WhatsApp"),
        ("Revisar decisores", len(decision_makers), "Sócios, compras e suprimentos mapeados"),
    ]
    task_rows = "".join(
        f'<div class="cx-task-row"><span>{value}</span><div><strong>{title}</strong><small>{description}</small></div></div>'
        for title, value, description in tasks
    )
    st.markdown(f'<section class="cx-task-panel"><h2>Próximas ações</h2>{task_rows}</section>', unsafe_allow_html=True)

    if st.button("Ver histórico completo", width="stretch"):
        st.switch_page("pages/7_search_history.py")
