import { NextRequest } from 'next/server';
import { ProcessedLead } from '@/lib/supabase';

export async function POST(req: NextRequest) {
  try {
    const { leads }: { leads: ProcessedLead[] } = await req.json();

    if (!leads || !Array.isArray(leads) || leads.length === 0) {
      return new Response('Nenhum lead fornecido para exportação', { status: 400 });
    }

    // Cabeçalhos do CSV
    const headers = [
      'Empresa',
      'Website',
      'Telefone',
      'E-mails Encontrados',
      'Fabricante (Sim/Nao)',
      'Categoria / Processo',
      'Relevancia (1-5)',
      'Tomadores de Decisao',
      'Resumo Gemini'
    ];

    const escapeCsv = (val: string | number) => {
      const str = String(val || '').replace(/"/g, '""');
      return `"${str}"`;
    };

    const rows = leads.map(lead => [
      escapeCsv(lead.nome),
      escapeCsv(lead.website),
      escapeCsv(lead.telefoneGeral),
      escapeCsv(lead.emailsCorporativos),
      escapeCsv(lead.ehFabricante),
      escapeCsv(lead.categoria),
      escapeCsv(lead.relevancia),
      escapeCsv(lead.tomadoresDecisao || 'Setor de Compras / Diretoria'),
      escapeCsv(lead.resumoIA)
    ]);

    const csvContent = '\uFEFF' + [headers.join(';'), ...rows.map(r => r.join(';'))].join('\n');

    return new Response(csvContent, {
      status: 200,
      headers: {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': `attachment; filename="prospeccao_embalagens_plasticas_${Date.now()}.csv"`,
      },
    });
  } catch (err: any) {
    return new Response(`Erro ao gerar CSV: ${err?.message}`, { status: 500 });
  }
}
