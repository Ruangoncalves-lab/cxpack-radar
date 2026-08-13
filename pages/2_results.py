"""
Tela de Resultados da Pesquisa, Score, Enriquecimento CNPJ/QSA, Decisores e Gestão de Empresas (pages/2_results.py).
"""

import streamlit as st
import pandas as pd
from database.connection import get_db_session
from database.repositories.searches import SearchRepository
from database.repositories.companies import CompanyRepository
from database.repositories.contacts import ContactRepository
from database.repositories.pages import PageRepository
from database.repositories.decision_makers import DecisionMakerRepository
from database.repositories.partners import PartnerRepository
from database.repositories.department_contacts import DepartmentContactRepository
from services.enrichment_service import EnrichmentService
from services.department_contact_service import DepartmentContactService
from services.scoring_service import ScoringService
from services.decision_maker_service import DECISION_MAKER_MIN_SCORE
from ui.layout import apply_app_shell
from ui.components.status_badge import get_status_badge

st.set_page_config(page_title="Resultados - CXPack Radar", page_icon="📊", layout="wide")
apply_app_shell(current_page="results")

st.markdown('<div class="cx-hero-title">Resultados & Banco de Empresas</div>', unsafe_allow_html=True)
st.markdown('<div class="cx-hero-subtitle">Base de fornecedores prospectados, enriquecimento de CNPJ/QSA e contatos do setor de Compras.</div>', unsafe_allow_html=True)

session = next(get_db_session())
search_repo = SearchRepository(session)
company_repo = CompanyRepository(session)
contact_repo = ContactRepository(session)
page_repo = PageRepository(session)
dm_repo = DecisionMakerRepository(session)
partner_repo = PartnerRepository(session)
dept_repo = DepartmentContactRepository(session)
enrichment_service = EnrichmentService(session)
dept_service = DepartmentContactService(session)
scoring_service = ScoringService()

col_f1, col_f2 = st.columns(2)
with col_f1:
    min_score = st.slider("Score Mínimo", min_value=0, max_value=100, value=0)
with col_f2:
    company_type_filter = st.selectbox("Filtrar por Tipo", ["TODOS", "FABRICANTE", "DISTRIBUIDOR", "DESCONHECIDO"])

companies = company_repo.list_companies(min_score=min_score, company_type=company_type_filter)

if not companies:
    st.info("Nenhuma empresa encontrada com os filtros selecionados. Realize uma nova pesquisa na tela `1_new_search`.")
