import { searchGoogleOfficial } from './google-search';
import { fetchWebsiteContacts } from './scraper';
import { classifyLeadWithGemini } from './gemini';
import { saveLeadToSupabase, ProcessedLead } from './supabase';

export interface PipelineProgressEvent {
  step: 'SEARCH' | 'SCRAPING' | 'AI_QUALIFY' | 'SAVED' | 'COMPLETE' | 'ERROR';
  totalLeads: number;
  processedCount: number;
  currentLeadName?: string;
  currentLead?: ProcessedLead;
  message: string;
}

/**
 * Fluxo Principal do Pipeline de Prospecção
 */
export async function runProspectingPipeline(
  searchQuery: string, 
  targetCount = 20,
  onProgress?: (event: PipelineProgressEvent) => void
): Promise<ProcessedLead[]> {
  const notify = (evt: PipelineProgressEvent) => {
    if (onProgress) onProgress(evt);
  };

  // Passo 1: Busca no Google Custom Search API
  notify({
    step: 'SEARCH',
    totalLeads: targetCount,
    processedCount: 0,
    message: `[1/3] Buscando no Google Custom Search API por: "${searchQuery}"...`
  });

  const rawLeads = await searchGoogleOfficial(searchQuery, targetCount);
  const totalFound = rawLeads.length;

  notify({
    step: 'SCRAPING',
    totalLeads: totalFound,
    processedCount: 0,
    message: `[2/3] Encontrados ${totalFound} resultados. Iniciando enriquecimento de contatos e análise por IA...`
  });

  const processedLeads: ProcessedLead[] = [];
  let index = 0;

  for (const lead of rawLeads) {
    index++;
    
    notify({
      step: 'SCRAPING',
      totalLeads: totalFound,
      processedCount: index - 1,
      currentLeadName: lead.title,
      message: `Extraindo contatos corporativos em ${lead.website}...`
    });

    // Passo 2: Enriquecimento de e-mails acessando o site oficial
    const extraContacts = await fetchWebsiteContacts(lead.website);

    notify({
      step: 'AI_QUALIFY',
      totalLeads: totalFound,
      processedCount: index - 1,
      currentLeadName: lead.title,
      message: `Qualificando com Gemini 2.5 Flash...`
    });

    // Passo 3: Qualificação por IA com Gemini 2.5 Flash
    const aiAnalysis = await classifyLeadWithGemini({
      title: lead.title,
      website: lead.website,
      snippet: lead.snippet,
      emails: extraContacts.emails
    });

    if (aiAnalysis) {
      const processed: ProcessedLead = {
        nome: lead.title,
        website: lead.website,
        telefoneGeral: extraContacts.phone && extraContacts.phone !== '' ? extraContacts.phone : 'Consulte pelo site',
        emailsCorporativos: extraContacts.emails || 'contato@' + (lead.website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0] || 'empresa.com.br'),
        ehFabricante: aiAnalysis.isManufacturer ? 'SIM' : 'NÃO',
        categoria: aiAnalysis.category,
        relevancia: aiAnalysis.relevanceScore,
        resumoIA: aiAnalysis.summary,
        tomadoresDecisao: aiAnalysis.decisionMakers || 'Setor de Compras / Diretoria Comercial'
      };

      // Passo 4: Salvar no Supabase
      await saveLeadToSupabase(processed);
      processedLeads.push(processed);

      notify({
        step: 'SAVED',
        totalLeads: totalFound,
        processedCount: index,
        currentLeadName: lead.title,
        currentLead: processed,
        message: `Lead ${processed.nome} qualificado com sucesso!`
      });
    }

    // Pequena pausa para animação suave da barra de progresso no frontend
    await new Promise(resolve => setTimeout(resolve, 150));
  }

  notify({
    step: 'COMPLETE',
    totalLeads: totalFound,
    processedCount: processedLeads.length,
    message: `[3/3] Prospecção concluída! Total qualificado: ${processedLeads.length}`
  });

  return processedLeads;
}
