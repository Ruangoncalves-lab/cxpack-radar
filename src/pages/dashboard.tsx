import { ArrowRight, Building2, Check, Database, Search } from "lucide-react"
import { useEffect, useState } from "react"

import { type Overview, formatDate, request } from "@/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

export function DashboardPage() {
  const [data, setData] = useState<Overview | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    request<Overview>("/api/overview").then(setData).catch((reason) => setError(reason.message))
  }, [])

  if (error) return <PageError message={error} />
  if (!data) return <PageLoading />

  const metrics = [
    { label: "Empresas na base", value: data.metrics.companies, note: "registros persistidos" },
    { label: "Fabricantes comprovados", value: data.metrics.manufacturers, note: "com evidência comercial" },
    { label: "Leads acionáveis", value: data.metrics.actionable, note: "com contato público" },
    { label: "Pessoas mapeadas", value: data.metrics.decision_makers, note: "sócios e decisores" },
  ]

  return (
    <main className="page-frame">
      <section className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div>
          <h2 className="max-w-xl text-balance text-3xl font-semibold tracking-[-.035em] sm:text-[42px] sm:leading-[1.08]">Sua base comercial, sem caixa-preta.</h2>
          <p className="mt-3 max-w-[68ch] text-sm leading-6 text-muted">Cada empresa conserva o filtro que a encontrou, seus dados cadastrais e a origem de cada contato.</p>
        </div>
        <Button asChild variant="signal" size="lg"><a href="/nova-busca"><Search className="size-4" />Iniciar pesquisa</a></Button>
      </section>

      <section aria-label="Indicadores reais da base" className="order-sheet mb-7 grid sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric, index) => (
          <div key={metric.label} className="min-h-32 px-5 py-5 sm:px-6 xl:border-r xl:border-rule xl:last:border-r-0">
            <p className="text-xs font-semibold text-muted">{metric.label}</p>
            <strong className="mt-3 block font-mono text-3xl font-medium tabular-nums tracking-[-.04em]">{metric.value}</strong>
            <span className="mt-2 block text-xs text-muted">{metric.note}</span>
            {index === 0 && <span className="mt-4 block h-px w-12 bg-signal" />}
          </div>
        ))}
      </section>

      <div className="grid gap-7 xl:grid-cols-[minmax(0,1.7fr)_minmax(300px,.72fr)]">
        <div className="space-y-7">
          <section className="order-sheet overflow-hidden">
            <header className="section-head"><div><h3>Fila de investigação</h3><p>Ordenada por score e atualização</p></div><Button asChild variant="ghost" size="sm"><a href="/empresas">Abrir base <ArrowRight className="size-4" /></a></Button></header>
            <div className="divide-y divide-rule">
              {data.recent_companies.length ? data.recent_companies.map((company) => (
                <a key={company.id} href={`/empresas?company=${company.id}`} className="data-row group">
                  <div className="grid size-9 shrink-0 place-items-center rounded-lg bg-stock text-xs font-bold">{company.name.slice(0, 2).toUpperCase()}</div>
                  <div className="min-w-0 flex-1"><strong className="block truncate text-sm">{company.name}</strong><span className="mt-1 block truncate text-xs text-muted">{[company.city, company.state].filter(Boolean).join(" / ") || "Não informado"} · {company.company_type.replaceAll("_", " ")}</span></div>
                  <Badge variant={company.contact_count ? "success" : "outline"}>{company.contact_count ? "Contato encontrado" : "Enriquecer"}</Badge>
                  <span className="w-12 text-right font-mono text-sm tabular-nums">{company.score}</span>
                  <ArrowRight className="size-4 text-muted transition-transform group-hover:translate-x-0.5" />
                </a>
              )) : <EmptyRow text="A base está vazia. Inicie uma pesquisa para encontrar empresas." />}
            </div>
          </section>

          <section className="order-sheet overflow-hidden">
            <header className="section-head"><div><h3>Buscas recentes</h3><p>Ordens executadas e resultados persistidos</p></div><Button asChild variant="ghost" size="sm"><a href="/historico">Ver histórico <ArrowRight className="size-4" /></a></Button></header>
            <div className="divide-y divide-rule">
              {data.recent_searches.length ? data.recent_searches.map((search) => (
                <a key={search.id} href={`/empresas?search=${search.id}`} className="data-row">
                  <span className="w-20 shrink-0 font-mono text-[11px] text-muted">{formatDate(search.created_at).split(" ")[0]}</span>
                  <div className="min-w-0 flex-1"><strong className="block truncate text-sm">{[search.product, search.capacity, search.material].filter(Boolean).join(" · ")}</strong><span className="mt-1 block truncate text-xs text-muted">{search.location || "Brasil"}</span></div>
                  <Badge variant={search.status === "COMPLETED" ? "success" : search.status === "FAILED" ? "warning" : "outline"}>{search.status}</Badge>
                  <span className="font-mono text-sm tabular-nums">{search.companies_found || 0}</span>
                </a>
              )) : <EmptyRow text="Nenhuma busca registrada." />}
            </div>
          </section>
        </div>

        <aside className="space-y-5">
          <section className="bg-ink p-6 text-paper shadow-[0_18px_45px_rgba(20,22,18,.18)]">
            <div className="flex items-center justify-between"><Database className="size-5" /><span className="font-mono text-[11px] text-paper/55">DDGS / HOJE</span></div>
            <h3 className="mt-8 text-2xl font-semibold tracking-[-.03em]">{data.quota.remaining} consultas disponíveis</h3>
            <p className="mt-2 text-sm leading-6 text-paper/62">{data.quota.today_total} de {data.quota.safety_limit} consultas públicas usadas no limite interno.</p>
            <div className="mt-6 h-2 overflow-hidden rounded-full bg-white/13"><div className="h-full bg-signal" style={{ width: `${data.quota.usage_pct}%` }} /></div>
            <div className="mt-3 flex justify-between font-mono text-[11px] text-paper/52"><span>USO</span><span>{Math.round(data.quota.usage_pct)}%</span></div>
          </section>

          <section className="order-sheet p-5">
            <h3 className="text-base font-semibold">Próximas ações</h3>
            <ul className="mt-4 divide-y divide-rule">
              <ActionRow icon={Building2} label="Revisar empresas sem contato" value={Math.max(0, data.metrics.companies - data.metrics.actionable)} />
              <ActionRow icon={Check} label="Validar candidatos por CNAE" value={data.metrics.candidates} />
            </ul>
          </section>
        </aside>
      </div>
    </main>
  )
}

function ActionRow({ icon: Icon, label, value }: { icon: typeof Building2; label: string; value: number }) {
  return <li className="flex items-center gap-3 py-4"><Icon className="size-4 text-muted" /><span className="flex-1 text-sm">{label}</span><b className="font-mono text-sm tabular-nums">{value}</b></li>
}

function EmptyRow({ text }: { text: string }) {
  return <div className="px-5 py-12 text-center text-sm text-muted">{text}</div>
}

function PageLoading() {
  return <main className="page-frame"><div className="order-sheet h-44 animate-pulse bg-stock" /><div className="mt-7 grid gap-7 xl:grid-cols-2"><div className="order-sheet h-80 animate-pulse bg-stock" /><div className="order-sheet h-80 animate-pulse bg-stock" /></div></main>
}

function PageError({ message }: { message: string }) {
  return <main className="page-frame"><div className="border border-danger/30 bg-danger/8 p-5 text-sm text-danger"><strong>O painel não conseguiu carregar.</strong><p className="mt-1">{message} Verifique se a API está ativa.</p></div></main>
}