else:
    st.markdown(f"### 🏢 Empresas Cadastradas ({len(companies)})")

    data = []
    for c in companies:
        contacts = contact_repo.get_company_contacts(c.id)
        dms = dm_repo.get_company_decision_makers(c.id)
        partners = partner_repo.get_company_partners(c.id)
        dept_contacts = dept_repo.get_company_department_contacts(c.id)

        # Extrair e-mail e telefone principais dos contatos
        email_list = [ct.value for ct in contacts if "EMAIL" in ct.contact_type]
        phone_list = [ct.value for ct in contacts if ct.contact_type in ("TELEFONE", "WHATSAPP")]
        dept_emails = [dc.email for dc in dept_contacts if dc.email]

        main_email = email_list[0] if email_list else (dept_emails[0] if dept_emails else "Não identificado")
        main_phone = phone_list[0] if phone_list else "Não informado"

        data.append({
            "ID": c.id,
            "Score": c.score,
            "Empresa": c.name,
            "Domínio": c.domain,
            "CNPJ": c.cnpj or "Não vinculado",
            "E-mail Público": main_email,
            "Telefone / Whats": main_phone,
            "Tipo": c.company_type,
            "Cidade/UF": f"{c.city or ''}/{c.state or ''}".strip("/"),
            "Decisores": len(dms),
            "QSA Sócios": len(partners),
            "Última Atualização": c.updated_at.strftime("%d/%m/%Y %H:%M")
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    st.markdown("### 🔍 Inspecionar e Gerenciar Empresa")

    selected_domain = st.selectbox("Selecione uma empresa para inspecionar:", [c.domain for c in companies])
    if selected_domain:
        comp = company_repo.get_by_domain(selected_domain)
        if comp:
            col_d1, col_d2 = st.columns([2, 1])

            with col_d1:
                st.markdown(f"## 🏢 {comp.name}")
                if comp.legal_name:
                    st.markdown(f"**Razão Social:** `{comp.legal_name}`")
                st.markdown(f"**Website Oficial:** [{comp.website}]({comp.website})")
                st.markdown(f"**CNPJ Público:** `{comp.cnpj or 'Não vinculado'}` | **Situação:** `{comp.status_cadastral or 'ATIVA'}`")
                if comp.cnae_text:
                    st.markdown(f"**CNAE Principal:** `{comp.cnae_code}` - {comp.cnae_text}")

                b_type = "fabricante" if comp.company_type == "FABRICANTE" else ("distribuidor" if comp.company_type == "DISTRIBUIDOR" else "inferido")
                st.markdown(f"**Classificação:** {get_status_badge(comp.company_type, b_type)} | **Score Total:** `{comp.score}/100`", unsafe_allow_html=True)
                if comp.description:
                    st.markdown(f"**Descrição:** {comp.description}")

            with col_d2:
                st.markdown("#### ⚡ Ações Inteligentes")

                if st.button("🔍 ENRIQUECER EMPRESA (CNPJ, QSA & COMPRAS)", use_container_width=True):
                    with st.spinner(f"Executando enriquecimento em camadas para {comp.name}..."):
                        res = enrichment_service.enrich_company(comp.id, operator="usuario")
                        if res["success"]:
                            st.success(f"🎉 Enriquecimento concluído com sucesso! (Nível Alcançado: {res['best_level']})")
                            for log_msg in res["log"]:
                                st.info(f"• {log_msg}")
                            st.rerun()
                        else:
                            st.error(res["message"])

                st.write("")
                if st.button("🗑️ EXCLUIR EMPRESA DO BANCO", use_container_width=True):
                    if company_repo.delete_company(comp.id):
                        st.success(f"Empresa '{comp.name}' excluída com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao excluir empresa.")

            st.divider()

            tab_comp, tab_qsa, tab_score, tab_contacts, tab_ev = st.tabs([
                "🛒 COMPRAS E DECISORES",
                "🏛️ QSA SOCIETÁRIO",
                "🎯 Score",
                "📞 Contatos & Páginas",
                "📜 Evidências"
            ])

            with tab_comp:
                st.markdown("#### 🛒 DEPARTAMENTO DE COMPRAS & TOMADORES DE DECISÃO")

                levels_info = dept_service.classify_prospecting_levels(comp.id)
                st.markdown(f"**Melhor Nível de Abordagem B2B:** `{levels_info['best_level']}`")

                st.markdown("##### 🔵 Contatos do Setor (Departamento)")
                dept_contacts = dept_repo.get_company_department_contacts(comp.id)
                if dept_contacts:
                    dc_data = []
                    for dc in dept_contacts:
                        dc_data.append({
                            "Setor / Departamento": dc.department,
                            "E-mail do Setor": dc.email or "Não informado",
                            "Telefone / Whats": dc.phone or dc.whatsapp or "Não informado",
                            "Selo": "CONTATO DO SETOR",
                            "Fonte": dc.source_url or comp.website
                        })
                    st.dataframe(pd.DataFrame(dc_data), use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum e-mail direto de departamento (ex: compras@) cadastrado ainda.")

                st.divider()

                st.markdown("##### ⚙️ Decisores Operacionais (Compras, Suprimentos & Fábrica)")
                dms_op = [dm for dm in dm_repo.get_company_decision_makers(comp.id) if dm.decision_maker_type == "OPERATIONAL"]
                if dms_op:
                    dm_data = []
                    for dm in dms_op:
                        badge = "CONFIRMADO" if dm.email_status == "PUBLICADO" else ("CONTATO DO SETOR" if dm.email_status == "DEPARTAMENTO" else ("INFERIDO" if dm.email_status == "INFERIDO" else "NÃO ENCONTRADO"))
                        dm_data.append({
                            "Nome": dm.name,
                            "Cargo": dm.role,
                            "Departamento": dm.department or "Compras",
                            "E-mail Profissional": dm.email or "Não identificado",
                            "Selo de Veracidade": badge,
                            "Confiança": f"{int(dm.confidence * 100)}%",
                            "Fonte": dm.source_title or dm.source_url or "Website"
                        })
                    st.dataframe(pd.DataFrame(dm_data), use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum decisor operacional identificado ainda. Execute o botão **ENRIQUECER EMPRESA** acima.")

            with tab_qsa:
                st.markdown("#### 🏛️ QUADRO DE SÓCIOS E ADMINISTRADORES (QSA)")
                partners = partner_repo.get_company_partners(comp.id)
                if partners:
                    p_data = []
                    for p in partners:
                        p_data.append({
                            "Nome do Sócio / Administrador": p.name,
                            "Qualificação / Cargo": p.qualification,
                            "País": p.country,
                            "Fonte": p.source,
                            "Coletado em": p.created_at.strftime("%d/%m/%Y %H:%M")
                        })
                    st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)
                else:
                    st.info("QSA não consultado ou não disponível. Clique em **ENRIQUECER EMPRESA** para buscar os dados abertos do CNPJ na Receita Federal.")

            with tab_score:
                st.markdown("#### 📊 Decomposição Transparente da Nota")
                dms_count = len(dm_repo.get_company_decision_makers(comp.id))
                score_data = scoring_service.calculate_score(
                    company_type=comp.company_type,
                    product_matched=True,
                    material_matched=False,
                    capacity_matched=False,
                    location_matched=True,
                    has_phone=any(ct.contact_type in ("TELEFONE", "WHATSAPP") for ct in comp.contacts),
                    has_email=any("EMAIL" in ct.contact_type for ct in comp.contacts),
                    has_decision_maker=dms_count > 0
                )

                st.progress(score_data["total_score"] / 100.0)
                b_df = pd.DataFrame(score_data["breakdown"])
                st.dataframe(b_df, use_container_width=True, hide_index=True)

            with tab_contacts:
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    st.markdown("#### 📞 Contatos Públicos do Website")
                    contacts = contact_repo.get_company_contacts(comp.id)
                    if contacts:
                        c_data = []
                        for ct in contacts:
                            icon = "📧" if "EMAIL" in ct.contact_type else ("💬" if ct.contact_type == "WHATSAPP" else "📞")
                            c_data.append({
                                "Tipo": f"{icon} {ct.contact_type}",
                                "Contato": ct.value,
                                "Fonte": ct.source_url or comp.website
                            })
                        st.dataframe(pd.DataFrame(c_data), use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhum contato extraído ainda.")

                with col_c2:
                    st.markdown("#### 📄 Páginas Rastreadas")
                    pages = page_repo.get_company_pages(comp.id)
                    if pages:
                        p_data = []
                        for pg in pages:
                            p_data.append({
                                "Status": f"🟢 {pg.status_code}" if pg.status_code == 200 else f"🔴 {pg.status}",
                                "URL": pg.url,
                                "Título": pg.title or "Sem título"
                            })
                        st.dataframe(pd.DataFrame(p_data), use_container_width=True, hide_index=True)
                    else:
                        st.info("Nenhuma página rastreada ainda.")

            with tab_ev:
                if comp.evidences:
                    for ev in comp.evidences:
                        st.info(
                            f"**Campo:** `{ev.field_name}` | **Confiança:** `{int(ev.confidence*100)}%`\n\n"
                            f"**Texto:** {ev.source_text}\n\n"
                            f"**Fonte Original:** [{ev.source_title or ev.source_url}]({ev.source_url})"
                        )
                else:
                    st.write("Nenhuma evidência salva.")
