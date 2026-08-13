"""
Componente Integration Card (ui/components/integration_card.py).
Card de status de integração de API (Gemini, Banco, Provedores).
"""

import streamlit as st
from ui.components.status_badge import get_status_badge


def render_integration_header(provider_name: str, description: str, is_active: bool = True):
    """Renderiza o topo de um card de integração."""
    badge_html = get_status_badge("🟢 CONECTADO", "confirmado") if is_active else get_status_badge("🔴 PENDENTE", "erro")
    st.markdown(
        f"""
        <div class="cx-bento-card" style="margin-bottom: 12px; padding: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span style="font-size: 16px; font-weight: 700; color: #111111;">{provider_name}</span>
                    <div style="font-size: 13px; color: #6B6B70; margin-top: 2px;">{description}</div>
                </div>
                <div>{badge_html}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
