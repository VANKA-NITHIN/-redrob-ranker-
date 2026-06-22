import { useState, useEffect } from "react"
import { PageHeader } from "@/components/layout/page-header"
import { motion } from "framer-motion"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { getHealth, runRanking } from "@/lib/api"
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
  Loader2,
  CheckCircle2,
  XCircle,
} from "lucide-react"

export function SettingsPage() {
  const [darkMode, setDarkMode] = useState(document.documentElement.classList.contains("dark"))
  const [apiEndpoint, setApiEndpoint] = useState("http://localhost:8000")
  const [dataSource, setDataSource] = useState("sample")
  const [topK, setTopK] = useState(100)
  const [saved, setSaved] = useState(false)
  const [apiStatus, setApiStatus] = useState<"checking" | "connected" | "disconnected">("checking")
  const [apiVersion, setApiVersion] = useState("")
  const [rerunning, setRerunning] = useState(false)
  const [rerunResult, setRerunResult] = useState<string | null>(null)

  // Check API health on mount
  useEffect(() => {
    getHealth()
      .then((data) => {
        setApiStatus("connected")
        setApiVersion(data.version || "unknown")
      })
      .catch(() => {
        setApiStatus("disconnected")
      })
  }, [])

  const toggleDark = () => {
    setDarkMode(!darkMode)
    document.documentElement.classList.toggle("dark")
  }

  const handleSave = () => {
    // Persist to localStorage
    localStorage.setItem("redrob_settings", JSON.stringify({
      darkMode: !darkMode ? false : true,
      apiEndpoint,
      dataSource,
      topK,
    }))
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const handleRerun = async () => {
    setRerunning(true)
    setRerunResult(null)
    try {
      const result = await runRanking(dataSource)
      setRerunResult(`Pipeline completed: ${result.rankings.length} candidates ranked in ${result.metrics.processingTime.toFixed(1)}s`)
    } catch (err) {
      setRerunResult("Pipeline failed. Check the backend logs.")
    } finally {
      setRerunning(false)
    }
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
              className="w-full h-10 px-3 rounded-lg border border-border-light bg-surface-secondary/80 text-[13px] text-text-primary focus:outline-none focus:border-brand-500/50 shadow-sm font-mono transition-all"
            />
          </div>
          <div className="flex items-center gap-2 text-xs text-text-muted">
            {apiStatus === "checking" && (
              <>
                <Loader2 className="w-3 h-3 animate-spin" />
                <span>Checking connection...</span>
              </>
            )}
            {apiStatus === "connected" && (
              <>
                <CheckCircle2 className="w-3 h-3 text-success" />
                <span className="text-success">Connected</span>
                <span className="text-text-dim">·</span>
                <span>v{apiVersion}</span>
              </>
            )}
            {apiStatus === "disconnected" && (
              <>
                <XCircle className="w-3 h-3 text-danger" />
                <span className="text-danger">Disconnected</span>
                <span className="text-text-dim">·</span>
                <span>Start server: python -m uvicorn api.main:app --reload</span>
              </>
            )}
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
                  "px-4 py-2 rounded-lg text-xs font-medium border transition-all duration-200",
                  dataSource === source
                    ? "bg-brand-500/20 text-brand-300 border-brand-500/30 shadow-inner-button"
                    : "bg-surface-secondary/50 text-text-muted border-transparent hover:bg-white/5 hover:text-text-primary"
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
              className="w-full h-1.5 rounded-full bg-surface-secondary appearance-none cursor-pointer accent-brand-500"
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
              <div key={item.label} className="rounded-xl border border-border-light bg-surface-secondary/50 p-3 shadow-sm">
                <p className="text-[10px] text-text-dim uppercase tracking-wider">{item.label}</p>
                <p className="text-[13px] font-semibold text-text-primary mt-1">{item.value}</p>
                <p className="text-[10px] text-text-muted mt-0.5">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      ),
    },
  ]

  return (
    <div className="relative space-y-6 max-w-[1200px] mx-auto min-h-[calc(100vh-3.5rem)] px-[clamp(1rem,3vw,3rem)] py-[clamp(1rem,3vw,2rem)]">
      {/* Background glow */}
      <div className="absolute top-0 left-1/3 w-1/3 h-64 bg-brand-500/10 blur-[120px] rounded-full pointer-events-none -z-10" />
      <PageHeader 
        title="Settings"
        description="Configure ranking parameters, preferences, and platform behavior."
        badge={<Badge variant="brand">v4.0</Badge>}
        actions={
          <Button variant="outline" className="h-8 text-xs bg-surface-secondary" onClick={() => window.location.reload()}>Reset Defaults</Button>
        }
      />

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
            {rerunResult && (
              <p className={cn("text-xs mb-3 font-medium", rerunResult.includes("failed") ? "text-danger" : "text-success")}>
                {rerunResult}
              </p>
            )}
            <Button variant="destructive" size="sm" onClick={handleRerun} disabled={rerunning}>
              {rerunning ? (
                <>
                  <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
                  Re-run Pipeline
                </>
              )}
            </Button>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}
