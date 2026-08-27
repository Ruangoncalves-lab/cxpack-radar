import { type PropsWithChildren, useEffect, useState } from "react"
import { Building2, Gauge, History, Menu, Radar, Search } from "lucide-react"
import { motion } from "motion/react"

import { Button } from "@/components/ui/button"
import { Sheet, SheetClose, SheetContent, SheetTrigger } from "@/components/ui/sheet"
import { cn } from "@/lib/utils"
import { request } from "@/api"

const navigation = [
  { to: "/", label: "Visão geral", icon: Gauge },
  { to: "/nova-busca", label: "Nova busca", icon: Search },
  { to: "/empresas", label: "Empresas", icon: Building2 },
  { to: "/historico", label: "Histórico", icon: History },
]

const titles: Record<string, string> = {
  "/": "Visão geral",
  "/nova-busca": "Nova busca",
  "/empresas": "Empresas",
  "/historico": "Histórico",
}

function Navigation({ mobile = false }: { mobile?: boolean }) {
  return (
    <nav aria-label="Navegação principal" className="space-y-1">
      {navigation.map(({ to, label, icon: Icon }) => {
        const isActive = window.location.pathname === to
        const link = (
          <a
            key={to}
            href={to}
            className={cn(
              "relative flex min-h-11 items-center gap-3 rounded-[10px] px-3 text-sm font-semibold text-paper/68 transition-colors hover:bg-white/8 hover:text-paper focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-signal",
              isActive && "text-paper",
            )}
            aria-current={isActive ? "page" : undefined}
          >
            {isActive && <motion.span layoutId="nav-plate" className="absolute inset-0 rounded-[10px] bg-white/10" transition={{ type: "spring", stiffness: 420, damping: 38 }} />}
            <Icon className="relative size-[18px]" strokeWidth={1.8} />
            <span className="relative">{label}</span>
          </a>
        )
        return mobile ? <SheetClose asChild key={to}>{link}</SheetClose> : link
      })}
    </nav>
  )
}

export function AppShell({ children }: PropsWithChildren) {
  const title = titles[window.location.pathname] || "CXPack Radar"
  const [online, setOnline] = useState<boolean | null>(null)

  useEffect(() => {
    request<{ status: string }>("/api/health").then(() => setOnline(true)).catch(() => setOnline(false))
  }, [])

  return (
    <div className="min-h-svh bg-canvas text-ink">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-[244px] flex-col bg-ink px-4 py-5 text-paper lg:flex">
        <a href="/" className="mb-9 flex items-center gap-3 px-2 text-paper focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-signal">
          <span className="grid size-10 place-items-center rounded-[11px] border border-white/16 bg-white/7"><Radar className="size-5" /></span>
          <span><strong className="block text-[15px] tracking-[-.02em]">CXPack Radar</strong><small className="block text-[10px] font-medium tracking-[.14em] text-paper/48">PROSPECÇÃO INDUSTRIAL</small></span>
        </a>
        <Navigation />
        <div className="mt-auto border-t border-white/12 px-2 pt-4 text-[11px] leading-relaxed text-paper/48">
          Dados públicos rastreáveis<br />BrasilAPI · Minha Receita · DDGS
        </div>
      </aside>

      <div className="lg:pl-[244px]">
        <header className="sticky top-0 z-20 flex min-h-[70px] items-center justify-between border-b border-rule bg-canvas/95 px-4 sm:px-7 lg:px-9">
          <div className="flex items-center gap-3">
            <Sheet>
              <SheetTrigger asChild>
                <Button variant="outline" size="icon" className="lg:hidden" aria-label="Abrir menu"><Menu className="size-5" /></Button>
              </SheetTrigger>
              <SheetContent>
                <div className="mb-8 flex items-center gap-3 pr-12">
                  <span className="grid size-10 place-items-center rounded-[11px] bg-ink text-paper"><Radar className="size-5" /></span>
                  <strong>CXPack Radar</strong>
                </div>
                <Navigation mobile />
              </SheetContent>
            </Sheet>
            <div>
              <h1 className="text-[19px] font-semibold tracking-[-.02em] sm:text-[22px]">{title}</h1>
              <p className="hidden text-xs text-muted sm:block">Dados empresariais e contatos com fonte identificada</p>
            </div>
          </div>
          <div className={cn("flex items-center gap-2 text-xs font-semibold", online === true ? "text-success" : online === false ? "text-danger" : "text-muted")}>
            <span className={cn("size-2 rounded-full", online === true ? "bg-success" : online === false ? "bg-danger" : "bg-muted")} />
            {online === true ? "Sistema ativo" : online === false ? "Sistema indisponível" : "Verificando sistema"}
          </div>
        </header>
        {children}
      </div>
    </div>
  )
}
