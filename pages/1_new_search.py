"""
Tela de Nova Pesquisa (pages/1_new_search.py).
Formulário com Hero Search Panel, prospecção via DDGS, extração de contatos públicos e descoberta de Tomadores de Decisão.
"""

import streamlit as st
from database.connection import get_db_session
from services.search_service import SearchService
from services.quota_service import QuotaService
from services.cache_service import CacheService
from services.contact_service import ContactService
from services.decision_maker_service import DecisionMakerService
from core.exceptions import QuotaExceededError
from ui.layout import apply_app_shell
from ui.components.metric_card import render_metric_card
from ui.components.search_panel import render_search_panel_header

st.set_page_config(page_title="Nova Pesquisa - CXPack Radar", page_icon="🔍", layout="wide")
apply_app_shell(current_page="search")

st.markdown('<div class="cx-hero-title">Nova Pesquisa Industrial</div>', unsafe_allow_html=True)
st.markdown('<div class="cx-hero-subtitle">Módulo inteligente de prospecção de fabricantes, contatos públicos e tomadores de decisão via DDGS.</div>', unsafe_allow_html=True)

session = next(get_db_session())
quota_service = QuotaService(session)
cache_service = CacheService(session)
search_service = SearchService(session)
contact_service = ContactService(session)
dm_service = DecisionMakerService(session)

quota_info = quota_service.get_quota_dashboard_data()

# Cards de Cota Diária e Proteção Interna (Bento Grid)
col_q1, col_q2, col_q3 = st.columns(3)
with col_q1:
    render_metric_card("Buscas Web Hoje", f"{quota_info['today_total']}", delta="Provider: DDGS (R$ 0)")
with col_q2:
    render_metric_card("Limite Interno Diário", f"{quota_info['safety_limit']} buscas")
with col_q3:
    st.success("🟢 Busca Gratuita Ativa")

st.divider()

# Hero Search Panel Container
with st.form(key="search_form"):
    render_search_panel_header("Especificações do Produto & Filtros", "Preencha os critérios técnicos para buscar fabricantes compatíveis.")

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        product = st.text_input("Produto *", placeholder="Ex: Frasco plástico", help="Nome do produto desejado")
        capacity = st.text_input("Capacidade / Volume", placeholder="Ex: 500 ml", help="Volume ou capacidade técnica")
        material = st.text_input("Material", placeholder="Ex: PET", help="Material de fabricação (PET, PEAD, Alumínio, etc.)")

    with col_f2:
        country = st.text_input("País", value="Brasil")
        state = st.text_input("Estado / UF (Opcional)", placeholder="Ex: SP")
        company_type = st.selectbox("Tipo de Empresa Desejado", ["Fabricante", "Distribuidor", "Qualquer Tipo"])

    st.markdown("---")
    st.markdown("#### ⚙️ Parâmetros de Pesquisa Web Pública (DDGS)")
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        max_variations = st.slider("Variações de Busca Web (Queries Locais)", min_value=1, max_value=5, value=3, help="Máximo de buscas públicas por pesquisa (Padrão: 3)")
        only_manufacturers = st.checkbox("Somente Fabricantes", value=True)
    with col_opt2:
        search_contacts = st.checkbox("Buscar Contatos Públicos", value=True, help="Extrai e-mails, telefones e WhatsApp dos websites")
        search_decision_makers = st.checkbox(
            "Buscar Decisores",
            value=True,
            help="Procura Compras, Suprimentos, Procurement e Diretoria nas empresas qualificadas."
        )

    if search_decision_makers:
        st.info("💡 **Aviso:** A busca de decisores é executada apenas nas empresas qualificadas para economizar consultas.")

    st.divider()
    st.info(f"💡 **Execução responsável:** Esta pesquisa poderá executar até **{max_variations} consultas web públicas** via DDGS (R$ 0 de custo por API).")

    submit_button = st.form_submit_button("🚀 BUSCAR FORNECEDORES", use_container_width=True)

