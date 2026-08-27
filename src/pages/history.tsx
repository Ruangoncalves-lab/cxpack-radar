import { ArrowUpRight, History } from "lucide-react"
import { useEffect, useMemo, useState } from "react"

import { type SearchRecord, formatDate, request } from "@/api"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"

export function HistoryPage() {
  const [searches, setSearches] = useState<SearchRecord[]>([])
  const [query, setQuery] = useState("")
  const [error, setError] = useState("")
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    request<SearchRecord[]>("/api/searches?limit=250").then(setSearches).catch((reason) => setError(reason.message)).finally(() => setLoading(false))
  }, [])

  const filtered = useMemo(() => searches.filter((item) => `${item.product} ${item.capacity || ""} ${item.material || ""} ${item.location || ""}`.toLowerCase().includes(query.toLowerCase())), [searches, query])

  return (
    <main className="page-frame">
      <div className="mb-7 flex flex-col justify-between gap-4 sm:flex-row sm:items-end">
        <div><h2 className="text-3xl font-semibold tracking-[-.035em] sm:text-[40px]">Histórico de pesquisas</h2><p className="mt-2 text-sm text-muted">Recupere o filtro original e abra apenas as empresas associadas a cada execução.</p></div>
        <Input className="sm:w-80" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Filtrar por produto ou local..." aria-label="Filtrar histórico" />
      </div>

      {error && <div role="alert" className="mb-5 border border-danger/30 bg-danger/8 px-4 py-3 text-sm text-danger">{error}</div>}

      <section className="order-sheet overflow-hidden">
        <div className="hidden grid-cols-[90px_minmax(220px,1fr)_160px_120px_80px_28px] gap-4 border-b border-rule bg-stock/70 px-5 py-3 text-[10px] font-semibold uppercase tracking-[.08em] text-muted md:grid">
          <span>Executada</span><span>Especificação</span><span>Local</span><span>Status</span><span>Empresas</span><span></span>
        </div>
        <div className="divide-y divide-rule">
          {loading ? Array.from({ length: 8 }).map((_, index) => <div className="h-[76px] animate-pulse bg-stock/55" key={index} />) : filtered.length ? filtered.map((item) => (
            <a key={item.id} href={`/empresas?search=${item.id}`} className="grid grid-cols-[minmax(0,1fr)_auto] items-center gap-4 px-4 py-4 hover:bg-stock/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-signal md:grid-cols-[90px_minmax(220px,1fr)_160px_120px_80px_28px] md:px-5">
              <span className="hidden font-mono text-[11px] text-muted md:block">{formatDate(item.created_at).split(" ")[0]}</span>
              <span className="min-w-0"><strong className="block truncate text-sm">{item.product}</strong><small className="mt-1 block truncate text-xs text-muted">{[item.capacity, item.material, item.company_type].filter(Boolean).join(" · ")}</small></span>
              <span className="hidden truncate text-xs text-muted md:block">{item.location || "Brasil"}</span>
              <Badge className="hidden w-fit md:inline-flex" variant={item.status === "COMPLETED" ? "success" : item.status === "FAILED" ? "warning" : "outline"}>{item.status}</Badge>
              <span className="font-mono text-sm tabular-nums">{item.companies_found || 0}</span>
              <ArrowUpRight className="size-4 text-muted" />
            </a>
          )) : <div className="px-5 py-16 text-center"><History className="mx-auto size-6 text-muted" /><p className="mt-3 text-sm text-muted">Nenhuma pesquisa corresponde ao filtro atual.</p></div>}
        </div>
      </section>
    </main>
  )
}
