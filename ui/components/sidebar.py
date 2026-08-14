"""
Componente Sidebar Aprimorado (ui/components/sidebar.py).
Renderiza o menu lateral categorizado, com status em tempo real e card do usuário logado.
"""

import textwrap
import streamlit as st
from core.secrets import is_gemini_configured
from database.connection import test_db_connection, get_database_url
from ui.auth import logout_user


def render_sidebar():
    """Renderiza a Sidebar categorizada no estilo SaaS B2B Premium."""
    user = st.session_state.get("user", {})
    user_name = user.get("name", "Administrador")
    user_email = user.get("email", "admin@cxpack.com.br")

    gemini_ok = is_gemini_configured()
    db_ok, _ = test_db_connection()
    db_url = get_database_url()
    db_mode = "Supabase" if "postgresql" in db_url else "SQLite"

    with st.sidebar:
        header_html = textwrap.dedent("""
        <div class="cx-sidebar-header">
            <div style="font-size: 20px; font-weight: 800; color: #111111; letter-spacing: -0.5px;">📡 CXPack Radar</div>
            <div style="font-size: 10px; font-weight: 800; color: #D7FE03; background: #000000; display: inline-block; padding: 2px 8px; border-radius: 10px; margin-top: 4px;">
                RADAR INDUSTRIAL B2B
            </div>
        </div>
        """).strip()
        st.markdown(header_html, unsafe_allow_html=True)

        # Categoria 1: Prospecção
        st.markdown('<div class="cx-sidebar-category">Prospecção</div>', unsafe_allow_html=True)
        if st.button("⌂  Visão geral", use_container_width=True):
            st.switch_page("streamlit_app.py")
        if st.button("＋  Nova prospecção", use_container_width=True):
            st.switch_page("pages/1_new_search.py")
        if st.button("◎  Empresas e evidências", use_container_width=True):
            st.switch_page("pages/2_results.py")
        if st.button("◇  Decisores", use_container_width=True):
            st.switch_page("pages/4_decision_makers.py")

        # Categoria 2: Gestão Comercial
        st.markdown('<div class="cx-sidebar-category">Operação comercial</div>', unsafe_allow_html=True)
        if st.button("▦  Pipeline CRM", use_container_width=True):
            st.switch_page("pages/5_crm.py")
        if st.button("↗  Indicadores", use_container_width=True):
            st.switch_page("pages/6_dashboard.py")
        if st.button("📊 Uso da API & Cotas", use_container_width=True):
            st.switch_page("pages/3_api_usage.py")

        # Categoria 3: Sistema
        st.markdown('<div class="cx-sidebar-category">⚙️ Sistema</div>', unsafe_allow_html=True)
        if st.button("⚙️ Configurações & Chaves", use_container_width=True):
            st.switch_page("pages/0_settings.py")

        st.divider()

        # Status em Tempo Real
        st.markdown('<div class="cx-sidebar-category">🔌 Status da Infra</div>', unsafe_allow_html=True)
        st.markdown(f"• **Search Provider:** `DDGS (R$ 0)`")
        st.markdown(f"• **Gemini 3.1:** {'🟢 Ativo' if gemini_ok else '🔴 Inativo'}")
        st.markdown(f"• **Banco:** `🟢 {db_mode}`" if db_ok else "• **Banco:** `🔴 Erro` ")

        # Card do Usuário Logado no Rodapé
        user_card_html = textwrap.dedent(f"""
        <div class="cx-user-profile-card">
            <div style="font-weight: 700; font-size: 13px; color: #111111;">👤 {user_name}</div>
            <div style="font-size: 11px; color: #6B6B70; margin-top: 2px;">{user_email}</div>
        </div>
        """).strip()
        st.markdown(user_card_html, unsafe_allow_html=True)

        if st.session_state.get("authenticated"):
            if st.button("🚪 SAIR DA CONTA", use_container_width=True):
                logout_user()
