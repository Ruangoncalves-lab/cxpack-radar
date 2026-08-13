"""
Componente Topbar do App Shell (ui/components/topbar.py).
Renderiza a barra de navegação superior no estilo do Lumin mantendo o token de autenticação ativo.
"""

import textwrap
import streamlit as st


def render_topbar(current_page: str = "home"):
    """Renderiza a Topbar superior padronizada do Lumin com pills ativas e preservação de sessão."""
    user = st.session_state.get("user", {})
    user_name = user.get("name", "Michael")

    pages = [
        ("home", "Dashboard", "/"),
        ("search", "Nova Pesquisa", "/new_search"),
        ("results", "Empresas & QSA", "/results"),
        ("decision_makers", "Decisores", "/decision_makers"),
        ("crm", "Mini CRM", "/crm"),
        ("dashboard", "Analytics", "/dashboard"),
        ("settings", "Configurações", "/settings")
    ]

    pills_html = ""
    for p_id, p_title, p_route in pages:
        active_cls = "active" if current_page == p_id else ""
        route_url = f"{p_route}?auth_token=active" if p_route != "/" else "/?auth_token=active"
        pills_html += f'<a href="{route_url}" target="_self" class="cx-nav-pill {active_cls}">{p_title}</a>'

    html_code = textwrap.dedent(f"""
    <div class="cx-topbar">
        <a href="/?auth_token=active" target="_self" class="cx-topbar-brand">
            <span>📡 CXPack Radar</span>
        </a>
        <div class="cx-topbar-nav">
            {pills_html}
        </div>
        <div style="display: flex; align-items: center; gap: 14px;">
            <div style="font-size: 14px; font-weight: 700; color: #111111;">
                Olá, {user_name.split()[0]}
            </div>
            <div style="width: 38px; height: 38px; border-radius: 50%; background: #000000; color: #D7FE03; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 14px;">
                {user_name[0].upper()}
            </div>
        </div>
    </div>
    """).strip()

    st.markdown(html_code, unsafe_allow_html=True)
