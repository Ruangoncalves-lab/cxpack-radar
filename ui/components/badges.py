"""
Componente de Badges e Selos de Status (ui/components/badges.py).
"""

import streamlit as st


def get_badge_html(text: str, badge_type: str = "inferido") -> str:
    """Retorna o código HTML formatado do selo."""
    b_type = badge_type.lower()
    css_class = f"cx-badge cx-badge-{b_type}"
    return f'<span class="{css_class}">{text}</span>'


def render_badge(text: str, badge_type: str = "inferido"):
    """Renderiza diretamente o selo no Streamlit."""
    st.markdown(get_badge_html(text, badge_type), unsafe_allow_html=True)
