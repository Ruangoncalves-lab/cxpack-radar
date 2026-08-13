"""
Painel de Configurações, Credenciais & Gestão de Equipe (pages/0_settings.py).
Permite visualizar, cadastrar, salvar e testar a GEMINI_API_KEY e a DATABASE_URL do Supabase (PostgreSQL).
"""

import os
import streamlit as st
import pandas as pd
from core.config import DEFAULT_GEMINI_MODEL, SEARCH_PROVIDER, MAX_WEB_SEARCHES_PER_USER_DAY
from core.secrets import is_gemini_configured, get_gemini_api_key, get_secret
from database.connection import test_db_connection, get_database_url, get_db_session
from database.repositories.settings import SettingsRepository
from providers.llm.gemini_provider import GeminiProvider
from services.team_service import TeamService
from ui.layout import apply_app_shell
from ui.components.status_badge import render_status_badge

st.set_page_config(page_title="Configurações - CXPack Radar", page_icon="⚙️", layout="wide")
apply_app_shell(current_page="settings")

st.markdown('<div class="cx-hero-title">Painel de Configurações & Credenciais</div>', unsafe_allow_html=True)
st.markdown('<div class="cx-hero-subtitle">Gerencie chaves de API, banco de dados Supabase (PostgreSQL), busca web (DDGS) e colaboradores.</div>', unsafe_allow_html=True)

session = next(get_db_session())
settings_repo = SettingsRepository(session)
team_service = TeamService(session)

tab1, tab2, tab3 = st.tabs(["🔑 Credenciais & Integrações", "👥 Membros da Equipe", "☁️ Guia Supabase PostgreSQL"])

