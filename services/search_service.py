"""
Orquestrador do Pipeline de Prospecção (SearchService - Fase 1, 2 & 3).
Integra QueryGenerator, DDGSSearchProvider (via abstração SearchProvider), QuotaService, CacheService, ScoringService e Repositórios.
"""

import re
import unicodedata
from difflib import get_close_matches
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from core.config import MAX_WEB_QUERIES_PER_SEARCH
from core.exceptions import QuotaExceededError
from utils.domains import normalize_domain, is_blacklisted
from utils.normalization import generate_search_hash
from utils.phones import normalize_phone_br
from providers.search.base import SearchProvider
from providers.search.ddgs_provider import DDGSSearchProvider
from services.query_generator import QueryGenerator
from services.quota_service import QuotaService
from services.cache_service import CacheService
from services.scoring_service import ScoringService
from database.repositories.searches import SearchRepository
from database.repositories.companies import CompanyRepository
from database.repositories.contacts import ContactRepository
from database.repositories.usage import UsageRepository
from providers.cnpj.public_cnpj_provider import PublicCNPJProvider


class SearchService:
    def __init__(self, session: Session, search_provider: Optional[SearchProvider] = None):
        self.session = session
        self.search_repo = SearchRepository(session)
        self.company_repo = CompanyRepository(session)
        self.contact_repo = ContactRepository(session)
        self.usage_repo = UsageRepository(session)
        self.quota_service = QuotaService(session)
        self.cache_service = CacheService(session)
        self.scoring_service = ScoringService()
        self.query_generator = QueryGenerator()
        self.search_provider = search_provider or DDGSSearchProvider()
        self.cnpj_provider = PublicCNPJProvider()

    def _registry_cnae(self, product: str, material: str) -> Optional[str]:
        text = self._normalize(f"{product} {material}")
        packaging = any(term in text for term in ("frasco", "garrafa", "pote", "tampa", "bisnaga", "embalagem"))
        if packaging and any(term in text for term in ("plastico", "resina", "pet", "pead", "polipropileno", "pp")):
            return "2222600"
        if packaging and "vidro" in text:
            return "2312500"
        return None

    @staticmethod
    def _normalize(value: str) -> str:
        value = unicodedata.normalize("NFKD", value or "").encode("ascii", "ignore").decode().lower()
        return re.sub(r"[^a-z0-9]+", " ", value).strip()

    def _candidate_matches_filters(self, candidate, product, capacity, material, location, company_type):
        """Qualifica somente pelo título/snippet público; a query nunca conta como evidência."""
        evidence = self._normalize(f"{candidate.source_title or ''} {candidate.reason or ''}")
        domain = (candidate.domain or "").lower()
        manufacturer = any(term in evidence for term in ("fabricante", "fabrica ", "industria", "producao propria"))
        stopwords = {"de", "da", "do", "das", "dos", "para", "com", "em"}
        product_terms = [term.rstrip("s") for term in self._normalize(product).split() if term not in stopwords and len(term) > 2]
        aliases = {
            "frasco": ("frasco", "garrafa", "recipiente", "embalagem"),
            "garrafa": ("garrafa", "frasco"),
            "pote": ("pote", "frasco boca larga"),
            "bisnaga": ("bisnaga", "tubo flexivel"),
        }
        canonical_terms = [get_close_matches(term, aliases, n=1, cutoff=0.72)[0] if get_close_matches(term, aliases, n=1, cutoff=0.72) else term for term in product_terms]
        product_match = all(any(alias in evidence for alias in aliases.get(term, (term,))) for term in canonical_terms)
        material_terms = [term for term in self._normalize(material).split() if term not in stopwords]
        material_aliases = {
            "resina": ("resina", "plastico", "pet", "pead", "polietileno", "polipropileno", " pp "),
            "plastico": ("plastico", "pet", "pead", "polietileno", "polipropileno", " pp "),
        }
        material_match = not material_terms or all(any(alias in f" {evidence} " for alias in material_aliases.get(term, (term,))) for term in material_terms)
        capacity_clean = self._normalize(capacity).replace(" ", "").replace("litros", "l").replace("litro", "l")
        evidence_compact = evidence.replace(" ", "").replace("litros", "l").replace("litro", "l")
        capacity_match = not capacity_clean or capacity_clean in evidence_compact
        location_clean = self._normalize(location)
        requested_state = next((part.lower() for part in re.findall(r"\b[A-Za-z]{2}\b", location or "") if part.lower() != "de"), None)
        if requested_state:
            location_match = requested_state in evidence.split()
        elif "brasil" in location_clean:
            location_match = domain.endswith(".br") or "brasil" in evidence
        else:
            location_match = not location_clean or location_clean in evidence
        type_match = (company_type or "").upper() != "FABRICANTE" or manufacturer
        matches = product_match and material_match and capacity_match and location_match and type_match
        return matches, {"manufacturer": manufacturer, "product": product_match, "material": material_match, "capacity": capacity_match, "location": location_match}

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
                    else:
                        old_matches = self._candidate_matches_filters(
                            unique_candidates_by_domain[clean_domain], product, capacity, material, location, company_type
                        )[0]
                        new_matches = self._candidate_matches_filters(
                            cand, product, capacity, material, location, company_type
                        )[0]
                        if new_matches and not old_matches:
                            unique_candidates_by_domain[clean_domain] = cand

            new_companies_count = 0

            qualified_candidates = []
            for domain, cand in unique_candidates_by_domain.items():
                matches, match_info = self._candidate_matches_filters(cand, product, capacity, material, location, company_type)
                if matches:
                    qualified_candidates.append((domain, cand, match_info))

            total_companies_found = len(qualified_candidates)
            for domain, cand, match_info in qualified_candidates:
                # Calcular score determinístico via ScoringService
                score_info = self.scoring_service.calculate_score(
                    company_type="FABRICANTE" if match_info["manufacturer"] else "DESCONHECIDO",
                    product_matched=match_info["product"],
                    material_matched=match_info["material"],
                    capacity_matched=match_info["capacity"],
                    location_matched=match_info["location"],
                    has_phone=False,
                    has_email=False,
                    has_decision_maker=False
                )

                comp, is_new = self.company_repo.upsert_company(
                    domain=domain,
                    name=cand.company_name,
                    website=cand.website,
                    company_type="FABRICANTE" if match_info["manufacturer"] else "DESCONHECIDO",
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
                        field_name="qualified_search_match",
                        value=f"{product} | {material or '-'} | {capacity or '-'} | {location}",
                        source_url=cand.source_url,
                        source_title=cand.source_title,
                        source_text=f"Evidência pública compatível: {cand.source_title or ''} | {cand.reason or ''}",
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

            # 8. Ampliar via CNPJ/CNAE sem confundir candidato oficial com produto comprovado.
            registry_count = 0
            cnae = self._registry_cnae(product, material or "")
            requested_state = next((part.upper() for part in re.findall(r"\b[A-Za-z]{2}\b", location or "") if part.lower() != "de"), None)
            if cnae and (company_type or "").upper() == "FABRICANTE":
                for official in self.cnpj_provider.search_companies_by_cnae(cnae, requested_state, limit=100):
                    identity = f"cnpj-{official['cnpj']}.receita.local"
                    comp, is_new = self.company_repo.upsert_company(
                        domain=identity,
                        name=official["trade_name"] or official["legal_name"],
                        website=None,
                        company_type="CANDIDATO_CNAE",
                        city=official["city"],
                        state=official["state"],
                        score=55,
                        confidence=0.95,
                        description=f"Candidato oficial ativo no CNAE {cnae}: {official['cnae_text']}",
                    )
                    comp.cnpj = official["cnpj"]
                    comp.legal_name = official["legal_name"]
                    comp.trade_name = official["trade_name"]
                    comp.cnae_code = official["cnae_code"]
                    comp.cnae_text = official["cnae_text"]
                    comp.status_cadastral = official["status_cadastral"]
                    official_phones = official.get("phones") or [official.get("phone")]
                    for raw_phone in filter(None, official_phones):
                        phone_digits = re.sub(r"\D", "", raw_phone)
                        local_phone_digits = phone_digits[2:] if phone_digits.startswith("55") and len(phone_digits) in (12, 13) else phone_digits
                        if len(local_phone_digits) in (10, 11):
                            self.contact_repo.add_contact(
                                company_id=comp.id,
                                contact_type="TELEFONE",
                                value=normalize_phone_br(raw_phone),
                                raw_value=raw_phone,
                                source_url="https://minhareceita.org/",
                                is_verified=True,
                            )
                    public_email = (official.get("email") or "").strip()
                    if "@" in public_email:
                        self.contact_repo.add_contact(
                            company_id=comp.id,
                            contact_type="EMAIL_PUBLICO",
                            value=public_email,
                            source_url="https://minhareceita.org/",
                            is_verified=True,
                        )
                    self.company_repo.add_evidence(
                        company_id=comp.id,
                        field_name="official_cnae_candidate",
                        value=f"{official['cnpj']} | CNAE {cnae}",
                        source_url="https://minhareceita.org/",
                        source_title="Dados Abertos CNPJ / Receita Federal",
                        source_text=f"Empresa ativa enquadrada no CNAE {cnae}: {official['cnae_text']}",
                        confidence=0.95,
                    )
                    self.search_repo.add_result(
                        search_id=search_record.id,
                        domain=identity,
                        company_id=comp.id,
                        source_url="https://minhareceita.org/",
                        source_title="Dados Abertos CNPJ / Receita Federal",
                        confidence=0.95,
                        reason=f"Candidato por CNAE {cnae}; produto e capacidade ainda precisam de validação no site.",
                    )
                    registry_count += 1
                    if is_new:
                        new_companies_count += 1

            total_companies_found += registry_count

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
                "registry_candidates": registry_count,
                "status": "COMPLETED"
            }

        except Exception as e:
            self.search_repo.update_status(search_record.id, "FAILED", error_message=str(e))
            raise
