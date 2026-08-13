'use client';

import React, { useState, useMemo } from 'react';
import { ProcessedLead } from '@/lib/supabase';
import { 
  Building2, 
  ExternalLink, 
  Mail, 
  Phone, 
  CheckCircle2, 
  XCircle, 
  Star, 
  Download, 
  Copy, 
  Filter, 
  Search, 
  Sparkles, 
  Eye, 
  Check, 
  Tag, 
  Layers 
} from 'lucide-react';

interface InteractiveResultsTableProps {
  leads: ProcessedLead[];
  onExportCsv: () => void;
  isExporting?: boolean;
}

export const InteractiveResultsTable: React.FC<InteractiveResultsTableProps> = ({ 
  leads, 
  onExportCsv, 
  isExporting 
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [onlyManufacturers, setOnlyManufacturers] = useState(false);
  const [minScore, setMinScore] = useState<number>(0);
  const [selectedLead, setSelectedLead] = useState<ProcessedLead | null>(null);
  const [copiedEmail, setCopiedEmail] = useState<string | null>(null);
  const [copiedAll, setCopiedAll] = useState(false);

  // Filtered leads computation
  const filteredLeads = useMemo(() => {
    return leads.filter((lead) => {
      const matchesSearch = 
        lead.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.categoria.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.emailsCorporativos.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.website.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesFab = onlyManufacturers ? lead.ehFabricante === 'SIM' : true;
      const matchesScore = lead.relevancia >= minScore;

      return matchesSearch && matchesFab && matchesScore;
    });
  }, [leads, searchTerm, onlyManufacturers, minScore]);

  // Copy single email to clipboard
  const handleCopyEmail = (emails: string) => {
    if (!emails) return;
    navigator.clipboard.writeText(emails);
    setCopiedEmail(emails);
    setTimeout(() => setCopiedEmail(null), 2000);
  };

  // Copy all emails in filtered table
  const handleCopyAllEmails = () => {
    const allEmails = filteredLeads
      .map(l => l.emailsCorporativos)
      .filter(e => e && e !== 'Não localizado')
      .join(', ');
    
    if (allEmails) {
      navigator.clipboard.writeText(allEmails);
      setCopiedAll(true);
      setTimeout(() => setCopiedAll(false), 2500);
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800/80 shadow-2xl space-y-6">
      
      {/* Table Header & Quick Action Buttons */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-5 border-b border-slate-800/80">
        <div>
          <div className="flex items-center gap-3">
            <h3 className="text-xl font-extrabold text-white flex items-center gap-2">
              <Building2 className="w-5 h-5 text-cyan-400" />
              Resultados Qualificados por IA
            </h3>
            <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
              {filteredLeads.length} de {leads.length} Leads
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Empresas analisadas pelo Gemini 2.5 Flash com e-mails corporativos extraídos em tempo real.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={handleCopyAllEmails}
            disabled={filteredLeads.length === 0}
            className="px-4 py-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-2 transition-colors disabled:opacity-50"
          >
            {copiedAll ? (
              <>
                <Check className="w-4 h-4 text-emerald-400" />
                <span className="text-emerald-300">E-mails Copiados!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4 text-cyan-400" />
                <span>Copiar Todos E-mails</span>
              </>
            )}
          </button>

          <button
            onClick={onExportCsv}
            disabled={isExporting || leads.length === 0}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs font-bold shadow-lg shadow-emerald-600/20 flex items-center gap-2 transition-all transform hover:scale-[1.02] active:scale-[0.98] disabled:opacity-50"
          >
            <Download className="w-4 h-4" />
            <span>{isExporting ? 'Exportando...' : 'Exportar para CSV'}</span>
          </button>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-950/60 p-3.5 rounded-xl border border-slate-800/80">
        
        {/* Text Filter */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-3" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Filtrar por nome, categoria ou e-mail..."
            className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-800 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        {/* Manufacturer Only Toggle */}
        <div className="flex items-center">
          <label className="flex items-center gap-2 text-xs font-medium text-slate-300 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={onlyManufacturers}
              onChange={(e) => setOnlyManufacturers(e.target.checked)}
              className="w-4 h-4 rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-cyan-500/40"
            />
            <span className="flex items-center gap-1.5">
              <Building2 className="w-3.5 h-3.5 text-cyan-400" />
              Apenas Fabricantes (Sim)
            </span>
          </label>
        </div>

        {/* Score Stars Filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs text-slate-400 font-medium">Estrelas Mínimas:</span>
          <select
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            className="bg-slate-900 border border-slate-800 rounded-lg text-xs text-white px-2 py-2 focus:outline-none focus:border-cyan-500 cursor-pointer"
          >
            <option value={0}>Todas as Notas (1 a 5 ★)</option>
            <option value={3}>3+ Estrelas (Relevância Média)</option>
            <option value={4}>4+ Estrelas (Alta Relevância)</option>
            <option value={5}>5 Estrelas (Fabricantes Top B2B)</option>
          </select>
        </div>

      </div>

      {/* Table Component */}
      <div className="overflow-x-auto rounded-xl border border-slate-800/80 bg-slate-950/40">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/90 text-slate-400 uppercase font-semibold text-[11px] border-b border-slate-800">
            <tr>
              <th className="py-3.5 px-4">Empresa</th>
              <th className="py-3.5 px-4">Website</th>
              <th className="py-3.5 px-4">Telefone Geral</th>
              <th className="py-3.5 px-4">E-mails Corporativos</th>
              <th className="py-3.5 px-4">Tomadores de Decisão</th>
              <th className="py-3.5 px-4">Fabricante</th>
              <th className="py-3.5 px-4">Categoria / Processo</th>
              <th className="py-3.5 px-4">Relevância</th>
              <th className="py-3.5 px-4">Resumo do Gemini</th>
              <th className="py-3.5 px-4 text-center">Ações</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {filteredLeads.length === 0 ? (
              <tr>
                <td colSpan={10} className="py-12 text-center text-slate-500">
                  <div className="max-w-xs mx-auto space-y-2">
                    <Building2 className="w-8 h-8 text-slate-600 mx-auto" />
                    <p className="font-semibold text-slate-400">Nenhum lead encontrado com os filtros selecionados.</p>
                    <p className="text-[11px]">Tente alterar os termos da busca ou desativar os filtros de relevância.</p>
                  </div>
                </td>
              </tr>
            ) : (
              filteredLeads.map((lead, idx) => (
                <tr key={idx} className="hover:bg-slate-900/60 transition-colors group">
                  
                  {/* Company Name */}
                  <td className="py-3.5 px-4 font-bold text-white max-w-[180px] truncate">
                    {lead.nome}
                  </td>

                  {/* Website */}
                  <td className="py-3.5 px-4">
                    <a
                      href={lead.website.startsWith('http') ? lead.website : `https://${lead.website}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 font-mono hover:underline max-w-[140px] truncate"
                    >
                      {lead.website.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]}
                      <ExternalLink className="w-3 h-3 flex-shrink-0" />
                    </a>
                  </td>

                  {/* Phone */}
                  <td className="py-3.5 px-4 text-slate-300 font-mono">
                    <div className="flex items-center gap-1.5">
                      <Phone className="w-3.5 h-3.5 text-slate-500" />
                      <span>{lead.telefoneGeral}</span>
                    </div>
                  </td>

                  {/* Emails */}
                  <td className="py-3.5 px-4">
                    {lead.emailsCorporativos && lead.emailsCorporativos !== 'Não localizado' ? (
                      <div className="flex items-center gap-1.5 max-w-[200px]">
                        <Mail className="w-3.5 h-3.5 text-emerald-400 flex-shrink-0" />
                        <span className="truncate font-mono text-[11px] text-emerald-300" title={lead.emailsCorporativos}>
                          {lead.emailsCorporativos}
                        </span>
                        <button
                          onClick={() => handleCopyEmail(lead.emailsCorporativos)}
                          className="p-1 hover:bg-slate-800 rounded text-slate-400 hover:text-white transition-colors"
                          title="Copiar E-mail"
                        >
                          {copiedEmail === lead.emailsCorporativos ? (
                            <Check className="w-3 h-3 text-emerald-400" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </button>
                      </div>
                    ) : (
                      <span className="text-slate-500 italic text-[11px]">Não localizado</span>
                    )}
                  </td>

                  {/* Decision Makers */}
                  <td className="py-3.5 px-4 max-w-[200px]">
                    <span className="text-[11px] text-sky-300 font-medium block truncate" title={lead.tomadoresDecisao || 'Setor de Compras'}>
                      {lead.tomadoresDecisao || 'Setor de Compras / Diretoria'}
                    </span>
                  </td>

                  {/* Manufacturer Badge */}
                  <td className="py-3.5 px-4">
                    {lead.ehFabricante === 'SIM' ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                        <CheckCircle2 className="w-3 h-3" /> FABRICANTE
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                        <XCircle className="w-3 h-3" /> REVENDA/OUTRO
                      </span>
                    )}
                  </td>

                  {/* Category */}
                  <td className="py-3.5 px-4">
                    <span className="px-2.5 py-1 rounded-lg bg-slate-900 text-slate-300 border border-slate-800 font-medium text-[11px] block truncate max-w-[150px]">
                      {lead.categoria}
                    </span>
                  </td>

                  {/* Relevance Stars */}
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-0.5" title={`Relevância: ${lead.relevancia}/5`}>
                      {[1, 2, 3, 4, 5].map((star) => (
                        <Star
                          key={star}
                          className={`w-3.5 h-3.5 ${
                            star <= lead.relevancia
                              ? 'text-amber-400 fill-amber-400'
                              : 'text-slate-700'
                          }`}
                        />
                      ))}
                    </div>
                  </td>

                  {/* Gemini Summary */}
                  <td className="py-3.5 px-4 max-w-[240px]">
                    <p className="text-[11px] text-slate-300 line-clamp-2 leading-relaxed" title={lead.resumoIA}>
                      {lead.resumoIA}
                    </p>
                  </td>

                  {/* Detail Modal Action */}
                  <td className="py-3.5 px-4 text-center">
                    <button
                      onClick={() => setSelectedLead(lead)}
                      className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
                      title="Ver Detalhes do Lead"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </td>

                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal Detailed View */}
      {selectedLead && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="glass-panel w-full max-w-xl rounded-2xl p-6 border border-slate-800 shadow-2xl space-y-5 animate-scaleUp">
            
            <div className="flex items-start justify-between pb-4 border-b border-slate-800">
              <div>
                <span className="text-[10px] uppercase font-bold tracking-widest text-cyan-400 block mb-1">
                  Ficha de Qualificação B2B
                </span>
                <h4 className="text-xl font-bold text-white">{selectedLead.nome}</h4>
              </div>
              <button
                onClick={() => setSelectedLead(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span className="text-slate-500 font-semibold block">WEBSITE OFICIAL</span>
                <a
                  href={selectedLead.website}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-cyan-400 hover:underline font-mono text-sm flex items-center gap-1.5"
                >
                  {selectedLead.website} <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <span className="text-slate-500 font-semibold block">TELEFONE GERAL</span>
                  <span className="text-white font-mono text-sm">{selectedLead.telefoneGeral}</span>
                </div>
                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                  <span className="text-slate-500 font-semibold block">ENQUADRAMENTO</span>
                  <span className={`font-bold text-sm ${selectedLead.ehFabricante === 'SIM' ? 'text-emerald-400' : 'text-amber-400'}`}>
                    {selectedLead.ehFabricante === 'SIM' ? '✓ FABRICANTE DIRETO' : '⚠ REVENDA / OUTROS'}
                  </span>
                </div>
              </div>

              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span className="text-slate-500 font-semibold block">TOMADORES DE DECISÃO & CARGOS</span>
                <span className="text-sky-300 font-semibold text-xs block">{selectedLead.tomadoresDecisao || 'Gerente de Compras / Diretoria Comercial'}</span>
              </div>

              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 space-y-1">
                <span className="text-slate-500 font-semibold block">E-MAILS EXTRAÍDOS DO SITE</span>
                <div className="flex items-center justify-between">
                  <span className="text-emerald-300 font-mono text-sm">{selectedLead.emailsCorporativos}</span>
                  <button
                    onClick={() => handleCopyEmail(selectedLead.emailsCorporativos)}
                    className="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-[11px]"
                  >
                    Copiar
                  </button>
                </div>
              </div>

              <div className="p-4 rounded-xl bg-cyan-950/30 border border-cyan-900/50 space-y-2">
                <div className="flex items-center gap-2 text-cyan-400 font-bold text-xs">
                  <Sparkles className="w-4 h-4" />
                  ANÁLISE E RESUMO GEMINI 2.5 FLASH
                </div>
                <p className="text-slate-200 text-xs leading-relaxed">
                  {selectedLead.resumoIA}
                </p>
                <div className="flex items-center gap-2 pt-2">
                  <span className="text-slate-400">Categoria:</span>
                  <span className="px-2 py-0.5 rounded bg-slate-900 text-cyan-300 border border-cyan-800 font-medium">
                    {selectedLead.categoria}
                  </span>
                </div>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedLead(null)}
                className="px-5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-white font-semibold text-xs"
              >
                Fechar Ficha
              </button>
            </div>

          </div>
        </div>
      )}

    </div>
  );
};
