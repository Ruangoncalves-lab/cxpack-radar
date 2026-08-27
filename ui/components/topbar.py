"""App shell responsivo inspirado em dashboards operacionais de alta densidade."""

import html
from datetime import datetime

import streamlit as st


_ICONS = {
    "home": '<path d="M4 5h6v6H4zM14 5h6v6h-6zM4 15h6v6H4zM14 15h6v6h-6z"/>',
    "search": '<circle cx="11" cy="11" r="6"/><path d="m16 16 4 4M11 8v6M8 11h6"/>',
    "history": '<path d="M4 6h16M4 12h16M4 18h10"/>',
    "results": '<path d="M4 20V8l8-4 8 4v12M8 20v-5h8v5M8 10h.01M12 10h.01M16 10h.01"/>',
    "decision_makers": '<circle cx="12" cy="8" r="3"/><path d="M5 20c.7-4 3-6 7-6s6.3 2 7 6"/>',
    "crm": '<path d="M4 6h16v12H4zM4 10h16"/>',
    "dashboard": '<path d="M5 20V10M12 20V4M19 20v-7"/>',
    "settings": '<circle cx="12" cy="12" r="3"/><path d="M19 12a7 7 0 0 0-.1-1l2-1.5-2-3.4-2.4 1A7 7 0 0 0 15 6l-.3-2.6h-4L10.4 6A7 7 0 0 0 8 7.1l-2.4-1-2 3.4 2 1.5a7 7 0 0 0 0 2l-2 1.5 2 3.4 2.4-1A7 7 0 0 0 10.4 18l.3 2.6h4L15 18a7 7 0 0 0 1.6-1.1l2.4 1 2-3.4-2-1.5a7 7 0 0 0 .1-1z"/>',
}


def _nav_link(page_id: str, label: str, route: str, current_page: str) -> str:
    active = " active" if current_page == page_id else ""
    current = ' aria-current="page"' if current_page == page_id else ""
    url = f"{route}?auth_token=active" if route != "/" else "/?auth_token=active"
    return (
        f'<a href="{url}" target="_self" class="cx-rail-link{active}" aria-label="{label}" title="{label}"{current}>'
        f'<svg viewBox="0 0 24 24" aria-hidden="true">{_ICONS[page_id]}</svg></a>'
    )


def render_topbar(current_page: str = "home"):
    """Renderiza rail desktop, cabeçalho contextual e navegação mobile."""
    user = st.session_state.get("user", {})
    user_name = html.escape(user.get("name", "Administrador"))
    first_name = user_name.split()[0]
    greeting = "Bom dia" if datetime.now().hour < 12 else ("Boa tarde" if datetime.now().hour < 18 else "Boa noite")

    primary_pages = [
        ("home", "Visão geral", "/"),
        ("search", "Nova busca", "/new_search"),
        ("history", "Histórico", "/search_history"),
        ("results", "Empresas", "/results"),
        ("decision_makers", "Decisores", "/decision_makers"),
        ("crm", "Pipeline CRM", "/crm"),
        ("dashboard", "Indicadores", "/dashboard"),
    ]
    rail_links = "".join(_nav_link(*page, current_page) for page in primary_pages)
    settings_link = _nav_link("settings", "Configurações", "/settings", current_page)

    st.markdown(
        f"""
        <aside class="cx-rail" aria-label="Navegação principal">
            <a class="cx-rail-brand" href="/?auth_token=active" target="_self" aria-label="CXPack Radar">CX</a>
            <nav>{rail_links}</nav>
            <div class="cx-rail-foot">{settings_link}</div>
        </aside>
        <header class="cx-topbar">
            <div><strong class="cx-greeting">{greeting}, {first_name}!</strong><p>Seu radar comercial está pronto para operar.</p></div>
            <div class="cx-user-chip"><span>{user_name[:1].upper()}</span><strong>{first_name}</strong></div>
        </header>
        <nav class="cx-mobile-nav" aria-label="Navegação principal">
            <a href="/?auth_token=active" target="_self" class="{'active' if current_page == 'home' else ''}"{' aria-current="page"' if current_page == 'home' else ''}><svg viewBox="0 0 24 24">{_ICONS['home']}</svg><span>Início</span></a>
            <a href="/new_search?auth_token=active" target="_self" class="{'active' if current_page == 'search' else ''}"{' aria-current="page"' if current_page == 'search' else ''}><svg viewBox="0 0 24 24">{_ICONS['search']}</svg><span>Buscar</span></a>
            <a href="/search_history?auth_token=active" target="_self" class="{'active' if current_page == 'history' else ''}"{' aria-current="page"' if current_page == 'history' else ''}><svg viewBox="0 0 24 24">{_ICONS['history']}</svg><span>Histórico</span></a>
            <a href="/results?auth_token=active" target="_self" class="{'active' if current_page == 'results' else ''}"{' aria-current="page"' if current_page == 'results' else ''}><svg viewBox="0 0 24 24">{_ICONS['results']}</svg><span>Empresas</span></a>
            <details class="cx-mobile-more">
                <summary class="{'active' if current_page in ('decision_makers', 'crm', 'dashboard', 'api_usage', 'settings') else ''}">
                    <svg viewBox="0 0 24 24"><circle cx="5" cy="12" r="1"/><circle cx="12" cy="12" r="1"/><circle cx="19" cy="12" r="1"/></svg><span>Mais</span>
                </summary>
                <div class="cx-mobile-more-menu">
                    <a href="/decision_makers?auth_token=active" target="_self">Decisores</a>
                    <a href="/crm?auth_token=active" target="_self">Pipeline CRM</a>
                    <a href="/dashboard?auth_token=active" target="_self">Indicadores</a>
                    <a href="/api_usage?auth_token=active" target="_self">Uso da API</a>
                    <a href="/settings?auth_token=active" target="_self">Configurações</a>
                </div>
            </details>
        </nav>
        """,
        unsafe_allow_html=True,
    )
