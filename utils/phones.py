"""
Utilitários para telefones brasileiros.
"""

import re
from typing import Optional


def normalize_phone_br(phone_str: str) -> Optional[str]:
    """
    Limpa e formata números de telefone brasileiros.
    Retorna no formato (XX) XXXXX-XXXX ou (XX) XXXX-XXXX se válido.
    """
    if not phone_str:
        return None

    digits = re.sub(r"\D", "", phone_str)

    # Remover código do país +55 se presente
    if digits.startswith("55") and len(digits) in (12, 13):
        digits = digits[2:]

    if len(digits) == 11:
        return f"({digits[:2]}) {digits[2:7]}-{digits[7:]}"
    elif len(digits) == 10:
        return f"({digits[:2]}) {digits[2:6]}-{digits[6:]}"

    return phone_str.strip()
