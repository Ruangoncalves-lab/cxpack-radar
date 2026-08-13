'use client';

import React, { useState } from 'react';
import { Search, MapPin, Layers, Sparkles, SlidersHorizontal, Loader2, ArrowRight } from 'lucide-react';

interface SearchFormProps {
  onSearch: (params: { query: string; count: number; region: string }) => void;
  isLoading: boolean;
}

export const SearchForm: React.FC<SearchFormProps> = ({ onSearch, isLoading }) => {
  const [query, setQuery] = useState('frasco plástico PEAD 500ml');
  const [count, setCount] = useState(25);
  const [region, setRegion] = useState('');

  const quickSuggestions = [
    'frasco plástico 500ml',
    'bisnaga cosmética PEAD',
    'tampa flip top 28mm',
    'pote acrílico de parede dupla',
    'bombona plástica 20L',
    'embalagem para saneantes sopro'
  ];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSearch({ query: query.trim(), count, region });
  };

  return (
    <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-slate-800/80 shadow-2xl relative overflow-hidden">
      {/* Dynamic Background Glow */}
      <div className="absolute -top-24 -right-24 w-72 h-72 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />
      <div className="absolute -bottom-24 -left-24 w-72 h-72 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none" />

      <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-800/80">
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2.5">
            <Search className="w-5 h-5 text-cyan-400" />
            Prospecção B2B de Fabricantes & Indústrias
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Encontre fábricas de embalagens plásticas com e-mails corporativos extraídos e qualificação Gemini 2.5.
          </p>
        </div>
        <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-cyan-950/40 border border-cyan-800/40 text-cyan-300 text-xs font-medium">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          IA de Análise Ativa
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        
        {/* Row 1: Product Search Term */}
        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-2 flex items-center justify-between">
            <span>PRODUTO OU TIPO DE EMBALAGEM *</span>
            <span className="text-[11px] text-slate-500 font-normal">Ex: frascos, bisnagas, potes, tampas, bombonas</span>
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
              <Search className="h-4 w-4 text-slate-500" />
            </div>
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Digite o produto de plástico (ex: frasco plástico 500ml PEAD)"
              required
              className="block w-full pl-10 pr-4 py-3.5 bg-slate-950/80 border border-slate-800 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all font-medium"
            />
          </div>
        </div>

        {/* Quick Suggestion Chips */}
        <div>
          <span className="text-[11px] font-medium text-slate-400 block mb-2">Sugestões rápidas de prospecção:</span>
          <div className="flex flex-wrap gap-2">
            {quickSuggestions.map((chip, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => setQuery(chip)}
                className={`text-xs px-3 py-1.5 rounded-lg transition-all border ${
                  query === chip
                    ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 font-semibold'
                    : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:border-slate-700 hover:text-slate-200'
                }`}
              >
                {chip}
              </button>
            ))}
          </div>
        </div>

        {/* Row 2: Lead Quantity Selector & Regional Filter */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          
          {/* Quantity Selector */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-slate-400" />
              QUANTIDADE DE LEADS
            </label>
            <select
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              className="block w-full px-3.5 py-3 bg-slate-950/80 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all cursor-pointer font-medium"
            >
              <option value={25}>25 Leads Qualificados (Recomendado)</option>
              <option value={50}>50 Leads Qualificados</option>
              <option value={100}>100 Leads Qualificados (Busca Ampla)</option>
            </select>
          </div>

          {/* Regional Filter */}
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-2 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-slate-400" />
              FILTRO REGIONAL (OPCIONAL)
            </label>
            <select
              value={region}
              onChange={(e) => setRegion(e.target.value)}
              className="block w-full px-3.5 py-3 bg-slate-950/80 border border-slate-800 rounded-xl text-sm text-white focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500 transition-all cursor-pointer font-medium"
            >
              <option value="">Todo o Brasil (Nacional)</option>
              <option value="São Paulo SP">Estado de São Paulo (SP)</option>
              <option value="Região Sul RS SC PR">Região Sul (RS, SC, PR)</option>
              <option value="Minas Gerais MG RJ">Sudeste (MG, RJ, ES)</option>
              <option value="Nordeste">Região Nordeste</option>
            </select>
          </div>

        </div>

        {/* Submit CTA Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-4 px-6 rounded-xl font-bold text-sm text-white bg-gradient-to-r from-cyan-600 via-sky-600 to-indigo-600 hover:from-cyan-500 hover:via-sky-500 hover:to-indigo-500 shadow-xl shadow-cyan-600/25 transition-all transform hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 group"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin text-white" />
                <span>Processando Pipeline B2B com Gemini...</span>
              </>
            ) : (
              <>
                <span>Iniciar Prospecção de Fabricantes</span>
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </>
            )}
          </button>
        </div>

      </form>
    </div>
  );
};
