"""
Gerador local de queries de busca industrial (QueryGenerator).
Gera variações naturais e de alto rendimento para buscas web públicas (DDGS).
"""

from typing import List, Optional, Dict
from utils.normalization import normalize_text

DEFAULT_SYNONYMS: Dict[str, List[str]] = {
    "frasco": ["frascos", "garrafas", "embalagens rígidas", "recipientes"],
    "bisnaga": ["bisnagas", "tubos plásticos", "tubos flexíveis"],
    "pote": ["potes", "frascos boca larga", "embalagens"],
    "tampa": ["tampas plásticas", "tampas rosca"],
    "caixa": ["caixas plásticas", "estojos plásticos"],
}


class QueryGenerator:
    def __init__(self, synonyms_dict: Optional[Dict[str, List[str]]] = None):
        self.synonyms = synonyms_dict or DEFAULT_SYNONYMS

    def generate_queries(
        self,
        product: str,
        capacity: Optional[str] = None,
        material: Optional[str] = None,
        location: Optional[str] = "Brasil",
        company_type: Optional[str] = "Fabricante",
        max_queries: int = 3
    ) -> List[str]:
        """
        Gera uma lista de variações de busca usando termos naturais e diretos.
        """
        clean_prod = normalize_text(product or "embalagem")
        clean_cap = capacity.strip() if capacity else ""
        clean_mat = material.strip() if material else ""
        clean_loc = location.strip() if location else "Brasil"

        queries: List[str] = []

        # Query 1: Fabricantes diretos do produto e localização (Preservando PET, 500 ml)
        q1 = f"fabricante de {clean_prod} {clean_mat} {clean_cap} {clean_loc}".strip()
        queries.append(" ".join(q1.split()))

        # Query 2: Indústria / fábrica com capacidade ou material
        q2 = f"fábrica de {clean_prod} {clean_cap} {clean_mat}".strip()
        q2_clean = " ".join(q2.split())
        if q2_clean not in queries:
            queries.append(q2_clean)

        # Query 3: Fornecedores / catálogo de embalagens industriais
        syns = self.synonyms.get(clean_prod.lower(), [clean_prod])
        alt_prod = syns[0] if syns else clean_prod
        q3 = f"fornecedores de {alt_prod} {clean_loc}".strip()
        q3_clean = " ".join(q3.split())
        if q3_clean not in queries:
            queries.append(q3_clean)

        return queries[:max_queries]
