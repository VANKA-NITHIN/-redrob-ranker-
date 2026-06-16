import { Bell, Search, Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useState } from "react"

interface TopBarProps {
  title: string
  subtitle?: string
}

export function TopBar({ title, subtitle }: TopBarProps) {
  const [darkMode, setDarkMode] = useState(false)

  const toggleTheme = () => {
    setDarkMode(!darkMode)
    document.documentElement.classList.toggle("dark")
  }

  return (
    <header className="h-14 border-b border-border/50 bg-surface/80 backdrop-blur-md sticky top-0 z-40 flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <div>
          <h1 className="text-base font-semibold text-text-primary">{title}</h1>
          {subtitle && (
            <p className="text-xs text-text-muted mt-0.5">{subtitle}</p>
          )}
        </div>
      </div>

      <div className="flex items-center gap-2">
        {/* Search */}
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-text-dim" aria-hidden="true" />
          <input
            type="text"
            placeholder="Search candidates..."
            aria-label="Search candidates"
            className="h-9 w-48 rounded-[8px] border border-border/50 bg-surface-secondary pl-9 pr-3 text-xs text-text-primary placeholder:text-text-dim focus:outline-none focus:border-brand-300 focus:ring-1 focus:ring-brand-200 transition-all"
          />
        </div>

        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative" aria-label="Notifications">
          <Bell className="w-4 h-4" aria-hidden="true" />
          <span className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-danger animate-pulse" aria-hidden="true" />
        </Button>

        {/* Theme toggle */}
        <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}>
          {darkMode ? <Sun className="w-4 h-4" aria-hidden="true" /> : <Moon className="w-4 h-4" aria-hidden="true" />}
        </Button>
      </div>
    </header>
  )
}
