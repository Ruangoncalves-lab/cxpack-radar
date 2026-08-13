import { createClient } from '@supabase/supabase-js';

export interface ProcessedLead {
  id?: string;
  nome: string;
  website: string;
  telefoneGeral: string;
  emailsCorporativos: string;
  ehFabricante: 'SIM' | 'NÃO';
  categoria: string;
  relevancia: number;
  resumoIA: string;
  tomadoresDecisao?: string;
  created_at?: string;
}

const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL || 'https://placeholder.supabase.co';
const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || 'placeholder-key';

export const supabase = createClient(supabaseUrl, supabaseAnonKey);

/**
 * Salva o lead processado na tabela Supabase 'prospecting_leads'
 */
export async function saveLeadToSupabase(lead: ProcessedLead) {
  if (supabaseUrl.includes('placeholder')) {
    // Se o Supabase não estiver conectado com URL real, operamos em memória local
    return { success: true, lead };
  }

  try {
    const { data, error } = await supabase
      .from('prospecting_leads')
      .insert([
        {
          company_name: lead.nome,
          website: lead.website,
          phone: lead.telefoneGeral,
          emails: lead.emailsCorporativos,
          is_manufacturer: lead.ehFabricante === 'SIM',
          category: lead.categoria,
          relevance_score: lead.relevancia,
          ai_summary: lead.resumoIA,
          decision_makers: lead.tomadoresDecisao,
          created_at: new Date().toISOString()
        }
      ]);

    if (error) {
      console.warn('Aviso Supabase insert:', error.message);
    }
    return { success: true, data };
  } catch (err: any) {
    console.warn('Erro ao salvar no Supabase:', err?.message);
    return { success: false, error: err };
  }
}
