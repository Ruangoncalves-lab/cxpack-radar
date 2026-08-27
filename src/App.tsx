import { motion, useReducedMotion } from "motion/react"

import { AppShell } from "@/components/app-shell"
import { CompaniesPage } from "@/pages/companies"
import { DashboardPage } from "@/pages/dashboard"
import { HistoryPage } from "@/pages/history"
import { NewSearchPage } from "@/pages/new-search"

export default function App() {
  const reducedMotion = useReducedMotion()
  const path = window.location.pathname
  const Page = path === "/nova-busca"
    ? NewSearchPage
    : path === "/empresas"
      ? CompaniesPage
      : path === "/historico"
        ? HistoryPage
        : DashboardPage

  return (
    <AppShell>
      <motion.div
        key={path}
        initial={reducedMotion ? false : { opacity: .72, clipPath: "inset(0 0 22px 0)", y: 8 }}
        animate={{ opacity: 1, clipPath: "inset(0 0 0 0)", y: 0 }}
        transition={{ duration: .46, ease: [0.16, 1, 0.3, 1] }}
      >
        <Page />
      </motion.div>
    </AppShell>
  )
}