# Processar o envio da pesquisa
if submit_button:
    if not product or not product.strip():
        st.error("Por favor, preencha o campo **Produto *** antes de pesquisar.")
    else:
        cache_info = cache_service.check_cache(
            product=product,
            capacity=capacity,
            material=material,
            location=f"{state}, {country}" if state else country,
            company_type=company_type
        )

        if cache_info["hit"] and not st.session_state.get("force_refresh_click"):
            st.warning(f"⚠️ {cache_info['message']}")
            st.info(f"Foram encontradas **{cache_info['companies_found']} empresas** salvas nesta busca anterior.")

            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("👁️ VER RESULTADOS EXISTENTES", use_container_width=True):
                    st.session_state["active_search_id"] = cache_info["existing_search_id"]
                    st.switch_page("pages/2_results.py")
            with col_btn2:
                if st.button("🌐 BUSCAR NOVOS FORNECEDORES NA INTERNET", use_container_width=True):
                    st.session_state["force_refresh_click"] = True
                    st.rerun()
        else:
            st.session_state["force_refresh_click"] = False

            with st.status("🔍 Prospectando fornecedores, contatos e decisores...", expanded=True) as status:
                st.write("1. Verificando base de dados local...")
                st.write("2. Gerando variações de queries industriais locais...")
                st.write(f"3. Executando até {max_variations} buscas web públicas via DDGS...")

                try:
                    res = search_service.execute_prospecting_search(
                        product=product,
                        capacity=capacity,
                        material=material,
                        location=f"{state}, {country}" if state else country,
                        company_type=company_type,
                        max_queries=max_variations,
                        operator="usuario",
                        force_refresh=True
                    )

                    from database.repositories.companies import CompanyRepository
                    comp_repo = CompanyRepository(session)
                    recent_companies = comp_repo.list_companies(limit=12)

                    contacts_saved_total = 0
                    if search_contacts and recent_companies:
                        st.write("4. Rastreando websites e extraindo contatos públicos (E-mails, Telefones, WhatsApp)...")
                        for idx, comp in enumerate(recent_companies, 1):
                            st.write(f"  • Rastreando site {idx}/{len(recent_companies)}: {comp.name}")
                            c_res = contact_service.crawl_and_extract_company_contacts(comp.id)
                            if c_res.get("success"):
                                contacts_saved_total += c_res.get("new_contacts_saved", 0)

                    dm_saved = 0
                    if search_decision_makers and recent_companies:
                        st.write("5. Mapeando tomadores de decisão das empresas qualificadas...")
                        for idx, comp in enumerate(recent_companies, 1):
                            if comp.score >= 70:
                                st.write(f"  • Buscando decisores {idx}/{len(recent_companies)}: {comp.name}")
                                dm_res = dm_service.search_decision_makers(
                                    comp.id,
                                    operator="usuario",
                                    progress_callback=lambda msg: st.write(f"    └─ {msg}")
                                )
                                if dm_res.get("success"):
                                    dm_saved += dm_res.get("new_decision_makers_saved", 0)

                    status.update(label="✅ Pesquisa concluída com sucesso!", state="complete", expanded=False)

                    msg_cnt = f", **{contacts_saved_total} contatos**" if search_contacts else ""
                    msg_dm = f" e **{dm_saved} decisores**" if search_decision_makers else ""
                    st.success(
                        f"🎉 Encontradas **{res['companies_found']} empresas** "
                        f"({res['new_companies_found']} novas salvas no banco){msg_cnt}{msg_dm}."
                    )

                    st.session_state["active_search_id"] = res["search_id"]
                    if st.button("👉 IR PARA RESULTADOS DA PESQUISA", use_container_width=True):
                        st.switch_page("pages/2_results.py")

                except QuotaExceededError as qe:
                    status.update(label="🔴 Limite Interno Atingido", state="error")
                    st.error(f"❌ {qe.user_friendly_message}")
                except Exception as ex:
                    status.update(label="🔴 Erro Inesperado", state="error")
                    st.error(f"Ocorreu um erro ao processar a pesquisa: {str(ex)}")
