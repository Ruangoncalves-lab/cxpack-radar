"""
Painel Dedicado de Tomadores de Decisão (pages/4_decision_makers.py).
Permite visualizar, filtrar, exportar e atualizar manualmente os decisores de empresas qualificadas.
"""

import streamlit as st
import pandas as pd
from database.connection import get_db_session
from database.repositories.decision_makers import DecisionMakerRepository
from database.repositories.companies import CompanyRepository
from services.decision_maker_service import DecisionMakerService
from ui.layout import apply_app_shell

st.set_page_config(page_title="Decisores - CXPack Radar", page_icon="👤", layout="wide")
apply_app_shell(current_page="decision_makers")

st.markdown('<div class="cx-hero-title">Tomadores de Decisão & QSA Societário</div>', unsafe_allow_html=True)
st.markdown('<div class="cx-hero-subtitle">Mapeamento de profissionais em Compras, Suprimentos, Procurement, Diretoria e Quadro Societário da Receita Federal.</div>', unsafe_allow_html=True)

session = next(get_db_session())
dm_repo = DecisionMakerRepository(session)
company_repo = CompanyRepository(session)
dm_service = DecisionMakerService(session)

# Seção de Atualização Manual
st.markdown("#### 🔄 Atualizar Decisores Manualmente")
eligible_companies = [c for c in company_repo.list_companies(limit=100) if c.score >= 70]

if eligible_companies:
    col_up1, col_up2 = st.columns([3, 1])
    with col_up1:
        comp_to_update = st.selectbox(
            "Selecione uma empresa qualificada (Score >= 70) para atualizar decisores:",
            eligible_companies,
            format_func=lambda c: f"{c.name} ({c.domain}) - Score: {c.score}/100"
        )
    with col_up2:
        st.write("")
        st.write("")
        if st.button("🔄 ATUALIZAR DECISORES", use_container_width=True):
            with st.spinner(f"Atualizando decisores de {comp_to_update.name}..."):
                res = dm_service.search_decision_makers(comp_to_update.id, operator="usuario", force_refresh=True)
                if res["success"]:
                    st.success(f"🎉 {res['new_decision_makers_saved']} novos decisores encontrados para {comp_to_update.name}!")
                    st.rerun()
                else:
                    st.error(res["message"])

st.divider()

col_f1, col_f2 = st.columns(2)
with col_f1:
    type_filter = st.selectbox("Filtrar por Tipo de Decisor:", ["TODOS", "OPERATIONAL (Compras/Diretoria)", "CORPORATE (QSA Societário)"])
with col_f2:
    status_filter = st.selectbox("Filtrar por Status do E-mail:", ["TODOS", "PUBLICADO", "DEPARTAMENTO", "INFERIDO", "NAO_ENCONTRADO"])

decision_makers = dm_repo.list_all_decision_makers(limit=250)

if type_filter == "OPERATIONAL (Compras/Diretoria)":
    decision_makers = [dm for dm in decision_makers if dm.decision_maker_type == "OPERATIONAL"]
elif type_filter == "CORPORATE (QSA Societário)":
    decision_makers = [dm for dm in decision_makers if dm.decision_maker_type == "CORPORATE"]

if status_filter != "TODOS":
    decision_makers = [dm for dm in decision_makers if dm.email_status == status_filter]

if not decision_makers:
    st.info("Nenhum tomador de decisão encontrado com os filtros selecionados.")
else:
    st.markdown(f"### 👥 Profissionais Mapeados ({len(decision_makers)})")

    table_data = []
    for dm in decision_makers:
        comp = company_repo.get_by_domain(dm.company.domain) if dm.company else None
        comp_name = comp.name if comp else "Empresa"

        # Identificar Nível do Resultado (NÍVEL A, NÍVEL B, NÍVEL C)
        if dm.name and dm.role and (dm.email or dm.phone):
            level_text = "NÍVEL A (Nome+Cargo+Contato)"
        elif dm.name and dm.role:
            level_text = "NÍVEL B (Nome+Cargo)"
        else:
            level_text = "NÍVEL C (Depto)"

        table_data.append({
            "Empresa": comp_name,
            "Nome": dm.name,
            "Cargo": dm.role,
            "Departamento": dm.department or "Compras",
            "Nível Resultado": level_text,
            "Prioridade": dm.decision_priority,
            "E-mail Profissional": dm.email or "Não identificado",
            "Status E-mail": dm.email_status,
            "Confiança": f"{int(dm.confidence * 100)}%",
            "Fonte Pública": dm.source_title or dm.source_url or "Busca Web",
            "Mapeado em": dm.created_at.strftime("%d/%m/%Y %H:%M")
        })

    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True, hide_index=True)
