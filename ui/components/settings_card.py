"""
Componente Settings Card (ui/components/settings_card.py).
Container modular estilo SaaS B2B Premium para opções de configuração.
"""

import streamlit as st


def render_settings_card_header(title: str, subtitle: str = "", status_html: str = ""):
    """Renderiza o cabeçalho estilizado de um card de configuração."""
    sub_html = f'<div style="color: #6B6B70; font-size: 13px; margin-top: 2px;">{subtitle}</div>' if subtitle else ''
    st.markdown(
        f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
            <div>
                <h3 style="font-size: 18px; font-weight: 600; color: #111111; margin: 0; letter-spacing: -0.3px;">{title}</h3>
                {sub_html}
            </div>
            <div>{status_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
