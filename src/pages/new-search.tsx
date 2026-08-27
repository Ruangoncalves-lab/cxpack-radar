import { ArrowRight, Check, LoaderCircle, Search } from "lucide-react"
import { motion } from "motion/react"
import { FormEvent, useEffect, useRef, useState } from "react"

import { type SearchJob, type SearchPayload, request } from "@/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

const initialPayload: SearchPayload = {
  product: "",
  capacity: "",
  material: "",
  country: "Brasil",
  state: "",
  company_type: "Fabricante",
  max_queries: 3,
  search_contacts: true,
  search_decision_makers: true,
  force_refresh: false,
}

export function NewSearchPage() {
  const [form, setForm] = useState(initialPayload)
  const [job, setJob] = useState<SearchJob | null>(null)
  const [error, setError] = useState("")
  const timer = useRef<number>()

  useEffect(() => () => window.clearTimeout(timer.current), [])

  function update<K extends keyof SearchPayload>(key: K, value: SearchPayload[K]) {
    setForm((current) => ({ ...current, [key]: value }))
  }

  async function poll(jobId: string) {
    try {
      const next = await request<SearchJob>(`/api/search-jobs/${jobId}`)
      setJob(next)
      if (next.status === "COMPLETED" || next.status === "FAILED") return
      timer.current = window.setTimeout(() => poll(jobId), 1100)
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : "A execução foi interrompida."
      setError(message)
      setJob((current) => current?.id === jobId ? { ...current, status: "FAILED", stage: "Execução interrompida", error: message } : current)
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault()
    setError("")
    if (form.product.trim().length < 2) {
      setError("Informe o produto com pelo menos dois caracteres.")
      return
    }
    try {
      const created = await request<SearchJob>("/api/search-jobs", { method: "POST", body: JSON.stringify({ ...form, state: form.state.toUpperCase() }) })
      setJob(created)
      poll(created.id)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Não foi possível iniciar a pesquisa.")
    }
  }

  const running = job?.status === "QUEUED" || job?.status === "RUNNING"

  return (
    <main className="page-frame">
      <div className="mb-8 max-w-3xl">
        <h2 className="text-balance text-3xl font-semibold tracking-[-.035em] sm:text-[42px] sm:leading-[1.08]">Descreva exatamente o que precisa encontrar.</h2>
        <p className="mt-3 max-w-[70ch] text-sm leading-6 text-muted">Produto, material e capacidade são tratados como critérios de qualificação. Candidatos oficiais por CNAE permanecem identificados até a confirmação comercial.</p>
      </div>

      <div className="grid items-start gap-7 xl:grid-cols-[minmax(0,1.55fr)_minmax(320px,.62fr)]">
        <form onSubmit={submit} className="order-sheet overflow-hidden">
          <header className="section-head border-b-2 border-ink"><div><h3>Ordem de pesquisa</h3><p>Campos técnicos da prospecção</p></div><span className="font-mono text-[11px] text-muted">BR / WEB / CNPJ</span></header>

          <div className="grid gap-x-6 gap-y-5 p-5 sm:grid-cols-2 sm:p-7">
            <Field className="sm:col-span-2" id="product" label="Produto obrigatório" hint="O item que a empresa precisa fabricar.">
              <Input id="product" autoFocus value={form.product} onChange={(event) => update("product", event.target.value)} placeholder="Ex.: frasco de resina" disabled={running} />
            </Field>
            <Field id="capacity" label="Capacidade ou volume" hint="Especificação que deve aparecer na evidência.">
              <Input id="capacity" value={form.capacity} onChange={(event) => update("capacity", event.target.value)} placeholder="Ex.: 500 ml" disabled={running} />
            </Field>
            <Field id="material" label="Material" hint="PET, PEAD, PP, vidro ou outro material.">
              <Input id="material" value={form.material} onChange={(event) => update("material", event.target.value)} placeholder="Ex.: PEAD" disabled={running} />
            </Field>
            <Field id="country" label="País">
              <Input id="country" value={form.country} onChange={(event) => update("country", event.target.value)} disabled={running} />
            </Field>
            <Field id="state" label="Estado / UF" hint="Deixe vazio para pesquisar no Brasil inteiro.">
              <Input id="state" maxLength={2} value={form.state} onChange={(event) => update("state", event.target.value.replace(/[^a-z]/gi, ""))} placeholder="Ex.: SP" disabled={running} />
            </Field>
            <Field id="company-type" label="Tipo de empresa">
              <Select value={form.company_type} onValueChange={(value) => update("company_type", value)} disabled={running}>
                <SelectTrigger id="company-type"><SelectValue /></SelectTrigger>
                <SelectContent><SelectItem value="Fabricante">Fabricante</SelectItem><SelectItem value="Distribuidor">Distribuidor</SelectItem><SelectItem value="Qualquer Tipo">Qualquer tipo</SelectItem></SelectContent>
              </Select>
            </Field>
            <Field id="queries" label="Variações de busca" hint="Mais variações aumentam a cobertura e o tempo.">
              <Select value={String(form.max_queries)} onValueChange={(value) => update("max_queries", Number(value))} disabled={running}>
                <SelectTrigger id="queries"><SelectValue /></SelectTrigger>
                <SelectContent>{[1, 2, 3, 4, 5].map((value) => <SelectItem key={value} value={String(value)}>{value} {value === 1 ? "consulta" : "consultas"}</SelectItem>)}</SelectContent>
              </Select>
            </Field>
          </div>

          <div className="border-t border-rule bg-stock/55 px-5 py-5 sm:px-7">
            <div className="grid gap-3 sm:grid-cols-2">
              <CheckField checked={form.search_contacts} onChange={(value) => update("search_contacts", value)} label="Extrair telefones e e-mails" disabled={running} />
              <CheckField checked={form.search_decision_makers} onChange={(value) => update("search_decision_makers", value)} label="Mapear compras e diretoria" disabled={running} />
            </div>
            {error && <div role="alert" className="mt-4 border border-danger/30 bg-danger/8 px-4 py-3 text-sm text-danger">{error}</div>}
            <div className="mt-5 flex flex-col items-stretch justify-between gap-3 sm:flex-row sm:items-center">
              <p className="text-xs leading-5 text-muted">A pesquisa usa fontes públicas. Nenhum contato é inventado.</p>
              <Button type="submit" variant="signal" size="lg" disabled={running}>
                {running ? <><LoaderCircle className="size-4 animate-spin" />Pesquisando</> : <><Search className="size-4" />Buscar fornecedores</>}
              </Button>
            </div>
          </div>
        </form>

        <aside className="space-y-5 xl:sticky xl:top-24">
          <section className="order-sheet p-5">
            <h3 className="text-base font-semibold">Como o filtro é aplicado</h3>
            <ol className="mt-4 divide-y divide-rule">
              <Rule title="Produto" text="Precisa aparecer no título ou trecho da fonte pública." />
              <Rule title="Material e capacidade" text="Quando informados, também precisam estar na evidência." />
              <Rule title="Localização" text="UF é validada; Brasil prioriza domínio .br ou menção explícita." />
              <Rule title="Fabricante" text="Exige sinais como fábrica, indústria ou produção própria." />
            </ol>
          </section>

          {job && (
            <section aria-live="polite" className="bg-ink p-5 text-paper shadow-[0_18px_45px_rgba(20,22,18,.18)]">
              <div className="flex items-center justify-between"><span className="font-mono text-[11px] text-paper/55">EXECUÇÃO</span><span className="font-mono text-[11px] text-paper/55">{job.progress}%</span></div>
              <h3 className="mt-5 text-xl font-semibold tracking-[-.025em]">{job.stage}</h3>
              <div className="mt-5 h-2 overflow-hidden rounded-full bg-white/12" role="progressbar" aria-label="Progresso da pesquisa" aria-valuemin={0} aria-valuemax={100} aria-valuenow={job.progress}><motion.div className={job.status === "FAILED" ? "h-full bg-danger" : "h-full bg-signal"} animate={{ width: `${job.progress}%` }} transition={{ duration: .55, ease: [0.16, 1, 0.3, 1] }} /></div>
              {job.status === "FAILED" && <p className="mt-4 text-sm leading-6 text-[#ffb4a3]">{job.error}</p>}
              {job.status === "COMPLETED" && job.result && (
                <div className="mt-5">
                  <dl className="grid grid-cols-2 gap-px bg-white/15"><ResultStat label="Empresas" value={job.result.companies_found} /><ResultStat label="Contatos" value={job.result.contacts_saved} /></dl>
                  <Button className="mt-4 w-full" variant="outline" onClick={() => window.location.assign(`/empresas?search=${job.result?.search_id}`)}>Abrir resultados <ArrowRight className="size-4" /></Button>
                </div>
              )}
            </section>
          )}
        </aside>
      </div>
    </main>
  )
}

function Field({ id, label, hint, className = "", children }: { id: string; label: string; hint?: string; className?: string; children: React.ReactNode }) {
  return <div className={className}><Label htmlFor={id}>{label}</Label>{hint && <p className="mt-1 text-[11px] leading-4 text-muted">{hint}</p>}<div className="mt-2">{children}</div></div>
}

function CheckField({ checked, onChange, label, disabled }: { checked: boolean; onChange: (value: boolean) => void; label: string; disabled: boolean }) {
  return <label className="flex min-h-11 cursor-pointer items-center gap-3 rounded-[10px] border border-rule bg-white px-3.5 text-sm font-medium hover:border-ink/40 has-[:focus-visible]:ring-2 has-[:focus-visible]:ring-signal"><input type="checkbox" className="size-4 accent-signal" checked={checked} onChange={(event) => onChange(event.target.checked)} disabled={disabled} />{label}</label>
}

function Rule({ title, text }: { title: string; text: string }) {
  return <li className="grid grid-cols-[90px_1fr] gap-3 py-3 text-xs leading-5"><strong>{title}</strong><span className="text-muted">{text}</span></li>
}

function ResultStat({ label, value }: { label: string; value: number }) {
  return <div className="bg-ink p-3"><dt className="text-[10px] text-paper/50">{label}</dt><dd className="mt-1 font-mono text-xl tabular-nums">{value}</dd></div>
}
