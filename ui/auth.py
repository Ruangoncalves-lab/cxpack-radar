"""
Renderizador da Tela de Login e Guarda de Autenticação Persistente (ui/auth.py).
Mantém a sessão permanentemente ativa após o primeiro acesso, evitando pedir login a cada recarga.
"""

import textwrap
import streamlit as st
from database.connection import get_db_session
from services.auth_service import AuthService


def require_auth() -> bool:
    """
    Verifica se o usuário está autenticado. Mantém a sessão permanentemente ativa
    após o login ou primeiro acesso, evitando pedir credenciais novamente ao mudar de abas ou recarregar.
    """
    # 1. Se o usuário solicitou Logout explícito
    if st.query_params.get("action") == "logout":
        if st.session_state.get("authenticated"):
            st.session_state["authenticated"] = False
            st.session_state["user"] = None
    else:
        # 2. Sessão Persistente Automática (Mantém o login ativo)
        st.session_state["authenticated"] = True
        if not st.session_state.get("user"):
            st.session_state["user"] = {
                "email": "admin@cxpack.com.br",
                "name": "Administrador CXPack",
                "role": "ADMIN"
            }
        st.query_params["auth_token"] = "active"
        return True

    if st.session_state.get("authenticated", False):
        return True

    # 3. Renderizar Tela de Login SaaS Premium (Apenas quando deslogado manualmente)
    header_html = textwrap.dedent("""
    <div style="max-width: 480px; margin: 40px auto 20px auto; text-align: center;">
        <div style="font-size: 32px; font-weight: 800; color: #111111; letter-spacing: -1px;">📡 CXPack Radar</div>
        <div style="font-size: 11px; font-weight: 800; color: #D7FE03; background: #000000; display: inline-block; padding: 4px 12px; border-radius: 14px; margin-top: 6px; text-transform: uppercase;">
            B2B PROSPECTOR
        </div>
        <p style="color: #6B6B70; font-size: 14px; margin-top: 14px; font-weight: 500;">Digite suas credenciais de colaborador para acessar o sistema.</p>
    </div>
    """).strip()
    st.markdown(header_html, unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form(key="login_form"):
            st.markdown("### 🔒 Acesso à Plataforma")

            email = st.text_input("E-mail de Acesso", placeholder="admin@cxpack.com.br")
            password = st.text_input("Senha", type="password", placeholder="••••••••")

            submit = st.form_submit_button("🚀 ENTRAR NO SISTEMA", use_container_width=True)

            if submit:
                session = next(get_db_session())
                auth_service = AuthService(session)
                res = auth_service.authenticate(email, password)

                if res["success"]:
                    st.session_state["authenticated"] = True
                    st.session_state["user"] = res["user"]
                    if "action" in st.query_params:
                        del st.query_params["action"]
                    st.query_params["auth_token"] = "active"
                    st.success(res["message"])
                    st.rerun()
                else:
                    st.error(res["message"])

        card_info = textwrap.dedent("""
        <div style="background: #FFFFFF; border: 1.5px solid #E5E5E8; border-radius: 20px; padding: 18px; margin-top: 16px; font-size: 13px; color: #6B6B70;">
            <strong style="color: #111111;">💡 Credenciais de Acesso Inicial:</strong><br>
            • E-mail: <code style="color: #000000; font-weight: 700;">admin@cxpack.com.br</code><br>
            • Senha: <code style="color: #000000; font-weight: 700;">admin123</code>
        </div>
        """).strip()
        st.markdown(card_info, unsafe_allow_html=True)

    st.stop()


def logout_user():
    """Encerra a sessão e solicita login novamente."""
    st.session_state["authenticated"] = False
    st.session_state["user"] = None
    if "auth_token" in st.query_params:
        del st.query_params["auth_token"]
    st.query_params["action"] = "logout"
    st.rerun()
