"""
Calculadora Determinística de Score de Relevância (ScoringService - Fase 3).
Calcula nota de 0 a 100 estritamente por regras transparentes e auditáveis.
"""

from typing import Dict, Any, Optional
from database.models import Company


class ScoringService:
    def calculate_score(
        self,
        company_type: str = "DESCONHECIDO",
        product_matched: bool = True,
        material_matched: bool = False,
        capacity_matched: bool = False,
        location_matched: bool = True,
        has_phone: bool = False,
        has_email: bool = False,
        has_decision_maker: bool = False
    ) -> Dict[str, Any]:
        """
        Calcula o score de 0 a 100 de uma empresa segundo a soma de regras industriais.
        """
        score = 0
        breakdown = []

        # 1. Fabricante confirmado (+30)
        c_type = (company_type or "").upper()
        if c_type in ("FABRICANTE", "INDÚSTRIA"):
            score += 30
            breakdown.append({"rule": "Fabricante Confirmado", "points": +30})
        elif c_type in ("DISTRIBUIDOR", "IMPORTADOR"):
            score += 15
            breakdown.append({"rule": "Distribuidor/Importador", "points": +15})

        # 2. Produto compatível (+25)
        if product_matched:
            score += 25
            breakdown.append({"rule": "Produto Compatível", "points": +25})

        # 3. Material compatível (+15)
        if material_matched:
            score += 15
            breakdown.append({"rule": "Material Compatível", "points": +15})

        # 4. Capacidade compatível (+15)
        if capacity_matched:
            score += 15
            breakdown.append({"rule": "Capacidade/Volume Compatível", "points": +15})

        # 5. Localização no Brasil/UF (+5)
        if location_matched:
            score += 5
            breakdown.append({"rule": "Localização Compatível", "points": +5})

        # 6. Telefone corporativo cadastrado (+3)
        if has_phone:
            score += 3
            breakdown.append({"rule": "Telefone Cadastrado", "points": +3})

        # 7. E-mail público cadastrado (+3)
        if has_email:
            score += 3
            breakdown.append({"rule": "E-mail Cadastrado", "points": +3})

        # 8. Decisor identificado (+4)
        if has_decision_maker:
            score += 4
            breakdown.append({"rule": "Decisor Encontrado", "points": +4})

        total_score = min(100, score)

        return {
            "total_score": total_score,
            "breakdown": breakdown
        }

    def update_company_score(self, company: Company, search_params: Optional[Dict[str, Any]] = None) -> int:
        """
        Recalcula e atualiza o score de um objeto Company persistido.
        """
        search_params = search_params or {}

        # Checar contatos cadastrados
        has_phone = any(ct.contact_type in ("TELEFONE", "WHATSAPP") for ct in company.contacts) if hasattr(company, "contacts") and company.contacts else False
        has_email = any("EMAIL" in ct.contact_type for ct in company.contacts) if hasattr(company, "contacts") and company.contacts else False

        # Verificar se o material/capacidade bate com o texto da empresa ou evidencias
        ev_text = " ".join([ev.source_text or "" for ev in company.evidences]) if hasattr(company, "evidences") and company.evidences else ""
        desc_text = (company.description or "") + " " + ev_text
        desc_text_lower = desc_text.lower()

        req_material = search_params.get("material", "").lower()
        req_capacity = search_params.get("capacity", "").lower()

        material_matched = bool(req_material and req_material in desc_text_lower)
        capacity_matched = bool(req_capacity and req_capacity in desc_text_lower)

        score_res = self.calculate_score(
            company_type=company.company_type,
            product_matched=True,
            material_matched=material_matched,
            capacity_matched=capacity_matched,
            location_matched=True,
            has_phone=has_phone,
            has_email=has_email,
            has_decision_maker=False
        )

        company.score = score_res["total_score"]
        return company.score
