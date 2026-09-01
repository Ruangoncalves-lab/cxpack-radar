import { ArrowUpRight, Building2, Download, ExternalLink, Mail, MessageCircle, Phone, RefreshCw, Search, Trash2, UserRound } from "lucide-react"
import { AnimatePresence, motion } from "motion/react"
import { useCallback, useEffect, useMemo, useState } from "react"

import { type Company, type CompanyDetail, formatDate, formatMoney, request, whatsappUrl } from "@/api"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export function CompaniesPage() {
  const searchId = useMemo(() => new URLSearchParams(window.location.search).get("search"), [])
  const [selectedId, setSelectedId] = useState(() => Number(new URLSearchParams(window.location.search).get("company") || 0))
  const [companies, setCompanies] = useState<Company[]>([])
  const [detail, setDetail] = useState<CompanyDetail | null>(null)
  const [query, setQuery] = useState("")
  const [type, setType] = useState("TODOS")
  const [loading, setLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [error, setError] = useState("")

  const loadCompanies = useCallback(async () => {
    setLoading(true)
    setError("")
    try {
      const search = searchId ? `?search_id=${searchId}` : ""
      setCompanies(await request<Company[]>(`/api/companies${search}`))
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Não foi possível carregar as empresas.")
    } finally {
      setLoading(false)
    }
  }, [searchId])

  useEffect(() => { loadCompanies() }, [loadCompanies])
  useEffect(() => {
    if (!selectedId) { setDetail(null); return }
    const controller = new AbortController()
    setDetail(null)
    setDetailLoading(true)
    request<CompanyDetail>(`/api/companies/${selectedId}`, { signal: controller.signal })
      .then(setDetail)
      .catch((reason) => { if (reason.name !== "AbortError") setError(reason.message) })
      .finally(() => { if (!controller.signal.aborted) setDetailLoading(false) })
    return () => controller.abort()
  }, [selectedId])

  const filtered = useMemo(() => companies.filter((company) => {
    const text = `${company.name} ${company.legal_name || ""} ${company.cnpj || ""} ${company.city || ""} ${company.state || ""}`.toLowerCase()
    return text.includes(query.toLowerCase()) && (type === "TODOS" || company.company_type === type)
  }), [companies, query, type])
  const exportParams = new URLSearchParams()
  if (searchId) exportParams.set("search_id", searchId)
  if (type !== "TODOS") exportParams.set("company_type", type)
  if (query.trim()) exportParams.set("q", query.trim())
  const exportUrl = `/api/companies-export.xlsx${exportParams.size ? `?${exportParams}` : ""}`

  function selectCompany(id: number) {
    const url = new URL(window.location.href)
    url.searchParams.set("company", String(id))
    window.history.replaceState({}, "", `${url.pathname}${url.search}`)
    setSelectedId(id)
  }

  async function enrich() {
    if (!detail) return
    setDetailLoading(true)
    try {
      await request(`/api/companies/${detail.id}/enrich`, { method: "POST" })
      setDetail(await request<CompanyDetail>(`/api/companies/${detail.id}`))
      await loadCompanies()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Não foi possível completar os dados.")
    } finally {
      setDetailLoading(false)
    }
  }

  async function remove() {
    if (!detail || !window.confirm(`Excluir permanentemente ${detail.name} e seus dados relacionados?`)) return
    setDetailLoading(true)
    try {
      await request(`/api/companies/${detail.id}`, { method: "DELETE" })
      const url = new URL(window.location.href); url.searchParams.delete("company"); window.history.replaceState({}, "", `${url.pathname}${url.search}`); setSelectedId(0)
      setDetail(null)
      await loadCompanies()
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Não foi possível excluir a empresa.")
    } finally {
      setDetailLoading(false)
    }
  }

  return (
    <main className="page-frame">
      <div className="mb-7 flex flex-col justify-between gap-4 lg:flex-row lg:items-end">
        <div><h2 className="text-3xl font-semibold tracking-[-.035em] sm:text-[40px]">{searchId ? `Resultados da busca #${searchId}` : "Base de empresas"}</h2><p className="mt-2 text-sm text-muted">{companies.length} registros no escopo atual. Selecione uma linha para abrir todos os dados.</p></div>
        <div className="grid gap-3 sm:grid-cols-[minmax(220px,1fr)_180px_auto] lg:w-[700px]">
          <div className="relative"><Search className="pointer-events-none absolute left-3.5 top-1/2 size-4 -translate-y-1/2 text-muted" /><Input className="pl-10" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Nome, CNPJ, cidade..." aria-label="Filtrar empresas" /></div>
          <Select value={type} onValueChange={setType}><SelectTrigger aria-label="Filtrar por tipo"><SelectValue /></SelectTrigger><SelectContent><SelectItem value="TODOS">Todos os tipos</SelectItem><SelectItem value="FABRICANTE">Fabricantes</SelectItem><SelectItem value="CANDIDATO_CNAE">Candidatos CNAE</SelectItem><SelectItem value="DISTRIBUIDOR">Distribuidores</SelectItem><SelectItem value="DESCONHECIDO">Não classificados</SelectItem></SelectContent></Select>
          <Button asChild variant="outline"><a href={exportUrl}><Download className="size-4" />Exportar Excel</a></Button>
        </div>
      </div>

      {error && <div role="alert" className="mb-5 border border-danger/30 bg-danger/8 px-4 py-3 text-sm text-danger">{error}</div>}

      <div className={detail || detailLoading ? "grid items-start gap-6 2xl:grid-cols-[minmax(0,1.45fr)_minmax(390px,.75fr)]" : ""}>
        <section className="order-sheet min-w-0 overflow-hidden">
          <div className="hidden grid-cols-[minmax(220px,1.35fr)_130px_90px_150px_70px] gap-4 border-b border-rule bg-stock/70 px-5 py-3 text-[10px] font-semibold uppercase tracking-[.08em] text-muted md:grid">
            <span>Empresa</span><span>Local</span><span>Score</span><span>Contato</span><span></span>
          </div>
          <div className="divide-y divide-rule">
            {loading ? Array.from({ length: 7 }).map((_, index) => <div key={index} className="h-[74px] animate-pulse bg-stock/55" />) : filtered.length ? filtered.map((company) => (
              <button key={company.id} onClick={() => selectCompany(company.id)} className={`grid w-full grid-cols-[minmax(0,1fr)_auto] items-center gap-4 px-4 py-4 text-left transition-colors hover:bg-stock/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-signal md:grid-cols-[minmax(220px,1.35fr)_130px_90px_150px_70px] md:px-5 ${selectedId === company.id ? "bg-[#e8e2d4]" : ""}`}>
                <span className="min-w-0"><strong className="block truncate text-sm">{company.name}</strong><small className="mt-1 block truncate text-xs text-muted">{company.cnpj || company.domain}</small></span>
                <span className="hidden text-xs text-muted md:block">{[company.city, company.state].filter(Boolean).join(" / ") || "Brasil"}</span>
                <span className="font-mono text-sm tabular-nums md:block">{company.score}<small className="text-muted">/100</small></span>
                <span className="hidden md:block">{company.phone || company.email ? <span className="block truncate text-xs">{company.phone || company.email}</span> : <Badge variant="outline">Não encontrado</Badge>}</span>
                <ArrowUpRight className="ml-auto size-4 text-muted" />
              </button>
            )) : <div className="px-5 py-16 text-center"><Building2 className="mx-auto size-6 text-muted" /><p className="mt-3 text-sm text-muted">Nenhuma empresa corresponde ao filtro atual.</p></div>}
          </div>
        </section>

        <AnimatePresence mode="wait">
          {(detail || detailLoading) && (
            <motion.aside key={selectedId} initial={{ opacity: .55, x: 16 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }} transition={{ duration: .35, ease: [0.16, 1, 0.3, 1] }} className="order-sheet min-w-0 overflow-hidden 2xl:sticky 2xl:top-24">
              {detailLoading && !detail ? <div className="h-[620px] animate-pulse bg-stock" /> : detail && <CompanyPanel company={detail} onEnrich={enrich} onDelete={remove} loading={detailLoading} />}
            </motion.aside>
          )}
        </AnimatePresence>
      </div>
    </main>
  )
}

function CompanyPanel({ company, onEnrich, onDelete, loading }: { company: CompanyDetail; onEnrich: () => void; onDelete: () => void; loading: boolean }) {
  const phones = new Map<string, { value: string; type: string; verified?: boolean; source?: string }>()
  company.contacts.filter((item) => item.type === "TELEFONE" || item.type === "WHATSAPP").forEach((item) => phones.set(item.value.replace(/\D/g, ""), { value: item.value, type: item.type, verified: item.verified, source: item.source_url }))
  company.department_contacts.forEach((item) => {
    if (item.whatsapp) phones.set(item.whatsapp.replace(/\D/g, ""), { value: item.whatsapp, type: "WHATSAPP", source: item.source_url })
    if (item.phone) phones.set(item.phone.replace(/\D/g, ""), { value: item.phone, type: "TELEFONE", source: item.source_url })
  })
  company.decision_makers.forEach((item) => item.phone && phones.set(item.phone.replace(/\D/g, ""), { value: item.phone, type: "TELEFONE", source: item.source_url }))

  const emails = new Map<string, string | undefined>()
  company.contacts.filter((item) => item.type.includes("EMAIL")).forEach((item) => emails.set(item.value, item.source_url))
  company.department_contacts.forEach((item) => item.email && emails.set(item.email, item.source_url))
  company.decision_makers.forEach((item) => item.email && emails.set(item.email, item.source_url))

  return (
    <>
      <header className="border-b-2 border-ink p-5">
        <div className="flex flex-wrap items-start justify-between gap-3"><div className="min-w-0"><h3 className="break-words text-xl font-semibold tracking-[-.025em]">{company.name}</h3><p className="mt-1 break-all font-mono text-[11px] text-muted">{company.cnpj || company.domain}</p></div><Badge variant={company.company_type === "FABRICANTE" ? "success" : "warning"}>{company.company_type.replaceAll("_", " ")}</Badge></div>
        <div className="mt-5 grid gap-2 sm:grid-cols-2"><Button className="w-full" variant="signal" onClick={onEnrich} disabled={loading}>{loading ? <RefreshCw className="size-4 animate-spin" /> : <RefreshCw className="size-4" />}Completar dados</Button>{company.website ? <Button asChild className="w-full" variant="outline"><a href={company.website} target="_blank" rel="noreferrer">Abrir site <ExternalLink className="size-4" /></a></Button> : <Button className="w-full" variant="outline" disabled>Site não localizado</Button>}</div>
      </header>

      <div className="max-h-[calc(100svh-190px)] overflow-y-auto">
        <dl className="grid grid-cols-2 border-b border-rule">
          <Fact label="Razão social" value={company.legal_name} wide /><Fact label="Nome fantasia" value={company.trade_name} />
          <Fact label="Situação" value={company.status} /><Fact label="Score" value={`${company.score}/100`} mono />
          <Fact label="CNAE principal" value={[company.cnae_code, company.cnae_text].filter(Boolean).join(" — ")} wide />
          <Fact label="Capital social" value={formatMoney(company.capital_social)} /><Fact label="Cidade / UF" value={[company.city, company.state].filter(Boolean).join(" / ")} />
          <Fact label="Endereço cadastral" value={company.address} wide /><Fact label="CNAEs secundários" value={company.secondary_cnaes} wide />
          <Fact label="Status CRM" value={company.crm_status} /><Fact label="Atualização" value={formatDate(company.updated_at)} />
        </dl>

        <DetailSection title="Contato direto" count={phones.size + emails.size} open>
          {phones.size ? Array.from(phones.values()).map((phone) => {
            const isWhatsapp = phone.type === "WHATSAPP"
            const url = isWhatsapp ? whatsappUrl(phone.value) : `tel:${phone.value.replace(/[^\d+]/g, "")}`
            return <div key={phone.value} className="contact-row"><div className="min-w-0 flex-1"><strong className="font-mono text-sm tabular-nums">{phone.value}</strong><span className="mt-1 block truncate text-[11px] text-muted">{isWhatsapp ? "WhatsApp publicado" : "Telefone público"}{phone.verified ? " · verificado no CNPJ" : ""}</span></div>{url && <Button asChild size="sm" variant={isWhatsapp ? "signal" : "outline"}><a href={url} target={isWhatsapp ? "_blank" : undefined} rel={isWhatsapp ? "noreferrer" : undefined}>{isWhatsapp ? <MessageCircle className="size-4" /> : <Phone className="size-4" />}{isWhatsapp ? "WhatsApp" : "Ligar"}</a></Button>}</div>
          }) : <Missing text="Nenhum telefone encontrado. Use Completar dados para consultar CNPJ e site." />}
          {Array.from(emails.entries()).map(([email]) => <div key={email} className="contact-row"><div className="min-w-0 flex-1"><strong className="block truncate text-sm">{email}</strong><span className="mt-1 block text-[11px] text-muted">E-mail público</span></div><Button asChild size="sm" variant="outline"><a href={`mailto:${email}`}><Mail className="size-4" />E-mail</a></Button></div>)}
        </DetailSection>

        <DetailSection title="Compras e decisores" count={company.decision_makers.length + company.department_contacts.length}>
          {company.department_contacts.map((item, index) => <PersonRow key={`${item.department}-${index}`} name={item.department} role="Contato de departamento" detail={item.email || item.phone || item.whatsapp} />)}
          {company.decision_makers.map((item) => <PersonRow key={`${item.name}-${item.role}`} name={item.name} role={item.role} detail={item.email || item.phone} />)}
          {!company.decision_makers.length && !company.department_contacts.length && <Missing text="Nenhum tomador de decisão foi identificado." />}
        </DetailSection>

        <DetailSection title="QSA societário" count={company.partners.length}>
          {company.partners.map((item) => <PersonRow key={`${item.name}-${item.qualification}`} name={item.name} role={item.qualification} detail={item.country} />)}
          {!company.partners.length && <Missing text="QSA ainda não consultado ou indisponível." />}
        </DetailSection>

        <DetailSection title="Evidências" count={company.evidences.length}>
          {company.evidences.map((item, index) => <div key={`${item.field}-${index}`} className="border-b border-rule py-3 last:border-b-0"><div className="flex items-center justify-between gap-3"><strong className="text-xs">{item.field.replaceAll("_", " ")}</strong><span className="font-mono text-[10px] text-muted">{Math.round(item.confidence * 100)}%</span></div><p className="mt-1 text-xs leading-5 text-muted">{item.source_text || item.value || "Sem trecho registrado"}</p>{item.source_url && <a className="source-link mt-2 inline-flex" href={item.source_url} target="_blank" rel="noreferrer">Abrir fonte <ExternalLink className="size-3" /></a>}</div>)}
          {!company.evidences.length && <Missing text="Nenhuma evidência registrada." />}
        </DetailSection>

        <div className="p-5"><Button variant="destructive" size="sm" onClick={onDelete}><Trash2 className="size-4" />Excluir empresa</Button></div>
      </div>
    </>
  )
}

function Fact({ label, value, wide = false, mono = false }: { label: string; value?: string | null; wide?: boolean; mono?: boolean }) {
  return <div className={`min-w-0 border-b border-r border-rule p-3.5 ${wide ? "col-span-2" : ""}`}><dt className="text-[10px] font-semibold text-muted">{label}</dt><dd className={`mt-1.5 break-words text-xs leading-5 ${mono ? "font-mono tabular-nums" : ""}`}>{value || "Não informado"}</dd></div>
}

function DetailSection({ title, count, open = false, children }: { title: string; count: number; open?: boolean; children: React.ReactNode }) {
  return <details className="group border-b border-rule" open={open}><summary className="flex min-h-12 cursor-pointer list-none items-center gap-3 px-5 py-3 text-sm font-semibold hover:bg-stock/70 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-signal"><span className="flex-1">{title}</span><span className="font-mono text-[11px] text-muted">{count}</span><span className="text-muted transition-transform group-open:rotate-45">+</span></summary><div className="px-5 pb-4">{children}</div></details>
}

function PersonRow({ name, role, detail }: { name: string; role: string; detail?: string | null }) {
  return <div className="flex gap-3 border-b border-rule py-3 last:border-b-0"><span className="grid size-8 shrink-0 place-items-center rounded-lg bg-stock"><UserRound className="size-4" /></span><div className="min-w-0"><strong className="block truncate text-xs">{name}</strong><span className="mt-1 block truncate text-[11px] text-muted">{role}{detail ? ` · ${detail}` : ""}</span></div></div>
}

function Missing({ text }: { text: string }) {
  return <p className="py-4 text-xs leading-5 text-muted">{text}</p>
}
