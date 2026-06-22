import { useState, useEffect } from "react"
import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { MetricCardSkeleton, ChartSkeleton } from "@/components/ui/skeleton"
import { MetricCard } from "@/components/dashboard/metric-card"
import { getHoneypotData } from "@/lib/api"
import type { HoneypotData } from "@/types"
import {
  Shield,
  Skull,
  AlertTriangle,
  CheckCircle2,
  Activity,
  Filter,
  BarChart3,
} from "lucide-react"
import {
  Tooltip as ReTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart as RePieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend,
} from "recharts"

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
              <span className="font-medium text-text-primary">{typeof p.value === "number" ? p.value.toLocaleString() : p.value}</span>
            </div>
          ))}
        </div>
      </div>
    )
  }
  return null
}

// Fallback demo data when the backend is not available
const demoData: HoneypotData = {
  totalDetected: 16157,
  totalFlags: 16211,
  cleanProfiles: 72300,
  detectionRate: 16.2,
  violationBreakdown: [
    { name: "Timeline Inconsistencies", count: 4231, color: "#ef4444" },
    { name: "Keyword Density", count: 3240, color: "#f97316" },
    { name: "Fictional Companies", count: 2150, color: "#f59e0b" },
    { name: "Overlapping Education", count: 1880, color: "#eab308" },
    { name: "AI Skills No Background", count: 1560, color: "#06b6d4" },
    { name: "Missing Descriptions", count: 1420, color: "#8b5cf6" },
    { name: "Salary Range Inversion", count: 980, color: "#6366f1" },
    { name: "Temporal Inversion", count: 750, color: "#3b82f6" },
  ],
  riskDistribution: [
    { name: "Low Risk (0-10%)", value: 72300, color: "#10b981" },
    { name: "Medium Risk (11-30%)", value: 18100, color: "#f59e0b" },
    { name: "High Risk (31-60%)", value: 7200, color: "#f97316" },
    { name: "Critical (61-100%)", value: 2400, color: "#ef4444" },
  ],
  multiHitDistribution: [
    { hits: "0 checks", count: 65100 },
    { hits: "1-2 checks", count: 21400 },
    { hits: "3-5 checks", count: 9800 },
    { hits: "6-10 checks", count: 3200 },
    { hits: "10+ checks", count: 500 },
  ],
}

export function HoneypotPage() {
  const [data, setData] = useState<HoneypotData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let ignore = false
    getHoneypotData()
      .then((result) => {
        if (!ignore) {
          setData(result)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!ignore) {
          console.warn("Honeypot API not available, using demo data:", err)
          setData(demoData)
          setLoading(false)
          setError(null) // Demo mode is fine, no error shown
        }
      })
    return () => { ignore = true }
  }, [])

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.04 } },
  }

  if (error && !data) {
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
          {Array.from({ length: 4 }).map((_, i) => (<MetricCardSkeleton key={i} />))}
        </div>
        <div className="grid-charts gap-4">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
      </div>
    )
  }

  const {
    totalDetected,
    totalFlags,
    cleanProfiles,
    detectionRate,
    violationBreakdown,
    riskDistribution,
    multiHitDistribution,
  } = data!

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="relative space-y-8 max-w-[2200px] mx-auto min-h-[calc(100vh-3.5rem)] px-[clamp(1rem,3vw,3rem)] py-[clamp(1rem,3vw,2rem)]">
      {/* Background glow */}
      <div className="absolute top-0 right-1/4 w-1/3 h-64 bg-danger/10 blur-[120px] rounded-full pointer-events-none -z-10" />
      <PageHeader 
        title="Honeypot Detection"
        description="Real-time detection of adversarial profiles, fake candidates, and statistical anomalies."
        badge={<Badge variant="brand">20 Checks</Badge>}
        actions={
          <Button variant="outline" className="h-8 text-xs bg-surface-secondary">Export Threat Log</Button>
        }
      />

      {/* KPI Cards */}
      <motion.div variants={container} className="grid-metrics gap-3">
        <MetricCard label="Honeypots Detected" value={totalDetected.toLocaleString()} icon={<Skull className="w-4 h-4" style={{ color: "#ef4444" }} />} color="#ef4444" />
        <MetricCard label="Violation Flags" value={totalFlags.toLocaleString()} icon={<AlertTriangle className="w-4 h-4" style={{ color: "#f59e0b" }} />} color="#f59e0b" />
        <MetricCard label="Clean Profiles" value={cleanProfiles.toLocaleString()} icon={<CheckCircle2 className="w-4 h-4" style={{ color: "#10b981" }} />} color="#10b981" />
        <MetricCard label="Detection Rate" value={`${detectionRate.toFixed(1)}%`} icon={<Activity className="w-4 h-4" style={{ color: "#6366f1" }} />} color="#6366f1" />
      </motion.div>

      {/* Charts */}
      <div className="grid-charts gap-4">
        {/* Violation breakdown */}
        <motion.div variants={container}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-text-muted" />
                Violation Breakdown
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[clamp(250px,40vh,600px)] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={violationBreakdown} layout="vertical" margin={{ left: 20, right: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                    <YAxis dataKey="name" type="category" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} width={120} />
                    <ReTooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                      {violationBreakdown.map((entry, idx) => (
                        <Cell key={idx} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Risk distribution */}
        <motion.div variants={container}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="w-4 h-4 text-text-muted" />
                Risk Score Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[clamp(250px,40vh,600px)] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <RePieChart>
                    <Pie
                      data={riskDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {riskDistribution.map((entry, idx) => (
                        <Cell key={idx} fill={entry.color} stroke="transparent" />
                      ))}
                    </Pie>
                    <ReTooltip content={<CustomTooltip />} />
                    <Legend
                      wrapperStyle={{ fontSize: "11px" }}
                      formatter={(value: string) => <span style={{ color: "var(--color-text-muted)" }}>{value}</span>}
                    />
                  </RePieChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Multi-hit distribution */}
      <motion.div variants={container}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-text-muted" />
              Multi-Check Flag Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[clamp(250px,40vh,600px)] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={multiHitDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" vertical={false} />
                  <XAxis dataKey="hits" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                  <YAxis tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                  <ReTooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Detection Methods */}
      <motion.div variants={container} className="grid-auto-responsive gap-4">
        <Card>
          <CardContent className="pt-5">
            <h4 className="text-sm font-semibold text-text-primary mb-2">Rule-based Detection</h4>
            <p className="text-xs text-text-muted leading-relaxed">
              20 deterministic checks covering timeline consistency, overlapping education, fictional
              companies, salary anomalies, and career history validation.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <h4 className="text-sm font-semibold text-text-primary mb-2">Statistical Anomaly Detection</h4>
            <p className="text-xs text-text-muted leading-relaxed">
              Z-score based anomaly detection on skill counts, endorsement ratios, timeline smoothness,
              and description uniformity across the candidate pool.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-5">
            <h4 className="text-sm font-semibold text-text-primary mb-2">Behavioral Validation</h4>
            <p className="text-xs text-text-muted leading-relaxed">
              Cross-references skills against career descriptions, detects aspirant language patterns,
              and validates LinkedIn/Redrob profile engagement signals.
            </p>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
