"""
Gerador local de queries de busca industrial (QueryGenerator).
Gera variações inteligentes sem gastar cota da API Gemini.
"""

from typing import List, Optional, Dict
from utils.normalization import normalize_text

# Dicionário em memória de sinônimos industriais e expansões
DEFAULT_SYNONYMS: Dict[str, List[str]] = {
    "frasco": ["frasco", "garrafa", "recipiente", "embalagem rígida"],
    "bisnaga": ["bisnaga", "tubo plástico", "tubo flexível", "squeeze tube"],
    "fabricante": ["fabricante", "indústria", "fábrica", "produção de"],
    "pet": ["PET", "polietileno tereftalato"],
    "pead": ["PEAD", "HDPE", "polietileno de alta densidade"],
    "pebd": ["PEBD", "LDPE", "polietileno de baixa densidade"],
    "pp": ["PP", "polipropileno"],
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
        Gera uma lista de 1 a N variações de busca usando templates industriais.
        """
        clean_prod = normalize_text(product)
        clean_cap = normalize_text(capacity)
        clean_mat = normalize_text(material)
        clean_loc = normalize_text(location or "Brasil").title()
        clean_type = normalize_text(company_type or "Fabricante").title()

        queries: List[str] = []

        # Query 1: Direta e completa
        parts_1 = [clean_type, clean_prod]
        if clean_mat:
            parts_1.append(clean_mat.upper() if len(clean_mat) <= 4 else clean_mat)
        if clean_cap:
            parts_1.append(clean_cap)
        if clean_loc:
            parts_1.append(clean_loc)
        queries.append(" ".join(parts_1))

        # Query 2: Variação com "indústria de embalagem" ou "fábrica de"
        alt_type = "indústria" if clean_type.lower() == "fabricante" else "fornecedor"
        parts_2 = [alt_type, clean_prod]
        if clean_cap:
            parts_2.append(clean_cap)
        if clean_mat:
            parts_2.append(clean_mat)
        if clean_loc:
            parts_2.append(clean_loc)
        q2 = " ".join(parts_2)
        if q2 not in queries:
            queries.append(q2)

        # Query 3: Variação com sinônimo do produto ou termo fabril
        syns = self.synonyms.get(clean_prod, [clean_prod])
        alt_prod = syns[1] if len(syns) > 1 else clean_prod
        parts_3 = ["fábrica", alt_prod]
        if clean_mat:
            parts_3.append(clean_mat)
        if clean_loc:
            parts_3.append(clean_loc)
        q3 = " ".join(parts_3)
        if q3 not in queries:
            queries.append(q3)

        return queries[:max_queries]
