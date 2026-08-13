"""
Wrapper de Layout Global do App Shell (ui/layout.py).
Injeta automaticamente o tema, o CSS scoped, a guarda de autenticação, a Topbar e a nova Sidebar do Lumin.
"""

from ui.theme import apply_theme
from ui.auth import require_auth
from ui.components.topbar import render_topbar
from ui.components.sidebar import render_sidebar


def apply_app_shell(current_page: str = "home"):
    """Aplica a estrutura global do Lumin (Guarda de Autenticação + Topbar + Sidebar + Estilos)."""
    apply_theme()
    require_auth()
    render_topbar(current_page=current_page)
    render_sidebar()
