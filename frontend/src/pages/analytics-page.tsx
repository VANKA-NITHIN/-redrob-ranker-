import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import {
  Tooltip as ReTooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
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
  Legend,
  Cell,
} from "recharts"
import { BarChart3, TrendingUp, Activity, Target, Sparkles } from "lucide-react"

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-[8px] border border-border/50 bg-surface shadow-md p-3 text-xs">
        <p className="font-semibold text-text-primary mb-1">{label}</p>
        {payload.map((p: any, i: number) => (
          <p key={i} style={{ color: p.color }}>
            {p.name}: {typeof p.value === "number" ? p.value.toLocaleString() : p.value}
          </p>
        ))}
      </div>
    )
  }
  return null
}

// Score distribution data
const scoreDist = [
  { range: "0.0-0.1", count: 5200 },
  { range: "0.1-0.2", count: 8400 },
  { range: "0.2-0.3", count: 12100 },
  { range: "0.3-0.4", count: 15800 },
  { range: "0.4-0.5", count: 18200 },
  { range: "0.5-0.6", count: 16100 },
  { range: "0.6-0.7", count: 12400 },
  { range: "0.7-0.8", count: 7200 },
  { range: "0.8-0.9", count: 3400 },
  { range: "0.9-1.0", count: 1200 },
]

// Radar data for feature importance
const radarData = [
  { feature: "Career", value: 0.87, fullMark: 1.0 },
  { feature: "Semantic", value: 0.92, fullMark: 1.0 },
  { feature: "Retrieval", value: 0.78, fullMark: 1.0 },
  { feature: "Product", value: 0.71, fullMark: 1.0 },
  { feature: "Behavioral", value: 0.83, fullMark: 1.0 },
  { feature: "Availability", value: 0.65, fullMark: 1.0 },
]

// Experience vs Score scatter data
const scatterData = Array.from({ length: 50 }, () => ({
  experience: 1 + Math.random() * 19,
  score: 0.2 + Math.random() * 0.7,
  count: Math.floor(200 + Math.random() * 1800),
}))

// Processing time trend
const timeTrend = [
  { stage: "Phase 0\nTF-IDF", time: 8.2 },
  { stage: "Phase 1\nFilter", time: 3.5 },
  { stage: "Phase 2\nDeep", time: 42.1 },
  { stage: "Phase 3\nPolish", time: 1.2 },
]

// Skills distribution
const skillData = [
  { skill: "Python", count: 45200, color: "#6366f1" },
  { skill: "Machine Learning", count: 38100, color: "#8b5cf6" },
  { skill: "NLP", count: 22100, color: "#06b6d4" },
  { skill: "Deep Learning", count: 19800, color: "#10b981" },
  { skill: "PyTorch", count: 17200, color: "#f59e0b" },
  { skill: "TensorFlow", count: 15400, color: "#f97316" },
  { skill: "Computer Vision", count: 13100, color: "#ef4444" },
  { skill: "LLM", count: 9800, color: "#ec4899" },
]

export function AnalyticsPage() {
  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.05 } },
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="p-4 sm:p-6 space-y-4 sm:space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <div className="flex items-center gap-2 mb-1">
          <h2 className="text-fluid-section font-semibold text-text-primary">Analytics & Insights</h2>
          <Badge variant="brand">Live</Badge>
        </div>
        <p className="text-fluid-small text-text-muted">Pool-wide statistics, score distributions, and candidate feature analysis.</p>
      </motion.div>

      {/* Score Distribution + Radar Chart */}
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
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={scoreDist}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="range" tick={{ fontSize: 9, fill: "var(--color-text-muted)" }} />
                    <YAxis tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                    <ReTooltip content={<CustomTooltip />} />
                    <Bar dataKey="count" radius={[3, 3, 0, 0]}>
                      {scoreDist.map((entry, idx) => (
                        <Cell
                          key={idx}
                          fill={entry.range.startsWith("0.0") || entry.range.startsWith("0.1") ? "#ef4444" :
                                entry.range.startsWith("0.2") || entry.range.startsWith("0.3") ? "#f59e0b" :
                                entry.range.startsWith("0.4") || entry.range.startsWith("0.5") ? "#06b6d4" :
                                entry.range.startsWith("0.6") ? "#6366f1" :
                                entry.range.startsWith("0.7") ? "#8b5cf6" :
                                "#10b981"}
                        />
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
                Feature Importance Radar
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid stroke="var(--color-border)" />
                    <PolarAngleAxis dataKey="feature" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                    <PolarRadiusAxis angle={30} domain={[0, 1]} tick={{ fontSize: 9, fill: "var(--color-text-muted)" }} />
                    <Radar
                      name="Feature Importance"
                      dataKey="value"
                      stroke="#6366f1"
                      fill="#6366f1"
                      fillOpacity={0.15}
                      strokeWidth={2}
                    />
                    <ReTooltip content={<CustomTooltip />} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Scatter plot + Processing time */}
      <div className="grid-charts gap-4">
        <motion.div variants={container}>
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="w-4 h-4 text-text-muted" />
                Experience vs Score (Density)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 10, right: 20, bottom: 10, left: 10 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="experience" name="Years" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} label={{ value: "Years of Experience", position: "bottom", style: { fontSize: 10, fill: "var(--color-text-muted)" } }} />
                    <YAxis dataKey="score" name="Score" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} domain={[0, 1]} label={{ value: "Score", angle: -90, position: "insideLeft", style: { fontSize: 10, fill: "var(--color-text-muted)" } }} />
                    <ReTooltip content={<CustomTooltip />} />
                    <Scatter data={scatterData} fill="#6366f1" opacity={0.6} />
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
                Processing Pipeline Timing
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={timeTrend}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="stage" tick={{ fontSize: 9, fill: "var(--color-text-muted)" }} />
                    <YAxis tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} label={{ value: "Seconds", angle: -90, position: "insideLeft", style: { fontSize: 10, fill: "var(--color-text-muted)" } }} />
                    <ReTooltip content={<CustomTooltip} /> />
                    <Line type="monotone" dataKey="time" stroke="#6366f1" strokeWidth={2} dot={{ fill: "#6366f1", r: 4 }} activeDot={{ r: 6 }} />
                  </LineChart>
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
              Most Common Skills (Top 8)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="min-h-[200px] sm:min-h-[240px] h-auto">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={skillData} layout="vertical" margin={{ left: 120, right: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis type="number" tick={{ fontSize: 10, fill: "var(--color-text-muted)" }} />
                  <YAxis dataKey="skill" type="category" tick={{ fontSize: 11, fill: "var(--color-text-muted)" }} width={110} />
                  <ReTooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                    {skillData.map((entry, idx) => (
                      <Cell key={idx} fill={entry.color} />
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
