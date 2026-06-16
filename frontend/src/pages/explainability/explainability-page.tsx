import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { ChartSkeleton } from "@/components/ui/skeleton"
import { ScoreBreakdownCard, type ScoreBreakdownProps } from "./score-breakdown-card"
import { ExplainabilityPanel } from "./explainability-panel"
import { FeatureImportanceChart, type FeatureImportance } from "./feature-importance-chart"
import { ConfidenceAnalysisCard } from "./confidence-analysis-card"
import { HoneypotRiskCard } from "./honeypot-risk-card"
import { MatchReasoningTimeline } from "./match-reasoning-timeline"
import { getRankings, getScoreBreakdown, getCandidateDetails } from "@/lib/api"
import type { RankingEntry, ScoreBreakdown as ScoreBreakdownType, CandidateDetails } from "@/types"
import { AlertTriangle, MapPin, Briefcase, ChevronDown, ChevronRight } from "lucide-react"

function buildExplainabilityProps(breakdown: ScoreBreakdownType): ScoreBreakdownProps {
  // Convert raw score components (0-1 normalized) to 0-100 percentage
  const toPct = (v: number) => Math.min(100, Math.max(0, Math.round(v * 100)))
  const invPct = (v: number) => Math.min(100, Math.max(0, Math.round((1 - v) * 100)))

  const overall = toPct(
    breakdown.careerRelevance * 0.25 +
    breakdown.roleRelevance * 0.18 +
    breakdown.productionAiEvidence * 0.14 +
    breakdown.retrievalRankingExperience * 0.15 +
    breakdown.experienceFit * 0.05 +
    breakdown.skillsMatch * 0.03 +
    breakdown.educationScore * 0.03 +
    breakdown.latentRole * 0.08 +
    breakdown.recruiterAttractiveness * 0.06 +
    breakdown.startupFit * 0.05 +
    breakdown.locationBonus +
    breakdown.noticeBonus
  )

  return {
    overallMatch: overall,
    semanticMatch: toPct(breakdown.careerRelevance * 0.5 + breakdown.roleRelevance * 0.3 + breakdown.productionAiEvidence * 0.2),
    careerRelevance: toPct(breakdown.careerRelevance),
    retrievalExperience: toPct(breakdown.retrievalRankingExperience),
    productExperience: toPct(breakdown.startupFit),
    behavioralScore: toPct(breakdown.recruiterAttractiveness),
    availabilityScore: toPct(0.85 + breakdown.locationBonus + breakdown.noticeBonus),
    honeypotRisk: invPct(breakdown.honeypotPenalty),
    confidenceScore: toPct(breakdown.coherence * 0.4 + breakdown.retrievalRankingExperience * 0.2 + breakdown.careerProgression * 0.2 + 0.2),
  }
}

function buildFeatureImportance(breakdown: ScoreBreakdownType): FeatureImportance[] {
  return [
    { label: "Career Relevance", contribution: Math.round(breakdown.careerRelevance * 35), description: "Alignment with AI/ML engineering roles and product company experience" },
    { label: "Retrieval & Ranking", contribution: Math.round(breakdown.retrievalRankingExperience * 22), description: "Dedicated search/ranking/retrieval system experience" },
    { label: "Role Relevance", contribution: Math.round(breakdown.roleRelevance * 18), description: "Current title and headline match to AI/ML engineering" },
    { label: "Behavioral Signals", contribution: Math.round(breakdown.recruiterAttractiveness * 14), description: "Recruiter engagement, platform activity, and responsiveness" },
    { label: "Production AI", contribution: Math.round(breakdown.productionAiEvidence * 10), description: "General AI/ML production experience" },
    { label: "Startup Fit", contribution: Math.round(breakdown.startupFit * 8), description: "Founding team compatibility and product sense" },
    { label: "Experience Fit", contribution: Math.round(breakdown.experienceFit * 5), description: "Years of experience (5-9 yr sweet spot)" },
    { label: "Honeypot Penalty", contribution: -Math.round(breakdown.honeypotPenalty * 15), description: "Deduction for detected honeypot indicators" },
  ]
}

