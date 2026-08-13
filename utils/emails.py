"""
Utilitários de e-mail (validação e extração).
"""

import re
from typing import List

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"


def extract_emails(text: str) -> List[str]:
    """Extrai e-mails válidos de um texto usando Regex."""
    if not text:
        return []
    matches = re.findall(EMAIL_REGEX, text)
    return sorted(list(set(email.lower() for email in matches)))


def is_valid_email_format(email: str) -> bool:
    """Verifica se a string possui sintaxe válida de e-mail."""
    if not email:
        return False
    return bool(re.fullmatch(EMAIL_REGEX, email.strip()))
