import { useState } from "react"
import { motion } from "framer-motion"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import {
  Settings,
  Moon,
  Sun,
  Database,
  Server,
  Sliders,
  RefreshCw,
  Check,
  Info,
  Save,
} from "lucide-react"

export function SettingsPage() {
  const [darkMode, setDarkMode] = useState(document.documentElement.classList.contains("dark"))
  const [apiEndpoint, setApiEndpoint] = useState("http://localhost:8000")
  const [dataSource, setDataSource] = useState("sample")
  const [topK, setTopK] = useState(100)
  const [saved, setSaved] = useState(false)

  const toggleDark = () => {
    setDarkMode(!darkMode)
    document.documentElement.classList.toggle("dark")
  }

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const settingsSections = [
    {
      icon: <Moon className="w-4 h-4" />,
      title: "Appearance",
      description: "Customize the look and feel of the platform.",
      content: (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-text-primary">Dark Mode</p>
              <p className="text-xs text-text-muted">Switch between light and dark themes.</p>
            </div>
            <button
              onClick={toggleDark}
              className={cn(
                "relative w-12 h-6 rounded-full transition-colors duration-300",
                darkMode ? "bg-brand-600" : "bg-surface-tertiary"
              )}
              role="switch"
              aria-checked={darkMode}
              aria-label="Toggle dark mode"
            >
              <span
                className={cn(
                  "absolute top-0.5 left-0.5 w-5 h-5 rounded-full bg-white shadow-sm flex items-center justify-center transition-transform duration-300",
                  darkMode && "translate-x-6"
                )}
              >
                {darkMode ? <Moon className="w-3 h-3 text-brand-600" /> : <Sun className="w-3 h-3 text-amber-500" />}
              </span>
            </button>
          </div>
        </div>
      ),
    },
    {
      icon: <Server className="w-4 h-4" />,
      title: "API Configuration",
      description: "Configure the backend API connection.",
      content: (
        <div className="space-y-3">
          <div>
            <label className="text-xs font-medium text-text-primary block mb-1">API Endpoint</label>
            <input
              type="text"
              value={apiEndpoint}
              onChange={(e) => setApiEndpoint(e.target.value)}
              className="w-full h-9 px-3 rounded-[8px] border border-border/50 bg-surface-secondary text-xs text-text-primary focus:outline-none focus:border-brand-300 font-mono"
            />
          </div>
          <div className="flex items-center gap-2 text-xs text-text-muted">
            <div className="w-2 h-2 rounded-full bg-success" />
            <span>Connected</span>
            <span className="text-text-dim">·</span>
            <span>v4.0.0</span>
          </div>
        </div>
      ),
    },
    {
      icon: <Database className="w-4 h-4" />,
      title: "Data Source",
      description: "Select the candidate data source for ranking.",
      content: (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            {["sample", "full", "custom"].map((source) => (
              <button
                key={source}
                onClick={() => setDataSource(source)}
                className={cn(
                  "px-3 py-1.5 rounded-[8px] text-xs font-medium border transition-all",
                  dataSource === source
                    ? "bg-brand-100 text-brand-700 border-brand-200"
                    : "bg-surface-secondary text-text-muted border-border/30 hover:bg-surface-tertiary"
                )}
              >
                {source === "sample" ? "Sample (50)" : source === "full" ? "Full (100K)" : "Custom"}
              </button>
            ))}
          </div>
          <p className="text-[11px] text-text-muted">
            {dataSource === "sample" && "Using 50 sample candidates for development and testing."}
            {dataSource === "full" && "Running on the full 100,000 candidate dataset."}
            {dataSource === "custom" && "Upload a custom dataset via the data directory."}
          </p>
        </div>
      ),
    },
    {
      icon: <Sliders className="w-4 h-4" />,
      title: "Ranking Parameters",
      description: "Tune the ranking engine behavior.",
      content: (
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs font-medium text-text-primary">Top K Candidates</label>
              <span className="text-xs font-mono text-brand-600">{topK}</span>
            </div>
            <input
              type="range"
              min={10}
              max={500}
              step={10}
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="w-full h-1.5 rounded-full bg-surface-tertiary appearance-none cursor-pointer accent-brand-600"
              aria-label="Top K candidates"
            />
            <div className="flex justify-between text-[10px] text-text-dim mt-0.5">
              <span>10</span>
              <span>500</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            {[
              { label: "Phase 1 Speed", value: "Fast", desc: "5,000 c/s" },
              { label: "Phase 2 Depth", value: "Full", desc: "20 checks" },
              { label: "S-Curve", value: "Staged", desc: "NDCG@10" },
              { label: "Behavioral", value: "Enabled", desc: "Multiplier" },
            ].map((item) => (
              <div key={item.label} className="rounded-[8px] border border-border/30 bg-surface-secondary p-2.5">
                <p className="text-[10px] text-text-dim uppercase tracking-wider">{item.label}</p>
                <p className="text-xs font-semibold text-text-primary mt-0.5">{item.value}</p>
                <p className="text-[10px] text-text-muted">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-2 mb-1">
          <h2 className="text-fluid-section font-semibold text-text-primary">Settings</h2>
          <Badge variant="brand">v4.0</Badge>
        </div>
        <p className="text-fluid-small text-text-muted">Configure ranking parameters, preferences, and platform behavior.</p>
      </motion.div>

      {/* Settings sections */}
      <div className="space-y-4">
        {settingsSections.map((section, i) => (
          <motion.div
            key={section.title}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: i * 0.06 }}
          >
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-sm">
                  <span className="text-text-muted">{section.icon}</span>
                  {section.title}
                </CardTitle>
                <p className="text-xs text-text-muted mt-0.5">{section.description}</p>
              </CardHeader>
              <CardContent>{section.content}</CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Save button */}
      <motion.div
        className="flex items-center justify-between"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.3 }}
      >
        <div className="flex items-center gap-2 text-xs text-text-muted">
          <Info className="w-3.5 h-3.5" />
          <span>Changes apply after the next ranking run.</span>
        </div>
        <Button onClick={handleSave} className="min-w-[100px]">
          {saved ? (
            <>
              <Check className="w-4 h-4 mr-1.5" />
              Saved
            </>
          ) : (
            <>
              <Save className="w-4 h-4 mr-1.5" />
              Save Settings
            </>
          )}
        </Button>
      </motion.div>

      {/* Danger zone */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.35 }}
      >
        <Card className="border-danger/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-sm text-danger">
              <RefreshCw className="w-4 h-4" />
              Re-run Ranking Pipeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-text-muted mb-3">
              Invalidate the cache and re-process all candidates from scratch. This may take up to 5 minutes for 100K candidates.
            </p>
            <Button variant="destructive" size="sm">
              <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
              Re-run Pipeline
            </Button>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
