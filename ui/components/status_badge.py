"""
Componente Status Badge (ui/components/status_badge.py).
"""

import streamlit as st


def get_status_badge(text: str, status_type: str = "inferido") -> str:
    """Retorna o HTML do badge de status."""
    st_type = status_type.lower()
    return f'<span class="cx-badge cx-badge-{st_type}">{text}</span>'


def render_status_badge(text: str, status_type: str = "inferido"):
    """Renderiza o badge de status diretamente no Streamlit."""
    st.markdown(get_status_badge(text, status_type), unsafe_allow_html=True)
