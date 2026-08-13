"""
Serviço de Matching Empresa ↔ CNPJ (CNPJMatchingService - Fase C).
Calcula a pontuação de compatibilidade company_match_score (0 a 100) antes de vincular dados.
"""

from typing import Dict, Any, Optional
from utils.normalization import normalize_text
from utils.domains import normalize_domain

AUTO_CNPJ_MATCH_MIN_SCORE = 85


class CNPJMatchingService:
    def calculate_match_score(
        self,
        company_name: str,
        cnpj_legal_name: str,
        cnpj_trade_name: Optional[str] = None,
        company_city: Optional[str] = None,
        cnpj_city: Optional[str] = None,
        company_state: Optional[str] = None,
        cnpj_state: Optional[str] = None,
        company_phone: Optional[str] = None,
        cnpj_phone: Optional[str] = None,
        company_domain: Optional[str] = None,
        cnpj_email: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calcula o company_match_score (0 a 100) com base na compatibilidade de dados.
        """
        score = 0
        breakdown = []

        norm_comp_name = normalize_text(company_name)
        norm_legal = normalize_text(cnpj_legal_name)
        norm_trade = normalize_text(cnpj_trade_name or "")

        # 1. Nome muito compatível (+40)
        if norm_comp_name and (norm_comp_name in norm_legal or norm_legal in norm_comp_name or (norm_trade and norm_comp_name in norm_trade)):
            score += 40
            breakdown.append({"criterion": "Nome / Razão Social Compatível", "points": +40})
        elif norm_comp_name and len(set(norm_comp_name.split()).intersection(set(norm_legal.split()))) >= 2:
            score += 25
            breakdown.append({"criterion": "Nomes Parcialmente Semelhantes", "points": +25})

        # 2. Mesma Cidade (+15)
        if company_city and cnpj_city and normalize_text(company_city) == normalize_text(cnpj_city):
            score += 15
            breakdown.append({"criterion": "Mesmo Município", "points": +15})

        # 3. Mesmo Estado (+5)
        if company_state and cnpj_state and normalize_text(company_state) == normalize_text(cnpj_state):
            score += 5
            breakdown.append({"criterion": "Mesmo Estado (UF)", "points": +5})

        # 4. Telefone igual (+20)
        if company_phone and cnpj_phone and normalize_text(company_phone) == normalize_text(cnpj_phone):
            score += 20
            breakdown.append({"criterion": "Telefone Coincidente", "points": +20})

        # 5. Domínio associado no e-mail corporativo do CNPJ (+20)
        if company_domain and cnpj_email:
            email_dom = normalize_domain(cnpj_email)
            comp_dom = normalize_domain(company_domain)
            if email_dom and comp_dom and (email_dom == comp_dom or comp_dom in email_dom):
                score += 20
                breakdown.append({"criterion": "Domínio Coincidente no E-mail Oficial", "points": +20})

        total_score = min(100, score)
        is_auto_matched = total_score >= AUTO_CNPJ_MATCH_MIN_SCORE

        return {
            "match_score": total_score,
            "is_auto_matched": is_auto_matched,
            "status": "AUTO_MATCHED" if is_auto_matched else "CNPJ_MATCH_REVIEW",
            "breakdown": breakdown
        }