with tab1:
    col_c1, col_c2 = st.columns(2)

    with col_c1:
        st.markdown(
            """
            <div class="cx-bento-card">
                <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 4px;">🌐 Busca Web Pública (Search Provider)</h3>
                <p style="font-size: 13px; color: #6B6B70; margin-bottom: 12px;">Motor desacoplado de prospecção web gratuita.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(f"**Provedor Ativo:** `{SEARCH_PROVIDER.upper()}` (DuckDuckGo Search)")
        st.markdown("**Modo de Operação:** `Busca pública gratuita (Custo: R$ 0)`")
        st.markdown(f"**Limite Interno Diário:** `{MAX_WEB_SEARCHES_PER_USER_DAY} buscas/usuário`")
        render_status_badge("🟢 PROVIDER DISPONÍVEL", "confirmado")

        st.divider()

        st.markdown(
            """
            <div class="cx-bento-card">
                <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 4px;">🤖 Inteligência Artificial (Google Gemini)</h3>
                <p style="font-size: 13px; color: #6B6B70; margin-bottom: 12px;">Responsável exclusivamente por análise semântica, classificação e extração.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        current_key = get_gemini_api_key() or settings_repo.get("GEMINI_API_KEY", "")

        input_key = st.text_input(
            "Chave de API do Gemini (GEMINI_API_KEY)",
            value=current_key if current_key else "",
            type="password",
            placeholder="AIzaSyD...",
            help="Sua chave de API do Google AI Studio"
        )

        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("💾 SALVAR CHAVE GEMINI", use_container_width=True):
                if input_key and input_key.strip():
                    new_k = input_key.strip()
                    os.environ["GEMINI_API_KEY"] = new_k
                    settings_repo.set("GEMINI_API_KEY", new_k, "Chave da API do Google Gemini cadastrada via UI")

                    try:
                        secrets_dir = os.path.join(os.getcwd(), ".streamlit")
                        secrets_path = os.path.join(secrets_dir, "secrets.toml")
                        if not os.path.exists(secrets_dir):
                            os.makedirs(secrets_dir, exist_ok=True)

                        # Ler conteúdo existente
                        existing_content = ""
                        if os.path.exists(secrets_path):
                            with open(secrets_path, "r", encoding="utf-8") as f:
                                existing_content = f.read()

                        # Atualizar ou adicionar GEMINI_API_KEY
                        lines = [l for l in existing_content.splitlines() if not l.startswith("GEMINI_API_KEY")]
                        lines.append(f'GEMINI_API_KEY = "{new_k}"')
                        with open(secrets_path, "w", encoding="utf-8") as f:
                            f.write("\n".join(lines) + "\n")
                    except Exception:
                        pass

                    st.success("🎉 GEMINI_API_KEY salva com sucesso!")
                    st.rerun()
                else:
                    st.error("Por favor, digite uma chave válida antes de salvar.")

        with col_b2:
            if st.button("🧪 TESTAR GEMINI", use_container_width=True):
                with st.spinner("Conectando ao Google Gemini..."):
                    provider = GeminiProvider()
                    success, user_msg, tech_details = provider.test_connection()
                    if success:
                        st.success(user_msg)
                        st.session_state["gemini_test_status"] = "CONNECTED"
                    else:
                        st.error(user_msg)
                        st.session_state["gemini_test_status"] = "ERROR"

        st.markdown(f"**Modelo Configurado:** `Gemini 3.1 Flash-Lite` (`{DEFAULT_GEMINI_MODEL}`)")

    with col_c2:
        st.markdown(
            """
            <div class="cx-bento-card">
                <h3 style="font-size: 20px; font-weight: 600; margin-bottom: 4px;">🗄️ Banco de Dados Supabase (PostgreSQL / SQLite)</h3>
                <p style="font-size: 13px; color: #6B6B70; margin-bottom: 12px;">Conecte seu banco PostgreSQL no Supabase para dados em nuvem.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        current_db_url = get_database_url()
        input_db_url = st.text_input(
            "String de Conexão (DATABASE_URL)",
            value=current_db_url if "postgresql" in current_db_url else "",
            type="password",
            placeholder="postgresql://postgres:SuaSenha@db.xyz.supabase.co:5432/postgres",
            help="URL de conexão PostgreSQL obtida no painel do Supabase"
        )

        col_db1, col_db2 = st.columns(2)
        with col_db1:
            if st.button("💾 SALVAR SUPABASE URL", use_container_width=True):
                if input_db_url and input_db_url.strip():
                    new_db = input_db_url.strip()
                    os.environ["DATABASE_URL"] = new_db

                    try:
                        secrets_dir = os.path.join(os.getcwd(), ".streamlit")
                        secrets_path = os.path.join(secrets_dir, "secrets.toml")
                        if not os.path.exists(secrets_dir):
                            os.makedirs(secrets_dir, exist_ok=True)

                        existing_content = ""
                        if os.path.exists(secrets_path):
                            with open(secrets_path, "r", encoding="utf-8") as f:
                                existing_content = f.read()

                        lines = [l for l in existing_content.splitlines() if not l.startswith("DATABASE_URL")]
                        lines.append(f'DATABASE_URL = "{new_db}"')
                        with open(secrets_path, "w", encoding="utf-8") as f:
                            f.write("\n".join(lines) + "\n")
                    except Exception:
                        pass

                    st.success("🎉 DATABASE_URL salva com sucesso!")
                    st.rerun()
                else:
                    st.error("Por favor, digite uma URL válida do Supabase antes de salvar.")

        with col_db2:
            if st.button("🧪 TESTAR BANCO", use_container_width=True):
                with st.spinner("Testando conexão com a base de dados..."):
                    success, msg = test_db_connection()
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")

        st.divider()

        db_ok, db_msg = test_db_connection()
        db_url_active = get_database_url()
        mode_str = "CLOUD (PostgreSQL / Supabase)" if "postgresql" in db_url_active else "LOCAL (SQLite Local)"

        st.markdown(f"**Modo de Operação Atual:** `{mode_str}`")

        st.markdown("**Status do Banco:**")
        if db_ok:
            render_status_badge("🟢 BANCO OPERACIONAL", "confirmado")
        else:
            render_status_badge("🔴 BANCO DESCONECTADO", "erro")

with tab2:
    st.markdown("#### 👥 Cadastro e Gestão de Colaboradores")
    st.markdown("Cadastre os membros da equipe para atribuição de leads no CRM. *(Sem armazenamento de senhas)*")

    col_add1, col_add2, col_add3 = st.columns([2, 2, 1])
    with col_add1:
        new_name = st.text_input("Nome do Colaborador:", placeholder="Ex: Sérgio, Maria, João")
    with col_add2:
        new_email = st.text_input("E-mail do Colaborador:", placeholder="exemplo@empresa.com.br")
    with col_add3:
        st.write("")
        st.write("")
        if st.button("➕ ADICIONAR", use_container_width=True):
            res = team_service.add_member(new_name, new_email)
            if res["success"]:
                st.success(f"Membro {res['name']} cadastrado com sucesso!")
                st.rerun()
            else:
                st.error(res["message"])

    st.divider()
    st.markdown("#### 📋 Lista de Membros Cadastrados")

    members = team_service.list_all_members()
    if not members:
        st.info("Nenhum colaborador cadastrado ainda.")
    else:
        m_data = []
        for m in members:
            m_data.append({
                "ID": m.id,
                "Nome": m.name,
                "E-mail": m.email,
                "Status": "Ativo" if m.active else "Inativo",
                "Cadastrado em": m.created_at.strftime("%d/%m/%Y %H:%M")
            })
        st.dataframe(pd.DataFrame(m_data), use_container_width=True, hide_index=True)

with tab3:
    st.markdown("#### ☁️ Como Criar seu Banco de Dados Gratuito no Supabase")
    st.markdown("""
    Siga os passos abaixo para conectar o **CXPack Radar** ao seu banco de dados PostgreSQL na nuvem:

    1. Acesse **[https://supabase.com](https://supabase.com)** e crie uma conta gratuita.
    2. Clique em **New Project** e digite o nome do projeto (ex: `cxpack-radar`).
    3. Defina uma senha forte para o banco de dados.
    4. Vá em **Project Settings -> Database -> Connection string -> URI**.
    5. Copie a URL gerada (exemplo: `postgresql://postgres:SuaSenha@db.xyz.supabase.co:5432/postgres`).
    6. Cole essa URL no campo **DATABASE_URL** da aba de credenciais ao lado e clique em **SALVAR SUPABASE URL**.

    O CXPack Radar irá criar automaticamente todas as tabelas e migrar a base para a nuvem!
    """)
