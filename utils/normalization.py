"""
Utilitários de normalização de textos e geração de hashes para cache de pesquisas.
"""

import hashlib
import re
from typing import Optional


def normalize_text(text: Optional[str]) -> str:
    """
    Remove caracteres especiais desnecessários, espaços duplos e converte para minúsculas.
    """
    if not text:
        return ""
    cleaned = text.strip().lower()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def generate_search_hash(
    product: str,
    capacity: Optional[str] = None,
    material: Optional[str] = None,
    location: Optional[str] = "Brasil",
    company_type: Optional[str] = "Fabricante"
) -> str:
    """
    Gera um hash SHA-256 único determinístico para identificar uma pesquisa (Cache).
    """
    norm_product = normalize_text(product)
    norm_capacity = normalize_text(capacity)
    norm_material = normalize_text(material)
    norm_location = normalize_text(location or "brasil")
    norm_type = normalize_text(company_type or "fabricante")

    # v2 invalida caches gerados antes da qualificação estrita por evidência.
    raw_string = f"v4|{norm_product}|{norm_capacity}|{norm_material}|{norm_location}|{norm_type}"
    return hashlib.sha256(raw_string.encode("utf-8")).hexdigest()
