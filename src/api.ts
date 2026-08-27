export type SearchRecord = {
  id: number
  product: string
  capacity?: string
  material?: string
  location?: string
  company_type?: string
  status: string
  companies_found: number
  new_companies_found: number
  error_message?: string
  created_at: string
  completed_at?: string
}

export type Company = {
  id: number
  name: string
  legal_name?: string
  trade_name?: string
  domain: string
  website?: string
  cnpj?: string
  status?: string
  cnae_code?: string
  cnae_text?: string
  capital_social?: number
  company_type: string
  description?: string
  city?: string
  state?: string
  country?: string
  score: number
  confidence: number
  crm_status: string
  assigned_to?: string
  email?: string
  phone?: string
  contact_count: number
  decision_maker_count: number
  partner_count: number
  updated_at: string
}

export type Contact = {
  id?: number
  type: string
  value: string
  source_url?: string
  verified?: boolean
}

export type CompanyDetail = Company & {
  address?: string
  secondary_cnaes?: string
  notes?: string
  first_seen_at?: string
  last_seen_at?: string
  last_crawled_at?: string
  contacts: Contact[]
  department_contacts: Array<{ department: string; email?: string; phone?: string; whatsapp?: string; source_url?: string }>
  decision_makers: Array<{ name: string; role: string; department?: string; email?: string; phone?: string; linkedin_url?: string; confidence: number; source_url?: string }>
  partners: Array<{ name: string; qualification: string; country: string; source: string }>
  evidences: Array<{ field: string; value?: string; source_url?: string; source_title?: string; source_text?: string; confidence: number }>
}

export type Overview = {
  metrics: { companies: number; manufacturers: number; candidates: number; actionable: number; decision_makers: number }
  quota: { today_total: number; safety_limit: number; remaining: number; usage_pct: number; alert_level: string }
  recent_companies: Company[]
  recent_searches: SearchRecord[]
}

export type SearchJob = {
  id: string
  status: "QUEUED" | "RUNNING" | "COMPLETED" | "FAILED"
  stage: string
  progress: number
  error?: string
  result?: { search_id: number; companies_found: number; new_companies_found: number; contacts_saved: number; decision_makers_saved: number }
}

export type SearchPayload = {
  product: string
  capacity: string
  material: string
  country: string
  state: string
  company_type: string
  max_queries: number
  search_contacts: boolean
  search_decision_makers: boolean
  force_refresh: boolean
}

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  })
  if (!response.ok) {
    const payload = await response.json().catch(() => null)
    throw new Error(payload?.detail || "Não foi possível concluir a solicitação.")
  }
  if (response.status === 204) return undefined as T
  return response.json()
}

export function whatsappUrl(phone?: string) {
  let digits = (phone || "").replace(/\D/g, "")
  if (!digits) return null
  if (!digits.startsWith("55") && (digits.length === 10 || digits.length === 11)) digits = `55${digits}`
  return digits.length === 12 || digits.length === 13 ? `https://wa.me/${digits}` : null
}

export function formatDate(value?: string) {
  return value ? new Intl.DateTimeFormat("pt-BR", { dateStyle: "short", timeStyle: "short" }).format(new Date(value)) : "Não informado"
}

export function formatMoney(value?: number) {
  return typeof value === "number" ? new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" }).format(value) : "Não informado"
}
