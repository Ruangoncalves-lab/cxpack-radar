"""Histórico navegável das pesquisas e acesso aos respectivos resultados."""

import pandas as pd
import streamlit as st

from database.connection import get_db_session
from database.repositories.searches import SearchRepository
from ui.layout import apply_app_shell


st.set_page_config(page_title="Histórico - CXPack Radar", page_icon="◫", layout="wide")
apply_app_shell(current_page="history")

session = next(get_db_session())
search_repo = SearchRepository(session)
searches = search_repo.list_searches(limit=100)

st.markdown('<h1 class="cx-hero-title">Histórico de buscas</h1>', unsafe_allow_html=True)
st.markdown(
    '<div class="cx-hero-subtitle">Consulte o briefing usado, a execução e as empresas encontradas em cada prospecção.</div>',
    unsafe_allow_html=True,
)

if not searches:
    st.info("Nenhuma busca realizada ainda. Inicie uma prospecção para criar seu primeiro histórico.")
    if st.button("Iniciar primeira busca", type="primary", width="stretch"):
        st.switch_page("pages/1_new_search.py")
    st.stop()

completed = sum(search.status == "COMPLETED" for search in searches)
total_companies = sum(search.companies_found or 0 for search in searches)
metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("Buscas registradas", len(searches))
metric_b.metric("Concluídas", completed)
metric_c.metric("Resultados acumulados", total_companies)

status_filter = st.selectbox("Status", ["TODOS", "COMPLETED", "RUNNING", "FAILED"])
visible_searches = [search for search in searches if status_filter == "TODOS" or search.status == status_filter]

history_rows = [
    {
        "Busca": f"#{search.id}",
        "Data": search.created_at.strftime("%d/%m/%Y %H:%M"),
        "Produto": search.product,
        "Capacidade": search.capacity or "—",
        "Material": search.material or "—",
        "Região": search.location or "Brasil",
        "Status": search.status,
        "Empresas": search.companies_found or 0,
        "Novas": search.new_companies_found or 0,
    }
    for search in visible_searches
]
st.dataframe(pd.DataFrame(history_rows), width="stretch", hide_index=True)

if not visible_searches:
    st.info("Nenhuma busca corresponde ao status selecionado.")
    st.stop()

st.markdown("### Abrir uma busca")
selected_search_id = st.selectbox(
    "Selecione a pesquisa",
    [search.id for search in visible_searches],
    format_func=lambda search_id: next(
        f"Busca #{search.id} — {search.product} · {search.capacity or 'sem capacidade'} · {search.location or 'Brasil'}"
        for search in visible_searches if search.id == search_id
    ),
)

selected_search = next(search for search in visible_searches if search.id == selected_search_id)
companies = search_repo.list_companies_for_search(selected_search_id)
st.caption(
    f"{len(companies)} empresas vinculadas · {selected_search.grounded_calls or 0} consultas web · "
    f"executada por {selected_search.operator or 'sistema'}"
)

if companies:
    st.dataframe(
        pd.DataFrame([
            {
                "Empresa": company.name,
                "Tipo": company.company_type,
                "Score": company.score,
                "CNPJ": company.cnpj or "Não vinculado",
                "Cidade/UF": "/".join(filter(None, [company.city, company.state])) or "—",
                "Site": company.website or "Não localizado",
            }
            for company in companies
        ]),
        width="stretch",
        hide_index=True,
    )
else:
    st.info("Esta execução não possui empresas vinculadas.")

if st.button("Abrir empresas desta busca", type="primary", width="stretch"):
    st.session_state["active_search_id"] = selected_search_id
    st.switch_page("pages/2_results.py")
