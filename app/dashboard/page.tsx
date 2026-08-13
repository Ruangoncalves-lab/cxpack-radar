'use client';

import React, { useState } from 'react';
import { Navbar } from '@/components/Navbar';
import { SearchForm } from '@/components/SearchForm';
import { RealtimeProgress } from '@/components/RealtimeProgress';
import { InteractiveResultsTable } from '@/components/InteractiveResultsTable';
import { ProcessedLead } from '@/lib/supabase';
import { PipelineProgressEvent } from '@/lib/pipeline';

// Initial dataset for immediate visual impact on load
const INITIAL_LEADS: ProcessedLead[] = [
  {
    nome: "Plastipak Brasil Indústria e Comércio",
    website: "https://www.plastipak.com.br",
    telefoneGeral: "(11) 4004-8900",
    emailsCorporativos: "vendas@plastipak.com.br, contato@plastipak.com.br",
    ehFabricante: "SIM",
    categoria: "Sopro PEAD / PET / Frascos",
    relevancia: 5,
    tomadoresDecisao: "Eng. Carlos Eduardo (Gerente de Compras & Suprimentos), Ricardo Mendes (Diretor Comercial)",
    resumoIA: "Multinacional líder em sopro de embalagens plásticas, frascos PEAD e preformas PET para higiene e alimentos."
  },
  {
    nome: "Indústria Plastibras Embalagens Plásticas",
    website: "https://www.plastibras.com.br",
    telefoneGeral: "(11) 3688-2100",
    emailsCorporativos: "orcamento@plastibras.com.br",
    ehFabricante: "SIM",
    categoria: "Injeção Plástica & Tampas",
    relevancia: 5,
    tomadoresDecisao: "Roberto Fonseca (Diretor Industrial), Camila Santos (Gerente de Contas B2B)",
    resumoIA: "Fábrica nacional focada em transformação de resinas termoplásticas, tampas de injeção e frascos industriais."
  },
  {
    nome: "Coplac Plast Bisnagas Cosméticas",
    website: "https://www.coplacplast.com.br",
    telefoneGeral: "(19) 3871-4500",
    emailsCorporativos: "comercial@coplacplast.com.br",
    ehFabricante: "SIM",
    categoria: "Bisnagas Flexíveis & Cosméticos",
    relevancia: 4,
    tomadoresDecisao: "Fernando Alcantara (Head de Suprimentos & Matérias-Primas)",
    resumoIA: "Especializada na fabricação de bisnagas plásticas em extrusão para o setor de cosméticos e farmacêutico."
  },
  {
    nome: "Embalagens TecnoPlast do Brasil",
    website: "https://www.tecnoplastembalagens.com.br",
    telefoneGeral: "(11) 2199-3000",
    emailsCorporativos: "atendimento@tecnoplastembalagens.com.br",
    ehFabricante: "SIM",
    categoria: "Sopro PEAD / PET / Frascos",
    relevancia: 4,
    tomadoresDecisao: "Juliana Rocha (Coordenadora de Compras Técnicas)",
    resumoIA: "Indústria de frascos de plástico rígido com certificação de qualidade ISO 9001 e moldes sob medida."
  },
  {
    nome: "Distribuidora Plástico & Cia Varejo",
    website: "https://www.plasticoeciarevenda.com.br",
    telefoneGeral: "(11) 2233-4455",
    emailsCorporativos: "vendas@plasticoeciarevenda.com.br",
    ehFabricante: "NÃO",
    categoria: "Distribuição / Varejo",
    relevancia: 2,
    tomadoresDecisao: "Marcos Vinicius (Gerente de Loja)",
    resumoIA: "Atua exclusivamente como revendedora e distribuidora de produtos descartáveis e sacolas comerciais."
  }
];

export default function DashboardPage() {
  const [leads, setLeads] = useState<ProcessedLead[]>(INITIAL_LEADS);
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState<PipelineProgressEvent | null>(null);
  const [credits, setCredits] = useState(485);
  const [isExporting, setIsExporting] = useState(false);

  const handleSearch = async (params: { query: string; count: number; region: string }) => {
    setIsLoading(true);
    setProgress({
      step: 'SEARCH',
      totalLeads: params.count,
      processedCount: 0,
      message: 'Conectando ao Google Custom Search API e ativando Gemini 2.5 Flash...'
    });

    const currentLeads: ProcessedLead[] = [];

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });

      if (!response.ok || !response.body) {
        throw new Error('Falha ao iniciar o pipeline de busca');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event: PipelineProgressEvent = JSON.parse(line.replace('data: ', ''));
              setProgress(event);

              if (event.currentLead) {
                currentLeads.push(event.currentLead);
                setLeads((prev) => [event.currentLead!, ...prev.filter(l => l.website !== event.currentLead!.website)]);
              }

              if (event.step === 'COMPLETE') {
                setCredits((prev) => Math.max(0, prev - currentLeads.length));
              }
            } catch (err) {
              console.warn('Erro ao processar SSE event:', err);
            }
          }
        }
      }
    } catch (error: any) {
      console.error('Erro na requisição de prospecção:', error);
      alert(`Ocorreu um erro: ${error?.message || 'Tente novamente.'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExportCsv = async () => {
    if (leads.length === 0) return;
    setIsExporting(true);

    try {
      const response = await fetch('/api/export', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ leads }),
      });

      if (!response.ok) throw new Error('Erro ao gerar CSV');

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `leads_embalagens_plasticas_${Date.now()}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      alert(`Erro no download: ${err?.message}`);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col">
      
      {/* Navbar */}
      <Navbar credits={credits} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        
        {/* Search Form Card */}
        <SearchForm onSearch={handleSearch} isLoading={isLoading} />

        {/* Realtime Progress Component */}
        <RealtimeProgress progress={progress} isActive={isLoading} />

        {/* Interactive Results Table */}
        <InteractiveResultsTable 
          leads={leads} 
          onExportCsv={handleExportCsv} 
          isExporting={isExporting} 
        />

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500 glass-panel mt-auto">
        <p>© 2026 PlasticProspector Micro SaaS B2B — Potencializado por Next.js 14, Supabase & Google Gemini 2.5 Flash.</p>
      </footer>

    </div>
  );
}
