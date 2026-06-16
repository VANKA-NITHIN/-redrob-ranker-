import { motion, AnimatePresence } from "framer-motion"
import { useState } from "react"
import {
  Search,
  BarChart3,
  UserCheck,
  Clock,
  Shield,
  Brain,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
} from "lucide-react"
import { cn } from "@/lib/utils"

interface TimelineStage {
  id: string
  label: string
  icon: React.ReactNode
  description: string
  detail?: string
  passed?: boolean
}

interface MatchReasoningTimelineProps {
  stages: TimelineStage[]
}

const defaultStages: TimelineStage[] = [
  {
    id: "career",
    label: "Career History Analysis",
    icon: <Search className="w-3.5 h-3.5" />,
    description: "Analyzing job titles, company types, and career progression.",
    detail: "Tier A/B/C title classification, product vs services detection, company quality scoring, career trajectory analysis.",
    passed: true,
  },
  {
    id: "retrieval",
    label: "Retrieval Experience Detection",
    icon: <BarChart3 className="w-3.5 h-3.5" />,
    description: "Detecting search, ranking, retrieval, and recommendation experience.",
    detail: "Latent role classifier scans career descriptions for 120+ signal phrases across 6 role prototypes.",
    passed: true,
  },
  {
    id: "behavioral",
    label: "Behavioral Signals Evaluation",
    icon: <UserCheck className="w-3.5 h-3.5" />,
    description: "Evaluating recruiter engagement, platform activity, and responsiveness.",
    detail: "Recruiter attractiveness score from saved_by_recruiters, search_appearance, and response rates.",
    passed: true,
  },
  {
    id: "availability",
    label: "Availability Assessment",
    icon: <Clock className="w-3.5 h-3.5" />,
    description: "Checking notice period, relocation willingness, and open-to-work status.",
    detail: "Location bonus for Pune/Noida, notice period bonus for sub-30 day notice.",
    passed: true,
  },
  {
    id: "honeypot",
    label: "Honeypot Screening",
    icon: <Shield className="w-3.5 h-3.5" />,
    description: "Running 20 honeypot checks and statistical anomaly detection.",
    detail: "Rule-based checks (timeline, overlapping, fictional companies) + Z-score anomaly detection.",
    passed: true,
  },
  {
    id: "final",
    label: "Final Rank Generated",
    icon: <Brain className="w-3.5 h-3.5" />,
    description: "S-curve optimization applied. Final score computed.",
    detail: "Staged sigmoid transformation applied for NDCG@10 optimization. Generative reasoning added.",
    passed: true,
  },
]

export function MatchReasoningTimeline({ stages = defaultStages }: { stages?: TimelineStage[] }) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  return (
    <div className="rounded-[14px] border border-border/50 bg-surface p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-success" />
          <h3 className="text-sm font-semibold text-text-primary">Match Reasoning Timeline</h3>
        </div>
      </div>

      <div className="relative">
        {/* Vertical line */}
        <div className="absolute left-[15px] top-2 bottom-2 w-px bg-border" aria-hidden="true" />

        <div className="space-y-5">
          {stages.map((stage, i) => {
            const isExpanded = expandedId === stage.id
            return (
              <motion.div
                key={stage.id}
                className="relative pl-10"
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, delay: i * 0.08 }}
              >
                {/* Timeline dot */}
                <div
                  className={cn(
                    "absolute left-2 top-0.5 w-6 h-6 rounded-full flex items-center justify-center border-2 z-10",
                    stage.passed === false
                      ? "border-warning bg-warning/10"
                      : "border-brand-200 bg-brand-50"
                  )}
                >
                  {stage.passed === false ? (
                    <span className="text-warning text-xs">✕</span>
                  ) : (
                    <span className="text-brand-600">{stage.icon}</span>
                  )}
                </div>

                {/* Content */}
                <button
                  onClick={() => setExpandedId(isExpanded ? null : stage.id)}
                  className="w-full text-left group"
                  aria-expanded={isExpanded}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-sm font-medium text-text-primary group-hover:text-brand-600 transition-colors">
                        {stage.label}
                      </span>
                      <p className="text-xs text-text-muted mt-0.5">{stage.description}</p>
                    </div>
                    {stage.detail && (
                      <span className="text-text-dim group-hover:text-text-muted transition-colors mt-0.5">
                        {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                      </span>
                    )}
                  </div>
                </button>

                {/* Expandable detail */}
                <AnimatePresence>
                  {isExpanded && stage.detail && (
                    <motion.div
                      className="mt-2 text-xs text-text-muted bg-surface-secondary rounded-[8px] p-3 border border-border/30"
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      {stage.detail}
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export type { TimelineStage }
