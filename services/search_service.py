"""
Orquestrador do Pipeline de Prospecção (SearchService - Fase 1, 2 & 3).
Integra QueryGenerator, DDGSSearchProvider (via abstração SearchProvider), QuotaService, CacheService, ScoringService e Repositórios.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from core.config import MAX_WEB_QUERIES_PER_SEARCH
from core.exceptions import QuotaExceededError
from utils.domains import normalize_domain, is_blacklisted
from utils.normalization import generate_search_hash
from providers.search.base import SearchProvider
from providers.search.ddgs_provider import DDGSSearchProvider
from services.query_generator import QueryGenerator
from services.quota_service import QuotaService
from services.cache_service import CacheService
from services.scoring_service import ScoringService
from database.repositories.searches import SearchRepository
from database.repositories.companies import CompanyRepository
from database.repositories.usage import UsageRepository


class SearchService:
    def __init__(self, session: Session, search_provider: Optional[SearchProvider] = None):
        self.session = session
        self.search_repo = SearchRepository(session)
        self.company_repo = CompanyRepository(session)
        self.usage_repo = UsageRepository(session)
        self.quota_service = QuotaService(session)
        self.cache_service = CacheService(session)
        self.scoring_service = ScoringService()
        self.query_generator = QueryGenerator()
        self.search_provider = search_provider or DDGSSearchProvider()

    def execute_prospecting_search(
        self,
        product: str,
        capacity: Optional[str] = None,
        material: Optional[str] = None,
        location: str = "Brasil",
        company_type: str = "Fabricante",
        max_queries: int = MAX_WEB_QUERIES_PER_SEARCH,
        operator: str = "sistema",
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Executa a prospecção completa:
        1. Normalização & Cálculo de Hash
        2. Verificação de Cache
        3. Validação de Cotas Internas
        4. Geração de Queries Locais
        5. Busca Web Pública via DDGSSearchProvider (R$ 0)
        6. Deduplicação e Limpeza de Domínios
        7. Cálculo Determinístico de Score
        8. Persistência de Empresas e Evidências no Banco
        """
        # 1. Normalização & Hash
        search_hash = generate_search_hash(product, capacity, material, location, company_type)

        # 2. Verificação de Cache
        if not force_refresh:
            cache_res = self.cache_service.check_cache(product, capacity, material, location, company_type)
            if cache_res["hit"]:
                existing_search = self.search_repo.get_search_with_results(cache_res["existing_search_id"])
                return {
                    "is_cache": True,
                    "search_id": existing_search.id,
                    "message": cache_res["message"],
                    "companies_found": existing_search.companies_found,
                    "new_companies_found": 0,
                    "web_search_calls": 0,
                    "grounded_calls": 0,
                    "status": "COMPLETED"
                }

        # 3. Gerar Queries Locais
        queries = self.query_generator.generate_queries(
            product=product,
            capacity=capacity,
            material=material,
            location=location,
            company_type=company_type,
            max_queries=max_queries
        )
        queries_to_run = queries[:max_queries]
        num_calls = len(queries_to_run)

        # 4. Validar Limites Internos
        quota_status = self.quota_service.check_quota_available(requested_calls=num_calls, user_or_operator=operator)

        # 5. Criar Registro de Pesquisa (Status CREATED -> RUNNING)
        search_record = self.search_repo.create_search(
            search_hash=search_hash,
            product=product,
            capacity=capacity,
            material=material,
            location=location,
            company_type=company_type,
            operator=operator
        )
        self.search_repo.update_status(search_record.id, "RUNNING")

        try:
            # Salvar queries no banco
            for q in queries_to_run:
                self.search_repo.add_query(search_record.id, q, query_type="LOCAL_TEMPLATE")

            all_candidates = []
            successful_web_calls = 0

            # 6. Executar busca web pública via DDGSSearchProvider para cada query
            for q_text in queries_to_run:
                try:
                    cands = self.search_provider.search_candidates(query=q_text, max_results=10)
                    all_candidates.extend(cands)
                    successful_web_calls += 1

                    # Registrar uso de busca web no banco
                    self.usage_repo.log_usage(
                        operation="ddgs_web_search",
                        user_or_operator=operator,
                        search_id=search_record.id,
                        request_count=1,
                        success=True
                    )
                except Exception as api_err:
                    self.usage_repo.log_usage(
                        operation="ddgs_web_search",
                        user_or_operator=operator,
                        search_id=search_record.id,
                        request_count=1,
                        success=False,
                        error_message=str(api_err)
                    )

            # 7. Deduplicação, Filtragem de Blacklist e Persistência no Banco
            unique_candidates_by_domain = {}
            for cand in all_candidates:
                clean_domain = normalize_domain(cand.domain or cand.website)
                if clean_domain and not is_blacklisted(clean_domain):
                    if clean_domain not in unique_candidates_by_domain:
                        unique_candidates_by_domain[clean_domain] = cand

            total_companies_found = len(unique_candidates_by_domain)
            new_companies_count = 0

            for domain, cand in unique_candidates_by_domain.items():
                # Calcular score determinístico via ScoringService
                score_info = self.scoring_service.calculate_score(
                    company_type=company_type.upper() if company_type else "FABRICANTE",
                    product_matched=True,
                    material_matched=bool(material and material.strip()),
                    capacity_matched=bool(capacity and capacity.strip()),
                    location_matched=True,
                    has_phone=False,
                    has_email=False,
                    has_decision_maker=False
                )

                comp, is_new = self.company_repo.upsert_company(
                    domain=domain,
                    name=cand.company_name,
                    website=cand.website,
                    company_type=company_type.upper() if company_type else "FABRICANTE",
                    score=score_info["total_score"],
                    confidence=cand.confidence,
                    description=cand.reason
                )

                if is_new:
                    new_companies_count += 1

                # Salvar evidência
                if cand.source_url:
                    self.company_repo.add_evidence(
                        company_id=comp.id,
                        field_name="ddgs_search_match",
                        value=cand.company_name,
                        source_url=cand.source_url,
                        source_title=cand.source_title,
                        source_text=f"Query: {cand.query} | Motivo: {cand.reason}",
                        confidence=cand.confidence
                    )

                # Salvar resultado vinculado à pesquisa
                self.search_repo.add_result(
                    search_id=search_record.id,
                    domain=domain,
                    company_id=comp.id,
                    source_url=cand.source_url,
                    source_title=cand.source_title,
                    confidence=cand.confidence,
                    reason=cand.reason
                )

            # Atualizar estatísticas da pesquisa
            search_record.grounded_calls = successful_web_calls
            search_record.companies_found = total_companies_found
            search_record.new_companies_found = new_companies_count
            self.search_repo.update_status(search_record.id, "COMPLETED")

            return {
                "is_cache": False,
                "search_id": search_record.id,
                "message": "Pesquisa concluída com sucesso!",
                "companies_found": total_companies_found,
                "new_companies_found": new_companies_count,
                "web_search_calls": successful_web_calls,
                "grounded_calls": successful_web_calls,
                "status": "COMPLETED"
            }

        except Exception as e:
            self.search_repo.update_status(search_record.id, "FAILED", error_message=str(e))
            raise
