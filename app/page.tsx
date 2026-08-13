import React from 'react';
import Link from 'next/link';
import { 
  Factory, 
  Sparkles, 
  Search, 
  Database, 
  Bot, 
  CheckCircle, 
  ArrowRight, 
  ShieldCheck, 
  Zap, 
  Download, 
  Building2, 
  Globe 
} from 'lucide-react';

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#090d16] text-slate-100 flex flex-col selection:bg-cyan-500 selection:text-white">
      
      {/* Top Navbar */}
      <header className="sticky top-0 z-50 glass-panel border-b border-slate-800/80">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-600 to-sky-500 p-[1px]">
              <div className="w-full h-full bg-slate-950 rounded-[11px] flex items-center justify-center">
                <Factory className="w-5 h-5 text-cyan-400" />
              </div>
            </div>
            <span className="font-extrabold text-lg tracking-tight">
              Plastic<span className="text-cyan-400">Prospector</span>
            </span>
          </Link>

          <div className="flex items-center gap-4">
            <Link 
              href="/dashboard" 
              className="text-xs font-bold text-slate-300 hover:text-white transition-colors"
            >
              Entrar
            </Link>
            <Link
              href="/dashboard"
              className="px-4 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-cyan-600 to-sky-600 hover:from-cyan-500 hover:to-sky-500 text-white shadow-lg shadow-cyan-600/20 transition-all hover:scale-105"
            >
              Testar Agora Grátis →
            </Link>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative pt-20 pb-16 px-4 sm:px-6 lg:px-8 overflow-hidden">
        {/* Glow Spheres */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[600px] bg-cyan-500/10 rounded-full blur-[140px] pointer-events-none" />
        
        <div className="max-w-5xl mx-auto text-center space-y-8 relative z-10">
          
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-950/60 border border-cyan-800/60 text-cyan-300 text-xs font-semibold shadow-inner">
            <Sparkles className="w-4 h-4 text-cyan-400 animate-pulse" />
            Micro SaaS com Motor Gemini 2.5 Flash & Supabase Realtime
          </div>

          <h1 className="text-4xl sm:text-6xl font-black tracking-tight leading-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
            Prospecção B2B Automática de <br className="hidden sm:inline" />
            <span className="bg-gradient-to-r from-cyan-400 via-sky-400 to-emerald-400 bg-clip-text text-transparent">
              Fabricantes de Embalagens Plásticas
            </span>
          </h1>

          <p className="text-base sm:text-lg text-slate-400 max-w-3xl mx-auto leading-relaxed">
            Localize fábricas de frascos PEAD, bisnagas cosméticas, tampas, potes e bombonas industriais em segundos. 
            Extraia e-mails corporativos diretos e qualifique a intenção de fabricação com IA estruturada.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
            <Link
              href="/dashboard"
              className="w-full sm:w-auto px-8 py-4 rounded-xl text-base font-bold bg-gradient-to-r from-cyan-600 via-sky-600 to-indigo-600 hover:from-cyan-500 hover:via-sky-500 hover:to-indigo-500 text-white shadow-xl shadow-cyan-600/30 transition-all hover:scale-105 flex items-center justify-center gap-2"
            >
              <span>Abrir Painel de Prospecção</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
            
            <a
              href="#recursos"
              className="w-full sm:w-auto px-6 py-4 rounded-xl text-base font-semibold bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors flex items-center justify-center gap-2"
            >
              Ver Recursos B2B
            </a>
          </div>

          {/* Trust Metrics */}
          <div className="pt-10 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto border-t border-slate-800/80">
            <div>
              <span className="block text-2xl font-black text-white font-mono">100%</span>
              <span className="text-xs text-slate-400">Leads Focados B2B</span>
            </div>
            <div>
              <span className="block text-2xl font-black text-cyan-400 font-mono">Gemini 2.5</span>
              <span className="text-xs text-slate-400">Structured Output</span>
            </div>
            <div>
              <span className="block text-2xl font-black text-emerald-400 font-mono">&lt; 6s</span>
              <span className="text-xs text-slate-400">Enriquecimento de E-mails</span>
            </div>
            <div>
              <span className="block text-2xl font-black text-amber-400 font-mono">CSV Direct</span>
              <span className="text-xs text-slate-400">Exportação Completa</span>
            </div>
          </div>

        </div>
      </section>

      {/* Feature Grid */}
      <section id="recursos" className="py-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full space-y-12">
        <div className="text-center space-y-3">
          <h2 className="text-2xl sm:text-3xl font-extrabold text-white">
            Como Funciona o Pipeline Inteligente
          </h2>
          <p className="text-sm text-slate-400">
            Uma arquitetura B2B desenvolvida sob medida para prospecção de indústrias termoplásticas.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          
          <div className="glass-card p-6 rounded-2xl space-y-4">
            <div className="w-12 h-12 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
              <Search className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">1. Google Search API</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Filtra sites de fabricantes reais em todo o Brasil por termo de produto especifico (ex: frascos PEAD, bisnagas, tampas).
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl space-y-4">
            <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Globe className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">2. Raspagem de E-mails</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Acessa automaticamente a aba de contato e home oficial das indústrias, capturando e-mails corporativos válidos via Regex.
            </p>
          </div>

          <div className="glass-card p-6 rounded-2xl space-y-4">
            <div className="w-12 h-12 rounded-xl bg-violet-500/10 border border-violet-500/30 flex items-center justify-center text-violet-400">
              <Bot className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">3. Qualificação Gemini 2.5</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Analisa se a empresa é fábrica direta ou mera revenda, calcula nota de relevância (1 a 5) e resume a capacidade produtiva em 1 frase.
            </p>
          </div>

        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto w-full">
        <div className="glass-panel p-8 sm:p-12 rounded-3xl text-center space-y-6 relative overflow-hidden border border-cyan-500/30">
          <h2 className="text-3xl font-extrabold text-white">
            Pronto para impulsionar suas vendas B2B de embalagens?
          </h2>
          <p className="text-sm text-slate-300 max-w-xl mx-auto">
            Acesse o painel completo agora mesmo e inicie sua prospecção de fabricantes com e-mails enriquecidos e exportação CSV.
          </p>
          <div>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 px-8 py-4 rounded-xl text-base font-bold bg-gradient-to-r from-cyan-600 via-sky-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white shadow-xl shadow-cyan-600/30 transition-all hover:scale-105"
            >
              <Zap className="w-5 h-5 fill-current" />
              Acessar Painel /dashboard
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-8 text-center text-xs text-slate-500 mt-auto">
        <p>© 2026 PlasticProspector Micro SaaS B2B — Todos os direitos reservados.</p>
      </footer>

    </div>
  );
}
