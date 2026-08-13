"""
Componentes Especiais da UI do Lumin (ui/components/bento_cards.py).
Renderiza o Dark Hero Card, os Lime Highlight Cards e o Feed de Histórico de Prospecção sem indentações acidentais de Markdown.
"""

import streamlit as st
from typing import List, Dict, Any


def render_dark_hero_card(total_companies: int, manufacturers_count: int, quota_used: int, safety_limit: int):
    """
    Renderiza o Dark Hero Card em preto absoluto (#000000) com letras brancas (#FFFFFF) e detalhes em Lime (#D7FE03).
    """
    pct = min(100, int((quota_used / safety_limit) * 100)) if safety_limit > 0 else 0
    manuf_pct = min(100, int((manufacturers_count / max(1, total_companies)) * 100))

    html_code = (
        f'<div class="cx-dark-hero-card">'
        f'<div class="cx-dark-hero-label">TOTAL DE EMPRESAS PROSPECTADAS</div>'
        f'<div class="cx-dark-hero-value">{total_companies}</div>'
        f'<div class="cx-dark-action-bar">'
        f'<div class="cx-dark-action-btn" title="Fabricantes Qualificados">🏭</div>'
        f'<div class="cx-dark-action-btn" title="Busca Web Ativa">🔍</div>'
        f'<div class="cx-dark-action-btn" title="QSA Oficial">🏛️</div>'
        f'<div class="cx-dark-action-btn" title="Filtros B2B">⚙️</div>'
        f'</div>'
        f'<div class="cx-dark-progress-box">'
        f'<div style="display: flex; justify-content: space-between; font-size: 13px; font-weight: 700; color: #FFFFFF;">'
        f'<span style="color: #FFFFFF !important;">FABRICANTES CONFIRMADOS</span>'
        f'<span style="color: #D7FE03 !important; font-weight: 800;">{manufacturers_count} empresas</span>'
        f'</div>'
        f'<div class="cx-dark-progress-bar">'
        f'<div class="cx-dark-progress-fill" style="width: {manuf_pct}%;"></div>'
        f'</div>'
        f'<div style="font-size: 11px; color: #A1A1AA !important; margin-top: 4px; font-weight: 500;">'
        f'{pct}% do limite diário interno utilizado'
        f'</div>'
        f'</div>'
        f'</div>'
    )

    st.markdown(html_code, unsafe_allow_html=True)


def render_lime_card(title: str, subtitle: str, badge_text: str = "PRO"):
    """
    Renderiza um Lime Highlight Card em tom verde/lime (#D7FE03) com letras e ícones estritamente pretos (#000000).
    """
    html_code = (
        f'<div class="cx-lime-card">'
        f'<div>'
        f'<span class="cx-lime-badge">{badge_text}</span>'
        f'<div class="cx-lime-title" style="margin-top: 12px; color: #000000 !important;">{title}</div>'
        f'</div>'
        f'<div style="font-size: 13px; font-weight: 700; color: #000000 !important; margin-top: 8px;">'
        f'{subtitle}'
        f'</div>'
        f'</div>'
    )

    st.markdown(html_code, unsafe_allow_html=True)


def render_history_feed(history_items: List[Dict[str, Any]]):
    """
    Renderiza o Feed de Histórico de Empresas com letras escuras (#111111) sobre fundo branco.
    """
    items_html = ""
    for item in history_items[:5]:
        name = item.get("name", "Empresa")
        domain = item.get("domain", "")
        score = item.get("score", 0)
        c_type = item.get("company_type", "FABRICANTE")
        time_str = item.get("time_str", "Hoje")
        initial = name[0].upper() if name else "E"

        items_html += (
            f'<div class="cx-history-item">'
            f'<div style="display: flex; align-items: center; gap: 12px;">'
            f'<div class="cx-history-icon">{initial}</div>'
            f'<div>'
            f'<div style="font-weight: 700; font-size: 14px; color: #111111 !important;">{name}</div>'
            f'<div style="font-size: 12px; color: #6B6B70 !important;">{domain} • <span style="color: #000000 !important; font-weight: 600;">{c_type}</span></div>'
            f'</div>'
            f'</div>'
            f'<div style="text-align: right;">'
            f'<div class="cx-history-score">{score} pts</div>'
            f'<div style="font-size: 11px; color: #8E8E93 !important;">{time_str}</div>'
            f'</div>'
            f'</div>'
        )

    if not items_html:
        items_html = '<div style="color: #6B6B70; font-size: 13px; padding: 12px 0;">Nenhuma prospecção recente no histórico.</div>'

    html_code = (
        f'<div class="cx-history-feed">'
        f'<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">'
        f'<h3 style="font-size: 18px; font-weight: 800; color: #111111 !important; margin: 0;">Últimas Prospecções</h3>'
        f'<span style="font-size: 12px; font-weight: 700; color: #6B6B70 !important;">HOJE</span>'
        f'</div>'
        f'{items_html}'
        f'</div>'
    )

    st.markdown(html_code, unsafe_allow_html=True)
