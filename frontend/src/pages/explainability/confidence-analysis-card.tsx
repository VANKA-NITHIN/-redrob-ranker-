import { motion } from "framer-motion"
import { Shield, CheckCircle2, AlertTriangle, Info } from "lucide-react"
import { cn } from "@/lib/utils"
import { RingGauge } from "@/components/ui/ring-gauge"

export interface ConfidenceCheck {
  label: string
  passed: boolean
  detail?: string
}

interface ConfidenceAnalysisCardProps {
  confidenceScore: number
  checks: ConfidenceCheck[]
}

function confidenceLevel(score: number): { label: string; color: string; description: string } {
  if (score >= 85)
    return { label: "High Confidence", color: "#10b981", description: "Strong profile consistency. Strong historical signals. Multiple supporting indicators. No contradictory evidence detected." }
  if (score >= 65)
    return { label: "Moderate Confidence", color: "#f59e0b", description: "Generally consistent profile but some signals are weaker or missing." }
  if (score >= 40)
    return { label: "Low Confidence", color: "#f97316", description: "Several inconsistencies found. Recommend manual verification before proceeding." }
  return { label: "Very Low Confidence", color: "#ef4444", description: "Significant profile inconsistencies detected. High risk of inaccurate ranking." }
}

export function ConfidenceAnalysisCard({ confidenceScore, checks }: ConfidenceAnalysisCardProps) {
  const level = confidenceLevel(confidenceScore)
  const passed = checks.filter((c) => c.passed).length
  const total = checks.length

  return (
    <motion.div
      className="rounded-[14px] border border-border/50 bg-surface p-5 space-y-4"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">Confidence Analysis</h3>
        <Shield className="w-3.5 h-3.5 text-text-dim" />
      </div>

      {/* Score & Level */}
      <div className="flex items-center gap-4">
        <RingGauge value={confidenceScore} size={72} color={level.color} delay={0.1} />

        <div className="space-y-1">
          <span className="text-sm font-semibold" style={{ color: level.color }}>{level.label}</span>
          <p className="text-[11px] text-text-muted leading-relaxed">{level.description}</p>
          <p className="text-[10px] text-text-dim">
            {passed}/{total} checks passed
          </p>
        </div>
      </div>

      {/* Checks */}
      <div className="space-y-2">
        <h4 className="text-xs font-semibold text-text-primary flex items-center gap-1.5">
          <Info className="w-3 h-3" />
          Consistency Checks
        </h4>
        <div className="space-y-1.5">
          {checks.map((check, i) => (
            <motion.div
              key={check.label}
              className="flex items-start gap-2 text-xs"
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.25, delay: i * 0.04 }}
            >
              {check.passed ? (
                <CheckCircle2 className="w-3.5 h-3.5 text-success mt-0.5 shrink-0" />
              ) : (
                <AlertTriangle className="w-3.5 h-3.5 text-warning mt-0.5 shrink-0" />
              )}
              <div>
                <span className={cn("font-medium", check.passed ? "text-text-primary" : "text-warning")}>
                  {check.label}
                </span>
                {!check.passed && check.detail && (
                  <span className="text-text-muted block mt-0.5">{check.detail}</span>
                )}
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  )
}
