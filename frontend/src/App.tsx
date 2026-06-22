import { useState, lazy, Suspense, useEffect } from "react"
import { Sidebar } from "@/components/layout/sidebar"
import { TopBar } from "@/components/layout/topbar"
import { ErrorBoundary } from "@/components/layout/error-boundary"
import { ChartSkeleton } from "@/components/ui/skeleton"
import {
  LayoutDashboard,
  Trophy,
  Users,
  GitCompare,
  Brain,
  BarChart3,
  Shield,
  Search,
  Settings,
} from "lucide-react"

const DashboardPage = lazy(() => import("@/pages/dashboard-page").then(m => ({ default: m.DashboardPage || (m as any).default })))
const RankingsPage = lazy(() => import("@/pages/rankings-page").then(m => ({ default: m.RankingsPage || (m as any).default })))
const CandidateDetailPage = lazy(() => import("@/pages/candidate-detail-page").then(m => ({ default: m.CandidateDetailPage || (m as any).default })))
const ComparisonPage = lazy(() => import("@/pages/comparison-page").then(m => ({ default: m.ComparisonPage || (m as any).default })))
const AnalyticsPage = lazy(() => import("@/pages/analytics-page").then(m => ({ default: m.AnalyticsPage || (m as any).default })))
const ExplainabilityPage = lazy(() => import("@/pages/explainability/explainability-page").then(m => ({ default: m.ExplainabilityPage || (m as any).default })))
const HoneypotPage = lazy(() => import("@/pages/honeypot-page").then(m => ({ default: m.HoneypotPage || (m as any).default })))
const SearchPage = lazy(() => import("@/pages/search-page").then(m => ({ default: m.SearchPage || (m as any).default })))
const SettingsPage = lazy(() => import("@/pages/settings-page").then(m => ({ default: m.SettingsPage || (m as any).default })))

const pageConfig: Record<string, { title: string; subtitle: string }> = {
  dashboard: { title: "Executive Overview", subtitle: "Real-time candidate intelligence dashboard" },
  rankings: { title: "Candidate Rankings", subtitle: "AI-powered ranking with full explainability" },
  details: { title: "Candidate Details", subtitle: "Deep profile analysis and scoring breakdown" },
  comparison: { title: "Candidate Comparison", subtitle: "Side-by-side candidate evaluation" },
  explainability: { title: "AI Explainability", subtitle: "Understanding every ranking decision" },
  analytics: { title: "Analytics & Insights", subtitle: "Pool-wide statistics and detection patterns" },
  honeypot: { title: "Honeypot Detection", subtitle: "Adversarial profile detection and risk scoring" },
  search: { title: "Search & Discovery", subtitle: "Find candidates across all dimensions" },
  settings: { title: "Settings", subtitle: "Configure ranking parameters and preferences" },
}

const mobileNavItems = [
  { icon: LayoutDashboard, label: "Overview", id: "dashboard" },
  { icon: Trophy, label: "Rankings", id: "rankings" },
  { icon: Users, label: "Profile", id: "details" },
  { icon: GitCompare, label: "Compare", id: "comparison" },
  { icon: Brain, label: "Explain", id: "explainability" },
  { icon: BarChart3, label: "Analytics", id: "analytics" },
  { icon: Shield, label: "Honeypot", id: "honeypot" },
]

function PageSkeleton() {
  return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
      <div className="grid-metrics gap-3">
        {Array.from({ length: 7 }).map((_, i) => (
          <div key={i} className="rounded-[14px] border border-border/50 bg-surface p-4 space-y-3">
            <div className="h-3 w-24 bg-surface-tertiary/50 rounded animate-pulse" />
            <div className="h-8 w-20 bg-surface-tertiary/50 rounded animate-pulse" />
            <div className="h-3 w-16 bg-surface-tertiary/50 rounded animate-pulse" />
          </div>
        ))}
      </div>
      <div className="grid-charts gap-4">
        <ChartSkeleton />
        <ChartSkeleton />
      </div>
    </div>
  )
}

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard")
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768)

  useEffect(() => {
    const check = () => setIsMobile(window.innerWidth < 768)
    window.addEventListener("resize", check)
    return () => window.removeEventListener("resize", check)
  }, [])

  const config = pageConfig[activeTab] || pageConfig.dashboard

  const renderPage = () => {
    const PageComponent = (() => {
      switch (activeTab) {
        case "dashboard": return DashboardPage
        case "rankings": return RankingsPage
        case "details": return CandidateDetailPage
        case "comparison": return ComparisonPage
        case "analytics": return AnalyticsPage
        case "explainability": return ExplainabilityPage
        case "honeypot": return HoneypotPage
        case "search": return SearchPage
        case "settings": return SettingsPage
        default: return null
      }
    })()

    return (
      <ErrorBoundary>
        <Suspense fallback={<PageSkeleton />}>
          {PageComponent ? <PageComponent /> : (
            <div className="p-4 sm:p-6 flex items-center justify-center h-[60vh]">
              <div className="text-center">
                <div className="w-16 h-16 rounded-[16px] bg-surface-secondary flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl">🚧</span>
                </div>
                <h3 className="text-fluid-body font-semibold text-text-primary mb-1">Coming Soon</h3>
                <p className="text-fluid-small text-text-muted max-w-sm mx-auto">
                  This module is being built with enterprise-grade precision.
                </p>
              </div>
            </div>
          )}
        </Suspense>
      </ErrorBoundary>
    )
  }

  return (
    <div className="flex h-[100dvh] overflow-hidden bg-surface">
      <div className="hidden md:flex">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      <div className="flex-1 flex flex-col min-w-0 mobile-nav-spacer layout-performance relative">
        <TopBar title={config.title} subtitle={config.subtitle} />
        <main className="flex-1 overflow-y-auto overflow-x-hidden" role="main" aria-label="Main content">
          {renderPage()}
        </main>
      </div>

      <nav
        className="md:hidden fixed bottom-[env(safe-area-inset-bottom,1.5rem)] left-1/2 -translate-x-1/2 z-50 bg-surface-secondary/80 backdrop-blur-xl border border-border-light rounded-2xl shadow-premium p-1.5"
        aria-label="Mobile navigation"
        role="navigation"
      >
        <div className="flex items-center overflow-x-auto px-1 py-1 gap-0.5 scrollbar-none">
          {mobileNavItems.map((item) => {
            const Icon = item.icon
            const isActive = activeTab === item.id
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                aria-label={item.label}
                aria-current={isActive ? "page" : undefined}
                className={`flex flex-col items-center justify-center gap-1 w-12 h-12 rounded-xl transition-all duration-300 shrink-0 relative ${
                  isActive
                    ? "text-brand-400 bg-white/5"
                    : "text-text-muted hover:text-text-primary hover:bg-white/5"
                }`}
              >
                {isActive && (
                  <div className="absolute inset-0 bg-brand-500/10 rounded-xl blur-md -z-10" />
                )}
                <Icon className="w-5 h-5" aria-hidden="true" />
              </button>
            )
          })}
        </div>
      </nav>
    </div>
  )
}
