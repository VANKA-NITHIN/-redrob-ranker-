import { motion } from "framer-motion"
import { useState, useEffect } from "react"
import { MetricCard } from "@/components/dashboard/metric-card"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { MetricCardSkeleton, ChartSkeleton } from "@/components/ui/skeleton"
import { getRankings } from "@/lib/api"
import type { DashboardMetrics, RankingEntry } from "@/types"
import {
  Trophy,
  Users,
  Clock,
  Shield,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
} from "lucide-react"
import {
  Tooltip as ReTooltip,
  ResponsiveContainer,
  PieChart as RePieChart,
  Pie,
  Cell,
  Area,
  AreaChart,
  CartesianGrid,
  XAxis,
  YAxis,
} from "recharts"

interface IntegrityItem {
  name: string
  value: number
  color: string
}

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-[8px] border border-border/50 bg-surface shadow-md p-3 text-xs">
        <p className="font-semibold text-text-primary mb-1">{label}</p>
        {payload.map((p: any, i: number) => (
          <p key={i} style={{ color: p.color }}>
            {p.name}: {p.value.toLocaleString()}
          </p>
        ))}
      </div>
    )
  }
  return null
}

export function DashboardPage() {
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [rankings, setRankings] = useState<RankingEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let ignore = false
    getRankings()
      .then((data) => {
        if (!ignore) {
          setMetrics(data.metrics)
          setRankings(data.rankings)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!ignore) {
          console.error("Failed to load rankings:", err)
          setError("Could not connect to the ranking backend. Make sure the API server is running on port 8000.")
          setLoading(false)
        }
      })
    return () => { ignore = true }
  }, [])

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-[12px] border border-danger/20 bg-danger/5 p-4 flex items-center gap-3">
          <AlertTriangle className="w-4 h-4 text-danger shrink-0" />
          <div>
            <p className="text-sm font-medium text-danger">Connection Error</p>
            <p className="text-xs text-text-muted mt-0.5">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
        <div className="grid-metrics gap-3">
          {Array.from({ length: 7 }).map((_, i) => (
            <MetricCardSkeleton key={i} />
          ))}
        </div>
        <div className="grid-charts gap-4">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
      </div>
    )
  }

  const integrityData: IntegrityItem[] = metrics
    ? [
        { name: "Verified", value: metrics.verifiedCount, color: "#10b981" },
        { name: "Suspicious", value: metrics.suspiciousCount, color: "#f59e0b" },
        { name: "Honeypot", value: metrics.honeypotCount, color: "#ef4444" },
      ]
    : []

  const scoreDistData: { range: string; count: number }[] = (() => {
    if (rankings.length === 0) return []
    const buckets: Record<string, number> = {}
    for (const r of rankings) {
      const bucket = Math.floor(r.score * 10) / 10
      const key = `${bucket.toFixed(1)}-${(bucket + 0.1).toFixed(1)}`
      buckets[key] = (buckets[key] || 0) + 1
    }
    return Object.entries(buckets).map(([range, count]) => ({ range, count }))
  })()

  const metricItems = metrics
    ? [
        { label: "Total Candidates", value: metrics.totalCandidates.toLocaleString(), icon: <Users className="w-4 h-4" style={{ color: "#6366f1" }} />, color: "#6366f1" as const, delay: 0 },
        { label: "Processing Time", value: `${metrics.processingTime.toFixed(1)}s`, icon: <Clock className="w-4 h-4" style={{ color: "#8b5cf6" }} />, color: "#8b5cf6" as const, delay: 0.05 },
        { label: "Top Score", value: metrics.topScore.toFixed(4), icon: <Trophy className="w-4 h-4" style={{ color: "#10b981" }} />, color: "#10b981" as const, delay: 0.1 },
        { label: "Bottom Score", value: metrics.bottomScore.toFixed(4), icon: <TrendingUp className="w-4 h-4" style={{ color: "#06b6d4" }} />, color: "#06b6d4" as const, delay: 0.15 },
        { label: "Verified", value: metrics.verifiedCount.toLocaleString(), icon: <CheckCircle className="w-4 h-4" style={{ color: "#10b981" }} />, color: "#10b981" as const, delay: 0.2 },
        { label: "Suspicious", value: metrics.suspiciousCount.toLocaleString(), icon: <AlertTriangle className="w-4 h-4" style={{ color: "#f59e0b" }} />, color: "#f59e0b" as const, delay: 0.25 },
        { label: "Honeypots", value: metrics.honeypotCount.toLocaleString(), icon: <Shield className="w-4 h-4" style={{ color: "#ef4444" }} />, color: "#ef4444" as const, delay: 0.3 },
      ]
    : []

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.04 } },
  }

  return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div className="flex items-center gap-2 mb-1">
          <h2 className="text-fluid-section font-semibold text-text-primary">Executive Overview</h2>
          <Badge variant="brand">v4.0</Badge>
        </div>
        <p className="text-fluid-small text-text-muted">Real-time intelligence across all candidate signals and ranking dimensions.</p>
      </motion.div>

      <motion.div variants={container} initial="hidden" animate="show" className="grid-metrics gap-3">
        {metricItems.map((m) => (<MetricCard key={m.label} {...m} />))}
      </motion.div>

      <div className="grid-charts gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.2 }}>
          <Card>
            <CardHeader><CardTitle>Score Distribution</CardTitle></CardHeader>
            <CardContent>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={scoreDistData}>
                    <defs>
                      <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="range" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                    <YAxis tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                    <ReTooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="count" stroke="#6366f1" fillOpacity={1} fill="url(#scoreGrad)" strokeWidth={2} />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.3 }}>
          <Card>
            <CardHeader><CardTitle>Candidate Integrity Breakdown</CardTitle></CardHeader>
            <CardContent>
              <div className="min-h-[200px] sm:min-h-[240px] lg:min-h-[280px] h-auto">
                <ResponsiveContainer width="100%" height="100%">
                  <RePieChart>
                    <Pie data={integrityData} cx="50%" cy="50%" innerRadius={60} outerRadius={90} paddingAngle={4} dataKey="value">
                      {integrityData.map((entry, idx) => (<Cell key={idx} fill={entry.color} stroke="transparent" />))}
                    </Pie>
                    <ReTooltip content={<CustomTooltip />} />
                  </RePieChart>
                </ResponsiveContainer>
                <div className="flex justify-center gap-4 mt-2">
                  {integrityData.map((entry) => (
                    <div key={entry.name} className="flex items-center gap-1.5">
                      <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
                      <span className="text-[11px] text-text-muted">{entry.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.4 }} className="grid-auto-responsive gap-4">
        <Card><CardHeader><CardTitle className="text-sm">Engine</CardTitle></CardHeader><CardContent><p className="text-xs text-text-muted">Multi-stage ranking pipeline with TF-IDF semantic matching</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Honeypot Checks</CardTitle></CardHeader><CardContent><p className="text-xs text-text-muted">20 rule-based checks + statistical anomaly detection</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Performance</CardTitle></CardHeader><CardContent><p className="text-xs text-text-muted">CPU-only, 2.1K candidates/sec, under 5 min</p></CardContent></Card>
      </motion.div>
    </div>
  )
}
