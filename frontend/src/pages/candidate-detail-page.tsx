import { useState, useEffect } from "react"
import { PageHeader } from "@/components/layout/page-header"
import { Button } from "@/components/ui/button"
import { motion } from "framer-motion"
import { Badge } from "@/components/ui/badge"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { MetricCard } from "@/components/dashboard/metric-card"
import { ChartSkeleton, MetricCardSkeleton } from "@/components/ui/skeleton"
import { ScoreBreakdownCard, type ScoreBreakdownProps } from "./explainability/score-breakdown-card"
import { getRankings, getCandidateDetails, getScoreBreakdown } from "@/lib/api"
import type { RankingEntry, CandidateDetails, ScoreBreakdown as ScoreBreakdownType } from "@/types"
import {
  MapPin, Briefcase, Building2, GraduationCap, Award,
  Calendar, ChevronRight, ExternalLink, Clock, Star,
  ArrowLeft, Mail, Phone, Globe, CheckCircle2,
  BookOpen, Code2, Layers, Heart,
} from "lucide-react"

function buildScoreProps(breakdown: ScoreBreakdownType): ScoreBreakdownProps {
  const toPct = (v: number) => Math.min(100, Math.max(0, Math.round(v * 100)))
  const invPct = (v: number) => Math.min(100, Math.max(0, Math.round((1 - v) * 100)))
  return {
    overallMatch: toPct(
      breakdown.careerRelevance * 0.25 + breakdown.roleRelevance * 0.18 +
      breakdown.productionAiEvidence * 0.14 + breakdown.retrievalRankingExperience * 0.15 +
      breakdown.experienceFit * 0.05 + breakdown.skillsMatch * 0.03 +
      breakdown.educationScore * 0.03 + breakdown.latentRole * 0.08 +
      breakdown.recruiterAttractiveness * 0.06 + breakdown.startupFit * 0.05
    ),
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

function durationStr(months: number): string {
  if (months >= 12) return `${Math.round(months / 12)}yr${Math.round(months / 12) > 1 ? "s" : ""}`
  return `${months}mo`
}

function dateStr(date: string): string {
  if (!date) return "Present"
  const parts = date.split("-")
  if (parts.length >= 2) {
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    return `${months[parseInt(parts[1]) - 1]} ${parts[0]}`
  }
  return date
}

export function CandidateDetailPage() {
  const [rankings, setRankings] = useState<RankingEntry[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [details, setDetails] = useState<CandidateDetails | null>(null)
  const [breakdown, setBreakdown] = useState<ScoreBreakdownType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let ignore = false
    getRankings()
      .then((data) => {
        if (!ignore) {
          setRankings(data.rankings)
          if (data.rankings.length > 0) setSelectedId(data.rankings[0].candidateId)
        }
      })
      .catch(() => {
        if (!ignore) setError("Could not load candidate data.")
      })
    return () => { ignore = true }
  }, [])

  useEffect(() => {
    if (!selectedId) { setLoading(false); return }
    let ignore = false
    setLoading(true); setError(null)
    Promise.all([getCandidateDetails(selectedId), getScoreBreakdown(selectedId)])
      .then(([det, bd]) => {
        if (!ignore) { setDetails(det); setBreakdown(bd); setLoading(false) }
      })
      .catch(() => {
        if (!ignore) { setError("Could not load candidate details."); setLoading(false) }
      })
    return () => { ignore = true }
  }, [selectedId])

  const scoreProps = breakdown ? buildScoreProps(breakdown) : null
  const profile = details?.profile
  const currentRank = rankings.find((r) => r.candidateId === selectedId)

  if (error) return (
    <div className="p-4 sm:p-6">
      <div className="rounded-[12px] border border-danger/20 bg-danger/5 p-4 flex items-center gap-3">
        <span className="text-sm text-danger">{error}</span>
      </div>
    </div>
  )

  if (loading || !details) return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
      <div className="grid grid-cols-2 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {Array.from({ length: 4 }).map((_, i) => <MetricCardSkeleton key={i} />)}
      </div>
      <ChartSkeleton />
    </div>
  )

  return (
    <div className="relative space-y-6 max-w-[2200px] mx-auto min-h-[calc(100vh-3.5rem)] px-[clamp(1rem,3vw,3rem)] py-[clamp(1rem,3vw,2rem)]">
      {/* Background glow */}
      <div className="absolute top-0 right-1/3 w-1/3 h-64 bg-brand-500/10 blur-[120px] rounded-full pointer-events-none -z-10" />

      <PageHeader 
        title="Candidate Profile"
        description="Detailed review of ranking signals and ML reasoning."
        actions={
          <Button variant="outline" className="h-8 text-xs">Compare Candidate</Button>
        }
      />

      {/* Candidate selector */}
      <div className="flex flex-wrap items-center gap-3 rounded-xl border border-border-light bg-surface/50 backdrop-blur-xl shadow-sm p-2">
        <span className="text-[10px] sm:text-[11px] font-medium text-text-muted uppercase tracking-wider">Candidate:</span>
        <div className="flex flex-wrap gap-1.5 overflow-x-auto">
          {rankings.slice(0, 12).map((c) => (
            <button key={c.candidateId} onClick={() => setSelectedId(c.candidateId)}
              className={`px-3 py-1.5 rounded-[8px] text-[12px] font-medium transition-all duration-300 whitespace-nowrap border ${
                selectedId === c.candidateId
                  ? "bg-white/10 text-text-primary border-border-light shadow-inner-button"
                  : "bg-transparent text-text-muted border-transparent hover:text-text-primary hover:bg-white/5"
              }`}
            >
              <span className="opacity-50 font-normal">#</span>{c.rank} <span className="ml-1 tracking-wider">{c.candidateId.slice(-6)}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Header card */}
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
        className="relative rounded-2xl border border-border-light bg-surface/40 backdrop-blur-xl shadow-premium overflow-hidden"
      >
        <div className="h-24 sm:h-32 bg-gradient-to-r from-brand-500/20 via-brand-400/10 to-transparent border-b border-border-light" />
        <div className="px-4 sm:px-8 pb-6 sm:pb-8 -mt-12 sm:-mt-16">
          <div className="flex flex-col sm:flex-row items-start sm:items-end gap-5">
            <div className="w-20 h-20 sm:w-24 sm:h-24 rounded-2xl bg-surface-secondary shadow-premium flex items-center justify-center border border-border-light z-10 relative overflow-hidden">
              <div className="absolute inset-0 bg-gradient-to-br from-white/10 to-transparent" />
              <span className="text-2xl sm:text-3xl font-bold text-text-primary relative">
                {selectedId?.slice(-4) || "?"}
              </span>
            </div>
            <div className="flex-1 min-w-0 mt-2 sm:mt-0">
              <h2 className="text-xl sm:text-2xl font-bold text-text-primary truncate">{selectedId}</h2>
              <p className="text-sm text-text-secondary truncate mt-0.5">
                {profile?.currentTitle || "Candidate"} <span className="text-text-dim px-1">•</span> {profile?.currentCompany || "No Company"}
              </p>
              <div className="flex flex-wrap items-center gap-3 sm:gap-4 mt-3 text-[13px] text-text-muted">
                <span className="flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5 text-text-dim" /> {profile?.location || "—"}</span>
                <span className="flex items-center gap-1.5"><Briefcase className="w-3.5 h-3.5 text-text-dim" /> {profile?.yearsOfExperience || 0} yrs</span>
                {currentRank && (
                  <Badge variant={currentRank.penalty > 0.5 ? "honeypot" : currentRank.penalty > 0.2 ? "suspicious" : "verified"} className="ml-1">
                    Rank #{currentRank.rank}
                  </Badge>
                )}
              </div>
            </div>
            {currentRank && (
              <div className="hidden sm:flex flex-col items-end gap-0.5 px-5 py-3 rounded-xl border border-border-light bg-surface-secondary/50 backdrop-blur-md shadow-sm">
                <span className="text-3xl font-bold text-brand-400 font-mono tracking-tight">{(currentRank.score * 100).toFixed(1)}</span>
                <span className="text-[10px] text-text-dim uppercase tracking-[0.1em] font-semibold">Match Score</span>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* Main grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Left: profile info */}
        <div className="space-y-4 order-2 lg:order-1">
          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2 text-sm"><Star className="w-4 h-4" /> Signals</CardTitle></CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1"><p className="text-[10px] text-text-dim uppercase tracking-wider">Open to Work</p><p className="text-xs font-semibold">{details.redrobSignals.openToWorkFlag ? "✅ Yes" : "❌ No"}</p></div>
                <div className="space-y-1"><p className="text-[10px] text-text-dim uppercase tracking-wider">Notice Period</p><p className="text-xs font-semibold">{details.redrobSignals.noticePeriodDays}d</p></div>
                <div className="space-y-1"><p className="text-[10px] text-text-dim uppercase tracking-wider">Relocate</p><p className="text-xs font-semibold">{details.redrobSignals.willingToRelocate ? "✅ Yes" : "❌ No"}</p></div>
                <div className="space-y-1"><p className="text-[10px] text-text-dim uppercase tracking-wider">GitHub</p><p className="text-xs font-semibold">{details.redrobSignals.githubActivityScore > 0 ? `${details.redrobSignals.githubActivityScore}` : "—"}</p></div>
                <div className="space-y-1"><p className="text-[10px] text-text-dim uppercase tracking-wider">Response Rate</p><p className="text-xs font-semibold">{(details.redrobSignals.recruiterResponseRate * 100).toFixed(0)}%</p></div>
                <div className="space-y-1"><p className="text-[10px] text-text-dim uppercase tracking-wider">Interview Rate</p><p className="text-xs font-semibold">{(details.redrobSignals.interviewCompletionRate * 100).toFixed(0)}%</p></div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="flex items-center gap-2 text-sm"><BookOpen className="w-4 h-4" /> Summary</CardTitle></CardHeader>
            <CardContent>
              <p className="text-xs text-text-muted leading-relaxed line-clamp-6">{profile?.summary || "No summary available."}</p>
            </CardContent>
          </Card>

          {scoreProps && (
            <div className="hidden lg:block">
              <ScoreBreakdownCard {...scoreProps} />
            </div>
          )}
        </div>

        {/* Center: Career history + Skills */}
        <div className="space-y-4 order-3 lg:order-2 lg:col-span-2">
          {scoreProps && (
            <div className="block lg:hidden">
              <ScoreBreakdownCard {...scoreProps} />
            </div>
          )}

          {/* Career History */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-sm">
                <Briefcase className="w-4 h-4" />
                Career History ({details.careerHistory.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {details.careerHistory.map((job, i) => (
                  <motion.div key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.25, delay: i * 0.04 }}
                    className="flex gap-3 sm:gap-4"
                  >
                    <div className="flex flex-col items-center">
                      <div className="w-2.5 h-2.5 rounded-full bg-brand-200 border-2 border-brand-400 mt-1.5" />
                      {i < details.careerHistory.length - 1 && <div className="w-px flex-1 bg-border mt-1" />}
                    </div>
                    <div className="flex-1 pb-4 min-w-0">
                      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
                        <h4 className="text-sm font-semibold text-text-primary">{job.title}</h4>
                        <span className="text-[10px] text-text-dim flex items-center gap-1 shrink-0">
                          <Calendar className="w-2.5 h-2.5" />
                          {dateStr(job.startDate)} — {job.endDate ? dateStr(job.endDate) : "Present"}
                          {" · "}{durationStr(job.durationMonths)}
                        </span>
                      </div>
                      <div className="flex flex-wrap items-center gap-2 mt-1">
                        <span className="text-xs text-text-secondary flex items-center gap-1">
                          <Building2 className="w-3 h-3" /> {job.company}
                        </span>
                        {job.isCurrent && <span className="text-[10px] text-success bg-success/8 px-1.5 py-0.5 rounded font-medium">Current</span>}
                      </div>
                      {job.description && (
                        <p className="text-xs text-text-muted mt-2 leading-relaxed line-clamp-3">{job.description}</p>
                      )}
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Education + Skills row */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2 text-sm"><GraduationCap className="w-4 h-4" /> Education</CardTitle></CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {details.education.map((edu, i) => (
                    <div key={i} className="text-xs space-y-0.5">
                      <p className="font-semibold text-text-primary">{edu.institution}</p>
                      <p className="text-text-muted">{edu.degree}{edu.fieldOfStudy ? ` in ${edu.fieldOfStudy}` : ""}</p>
                      <p className="text-text-dim">{edu.startYear} — {edu.endYear}{edu.grade ? ` · ${edu.grade}` : ""}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><CardTitle className="flex items-center gap-2 text-sm"><Code2 className="w-4 h-4" /> Skills ({details.skills.length})</CardTitle></CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-1.5">
                  {details.skills.slice(0, 30).map((skill) => (
                    <span key={skill.name}
                      className="inline-flex px-2 py-1 rounded-[6px] text-[10px] sm:text-[11px] font-medium bg-brand-50 text-brand-700 border border-brand-100"
                    >
                      {skill.name}
                      {skill.endorsements > 0 && <span className="ml-1 text-brand-400">·{skill.endorsements}</span>}
                    </span>
                  ))}
                  {details.skills.length > 30 && (
                    <span className="inline-flex px-2 py-1 rounded-[6px] text-[10px] font-medium bg-surface-secondary text-text-muted">
                      +{details.skills.length - 30} more
                    </span>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
