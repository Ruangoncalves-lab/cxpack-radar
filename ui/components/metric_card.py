"""
Componente de Card de KPI / Métrica (ui/components/metric_card.py).
Estilo limpo, fundo branco, cantos arredondados (Bento Grid).
"""

import streamlit as st
from typing import Optional


def render_metric_card(label: str, value: str, delta: Optional[str] = None):
    """Renderiza um card de KPI elegante sem emojis saturados."""
    delta_html = f'<div class="cx-metric-delta">{delta}</div>' if delta else ''
    st.markdown(
        f"""
        <div class="cx-metric-card">
            <div class="cx-metric-label">{label}</div>
            <div class="cx-metric-value">{value}</div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True
    )
