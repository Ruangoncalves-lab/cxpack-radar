/**
 * Raspagem de e-mails e contatos dentro do site oficial do lead
 */
export async function fetchWebsiteContacts(url: string): Promise<{ emails: string; phone?: string }> {
  if (!url || url === 'N/A') return { emails: '', phone: '' };

  // Garantir protocolo HTTP/HTTPS
  let targetUrl = url;
  if (!targetUrl.startsWith('http://') && !targetUrl.startsWith('https://')) {
    targetUrl = `https://${targetUrl}`;
  }

  try {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 6000); // Timeout de 6s

    const response = await fetch(targetUrl, { 
      signal: controller.signal,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
      }
    });

    const html = await response.text();
    clearTimeout(timeout);

    // Regex para identificar e-mails no HTML
    const emailRegex = /[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/g;
    const matches = html.match(emailRegex) || [];

    // Filtra e-mails duplicados e extensões de arquivos de imagem/templates
    const cleanEmails = [...new Set(matches)].filter(email => 
      !email.endsWith('.png') && 
      !email.endsWith('.jpg') && 
      !email.endsWith('.webp') &&
      !email.endsWith('.gif') &&
      !email.includes('wixpress') &&
      !email.includes('schema.org') &&
      !email.includes('example.com') &&
      !email.includes('domain.com')
    );

    // Regex para telefone corporativo (ex: (11) 4004-1234, 0800 123 4567, +55 11 98888-7777)
    const phoneRegex = /(?:\+?55\s?)?(?:\(?\d{2}\)?\s?)?(?:9?\d{4}[-\s]?\d{4}|0800[-\s]?\d{3}[-\s]?\d{4})/g;
    const phoneMatches = html.match(phoneRegex) || [];
    const cleanPhones = [...new Set(phoneMatches)].filter(p => p.length >= 8);

    return { 
      emails: cleanEmails.slice(0, 3).join(', '),
      phone: cleanPhones.length > 0 ? cleanPhones[0] : 'Consulte pelo site'
    };
  } catch (err) {
    return { emails: '', phone: '' };
  }
}
