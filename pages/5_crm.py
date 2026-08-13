"""
Tela do Mini CRM Industrial com opção de Edição, Atribuição e Exclusão de Empresas (pages/5_crm.py).
"""

import streamlit as st
import pandas as pd
from database.connection import get_db_session
from database.repositories.companies import CompanyRepository
from services.crm_service import CRMService, VALID_CRM_STATUSES
from services.team_service import TeamService
from services.export_service import ExportService
from ui.layout import apply_app_shell
from ui.components.metric_card import render_metric_card

st.set_page_config(page_title="CRM - CXPack Radar", page_icon="💼", layout="wide")
apply_app_shell(current_page="crm")

st.markdown('<div class="cx-hero-title">Mini CRM Industrial</div>', unsafe_allow_html=True)
st.markdown('<div class="cx-hero-subtitle">Pipeline comercial de prospecção, gestão de responsáveis, exclusão e exportação de dados em Excel/CSV.</div>', unsafe_allow_html=True)

session = next(get_db_session())
company_repo = CompanyRepository(session)
crm_service = CRMService(session)
team_service = TeamService(session)
export_service = ExportService(session)

active_members = team_service.list_active_members()
team_options = ["Não atribuído"] + [m.name for m in active_members]

funnel_summary = crm_service.get_crm_funnel_summary()

cols = st.columns(len(VALID_CRM_STATUSES))
for idx, st_name in enumerate(VALID_CRM_STATUSES):
    with cols[idx]:
        render_metric_card(st_name, str(funnel_summary.get(st_name, 0)))

st.divider()

col_e1, col_e2, col_space = st.columns([1, 1, 2])
with col_e1:
    csv_bytes = export_service.export_to_csv()
    st.download_button(
        label="📥 EXPORTAR CSV",
        data=csv_bytes,
        file_name="prospeccao_cxpack_radar.csv",
        mime="text/csv",
        use_container_width=True
    )
with col_e2:
    xlsx_bytes = export_service.export_to_xlsx()
    st.download_button(
        label="📊 EXPORTAR EXCEL (.XLSX)",
        data=xlsx_bytes,
        file_name="prospeccao_cxpack_radar.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

st.divider()

st.markdown("### 📋 Gestão dos Leads")

selected_status_filter = st.selectbox("Filtrar Funil por Estágio:", ["TODOS"] + VALID_CRM_STATUSES)

companies = company_repo.list_companies(min_score=0)
if selected_status_filter != "TODOS":
    companies = [c for c in companies if c.crm_status == selected_status_filter]

if not companies:
    st.info("Nenhuma empresa encontrada neste estágio do funil.")
else:
    for comp in companies:
        with st.expander(f"🏢 {comp.name} | Score: {comp.score} | Estágio: [{comp.crm_status}] | Responsável: [{comp.assigned_to or 'Não atribuído'}]", expanded=False):
            col_l1, col_l2 = st.columns([2, 1])

            with col_l1:
                st.markdown(f"**Website:** [{comp.website}]({comp.website}) | **Domínio:** `{comp.domain}`")
                st.markdown(f"**Tipo:** `{comp.company_type}` | **CNPJ:** `{comp.cnpj or 'Não informado'}`")
                st.markdown(f"**Localização:** {comp.city or ''}/{comp.state or ''}")
                if comp.description:
                    st.markdown(f"**Descrição:** {comp.description}")

            with col_l2:
                with st.form(key=f"crm_form_{comp.id}"):
                    new_st = st.selectbox("Mudar Estágio:", VALID_CRM_STATUSES, index=VALID_CRM_STATUSES.index(comp.crm_status) if comp.crm_status in VALID_CRM_STATUSES else 0)

                    current_assigned = comp.assigned_to or "Não atribuído"
                    if current_assigned not in team_options:
                        team_options.append(current_assigned)

                    new_assigned = st.selectbox("Responsável:", team_options, index=team_options.index(current_assigned))
                    new_notes = st.text_area("Notas Comerciais:", value=comp.notes or "", height=80)

                    save_btn = st.form_submit_button("💾 SALVAR LEAD", use_container_width=True)

                    if save_btn:
                        crm_service.update_lead_status(comp.id, new_st)
                        crm_service.assign_lead(comp.id, "" if new_assigned == "Não atribuído" else new_assigned)
                        crm_service.update_lead_notes(comp.id, new_notes)
                        st.success(f"Lead {comp.name} atualizado com sucesso!")
                        st.rerun()

                st.write("")
                if st.button("🗑️ EXCLUIR EMPRESA DO FUNIL", key=f"del_crm_{comp.id}", use_container_width=True):
                    if company_repo.delete_company(comp.id):
                        st.success(f"Empresa '{comp.name}' removida com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao excluir empresa.")
