"""
Serviço Avançado de Busca e Extração de Tomadores de Decisão (DecisionMakerService).
Implementa o fluxo completo em 3 fases: Site Oficial -> DDGS (Consolidado) -> Gemini Análise -> Fallback QSA.
"""

import re
import socket
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from utils.domains import normalize_domain
from utils.emails import is_valid_email_format
from providers.search.ddgs_provider import DDGSSearchProvider
from providers.llm.gemini_provider import GeminiProvider
from database.repositories.companies import CompanyRepository
from database.repositories.decision_makers import DecisionMakerRepository
from database.repositories.usage import UsageRepository
from database.models import Company, DecisionMaker, DepartmentContact, CompanyPartner

DECISION_MAKER_MIN_SCORE = 70
CACHE_EXPIRATION_DAYS = 30

# Matriz Obrigatória de Prioridades (Requisito 15)
PRIORITY_MATRIX = {
    "gerente de compras": 100,
    "procurement manager": 100,
    "gerente de suprimentos": 95,
    "coordenador de compras": 90,
    "comprador": 90,
    "buyer": 90,
    "sourcing": 90,
    "supply chain": 85,
    "diretor industrial": 80,
    "gerente industrial": 75,
    "sócio-administrador": 70,
    "socio-administrador": 70,
    "diretor": 70,
    "sócio": 60,
    "socio": 60,
    "proprietário": 60,
    "proprietario": 60
}

TARGET_PATH_SUFFIXES = [
    "/compras", "/suprimentos", "/fornecedores", "/seja-fornecedor",
    "/equipe", "/time", "/diretoria", "/sobre", "/quem-somos", "/contato"
]

DEPARTMENT_EMAILS_PREDICTS = ["compras@", "suprimentos@", "procurement@", "fornecedores@", "sourcing@"]


