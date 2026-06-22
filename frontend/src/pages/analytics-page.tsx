import { useState, useEffect } from "react"
import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { MetricCardSkeleton, ChartSkeleton } from "@/components/ui/skeleton"
import { getAnalytics } from "@/lib/api"
import {
  Tooltip as ReTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Cell,
} from "recharts"
import { BarChart3, TrendingUp, Activity, Target, Sparkles, AlertTriangle, Loader2 } from "lucide-react"

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

const colors = ["#6366f1", "#8b5cf6", "#06b6d4", "#10b981", "#f59e0b", "#f97316", "#ef4444", "#ec4899",
                "#3b82f6", "#14b8a6", "#a855f7", "#e11d48", "#84cc16", "#0891b2", "#7c3aed"]

interface AnalyticsState {
  scoreDistribution: { range: string; count: number }[]
  experienceDistribution: { range: string; count: number }[]
  topSkills: { skill: string; count: number }[]
  educationTiers: { tier: string; count: number }[]
  penaltyDistribution: { range: string; count: number }[]
  scatterData: { experience: number; score: number }[]
  totalCandidates: number
}

export function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsState | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let ignore = false
    getAnalytics()
      .then((result: any) => {
        if (!ignore) {
          setData(result)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!ignore) {
          setError("Could not load analytics data.")
          setLoading(false)
        }
      })
    return () => { ignore = true }
  }, [])

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.05 } },
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="rounded-[12px] border border-danger/20 bg-danger/5 p-4 flex items-center gap-3">
          <AlertTriangle className="w-4 h-4 text-danger shrink-0" />
          <span className="text-sm text-danger">{error}</span>
        </div>
      </div>
    )
  }

  if (loading || !data) {
    return (
      <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
        <div className="flex items-center gap-3">
          <Loader2 className="w-5 h-5 animate-spin text-brand-500" />
          <p className="text-sm text-text-muted">Computing analytics from candidate data...</p>
        </div>
        <div className="grid-charts gap-4">
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
      </div>
    )
  }

  // Build radar data from education tiers
  const radarData = data.educationTiers.map(t => ({
    feature: t.tier,
    value: t.count,
    fullMark: Math.max(...data.educationTiers.map(x => x.count)),
  }))

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="relative space-y-8 max-w-[2200px] mx-auto min-h-[calc(100vh-3.5rem)] px-[clamp(1rem,3vw,3rem)] py-[clamp(1rem,3vw,2rem)]">
      {/* Background glow */}
      <div className="absolute top-10 left-1/4 w-1/3 h-64 bg-brand-500/10 blur-[120px] rounded-full pointer-events-none -z-10" />
      <PageHeader 
        title="Analytics & Insights"
        description={`Pool-wide statistics from ${data.totalCandidates.toLocaleString()} candidates.`}
        badge={<Badge variant="brand">Live</Badge>}
        actions={
          <Button variant="outline" className="h-8 text-xs bg-surface-secondary">Export Analytics</Button>
        }
      />

      {/* Score Distribution + Education Radar */}
      <div className="grid-charts gap-4">
        <motion.div variants={container}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-text-muted" />
                Score Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[clamp(250px,40vh,600px)] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.scoreDistribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" vertical={false} />
                    <XAxis dataKey="range" tick={{ fontSize: 9, fill: "var(--color-text-muted)" }} />
                    <YAxis tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                    <ReTooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                      {data.scoreDistribution.map((_, idx) => (
                        <Cell key={idx} fill={colors[idx % colors.length]} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={container}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-text-muted" />
                Education Tier Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-72">
                {radarData.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <RadarChart data={radarData}>
                      <PolarGrid stroke="var(--color-border-light)" />
                      <PolarAngleAxis dataKey="feature" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                      <PolarRadiusAxis tick={{ fontSize: 9, fill: "var(--color-text-muted)" }} />
                      <Radar
                        name="Candidates"
                        dataKey="value"
                        stroke="#8b5cf6"
                        fill="#8b5cf6"
                        fillOpacity={0.15}
                        strokeWidth={2}
                      />
                      <ReTooltip content={<CustomTooltip />} />
                    </RadarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex items-center justify-center h-full text-text-muted text-sm">No education data</div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Scatter Plot + Experience Distribution */}
      <div className="grid-charts gap-4">
        <motion.div variants={container}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-4 h-4 text-text-muted" />
                Experience vs Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[clamp(250px,40vh,600px)] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" />
                    <XAxis dataKey="experience" name="Years" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} label={{ value: "Years of Experience", position: "bottom", style: { fontSize: 10, fill: "var(--color-text-muted)" } }} axisLine={false} tickLine={false} />
                    <YAxis dataKey="score" name="Score" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} domain={[0, 1]} label={{ value: "Score", angle: -90, position: "insideLeft", style: { fontSize: 10, fill: "var(--color-text-muted)" } }} axisLine={false} tickLine={false} />
                    <ReTooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3', stroke: 'var(--color-border-hover)' }} />
                    <Scatter data={data.scatterData} fill="#8b5cf6" opacity={0.6} />
                  </ScatterChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={container}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-text-muted" />
                Experience Distribution
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[clamp(250px,40vh,600px)] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={data.experienceDistribution}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" vertical={false} />
                    <XAxis dataKey="range" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                    <YAxis tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                    <ReTooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Skills distribution */}
      <motion.div variants={container}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-text-muted" />
              Most Common Skills (Top {Math.min(data.topSkills.length, 15)})
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-[clamp(250px,40vh,600px)] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.topSkills.slice(0, 15)} layout="vertical" margin={{ left: 120, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border-light)" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                  <YAxis dataKey="skill" type="category" tick={{ fontSize: 11, fill: "var(--color-text-muted)" }} width={110} />
                  <ReTooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {data.topSkills.slice(0, 15).map((_, idx) => (
                      <Cell key={idx} fill={colors[idx % colors.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </motion.div>
  )
}
