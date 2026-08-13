"""
Componente Hero Search Panel (ui/components/search_panel.py).
Wrapper visual para formulários de busca industrial com estilo Bento Grid.
"""

import streamlit as st


def render_search_panel_header(title: str = "O que você está procurando?", subtitle: str = ""):
    """Renderiza o cabeçalho estilizado do painel de pesquisa."""
    sub_html = f'<div style="color: #6B6B70; font-size: 14px; margin-bottom: 20px;">{subtitle}</div>' if subtitle else ''
    st.markdown(
        f"""
        <div style="margin-bottom: 12px;">
            <h2 style="font-size: 26px; font-weight: 600; color: #111111; letter-spacing: -0.5px; margin-bottom: 4px;">{title}</h2>
            {sub_html}
        </div>
        """,
        unsafe_allow_html=True
    )