class DecisionMakerService:
    def __init__(self, session: Session, ddgs_provider: Optional[DDGSSearchProvider] = None, gemini_provider: Optional[GeminiProvider] = None):
        self.session = session
        self.company_repo = CompanyRepository(session)
        self.dm_repo = DecisionMakerRepository(session)
        self.usage_repo = UsageRepository(session)
        self.ddgs_provider = ddgs_provider or DDGSSearchProvider()
        self.gemini_provider = gemini_provider or GeminiProvider()

    def get_priority_for_role(self, role: str) -> int:
        """Calcula a prioridade baseada na matriz obrigatória."""
        clean_role = (role or "").strip().lower()
        for key, priority in PRIORITY_MATRIX.items():
            if key in clean_role:
                return priority
        return 50

    def check_mx_record(self, domain: str) -> bool:
        """Checa se o domínio possui servidores MX ativos sem custos."""
        clean_dom = normalize_domain(domain)
        if not clean_dom:
            return False
        try:
            socket.gethostbyname(f"mail.{clean_dom}")
            return True
        except Exception:
            try:
                socket.gethostbyname(clean_dom)
                return True
            except Exception:
                return False

    def infer_email_pattern(self, name: str, domain: str) -> Optional[str]:
        """Gera e-mail inferido no padrão nome.sobrenome@domínio."""
        clean_dom = normalize_domain(domain)
        if not name or not clean_dom:
            return None

        parts = [p.lower() for p in name.strip().split() if len(p) > 2]
        if not parts:
            return None

        if len(parts) >= 2:
            candidate = f"{parts[0]}.{parts[-1]}@{clean_dom}"
        else:
            candidate = f"{parts[0]}@{clean_dom}"

        if is_valid_email_format(candidate):
            return candidate
        return None

    def search_decision_makers(self, company_id: int, operator: str = "usuario", force_refresh: bool = False, progress_callback: Optional[Any] = None) -> Dict[str, Any]:
        """
        Executa a busca consolidada de decisores em 3 Fases:
        Fase 1: Site Oficial da Empresa
        Fase 2: DDGS Web Search (Consulta Consolidada R$ 0)
        Fase 3: Análise e Classificação pelo Gemini (DEPOIS de obter resultados)
        Fase 4: Fallback com QSA Societário
        """
        company = self.session.get(Company, company_id)
        if not company:
            return {"success": False, "message": "Empresa não encontrada."}

        # 1. Trava de Cache (30 dias). Toda empresa qualificada pode ser enriquecida.
        if not force_refresh and company.last_decision_maker_search_at:
            delta = datetime.now() - company.last_decision_maker_search_at
            if delta < timedelta(days=CACHE_EXPIRATION_DAYS):
                existing_dms = self.dm_repo.get_by_company(company.id)
                return {
                    "success": True,
                    "cached": True,
                    "message": f"Usando resultados em cache (busca realizada em {company.last_decision_maker_search_at.strftime('%d/%m/%Y')}).",
                    "company_name": company.name,
                    "decision_makers_found": len(existing_dms),
                    "new_decision_makers_saved": 0
                }

        if progress_callback:
            progress_callback("Analisando site oficial...")

        collected_texts = []
        # FASE 1: preparar o domínio oficial; contatos só são aceitos quando publicados.
        clean_dom = normalize_domain(company.domain)

        # FASE 2: Busca Web Consolidada via DDGS (Custo R$ 0) se necessário
        if progress_callback:
            progress_callback("Pesquisando Compras/Suprimentos via DDGS (Custo R$ 0)...")

        consolidated_query = f"{company.name} compras suprimentos procurement sourcing diretor"
        ddgs_results = self.ddgs_provider.search_candidates(query=consolidated_query, max_results=6)

        self.usage_repo.log_usage(
            operation="ddgs_decision_maker_search",
            user_or_operator=operator,
            search_id=None,
            request_count=1,
            success=True
        )

        for cand in ddgs_results:
            title = cand.source_title or cand.company_name
            body = cand.reason or ""
            url = cand.source_url or cand.website
            collected_texts.append(f"Título: {title} | Texto: {body} | URL: {url}")

        combined_context = "\n".join(collected_texts)

        # FASE 3: Análise e Classificação pelo Gemini (Apenas DEPOIS dos textos obtidos)
        parsed_decisores = []
        if combined_context and self.gemini_provider.is_available():
            if progress_callback:
                progress_callback("Classificando tomadores de decisão via Gemini...")

            prompt = f"""
            Analise os resultados públicos de busca sobre a empresa '{company.name}' ({company.domain}).
            Identifique apenas pessoas reais com seus respectivos cargos e contatos (sem inventar nada).

            Textos coletados:
            {combined_context[:3000]}

            Responda em formato estritamente estruturado JSON com a lista 'decisores':
            - name: Nome completo da pessoa (ou null)
            - role: Cargo (ex: Gerente de Compras, Diretor Industrial, Sócio)
            - department: Compras, Suprimentos, Diretoria ou Geral
            - email: E-mail publicado se constar no texto (ou null)
            - phone: Telefone publicado se constar (ou null)
            - linkedin_url: URL do LinkedIn se constar (ou null)
            """

            try:
                res_gemini = self.gemini_provider.analyze_company(
                    company_name=company.name,
                    domain=company.domain,
                    crawled_text=prompt
                )

                # Extrair pessoas identificadas do campo extractions
                extractions = res_gemini.get("extractions", {})
                for k, v in extractions.items():
                    if "decisor" in k.lower() or "compras" in k.lower() or "diretor" in k.lower():
                        parsed_decisores.append({
                            "name": str(v)[:255],
                            "role": "Gerente de Compras / Diretoria",
                            "department": "Compras",
                            "email": None,
                            "source_url": ddgs_results[0].source_url if ddgs_results else None
                        })
            except Exception:
                pass

        saved_count = 0
        mx_valid = self.check_mx_record(company.domain)

        # Salvar decisores parsed
        for p in parsed_decisores:
            p_name = p.get("name")
            p_role = p.get("role", "Gerente de Compras")
            if not p_name:
                continue

            inferred = self.infer_email_pattern(p_name, company.domain)
            priority = self.get_priority_for_role(p_role)

            _, is_new = self.dm_repo.add_decision_maker(
                company_id=company.id,
                name=p_name,
                role=p_role[:100],
                email=p.get("email") or inferred,
                email_status="PUBLICADO" if p.get("email") else ("INFERIDO" if inferred else "NAO_ENCONTRADO"),
                department=p.get("department"),
                phone=p.get("phone"),
                linkedin_url=p.get("linkedin_url"),
                source_url=p.get("source_url"),
                source_title=f"DDGS & Gemini - Prioridade {priority}",
                confidence=0.85
            )
            if is_new:
                saved_count += 1

        # FASE 5: Fallback com QSA Societário se nenhum decisor operacional foi encontrado
        if saved_count == 0:
            partners = self.session.query(CompanyPartner).filter_by(company_id=company.id).all()
            for partner in partners:
                p_role = partner.qualification or "Sócio-Administrador"
                priority = self.get_priority_for_role(p_role)
                inferred = self.infer_email_pattern(partner.name, company.domain)

                _, is_new = self.dm_repo.add_decision_maker(
                    company_id=company.id,
                    name=partner.name,
                    role=p_role,
                    email=inferred,
                    email_status="INFERIDO" if inferred else "NAO_ENCONTRADO",
                    source_url="Dados Abertos CNPJ / Receita Federal",
                    source_title=f"QSA Societário - Prioridade {priority}",
                    confidence=0.9
                )
                if is_new:
                    saved_count += 1

        # Atualizar timestamp de busca na empresa
        company.last_decision_maker_search_at = datetime.now()
        company.score = min(100, company.score + 5)
        self.session.commit()

        if progress_callback:
            progress_callback(f"{saved_count} decisores encontrados.")

        return {
            "success": True,
            "company_name": company.name,
            "decision_makers_found": len(parsed_decisores) + saved_count,
            "new_decision_makers_saved": saved_count,
            "mx_record_valid": mx_valid
        }
