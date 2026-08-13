"""
Serviço de Extração de Dados e Contatos Públicos (ExtractionService).
Utiliza Trafilatura para texto limpo e regex para e-mails, telefones e WhatsApp.
"""

import re
from typing import Dict, Any, List, Optional
import trafilatura
from bs4 import BeautifulSoup
from utils.emails import extract_emails
from utils.phones import normalize_phone_br

CNPJ_REGEX = r"\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}"
PHONE_REGEX = r"(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?(?:9?\d{4}[-.\s]?\d{4})"


class ExtractionService:
    def extract_clean_text(self, html_content: str) -> str:
        """Extrai texto limpo e sem poluição HTML usando Trafilatura."""
        if not html_content:
            return ""
        extracted = trafilatura.extract(html_content, include_comments=False, include_tables=True)
        if extracted:
            return extracted.strip()

        # Fallback usando BeautifulSoup se Trafilatura retornar vazio
        try:
            soup = BeautifulSoup(html_content, "html.parser")
            for element in soup(["script", "style"]):
                element.decompose()
            return soup.get_text(separator=" ", strip=True)
        except Exception:
            return ""

    def extract_contacts_from_html(self, html_content: str, source_url: str) -> List[Dict[str, Any]]:
        """
        Extrai todos os contatos públicos (e-mails, telefones, WhatsApp) do HTML de uma página.
        """
        contacts: List[Dict[str, Any]] = []
        if not html_content:
            return contacts

        # 1. Extrair e-mails por mailto:
        soup = BeautifulSoup(html_content, "html.parser")
        seen_values = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"].strip()
            # mailto:
            if href.lower().startswith("mailto:"):
                email = href.split(":")[1].split("?")[0].strip().lower()
                if email and email not in seen_values:
                    seen_values.add(email)
                    contacts.append({
                        "contact_type": "EMAIL_PUBLICO",
                        "value": email,
                        "raw_value": href,
                        "source_url": source_url
                    })
            # WhatsApp link
            elif "wa.me/" in href.lower() or "api.whatsapp.com" in href.lower():
                digits = re.sub(r"\D", "", href)
                if len(digits) >= 10:
                    norm_wsp = normalize_phone_br(digits) or digits
                    if norm_wsp not in seen_values:
                        seen_values.add(norm_wsp)
                        contacts.append({
                            "contact_type": "WHATSAPP",
                            "value": norm_wsp,
                            "raw_value": href,
                            "source_url": source_url
                        })

        # 2. Extrair e-mails do texto usando Regex
        clean_text = self.extract_clean_text(html_content)
        emails_from_text = extract_emails(clean_text)
        for em in emails_from_text:
            if em not in seen_values:
                seen_values.add(em)
                contacts.append({
                    "contact_type": "EMAIL_PUBLICO",
                    "value": em,
                    "raw_value": em,
                    "source_url": source_url
                })

        # 3. Extrair telefones corporativos do texto
        phone_matches = re.findall(PHONE_REGEX, clean_text)
        for raw_ph in phone_matches:
            norm_ph = normalize_phone_br(raw_ph)
            if norm_ph and len(re.sub(r"\D", "", norm_ph)) >= 10:
                if norm_ph not in seen_values:
                    seen_values.add(norm_ph)
                    contacts.append({
                        "contact_type": "TELEFONE",
                        "value": norm_ph,
                        "raw_value": raw_ph,
                        "source_url": source_url
                    })

        return contacts

    def extract_cnpj(self, text_or_html: str) -> Optional[str]:
        """Extrai o primeiro CNPJ público válido encontrado no texto ou HTML."""
        if not text_or_html:
            return None
        matches = re.findall(CNPJ_REGEX, text_or_html)
        if matches:
            return matches[0]

        # Se não encontrou no texto limpo (ex: Trafilatura descartou o rodapé), busca no HTML completo
        try:
            soup = BeautifulSoup(text_or_html, "html.parser")
            full_text = soup.get_text(separator=" ", strip=True)
            full_matches = re.findall(CNPJ_REGEX, full_text)
            if full_matches:
                return full_matches[0]
        except Exception:
            pass

        return None
