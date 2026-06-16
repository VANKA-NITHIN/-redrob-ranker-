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

const DashboardPage = lazy(() => import("@/pages/dashboard-page"))
const RankingsPage = lazy(() => import("@/pages/rankings-page"))
const CandidateDetailPage = lazy(() => import("@/pages/candidate-detail-page"))
const ComparisonPage = lazy(() => import("@/pages/comparison-page"))
const AnalyticsPage = lazy(() => import("@/pages/analytics-page"))
const ExplainabilityPage = lazy(() => import("@/pages/explainability/explainability-page"))
const HoneypotPage = lazy(() => import("@/pages/honeypot-page"))
const SearchPage = lazy(() => import("@/pages/search-page"))
const SettingsPage = lazy(() => import("@/pages/settings-page"))

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
    <div className="flex h-screen overflow-hidden bg-surface">
      <div className="hidden md:flex">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
      </div>

      <div className="flex-1 flex flex-col min-w-0 mobile-nav-spacer">
        <TopBar title={config.title} subtitle={config.subtitle} />
        <main className="flex-1 overflow-y-auto" role="main" aria-label="Main content">
          {renderPage()}
        </main>
      </div>

      <nav
        className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-surface/95 backdrop-blur-lg border-t border-border/50 pb-[env(safe-area-inset-bottom)]"
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
                className={`flex flex-col items-center gap-0.5 px-2.5 py-1.5 min-w-[56px] min-h-[44px] rounded-[8px] transition-all duration-200 shrink-0 ${
                  isActive
                    ? "text-brand-600 bg-brand-50"
                    : "text-text-dim hover:text-text-muted hover:bg-surface-secondary"
                }`}
              >
                <Icon className="w-4 h-4" aria-hidden="true" />
                <span className="text-[9px] font-medium uppercase tracking-wider whitespace-nowrap">{item.label}</span>
              </button>
            )
          })}
        </div>
      </nav>
    </div>
  )
}
