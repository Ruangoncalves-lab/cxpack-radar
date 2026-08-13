"""
Orquestrador de Crawling e Contatos (ContactService - Fase 2).
Integra CrawlerService, ExtractionService, PageRepository e ContactRepository.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from services.crawler_service import CrawlerService
from services.extraction_service import ExtractionService
from database.repositories.companies import CompanyRepository
from database.repositories.pages import PageRepository
from database.repositories.contacts import ContactRepository


class ContactService:
    def __init__(self, session: Session):
        self.session = session
        self.company_repo = CompanyRepository(session)
        self.page_repo = PageRepository(session)
        self.contact_repo = ContactRepository(session)
        self.crawler = CrawlerService(max_pages_per_domain=5, timeout=8.0)
        self.extractor = ExtractionService()

    def crawl_and_extract_company_contacts(self, company_id: int) -> Dict[str, Any]:
        """
        Executa o crawling completo do website de uma empresa e extrai seus contatos públicos:
        1. Carrega dados da empresa no banco
        2. Crawlea até 5 páginas prioritárias do site
        3. Registra as páginas visitadas no banco
        4. Extrai e-mails, telefones, WhatsApp e CNPJ público
        5. Atualiza a empresa e adiciona evidências
        """
        company = self.session.get(CompanyRepository(self.session).session.query(CompanyRepository(self.session).session.get_bind().models.Company).class_, company_id) if hasattr(CompanyRepository(self.session), "models") else None
        
        # Obter empresa pelo ID direto da sessão
        from database.models import Company
        company = self.session.get(Company, company_id)

        if not company or not company.website:
            return {
                "success": False,
                "message": "Empresa não encontrada ou sem website cadastrado.",
                "pages_crawled": 0,
                "contacts_found": 0
            }

        target_url = company.website
        if not target_url.startswith(("http://", "https://")):
            target_url = "https://" + target_url

        # 1. Executar Crawler de até 5 páginas
        pages_res = self.crawler.crawl_website(target_url)

        pages_saved = 0
        all_extracted_contacts = []
        found_cnpj = None

        # 2. Processar e salvar páginas e extrair contatos
        for p in pages_res:
            html = p.get("html", "")
            clean_text = self.extractor.extract_clean_text(html) if html else ""

            # Salvar histórico da página visitada
            self.page_repo.add_page(
                company_id=company.id,
                url=p["url"],
                status_code=p["status_code"],
                status=p["status"],
                title=p["title"],
                content_text=clean_text
            )
            pages_saved += 1

            if html:
                # Extrair contatos públicos do HTML
                cands = self.extractor.extract_contacts_from_html(html, p["url"])
                all_extracted_contacts.extend(cands)

                # Verificar CNPJ se ainda não encontrado
                if not found_cnpj and clean_text:
                    found_cnpj = self.extractor.extract_cnpj(clean_text)

        # 3. Salvar e deduplicar contatos no banco
        contacts_saved = 0
        for c in all_extracted_contacts:
            _, is_new = self.contact_repo.add_contact(
                company_id=company.id,
                contact_type=c["contact_type"],
                value=c["value"],
                raw_value=c["raw_value"],
                source_url=c["source_url"]
            )
            if is_new:
                contacts_saved += 1
                # Adicionar evidência de contato
                self.company_repo.add_evidence(
                    company_id=company.id,
                    field_name=f"contact_{c['contact_type'].lower()}",
                    value=c["value"],
                    source_url=c["source_url"],
                    source_title=f"Contato encontrado em {c['source_url']}",
                    source_text=f"Tipo: {c['contact_type']} | Valor: {c['value']}",
                    confidence=0.9
                )

        # 4. Atualizar CNPJ da empresa se descoberto
        if found_cnpj and not company.cnpj:
            company.cnpj = found_cnpj
            self.company_repo.add_evidence(
                company_id=company.id,
                field_name="cnpj_publico",
                value=found_cnpj,
                source_url=target_url,
                source_title="CNPJ Encontrado no Website",
                source_text=f"CNPJ público extraído: {found_cnpj}",
                confidence=0.95
            )

        # Atualizar timestamp de último crawling
        company.last_crawled_at = datetime.now()
        self.session.commit()

        return {
            "success": True,
            "company_name": company.name,
            "pages_crawled": pages_saved,
            "contacts_found": len(all_extracted_contacts),
            "new_contacts_saved": contacts_saved,
            "cnpj_found": found_cnpj
        }
