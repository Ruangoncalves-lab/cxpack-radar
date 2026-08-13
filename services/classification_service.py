"""
Serviço de Classificação de Empresas (ClassificationService - Fase 3).
Combina regras locais de palavras-chave industriais com a IA Gemini para casos ambíguos.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from providers.llm.gemini_provider import GeminiProvider
from utils.domains import is_blacklisted

MANUFACTURER_KEYWORDS = [
    "fabricamos", "fabricante", "produção", "produzimos", "indústria", "fábrica",
    "parque fabril", "unidade fabril", "injeção", "sopro", "extrusão", "linha de produção",
    "nossa fábrica", "nossa indústria", "moldagem", "usinagem"
]

DISTRIBUTOR_KEYWORDS = [
    "distribuidor", "distribuidora", "revenda", "revendedor", "comércio", "distribuímos",
    "representante comercial", "multimarcas"
]


class CompanyClassification(BaseModel):
    """Modelo Pydantic para Structured Output da classificação com IA Gemini."""
    company_type: str = Field(..., description="FABRICANTE, DISTRIBUIDOR, REVENDEDOR, IMPORTADOR ou MARKETPLACE")
    confidence: float = Field(..., description="Nível de confiança entre 0.0 e 1.0")
    products: List[str] = Field(default_factory=list, description="Lista de produtos principais encontrados no site")
    materials: List[str] = Field(default_factory=list, description="Materiais mencionados (PET, PEAD, Alumínio, etc.)")
    capacities: List[str] = Field(default_factory=list, description="Capacidades ou volumes técnicos mencionados")
    evidence: str = Field(..., description="Trecho exato do texto do site que comprova a classificação")


class ClassificationService:
    def __init__(self, llm_provider: Optional[GeminiProvider] = None):
        self.llm_provider = llm_provider or GeminiProvider()

    def classify_by_local_rules(self, text_content: str, domain: str = "") -> Dict[str, Any]:
        """
        Classificação rápida por regras estáticas e dicionário de palavras-chave industriais.
        Retorna dict com company_type, confidence e method='LOCAL_RULES'.
        """
        if is_blacklisted(domain):
            return {
                "company_type": "MARKETPLACE",
                "confidence": 0.99,
                "evidence": f"Domínio {domain} pertence à blacklist de marketplaces/redes sociais.",
                "method": "LOCAL_RULES"
            }

        if not text_content:
            return {
                "company_type": "DESCONHECIDO",
                "confidence": 0.0,
                "evidence": "Nenhum texto disponível para análise local.",
                "method": "LOCAL_RULES"
            }

        text_lower = text_content.lower()

        # Contar ocorrências de fabricante
        mfg_matches = [kw for kw in MANUFACTURER_KEYWORDS if kw in text_lower]
        dist_matches = [kw for kw in DISTRIBUTOR_KEYWORDS if kw in text_lower]

        if len(mfg_matches) >= 2:
            return {
                "company_type": "FABRICANTE",
                "confidence": 0.90,
                "evidence": f"Palavras-chave industriais encontradas: {', '.join(mfg_matches[:3])}",
                "method": "LOCAL_RULES"
            }
        elif len(mfg_matches) == 1:
            return {
                "company_type": "FABRICANTE",
                "confidence": 0.70,
                "evidence": f"Palavra-chave industrial encontrada: {mfg_matches[0]}",
                "method": "LOCAL_RULES"
            }
        elif len(dist_matches) >= 1:
            return {
                "company_type": "DISTRIBUIDOR",
                "confidence": 0.80,
                "evidence": f"Termos de distribuição encontrados: {', '.join(dist_matches[:2])}",
                "method": "LOCAL_RULES"
            }

        return {
            "company_type": "DESCONHECIDO",
            "confidence": 0.30,
            "evidence": "Confiança insuficiente pelas regras locais.",
            "method": "LOCAL_RULES"
        }

    def classify_with_gemini(self, company_name: str, website_text: str) -> CompanyClassification:
        """
        Classificação avançada via Gemini utilizando Structured Output (Pydantic).
        """
        if not website_text or len(website_text.strip()) < 50:
            return CompanyClassification(
                company_type="DESCONHECIDO",
                confidence=0.0,
                products=[],
                materials=[],
                capacities=[],
                evidence="Texto do website muito curto ou indisponível."
            )

        prompt = (
            f"Analise o seguinte conteúdo público do site da empresa '{company_name}' e determine se ela é um "
            f"FABRICANTE (possui fábrica/indústria própria), DISTRIBUIDOR, REVENDEDOR ou IMPORTADOR.\n\n"
            f"Conteúdo do Website:\n\"\"\"\n{website_text[:4000]}\n\"\"\"\n\n"
            f"Extraia também a lista de produtos, materiais, capacidades e cite o TRECHO EXATO de evidência."
        )

        sys_inst = "Você é um especialista em classificação de indústrias e fornecedores B2B."

        res = self.llm_provider.generate_structured(
            prompt=prompt,
            schema=CompanyClassification,
            system_instruction=sys_inst
        )

        if isinstance(res, CompanyClassification):
            return res

        # Fallback se o SDK retornar dict ou objeto parsed
        return CompanyClassification(**res) if isinstance(res, dict) else CompanyClassification(
            company_type="DESCONHECIDO",
            confidence=0.5,
            products=[],
            materials=[],
            capacities=[],
            evidence="Não foi possível obter resposta estruturada do modelo."
        )
