import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Shield, CheckCircle2, AlertTriangle, ChevronDown, ChevronRight, Skull } from "lucide-react"
import { cn } from "@/lib/utils"
import { RingGauge } from "@/components/ui/ring-gauge"

export interface HoneypotCheck {
  label: string
  passed: boolean
  detail?: string
}

interface HoneypotRiskCardProps {
  riskScore: number
  checks: HoneypotCheck[]
}

function riskLevel(score: number): { label: string; color: string } {
  if (score <= 10) return { label: "Low Risk", color: "#10b981" }
  if (score <= 30) return { label: "Review", color: "#f59e0b" }
  return { label: "High Risk", color: "#ef4444" }
}

export function HoneypotRiskCard({ riskScore, checks }: HoneypotRiskCardProps) {
  const [expanded, setExpanded] = useState(false)
  const level = riskLevel(riskScore)
  const passed = checks.filter((c) => c.passed).length
  const total = checks.length

  return (
    <motion.div
      className="rounded-[14px] border border-border/50 bg-surface p-5 space-y-4"
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Skull className="w-4 h-4" style={{ color: level.color }} />
          <h3 className="text-sm font-semibold text-text-primary">Honeypot Risk Analysis</h3>
        </div>
        <span
          className="text-[10px] font-semibold uppercase tracking-wider rounded-full px-2 py-0.5 border"
          style={{
            color: level.color,
            borderColor: `${level.color}22`,
            backgroundColor: `${level.color}11`,
          }}
        >
          {level.label}
        </span>
      </div>

      {/* Risk gauge */}
      <div className="flex items-center gap-4">
        <RingGauge value={riskScore} size={72} color={level.color} delay={0.2} />

        <div className="space-y-1">
          <span className="text-sm font-semibold" style={{ color: level.color }}>{level.label}</span>
          <p className="text-[11px] text-text-muted">
            {passed}/{total} checks passed
            {riskScore <= 10 && " — Profile appears clean."}
            {riskScore > 10 && riskScore <= 30 && " — Some anomalies detected, review recommended."}
            {riskScore > 30 && " — Multiple honeypot indicators detected."}
          </p>
        </div>
      </div>

      {/* Expandable checks */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1.5 text-xs text-text-muted hover:text-text-primary transition-colors"
        aria-expanded={expanded}
        aria-label={expanded ? "Collapse consistency checks" : "Expand consistency checks"}
      >
        {expanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
        <span>Consistency Checks</span>
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            className="space-y-2"
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            {checks.map((check, i) => (
              <motion.div
                key={check.label}
                className="flex items-start gap-2 text-xs"
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2, delay: i * 0.03 }}
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
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  )
}
