'use client';

import React from 'react';
import Link from 'next/link';
import { Factory, Sparkles, Coins, Database, Zap, LogOut } from 'lucide-react';

interface NavbarProps {
  credits?: number;
}

export const Navbar: React.FC<NavbarProps> = ({ credits = 485 }) => {
  return (
    <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 via-sky-500 to-indigo-600 p-[1px] shadow-lg shadow-cyan-500/20 group-hover:scale-105 transition-transform">
            <div className="w-full h-full bg-slate-950 rounded-[11px] flex items-center justify-center">
              <Factory className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                Plastic<span className="text-cyan-400">Prospector</span>
              </span>
              <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                PRO B2B
              </span>
            </div>
            <p className="text-[11px] text-slate-400 -mt-0.5 flex items-center gap-1">
              <Sparkles className="w-3 h-3 text-amber-400 inline" /> Gemini 2.5 Flash Engine
            </p>
          </div>
        </Link>

        {/* User Balance & Actions */}
        <div className="flex items-center gap-4">
          
          {/* Credit Balance Badge */}
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/90 border border-slate-800 shadow-inner">
            <div className="w-6 h-6 rounded-lg bg-amber-500/10 flex items-center justify-center">
              <Coins className="w-3.5 h-3.5 text-amber-400 animate-pulse-slow" />
            </div>
            <div className="text-xs">
              <span className="text-slate-400 block text-[10px] leading-tight">Saldo de Créditos</span>
              <span className="font-bold text-amber-300 font-mono">{credits} Leads</span>
            </div>
            <button 
              onClick={() => alert('Para adicionar mais créditos, selecione um plano Micro SaaS.')}
              className="ml-1 px-2 py-0.5 text-[10px] font-semibold bg-cyan-600 hover:bg-cyan-500 text-white rounded-md transition-colors"
            >
              + Recarregar
            </button>
          </div>

          {/* Database Status Indicator */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/60 border border-slate-800/60 text-xs text-slate-300">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
            <Database className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden md:inline font-mono text-[11px]">Supabase Realtime</span>
          </div>

          {/* Dashboard / Home Link */}
          <Link
            href="/dashboard"
            className="flex items-center gap-2 text-xs font-semibold px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-sky-600 hover:from-cyan-500 hover:to-sky-500 text-white shadow-md shadow-cyan-600/20 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <Zap className="w-3.5 h-3.5 fill-current" />
            Painel B2B
          </Link>
        </div>

      </div>
    </header>
  );
};
