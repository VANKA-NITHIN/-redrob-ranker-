import { motion } from "framer-motion"
import { useState, useEffect } from "react"
import { MetricCard } from "@/components/dashboard/metric-card"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { PageHeader } from "@/components/layout/page-header"
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
      <div className="rounded-[8px] border border-border-light bg-surface-secondary/95 backdrop-blur-md shadow-premium p-3 text-[13px] min-w-[140px]">
        <p className="font-semibold text-text-primary mb-2 border-b border-border-light pb-1">{label}</p>
        <div className="space-y-1">
          {payload.map((p: any, i: number) => (
            <div key={i} className="flex items-center justify-between">
              <span className="text-text-muted flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full" style={{ backgroundColor: p.color }} />
                {p.name}
              </span>
              <span className="font-medium text-text-primary">{p.value.toLocaleString()}</span>
            </div>
          ))}
        </div>
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
        { label: "Total Candidates", value: metrics.totalCandidates.toLocaleString(), icon: <Users className="w-4 h-4" />, color: "#8b5cf6", delay: 0 },
        { label: "Processing Time", value: `${metrics.processingTime.toFixed(1)}s`, icon: <Clock className="w-4 h-4" />, color: "#c4b5fd", delay: 0.05 },
        { label: "Top Score", value: metrics.topScore.toFixed(4), icon: <Trophy className="w-4 h-4" />, color: "#10b981", delay: 0.1 },
        { label: "Bottom Score", value: metrics.bottomScore.toFixed(4), icon: <TrendingUp className="w-4 h-4" />, color: "#3b82f6", delay: 0.15 },
        { label: "Verified", value: metrics.verifiedCount.toLocaleString(), icon: <CheckCircle className="w-4 h-4" />, color: "#10b981", delay: 0.2 },
        { label: "Suspicious", value: metrics.suspiciousCount.toLocaleString(), icon: <AlertTriangle className="w-4 h-4" />, color: "#f59e0b", delay: 0.25 },
        { label: "Honeypots", value: metrics.honeypotCount.toLocaleString(), icon: <Shield className="w-4 h-4" />, color: "#ef4444", delay: 0.3 },
      ]
    : []

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.05 } },
  }

  return (
    <div className="relative space-y-8 max-w-[2200px] mx-auto min-h-[calc(100vh-3.5rem)] px-[clamp(1rem,3vw,3rem)] py-[clamp(1rem,3vw,2rem)]">
      {/* Background glow */}
      <div className="absolute top-0 left-1/4 w-1/2 h-64 bg-brand-500/10 blur-[100px] rounded-full pointer-events-none -z-10" />
      <PageHeader 
        title="Executive Overview" 
        description="Real-time intelligence across all candidate signals and ranking dimensions."
        badge={<Badge variant="brand">v4.0</Badge>}
        actions={
          <>
            <Button variant="outline" className="h-8 text-xs bg-surface-secondary">Export Report</Button>
            <Button className="h-8 text-xs bg-brand-500 hover:bg-brand-600 text-white border-0 shadow-premium">Refresh Data</Button>
          </>
        }
      />

      <motion.div variants={container} initial="hidden" animate="show" className="grid-metrics gap-3">
        {metricItems.map((m) => (<MetricCard key={m.label} {...m} />))}
      </motion.div>

      <div className="grid-charts gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.2 }}>
          <Card>
            <CardHeader><CardTitle>Score Distribution</CardTitle></CardHeader>
            <CardContent>
              <div className="h-[clamp(250px,40vh,600px)] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={scoreDistData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4}/>
                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" vertical={false} />
                    <XAxis dataKey="range" tick={{ fontSize: 11, fill: "var(--color-text-muted)" }} axisLine={false} tickLine={false} dy={10} />
                    <YAxis tick={{ fontSize: 11, fill: "var(--color-text-muted)" }} axisLine={false} tickLine={false} />
                    <ReTooltip content={<CustomTooltip />} cursor={{ stroke: 'var(--color-border-hover)', strokeWidth: 1, strokeDasharray: '4 4' }} />
                    <Area type="monotone" dataKey="count" stroke="#8b5cf6" fillOpacity={1} fill="url(#scoreGrad)" strokeWidth={2} activeDot={{ r: 4, fill: "#8b5cf6", stroke: "#fff", strokeWidth: 2 }} />
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
              <div className="h-[clamp(250px,40vh,600px)] w-full">
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

      {/* Main Data Section - Recent Top Candidates */}
      {rankings.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.35 }}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle>Top Candidates Preview</CardTitle>
              <Button variant="ghost" className="h-8 text-xs text-brand-400 hover:text-brand-300">View All Rankings</Button>
            </CardHeader>
            <CardContent>
              <div className="w-full overflow-x-auto scrollbar-hide rounded-lg border border-border-light">
                <table className="w-full text-left text-sm whitespace-nowrap">
                  <thead className="bg-surface-secondary/50 text-text-muted text-xs uppercase tracking-wider">
                    <tr>
                      <th className="px-4 py-3 font-medium">Candidate</th>
                      <th className="px-4 py-3 font-medium">Match Score</th>
                      <th className="px-4 py-3 font-medium">Integrity</th>
                      <th className="px-4 py-3 font-medium text-right">Experience</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border-light text-text-primary">
                    {rankings.slice(0, 5).map((r, i) => (
                      <tr key={i} className="hover:bg-surface-secondary/30 transition-colors">
                        <td className="px-4 py-3 font-medium">{r.name}</td>
                        <td className="px-4 py-3">
                          <span className="inline-flex items-center justify-center px-2 py-1 rounded bg-brand-500/10 text-brand-400 font-mono text-xs">
                            {r.score.toFixed(3)}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium capitalize ${
                            r.badge !== 'verified' ? "bg-danger/10 text-danger border border-danger/20" : "bg-success/10 text-success border border-success/20"
                          }`}>
                            {r.badge || "verified"}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-right text-text-muted">{r.experience || 0} yrs</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}

      {/* System Health Footer */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4, delay: 0.4 }} className="grid-auto-responsive gap-4">
        <Card><CardHeader><CardTitle className="text-sm">Engine</CardTitle></CardHeader><CardContent><p className="text-xs text-text-muted">Multi-stage ranking pipeline with TF-IDF semantic matching</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Honeypot Checks</CardTitle></CardHeader><CardContent><p className="text-xs text-text-muted">20 rule-based checks + statistical anomaly detection</p></CardContent></Card>
        <Card><CardHeader><CardTitle className="text-sm">Performance</CardTitle></CardHeader><CardContent><p className="text-xs text-text-muted">CPU-only, 2.1K candidates/sec, under 5 min</p></CardContent></Card>
      </motion.div>
    </div>
  )
}
