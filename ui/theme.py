"""
Módulo Helper de Aplicação de Tema e Design System (ui/theme.py).
Injeta o arquivo CSS centralizado e fontes personalizadas em todas as telas do Streamlit.
"""

import os
import streamlit as st

_CSS_PATH = os.path.join(os.path.dirname(__file__), "styles.css")


def apply_theme():
    """Injeta o CSS centralizado do CXPack Radar no Streamlit."""
    try:
        if os.path.exists(_CSS_PATH):
            with open(_CSS_PATH, "r", encoding="utf-8") as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Aviso ao carregar tema visual: {e}")
