import { cn } from "@/lib/utils"
import {
  LayoutDashboard,
  Trophy,
  Users,
  BarChart3,
  Search,
  Settings,
  Shield,
  Brain,
  GitCompare,
  ChevronLeft,
} from "lucide-react"
import { useState, useEffect } from "react"

const navItems = [
  { icon: LayoutDashboard, label: "Executive Overview", id: "dashboard" },
  { icon: Trophy, label: "Candidate Rankings", id: "rankings" },
  { icon: Users, label: "Candidate Details", id: "details" },
  { icon: GitCompare, label: "Comparison", id: "comparison" },
  { icon: Brain, label: "AI Explainability", id: "explainability" },
  { icon: BarChart3, label: "Analytics", id: "analytics" },
  { icon: Shield, label: "Honeypot Detection", id: "honeypot" },
  { icon: Search, label: "Search & Discovery", id: "search" },
  { icon: Settings, label: "Settings", id: "settings" },
]

interface SidebarProps {
  activeTab: string
  onTabChange: (tab: string) => void
}

export function Sidebar({ activeTab, onTabChange }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false)

  // Start collapsed on tablet (768-1024px)
  useEffect(() => {
    const check = () => {
      if (window.innerWidth >= 768 && window.innerWidth < 1024) {
        setCollapsed(true)
      }
    }
    check()
    window.addEventListener("resize", check)
    return () => window.removeEventListener("resize", check)
  }, [])

  return (
    <aside
      aria-label="Main navigation"
      className={cn(
        "h-screen sticky top-0 flex flex-col border-r border-border/50 bg-surface transition-all duration-300 ease-out",
        collapsed ? "w-[64px]" : "w-[220px]"
      )}
    >
      {/* Brand */}
      <div className={cn(
        "flex items-center h-14 border-b border-border/50 shrink-0",
        collapsed ? "justify-center px-2" : "gap-3 px-4"
      )}>
        <div className="w-8 h-8 rounded-[10px] bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center text-white text-sm font-bold shrink-0" aria-hidden="true">
          R
        </div>
        {!collapsed && (
          <div className="overflow-hidden min-w-0">
            <div className="text-sm font-semibold text-text-primary truncate">Redrob AI</div>
            <div className="text-[10px] text-text-muted font-medium uppercase tracking-wider truncate">Talent Intelligence</div>
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-3 space-y-0.5 overflow-y-auto" role="navigation">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activeTab === item.id
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              aria-label={item.label}
              aria-current={isActive ? "page" : undefined}
              className={cn(
                "w-full flex items-center gap-3 px-3 py-2.5 rounded-[10px] text-sm font-medium transition-all duration-200 min-h-[44px]",
                isActive
                  ? "bg-brand-50 text-brand-700"
                  : "text-text-muted hover:text-text-primary hover:bg-surface-secondary",
                collapsed && "justify-center px-2"
              )}
              title={collapsed ? item.label : undefined}
            >
              <Icon className="w-4 h-4 shrink-0" aria-hidden="true" />
              {!collapsed && <span className="truncate">{item.label}</span>}
              {isActive && !collapsed && (
                <div className="ml-auto w-1 h-4 rounded-full bg-brand-500" aria-hidden="true" />
              )}
              {isActive && collapsed && (
                <div className="absolute right-0 w-0.5 h-5 rounded-full bg-brand-500" aria-hidden="true" />
              )}
            </button>
          )
        })}
      </nav>

      {/* Version + Collapse - hidden on tablet */}
      <div className="border-t border-border/50 p-3 hidden xl:block">
        <button
          onClick={() => setCollapsed(!collapsed)}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          className="w-full flex items-center justify-center gap-2 px-2 py-2 rounded-[8px] text-xs text-text-muted hover:text-text-primary hover:bg-surface-secondary transition-all duration-200 min-h-[44px]"
        >
          <ChevronLeft
            aria-hidden="true"
            className={cn(
              "w-3.5 h-3.5 transition-transform duration-300",
              collapsed && "rotate-180"
            )}
          />
          {!collapsed && <span>v4.0 Enterprise</span>}
        </button>
      </div>
    </aside>
  )
}
