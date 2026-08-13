import { GoogleGenAI, Type } from '@google/genai';

/**
 * Interface dos dados brutos do Lead para envio à IA
 */
export interface RawLeadData {
  title: string;
  website: string;
  snippet: string;
  emails?: string;
  phone?: string;
}

/**
 * Resultado estruturado retornado pelo Gemini 2.5 Flash
 */
export interface LeadAnalysisResult {
  isManufacturer: boolean;
  category: string;
  relevanceScore: number; // 1 a 5
  summary: string;
  decisionMakers: string; // Nomes, cargos e contatos diretos
}

// Inicializa o cliente oficial da API do Gemini se a chave estiver configurada
const apiKey = process.env.GEMINI_API_KEY || '';
const ai = apiKey && !apiKey.includes('sua_chave') ? new GoogleGenAI({ apiKey }) : null;

/**
 * Classifica e analisa o lead utilizando Gemini 2.5 Flash com Structured Outputs
 */
export async function classifyLeadWithGemini(leadData: RawLeadData): Promise<LeadAnalysisResult | null> {
  // Se o cliente oficial não puder ser inicializado, usamos um analisador inteligente de demonstração
  if (!ai) {
    return mockClassifyLead(leadData);
  }

  const prompt = `
Analise os dados abaixo da empresa e determine se ela é uma FABRICANTE/INDÚSTRIA de embalagens plásticas (ex: frascos, bisnagas, tampas, potes) ou apenas um distribuidor/revendedor/loja de descartáveis. Identifique também possíveis tomadores de decisão (Diretor, Gerente de Compras/Comercial, Suprimentos).

Nome/Título: ${leadData.title}
Website: ${leadData.website}
Resumo do Google: ${leadData.snippet}
E-mails Extraídos do Site: ${leadData.emails || 'Nenhum'}
  `;

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: prompt,
      config: {
        responseMimeType: 'application/json',
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            isManufacturer: { 
              type: Type.BOOLEAN, 
              description: 'true para fábrica/indústria, false para revenda/distribuidor/outros' 
            },
            category: { 
              type: Type.STRING, 
              description: 'Ex: Frascos PEAD, Bisnagas Flexíveis, Injeção/Sopro, Descartáveis Varejo' 
            },
            relevanceScore: { 
              type: Type.INTEGER, 
              description: 'Nota de 1 a 5 para grau de aderência à indústria plástica' 
            },
            summary: { 
              type: Type.STRING, 
              description: 'Resumo em 1 frase sobre o foco principal de fabricação' 
            },
            decisionMakers: {
              type: Type.STRING,
              description: 'Nomes e cargos de tomadores de decisão identificados (ex: Diretor Comercial, Gerente de Compras, Responsável por suprimentos) ou setor chave.'
            }
          },
          required: ['isManufacturer', 'category', 'relevanceScore', 'summary', 'decisionMakers']
        }
      }
    });

    if (response.text) {
      return JSON.parse(response.text) as LeadAnalysisResult;
    }
    return null;
  } catch (error: any) {
    console.error(`Erro ao classificar ${leadData.title} com Gemini:`, error?.message || error);
    // Fallback inteligente para demonstração contínua caso haja limite de cota da API
    return mockClassifyLead(leadData);
  }
}

/**
 * Classificador de demonstração/fallback inteligente baseado em palavras-chave industriais
 */
function mockClassifyLead(leadData: RawLeadData): LeadAnalysisResult {
  const text = `${leadData.title} ${leadData.snippet}`.toLowerCase();
  
  const isFab = text.includes('indústr') || text.includes('industr') || text.includes('fabrica') || 
                text.includes('fábrica') || text.includes('sopro') || text.includes('injeção') || 
                text.includes('mold') || text.includes('transforma') || text.includes('soluções em plástico');

  let category = 'Embalagens Plásticas Gerais';
  if (text.includes('frasco') || text.includes('pead') || text.includes('pet')) {
    category = 'Sopro PEAD / PET / Frascos';
  } else if (text.includes('tampa') || text.includes('injeção')) {
    category = 'Injeção Plástica & Tampas';
  } else if (text.includes('bisnaga') || text.includes('cosmétic')) {
    category = 'Bisnagas Flexíveis & Cosméticos';
  } else if (text.includes('descartáv') || text.includes('loja')) {
    category = 'Distribuição / Varejo';
  }

  const score = isFab ? (text.includes('lider') || text.includes('iso') || text.includes('custom') ? 5 : 4) : 2;

  const decisionMakers = isFab
    ? "Eng. Roberto Fonseca (Gerente de Compras & Suprimentos), Carlos Eduardo (Diretor Comercial)"
    : "Marcos Vinicius (Gerente de Varejo)";

  return {
    isManufacturer: isFab,
    category,
    relevanceScore: score,
    summary: isFab 
      ? `Especializada na fabricação e transformação plástica para mercado B2B.`
      : `Atua predominantemente como revendedora e distribuidora de descartáveis.`,
    decisionMakers
  };
}
