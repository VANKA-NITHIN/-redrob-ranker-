import { motion } from "framer-motion"
import { RingGauge } from "@/components/ui/ring-gauge"

export interface ScoreBreakdownProps {
  overallMatch: number
  semanticMatch: number
  careerRelevance: number
  retrievalExperience: number
  productExperience: number
  behavioralScore: number
  availabilityScore: number
  honeypotRisk: number
  confidenceScore: number
}

function scoreColor(score: number, isHoneypot = false): string {
  if (isHoneypot) {
    if (score <= 10) return "#10b981"
    if (score <= 30) return "#f59e0b"
    return "#ef4444"
  }
  if (score >= 90) return "#10b981"
  if (score >= 70) return "#3b82f6"
  if (score >= 50) return "#f59e0b"
  return "#ef4444"
}

function scoreLabel(score: number, isHoneypot = false): string {
  if (isHoneypot) {
    if (score <= 10) return "Safe"
    if (score <= 30) return "Review"
    return "High Risk"
  }
  if (score >= 90) return "Excellent"
  if (score >= 70) return "Strong"
  if (score >= 50) return "Moderate"
  return "Weak"
}

function AnimatedGauge({ value, label }: { value: number; label: string }) {
  const color = scoreColor(value)

  return (
    <div className="relative flex flex-col items-center gap-2">
      <RingGauge value={value} size={150} strokeWidth={8} color={color} delay={0.2} />
      <div className="flex flex-col items-center">
        <span className="text-[10px] uppercase tracking-wider text-text-muted font-medium">{label}</span>
        <span className="text-[11px] font-semibold" style={{ color }}>{scoreLabel(value)}</span>
      </div>
    </div>
  )
}

function ScoreRow({ label, score, isHoneypot = false }: { label: string; score: number; isHoneypot?: boolean }) {
  const color = scoreColor(score, isHoneypot)
  return (
    <motion.div
      className="space-y-1"
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center justify-between text-xs">
        <span className="text-text-secondary font-medium">{label}</span>
        <span className="font-mono font-semibold" style={{ color }}>{score}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-surface-tertiary/50 overflow-hidden">
        <motion.div
          className="h-full rounded-full"
          style={{ backgroundColor: color }}
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
    </motion.div>
  )
}

export function ScoreBreakdownCard(props: ScoreBreakdownProps) {
  const items = [
    { label: "Semantic Match", score: props.semanticMatch },
    { label: "Career Relevance", score: props.careerRelevance },
    { label: "Retrieval Experience", score: props.retrievalExperience },
    { label: "Product Experience", score: props.productExperience },
    { label: "Behavioral Score", score: props.behavioralScore },
    { label: "Availability Score", score: props.availabilityScore },
  ]

  return (
    <div className="rounded-[14px] border border-border/50 bg-surface p-4 sm:p-5 space-y-4 sm:space-y-5">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">Score Breakdown</h3>
        <span className="text-[10px] text-text-dim uppercase tracking-wider">All dimensions</span>
      </div>

      <div className="flex justify-center relative">
        <AnimatedGauge value={props.overallMatch} label="Overall Match" size={150} />
      </div>

      <div className="space-y-2.5">
        {items.map((item) => (
          <ScoreRow key={item.label} label={item.label} score={item.score} />
        ))}
        <ScoreRow label="Honeypot Risk" score={props.honeypotRisk} isHoneypot />
        <ScoreRow label="Confidence" score={props.confidenceScore} />
      </div>
    </div>
  )
}
