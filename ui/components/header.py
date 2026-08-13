"""
Componente de Cabeçalho / Top Navbar (ui/components/header.py).
"""

import streamlit as st


def render_header(title: str, subtitle: str = ""):
    """Renderiza um cabeçalho limpo no estilo SaaS B2B Premium."""
    st.markdown(
        f"""
        <div class="cx-header">
            <div class="cx-brand">
                <span>📡 CXPack Radar</span>
                <span class="cx-brand-badge">B2B PROSPECTOR</span>
            </div>
        </div>
        <div class="cx-hero-title">{title}</div>
        """,
        unsafe_allow_html=True
    )
    if subtitle:
        st.markdown(f'<div class="cx-hero-subtitle">{subtitle}</div>', unsafe_allow_html=True)
