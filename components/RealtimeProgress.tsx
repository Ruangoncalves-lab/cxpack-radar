'use client';

import React from 'react';
import { PipelineProgressEvent } from '@/lib/pipeline';
import { Search, Globe, Sparkles, Database, CheckCircle2, Loader2, AlertCircle } from 'lucide-react';

interface RealtimeProgressProps {
  progress: PipelineProgressEvent | null;
  isActive: boolean;
}

export const RealtimeProgress: React.FC<RealtimeProgressProps> = ({ progress, isActive }) => {
  if (!isActive && !progress) return null;

  const total = progress?.totalLeads || 25;
  const current = progress?.processedCount || 0;
  const percent = Math.min(100, Math.round((current / Math.max(1, total)) * 100));

  const steps = [
    { id: 'SEARCH', label: 'Google Search API', icon: Search },
    { id: 'SCRAPING', label: 'Extrator de Contatos', icon: Globe },
    { id: 'AI_QUALIFY', label: 'Análise Gemini 2.5', icon: Sparkles },
    { id: 'SAVED', label: 'Supabase Realtime', icon: Database },
  ];

  const getStepStatus = (stepId: string) => {
    if (!progress) return 'pending';
    if (progress.step === 'COMPLETE') return 'completed';
    if (progress.step === stepId) return 'active';

    const order = ['SEARCH', 'SCRAPING', 'AI_QUALIFY', 'SAVED', 'COMPLETE'];
    const currentIdx = order.indexOf(progress.step);
    const stepIdx = order.indexOf(stepId);

    if (stepIdx < currentIdx) return 'completed';
    return 'pending';
  };

  return (
    <div className="glass-panel rounded-2xl p-6 border border-slate-800/80 shadow-2xl space-y-6 animate-fadeIn">
      
      {/* Header & Percentage */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800/80">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
            {progress?.step === 'COMPLETE' ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            ) : progress?.step === 'ERROR' ? (
              <AlertCircle className="w-5 h-5 text-rose-400" />
            ) : (
              <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
            )}
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              Pipeline de Prospecção em Tempo Real
              <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Supabase Realtime
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              {progress?.message || 'Iniciando scraping e qualificação de fabricantes...'}
            </p>
          </div>
        </div>

        {/* Big Counter */}
        <div className="flex items-center gap-3 bg-slate-950/80 px-4 py-2 rounded-xl border border-slate-800 self-start sm:self-auto">
          <div className="text-right">
            <span className="text-[10px] uppercase text-slate-400 font-semibold block">Progresso</span>
            <span className="text-lg font-mono font-extrabold text-cyan-400">
              {current} / {total} <span className="text-xs text-slate-500">Leads</span>
            </span>
          </div>
          <div className="w-12 h-12 rounded-full border-2 border-slate-800 flex items-center justify-center bg-slate-900 font-mono font-bold text-xs text-white">
            {percent}%
          </div>
        </div>
      </div>

      {/* Progress Bar */}
      <div>
        <div className="w-full h-3 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800/80">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 via-sky-400 to-emerald-400 rounded-full transition-all duration-300 shadow-lg shadow-cyan-500/50 relative overflow-hidden"
            style={{ width: `${percent}%` }}
          >
            <div className="absolute inset-0 animate-shimmer" />
          </div>
        </div>
      </div>

      {/* Pipeline Step Indicators */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {steps.map((step) => {
          const status = getStepStatus(step.id);
          const Icon = step.icon;

          return (
            <div
              key={step.id}
              className={`p-3 rounded-xl border transition-all flex items-center gap-2.5 ${
                status === 'completed'
                  ? 'bg-emerald-950/20 border-emerald-800/40 text-emerald-300'
                  : status === 'active'
                  ? 'bg-cyan-950/40 border-cyan-500/50 text-cyan-300 shadow-lg shadow-cyan-500/10'
                  : 'bg-slate-950/40 border-slate-800/60 text-slate-500'
              }`}
            >
              <div
                className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold ${
                  status === 'completed'
                    ? 'bg-emerald-500/20 text-emerald-400'
                    : status === 'active'
                    ? 'bg-cyan-500/20 text-cyan-400'
                    : 'bg-slate-900 text-slate-600'
                }`}
              >
                {status === 'completed' ? (
                  <CheckCircle2 className="w-4 h-4" />
                ) : status === 'active' ? (
                  <Loader2 className="w-4 h-4 animate-spin" />
                ) : (
                  <Icon className="w-3.5 h-3.5" />
                )}
              </div>
              <span className="text-xs font-semibold tracking-tight">{step.label}</span>
            </div>
          );
        })}
      </div>

      {/* Currently Scraping Banner */}
      {progress?.currentLeadName && (
        <div className="p-3.5 rounded-xl bg-slate-950/90 border border-cyan-900/40 flex items-center justify-between text-xs">
          <div className="flex items-center gap-2 overflow-hidden">
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span className="text-slate-400 font-medium">Processando agora:</span>
            <span className="font-semibold text-white truncate max-w-xs">{progress.currentLeadName}</span>
          </div>
          <span className="text-[11px] text-cyan-400 font-mono bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-800/40">
            Qualificando com IA...
          </span>
        </div>
      )}

    </div>
  );
};
