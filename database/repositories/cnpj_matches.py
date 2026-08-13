"""
Repositório para armazenamento e consulta de histórico de matching de CNPJ (CNPJMatch).
"""

from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.orm import Session
from database.models import CNPJMatch


class CNPJMatchRepository:
    def __init__(self, session: Session):
        self.session = session

    def add_match(
        self,
        company_id: int,
        cnpj: str,
        legal_name: str,
        trade_name: Optional[str] = None,
        cnae_code: Optional[str] = None,
        cnae_text: Optional[str] = None,
        status_cadastral: str = "ATIVA",
        city: Optional[str] = None,
        state: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        capital_social: Optional[float] = None,
        match_score: int = 0,
        is_auto_matched: bool = False
    ) -> CNPJMatch:
        """Salva o resultado do algoritmo de matching entre empresa e CNPJ."""
        clean_cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "").strip()
        match_rec = CNPJMatch(
            company_id=company_id,
            cnpj=clean_cnpj,
            legal_name=legal_name.strip(),
            trade_name=trade_name.strip() if trade_name else None,
            cnae_code=cnae_code,
            cnae_text=cnae_text,
            status_cadastral=status_cadastral,
            city=city,
            state=state,
            phone=phone,
            email=email,
            capital_social=capital_social,
            match_score=match_score,
            is_auto_matched=is_auto_matched
        )
        self.session.add(match_rec)
        self.session.commit()
        return match_rec

    def get_company_matches(self, company_id: int) -> List[CNPJMatch]:
        """Retorna os matches registrados para uma empresa ordenados por score."""
        stmt = select(CNPJMatch).where(CNPJMatch.company_id == company_id).order_by(CNPJMatch.match_score.desc())
        return list(self.session.scalars(stmt).all())
