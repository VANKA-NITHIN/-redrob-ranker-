import { motion } from "framer-motion"
import { CheckCircle2, AlertTriangle, Info } from "lucide-react"
import type { ScoreBreakdownProps } from "./score-breakdown-card"

interface ExplainabilityPanelProps {
  scores: ScoreBreakdownProps
  candidateId: string
  currentTitle: string
}

function generateExplanations(scores: ScoreBreakdownProps): { strengths: string[]; concerns: string[] } {
  const strengths: string[] = []
  const concerns: string[] = []

  if (scores.semanticMatch >= 80) strengths.push("Strong semantic alignment with the JD — candidate's profile naturally matches the role requirements.")
  else if (scores.semanticMatch >= 60) strengths.push("Good semantic alignment with the role requirements and responsibilities.")

  if (scores.careerRelevance >= 80) strengths.push("Career history demonstrates relevant AI/ML engineering experience at product companies.")
  else if (scores.careerRelevance >= 60) strengths.push("Career history shows some relevant technical experience.")

  if (scores.retrievalExperience >= 80) strengths.push("Proven experience building retrieval, ranking, or search systems in production.")
  else if (scores.retrievalExperience >= 60) strengths.push("Some exposure to retrieval or ranking systems in past roles.")
  else concerns.push("Limited demonstrated experience with retrieval or ranking systems.")

  if (scores.productExperience >= 80) strengths.push("Strong product-company background — ideal for a founding team role.")
  else if (scores.productExperience >= 60) strengths.push("Some product company experience in the career history.")
  else if (scores.productExperience < 40) concerns.push("Limited product company experience — primarily services or consulting background.")

  if (scores.behavioralScore >= 80) strengths.push("High recruiter engagement signals — responsive, active on the platform, likely to interview.")
  else if (scores.behavioralScore < 50) concerns.push("Low recruiter engagement signals — may be less responsive or active.")

  if (scores.availabilityScore >= 80) strengths.push("Excellent availability — short notice period, open to opportunities, willing to relocate if needed.")
  else if (scores.availabilityScore >= 60) strengths.push("Good availability with reasonable notice period.")
  else concerns.push("Extended notice period may delay potential start date.")

  if (scores.honeypotRisk <= 10) strengths.push("Clean profile with no honeypot indicators detected.")
  else if (scores.honeypotRisk <= 30) concerns.push("Some profile inconsistencies detected — recommend manual review.")
  else concerns.push("Multiple honeypot indicators detected — high risk profile.")

  if (scores.confidenceScore >= 85) strengths.push("High confidence in this ranking — strong profile consistency and supporting evidence.")
  else if (scores.confidenceScore < 60) concerns.push("Lower confidence in this ranking — some information may be incomplete or inconsistent.")

  return { strengths, concerns }
}

export function ExplainabilityPanel({ scores, candidateId, currentTitle }: ExplainabilityPanelProps) {
  const { strengths, concerns } = generateExplanations(scores)

  return (
    <div className="rounded-[14px] border border-border/50 bg-surface p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-text-primary">AI Decision Analysis</h3>
        <Info className="w-3.5 h-3.5 text-text-dim" />
      </div>

      <p className="text-xs text-text-muted">
        Explaining why <span className="font-mono font-medium text-text-primary">{candidateId}</span>
        {currentTitle ? ` (${currentTitle})` : ""} received this ranking score.
      </p>

      {/* Strengths */}
      {strengths.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-success flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5" />
            Why this candidate ranked well
          </h4>
          <div className="space-y-1.5">
            {strengths.map((s, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: i * 0.05 }}
                className="flex items-start gap-2 text-xs text-text-secondary"
              >
                <span className="text-success mt-0.5 shrink-0">✓</span>
                <span>{s}</span>
              </motion.div>
            ))}
          </div>
        </div>
      )}

      {/* Concerns */}
      {concerns.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-xs font-semibold text-warning flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5" />
            Areas to review
          </h4>
          <div className="space-y-1.5">
            {concerns.map((c, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.3, delay: i * 0.05 }}
                className="flex items-start gap-2 text-xs text-text-secondary"
              >
                <span className="text-warning mt-0.5 shrink-0">⚠</span>
                <span>{c}</span>
              </motion.div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
