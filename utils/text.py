"""
Utilitários de texto genéricos.
"""

def truncate_text(text: str, max_length: int = 150) -> str:
    """Trunca um texto adicionando reticências se exceder o tamanho."""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(" ", 1)[0] + "..."