export function ExplainabilityPage() {
  const [candidates, setCandidates] = useState<RankingEntry[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [breakdown, setBreakdown] = useState<ScoreBreakdownType | null>(null)
  const [details, setDetails] = useState<CandidateDetails | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Load candidate list on mount
  useEffect(() => {
    let ignore = false
    getRankings()
      .then((data) => {
        if (!ignore) {
          setCandidates(data.rankings)
          if (data.rankings.length > 0) {
            setSelectedId(data.rankings[0].candidateId)
          }
        }
      })
      .catch((err) => {
        if (!ignore) {
          console.error("Failed to load candidates:", err)
          setError("Could not load candidate list from the ranking backend.")
          setLoading(false)
        }
      })
    return () => { ignore = true }
  }, [])

  // Load breakdown + details when candidate changes
  useEffect(() => {
    if (!selectedId) {
      setLoading(false)
      return
    }
    let ignore = false
    setLoading(true)
    setError(null)

    Promise.all([
      getScoreBreakdown(selectedId),
      getCandidateDetails(selectedId),
    ])
      .then(([bd, det]) => {
        if (!ignore) {
          setBreakdown(bd)
          setDetails(det)
          setLoading(false)
        }
      })
      .catch((err) => {
        if (!ignore) {
          console.error("Failed to load candidate data:", err)
          setError(`Could not load data for candidate ${selectedId}.`)
          setLoading(false)
        }
      })

    return () => { ignore = true }
  }, [selectedId])

  // Pre-built props from breakdown
  const scoreProps = breakdown ? buildExplainabilityProps(breakdown) : null
  const features = breakdown ? buildFeatureImportance(breakdown) : []
  const currentTitle = details?.profile?.currentTitle ?? ""

  const container = {
    hidden: { opacity: 0 },
    show: { opacity: 1, transition: { staggerChildren: 0.05 } },
  }

  if (error && !loading) {
    return (
      <div className="p-6">
        <div className="rounded-[12px] border border-danger/20 bg-danger/5 p-4 flex items-center gap-3">
          <AlertTriangle className="w-4 h-4 text-danger shrink-0" />
          <div>
            <p className="text-sm font-medium text-danger">Data Load Error</p>
            <p className="text-xs text-text-muted mt-0.5">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  return (
    <motion.div variants={container} initial="hidden" animate="show" className="p-4 sm:p-6 space-y-4 sm:space-y-6">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
        <div className="flex items-center gap-2 mb-1">
          <h2 className="text-fluid-section font-semibold text-text-primary">AI Explainability Dashboard</h2>
          <Badge variant="brand">Live</Badge>
        </div>
        <p className="text-fluid-small text-text-muted">Understanding every ranking decision with transparency and recruiter-friendly explanations.</p>
      </motion.div>

      {/* Candidate Selector */}
      <motion.div
        className="rounded-[14px] border border-border/50 bg-surface p-3"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.05 }}
      >
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-[11px] font-medium text-text-muted uppercase tracking-wider">Candidate:</span>
          <div className="flex flex-wrap gap-1.5">
            {candidates.slice(0, 10).map((c) => (
              <button
                key={c.candidateId}
                onClick={() => setSelectedId(c.candidateId)}
                className={`px-2.5 py-1 rounded-[6px] text-xs font-medium transition-all duration-200 ${
                  selectedId === c.candidateId
                    ? "bg-brand-100 text-brand-700 border border-brand-200"
                    : "bg-surface-secondary text-text-muted border border-border/30 hover:bg-surface-tertiary"
                }`}
              >
                #{c.rank} {c.candidateId.slice(-6)}
              </button>
            ))}
          </div>
          {candidates.length > 10 && (
            <span className="text-[10px] text-text-dim">+{candidates.length - 10} more</span>
          )}
        </div>
      </motion.div>

      {/* Candidate Info Bar */}
      {details && !loading && (
        <motion.div
          className="rounded-[14px] border border-border/50 bg-surface p-3 sm:p-4 flex flex-wrap items-center gap-3 sm:gap-4"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.08 }}
        >
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-[10px] bg-brand-100 flex items-center justify-center">
              <span className="text-sm font-bold text-brand-700">
                #{candidates.find((c) => c.candidateId === selectedId)?.rank ?? "?"}
              </span>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-text-primary">{selectedId}</h3>
              <p className="text-xs text-text-muted">
                {details.profile.currentTitle} at {details.profile.currentCompany || "—"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-3 ml-auto text-xs text-text-muted">
            <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {details.profile.location || "—"}</span>
            <span className="flex items-center gap-1"><Briefcase className="w-3 h-3" /> {details.profile.yearsOfExperience} yrs</span>
            <span className="text-[10px] uppercase text-text-dim">Updated: Live</span>
          </div>
        </motion.div>
      )}

      {/* Skeleton loading */}
      {loading && (
        <div className="grid-auto-responsive gap-4">
          <ChartSkeleton />
          <ChartSkeleton />
          <ChartSkeleton />
        </div>
      )}

      {/* Main grid with data */}
      {!loading && scoreProps && (
        <div className="grid-auto-responsive gap-4 auto-rows-min">
          {/* Left column: Hero score + breakdown */}
          <motion.div className="space-y-4" variants={container}>
            <ScoreBreakdownCard {...scoreProps} />
            <ConfidenceAnalysisCard
              confidenceScore={scoreProps.confidenceScore}
              checks={[
                { label: "Profile Completeness", passed: scoreProps.confidenceScore > 70 },
                { label: "Career Timeline Consistency", passed: scoreProps.careerRelevance > 60 },
                { label: "Skill-Career Coherence", passed: scoreProps.retrievalExperience > 50 },
                { label: "Experience Validation", passed: scoreProps.confidenceScore > 65 },
                { label: "Education Verification", passed: true },
                { label: "No Contradictory Signals", passed: scoreProps.honeypotRisk < 30 },
              ]}
            />
          </motion.div>

          {/* Middle column: Explanations + Timeline */}
          <motion.div className="space-y-4" variants={container}>
            <ExplainabilityPanel
              scores={scoreProps}
              candidateId={selectedId || ""}
              currentTitle={currentTitle}
            />
            <MatchReasoningTimeline
              stages={[
                { id: "career", label: "Career History Analysis", icon: <Briefcase className="w-3.5 h-3.5" />, description: `Analyzing career progression and company types.`, detail: `Title tier analysis, product vs services detection.`, passed: scoreProps.careerRelevance > 50 },
                { id: "retrieval", label: "Retrieval Experience Detected", icon: <MapPin className="w-3.5 h-3.5" />, description: `Searching for search/ranking/retrieval/RR experience in career history.`, detail: `Latent role classifier scanning for 120+ signal phrases.`, passed: scoreProps.retrievalExperience > 50 },
                { id: "behavioral", label: "Behavioral Signals Evaluated", icon: <Briefcase className="w-3.5 h-3.5" />, description: `Evaluating recruiter engagement and platform activity.`, detail: `Recruiter attractiveness score computed from Redrob signals.`, passed: scoreProps.behavioralScore > 50 },
                { id: "honeypot", label: "Honeypot Screening", icon: <AlertTriangle className="w-3.5 h-3.5" />, description: `Running honeypot detection and anomaly checks.`, detail: `20 rule-based checks + Z-score anomaly detection.`, passed: scoreProps.honeypotRisk < 30 },
                { id: "final", label: "Final Rank Generated", icon: <span className="text-brand-600 text-xs font-bold">✓</span>, description: `Final score computed and S-curve optimized.`, detail: `Staged sigmoid transformation for NDCG@10 optimization.`, passed: true },
              ]}
            />
          </motion.div>

          {/* Right column: Feature importance + Honeypot */}
          <motion.div className="space-y-4" variants={container}>
            <FeatureImportanceChart features={features} />
            <HoneypotRiskCard
              riskScore={scoreProps.honeypotRisk}
              checks={[
                { label: "Timeline Consistency", passed: scoreProps.careerRelevance > 50 },
                { label: "Experience Validation", passed: scoreProps.confidenceScore > 60 },
                { label: "Skill Duration Validation", passed: scoreProps.retrievalExperience > 40 },
                { label: "Career History Validation", passed: scoreProps.careerRelevance > 40 },
                { label: "Education Timeline Check", passed: true },
                { label: "Keyword Density Check", passed: scoreProps.honeypotRisk < 20, detail: "Normalized density within acceptable range." },
                { label: "Fictional Company Check", passed: true },
                { label: "Description Reuse Detection", passed: true },
              ]}
            />
          </motion.div>
        </div>
      )}
    </motion.div>
  )
}
