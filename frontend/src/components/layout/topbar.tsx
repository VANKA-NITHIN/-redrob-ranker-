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
    <header className="h-14 border-b border-border-light bg-surface/80 backdrop-blur-xl sticky top-0 z-40 flex items-center justify-between px-6">
      <div className="flex items-center gap-2 text-sm">
        <span className="text-text-muted font-medium">Workspace</span>
        <span className="text-text-dim">/</span>
        <span className="text-text-primary font-semibold">{title}</span>
      </div>

      <div className="flex items-center gap-3">
        {/* Mock Global Search (Cmd+K) */}
        <button className="hidden md:flex items-center gap-3 h-8 px-3 rounded-[6px] border border-border-light bg-surface-secondary text-text-muted hover:bg-surface-tertiary hover:text-text-primary transition-colors shadow-sm text-xs">
          <Search className="w-3.5 h-3.5" />
          <span>Search...</span>
          <div className="flex items-center gap-1 ml-4 text-[10px] bg-surface border border-border-light px-1.5 py-0.5 rounded shadow-[0_1px_2px_rgba(0,0,0,0.1)]">
            <span className="font-sans">⌘</span>
            <span>K</span>
          </div>
        </button>

        <div className="h-4 w-px bg-border-light mx-1 hidden md:block" />

        <Button variant="ghost" size="icon" className="relative h-8 w-8 text-text-muted hover:text-text-primary" aria-label="Notifications">
          <Bell className="w-4 h-4" />
          <span className="absolute top-2 right-2 w-1.5 h-1.5 rounded-full bg-brand-500 shadow-[0_0_8px_rgba(139,92,246,0.8)]" />
        </Button>

        <Button variant="ghost" size="icon" onClick={toggleTheme} className="h-8 w-8 text-text-muted hover:text-text-primary" aria-label="Toggle theme">
          {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </Button>
        
        {/* User Avatar */}
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-brand-600 to-brand-400 p-[2px] ml-1 shrink-0 cursor-pointer shadow-premium">
          <div className="w-full h-full rounded-full bg-surface flex items-center justify-center">
            <div className="w-full h-full rounded-full bg-surface-secondary overflow-hidden">
              <img src="https://ui-avatars.com/api/?name=Admin&background=random" alt="User avatar" className="w-full h-full object-cover" />
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
