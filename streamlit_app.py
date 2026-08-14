"""CXPack Radar — visão geral da inteligência comercial industrial."""

import html

import streamlit as st

from database.connection import get_db_session, init_db
from database.repositories.companies import CompanyRepository
from database.repositories.decision_makers import DecisionMakerRepository
from services.quota_service import QuotaService
from ui.layout import apply_app_shell


st.set_page_config(
    page_title="CXPack Radar | Inteligência comercial industrial",
    page_icon="◉",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_app_shell(current_page="home")

try:
    init_db()
except Exception as exc:
    st.error(f"Não foi possível iniciar o banco de dados: {exc}")

session = next(get_db_session())
company_repo = CompanyRepository(session)
dm_repo = DecisionMakerRepository(session)
quota_service = QuotaService(session)

companies = company_repo.list_companies(min_score=0)
decision_makers = dm_repo.list_all_decision_makers(limit=1000)
quota = quota_service.get_quota_dashboard_data()

manufacturers = [company for company in companies if company.company_type == "FABRICANTE"]
qualified = [company for company in companies if company.score >= 70]
companies_with_contact = [company for company in companies if company.contacts or company.department_contacts]
actionable_rate = round(len(companies_with_contact) / len(companies) * 100) if companies else 0
user_name = st.session_state.get("user", {}).get("name", "Administrador").split()[0]

st.markdown(
    f"""
    <section class="cx-command-hero">
        <div class="cx-command-copy">
            <div class="cx-eyebrow"><span></span> INTELIGÊNCIA COMERCIAL INDUSTRIAL</div>
            <h1>Do produto que você precisa<br>ao <em>contato que decide.</em></h1>
            <p>Encontre fabricantes, valide evidências e descubra o melhor caminho de abordagem — sem transformar pesquisa em planilha infinita.</p>
            <div class="cx-trust-line">
                <span>✓ Fontes rastreáveis</span><span>✓ Dados públicos</span><span>✓ Busca web sem custo</span>
            </div>
        </div>
        <div class="cx-radar-visual" aria-label="Radar de prospecção">
            <div class="cx-radar-ring ring-1"></div><div class="cx-radar-ring ring-2"></div>
            <div class="cx-radar-sweep"></div><div class="cx-radar-core">CX</div>
            <span class="cx-radar-dot dot-1"></span><span class="cx-radar-dot dot-2"></span><span class="cx-radar-dot dot-3"></span>
            <div class="cx-radar-caption"><strong>{len(qualified)}</strong> oportunidades qualificadas</div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

cta_primary, cta_secondary, cta_space = st.columns([1.15, 1.05, 4])
with cta_primary:
    if st.button("Iniciar nova prospecção  →", type="primary", use_container_width=True):
        st.switch_page("pages/1_new_search.py")
with cta_secondary:
    if st.button("Explorar empresas", use_container_width=True):
        st.switch_page("pages/2_results.py")

st.markdown('<div class="cx-section-kicker">VISÃO DO PIPELINE</div>', unsafe_allow_html=True)
kpi_1, kpi_2, kpi_3, kpi_4 = st.columns(4)
metrics = [
    (kpi_1, "Base mapeada", len(companies), "empresas com domínio único"),
    (kpi_2, "Fabricantes", len(manufacturers), "identificados na base"),
    (kpi_3, "Leads acionáveis", f"{actionable_rate}%", "com contato publicado"),
    (kpi_4, "Decisores", len(decision_makers), "pessoas e setores mapeados"),
]
for column, label, value, note in metrics:
    with column:
        st.markdown(
            f'<div class="cx-pipeline-card"><div class="cx-pipeline-label">{label}</div>'
            f'<div class="cx-pipeline-value">{value}</div><div class="cx-pipeline-note">{note}</div></div>',
            unsafe_allow_html=True,
        )

left, right = st.columns([1.65, 1])
with left:
    st.markdown(
        '<div class="cx-section-heading"><div><span>PRÓXIMAS OPORTUNIDADES</span>'
        '<h2>Empresas prontas para investigar</h2></div></div>',
        unsafe_allow_html=True,
    )
    shortlist = companies[:5]
    if shortlist:
        rows = ""
        for company in shortlist:
            safe_name = html.escape(company.name or company.domain)
            safe_place = html.escape(" · ".join(filter(None, [company.city, company.state])) or "Brasil")
            status = "Pronto para contato" if company.contacts or company.department_contacts else "Enriquecer dados"
            status_class = "ready" if company.contacts or company.department_contacts else "enrich"
            rows += (
                f'<div class="cx-opportunity-row"><div class="cx-company-mark">{safe_name[:1].upper()}</div>'
                f'<div class="cx-company-main"><strong>{safe_name}</strong><span>{safe_place} · {company.company_type.title()}</span></div>'
                f'<div class="cx-opportunity-status {status_class}">{status}</div><div class="cx-score">{company.score}<small>/100</small></div></div>'
            )
        st.markdown(f'<div class="cx-opportunity-list">{rows}</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="cx-empty-state"><div class="cx-empty-icon">⌁</div><strong>Seu radar está pronto.</strong>'
            '<p>Faça a primeira busca para criar uma lista de fabricantes com evidências, contatos e decisores.</p></div>',
            unsafe_allow_html=True,
        )

with right:
    st.markdown(
        f"""
        <div class="cx-mission-card">
            <div class="cx-mission-top"><span>MISSÃO DE HOJE</span><span class="cx-live-dot">ATIVO</span></div>
            <h2>Transforme pesquisa<br>em conversa comercial.</h2>
            <div class="cx-mission-step"><b>01</b><div><strong>Defina o briefing</strong><span>Produto, material, volume e região.</span></div></div>
            <div class="cx-mission-step"><b>02</b><div><strong>Valide quem fabrica</strong><span>Score e evidências mantêm o dado honesto.</span></div></div>
            <div class="cx-mission-step"><b>03</b><div><strong>Encontre a porta de entrada</strong><span>Compras, suprimentos, diretoria ou QSA.</span></div></div>
            <div class="cx-mission-foot"><span>{quota['today_total']} buscas hoje</span><span>DDGS · R$ 0</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    f'<div class="cx-welcome-note">Olá, {html.escape(user_name)}. O radar prioriza dados publicados e sempre mantém a fonte junto da informação.</div>',
    unsafe_allow_html=True,
)
