import { useState, useEffect } from "react"
import { PageHeader } from "@/components/layout/page-header"
import { motion } from "framer-motion"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { MetricCardSkeleton } from "@/components/ui/skeleton"
import { cn, formatScore } from "@/lib/utils"
import { getRankings, compareCandidates, type CompareResponse } from "@/lib/api"
import type { RankingEntry } from "@/types"
import { GitCompare, ArrowUpDown, BarChart3, Loader2, Plus, X } from "lucide-react"

export function ComparisonPage() {
  const [rankings, setRankings] = useState<RankingEntry[]>([])
  const [selectedIds, setSelectedIds] = useState<string[]>([])
  const [compareData, setCompareData] = useState<CompareResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [comparing, setComparing] = useState(false)

  // Load rankings for the selector
  useEffect(() => {
    let ignore = false
    getRankings()
      .then((data) => {
        if (!ignore) {
          setRankings(data.rankings)
          // Auto-select top 2
          if (data.rankings.length >= 2) {
            const top2 = [data.rankings[0].candidateId, data.rankings[1].candidateId]
            setSelectedIds(top2)
          }
          setLoading(false)
        }
      })
      .catch(() => {
        if (!ignore) setLoading(false)
      })
    return () => { ignore = true }
  }, [])

  // Compare whenever selectedIds changes
  useEffect(() => {
    if (selectedIds.length < 2) {
      setCompareData(null)
      return
    }
    let ignore = false
    setComparing(true)
    compareCandidates(selectedIds)
      .then((data) => {
        if (!ignore) {
          setCompareData(data)
          setComparing(false)
        }
      })
      .catch(() => {
        if (!ignore) setComparing(false)
      })
    return () => { ignore = true }
  }, [selectedIds])

  const toggleCandidate = (id: string) => {
    setSelectedIds(prev => {
      if (prev.includes(id)) return prev.filter(x => x !== id)
      if (prev.length >= 3) return prev // max 3
      return [...prev, id]
    })
  }

  if (loading) {
    return (
      <div className="p-4 sm:p-6 space-y-4">
        <div className="grid-metrics gap-3">
          {Array.from({ length: 4 }).map((_, i) => <MetricCardSkeleton key={i} />)}
        </div>
      </div>
    )
  }

  const candidates = compareData?.candidates || []

  return (
    <div className="relative space-y-4 sm:space-y-6 max-w-[2200px] mx-auto min-h-[calc(100vh-3.5rem)] px-[clamp(1rem,3vw,3rem)] py-[clamp(1rem,3vw,2rem)]">
      <PageHeader 
        title="Candidate Comparison"
        description="Select up to 3 candidates for side-by-side comparison"
        actions={
          <Button variant="outline" className="h-8 text-xs bg-surface-secondary">Reset Selection</Button>
        }
      />

      {/* Candidate selector */}
      <div className="flex flex-wrap items-center gap-2 rounded-[14px] border border-border/50 bg-surface p-3">
        <span className="text-[10px] sm:text-[11px] font-medium text-text-muted uppercase tracking-wider">Select:</span>
        <div className="flex flex-wrap gap-1.5 overflow-x-auto">
          {rankings.slice(0, 15).map((c) => (
            <button
              key={c.candidateId}
              onClick={() => toggleCandidate(c.candidateId)}
              className={cn(
                "px-2 py-1 rounded-[6px] text-[11px] sm:text-xs font-medium transition-all duration-200 whitespace-nowrap",
                selectedIds.includes(c.candidateId)
                  ? "bg-brand-100 text-brand-700 border border-brand-200"
                  : "bg-surface-secondary text-text-muted border border-border/30 hover:bg-surface-tertiary"
              )}
            >
              #{c.rank} {c.candidateId.slice(-6)}
              {selectedIds.includes(c.candidateId) && <X className="w-3 h-3 ml-1 inline" />}
            </button>
          ))}
        </div>
      </div>

      {comparing && (
        <div className="flex items-center gap-2 text-sm text-text-muted">
          <Loader2 className="w-4 h-4 animate-spin" /> Computing comparison...
        </div>
      )}

      {/* Score comparison */}
      {candidates.length >= 2 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <GitCompare className="w-4 h-4 text-brand-500" />
                Score Comparison
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={cn("grid gap-4 items-start", candidates.length === 2 ? "grid-cols-1 sm:grid-cols-3" : "grid-cols-1 sm:grid-cols-3 lg:grid-cols-4")}>
                {candidates.map((c, i) => (
                  <div key={c.candidateId} className="space-y-3">
                    <div className="text-center">
                      <p className="font-mono font-bold text-text-primary">
                        {c.candidateId}
                      </p>
                      <p className="text-xs text-text-muted mt-0.5">{c.title}{c.company ? ` at ${c.company}` : ""}</p>
                      <Badge variant={c.badge as any} className="mt-1" />
                    </div>
                    <div className="space-y-2">
                      {[
                        { label: "Score", value: formatScore(c.score), color: "text-brand-600" },
                        { label: "Rank", value: `#${c.rank}`, color: "text-text-primary" },
                        { label: "Experience", value: `${c.experience}yrs`, color: "text-text-primary" },
                        { label: "Location", value: c.location || "—", color: "text-text-muted" },
                      ].map((stat) => (
                        <div key={stat.label} className="flex justify-between text-xs">
                          <span className="text-text-muted">{stat.label}</span>
                          <span className={cn("font-semibold", stat.color)}>{stat.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}

                {candidates.length === 2 && (
                  <div className="text-center space-y-2">
                    <ArrowUpDown className="w-6 h-6 mx-auto text-text-dim" />
                    <div className="text-sm font-bold">
                      <span className="text-success">
                        +{formatScore(Math.abs(candidates[0].score - candidates[1].score))}
                      </span>
                    </div>
                    <BarChart3 className="w-5 h-5 mx-auto text-brand-400" />
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Score breakdown comparison */}
          <Card className="mt-4">
            <CardHeader>
              <CardTitle className="text-sm">Score Dimension Comparison</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  "careerRelevance", "roleRelevance", "productionAiEvidence",
                  "retrievalRankingExperience", "experienceFit", "skillsMatch",
                  "educationScore", "recruiterAttractiveness", "startupFit",
                ].map((dim) => (
                  <div key={dim} className="space-y-1">
                    <p className="text-[11px] font-medium text-text-muted capitalize">
                      {dim.replace(/([A-Z])/g, " $1").trim()}
                    </p>
                    <div className="flex gap-2">
                      {candidates.map((c) => {
                        const val = (c.breakdown as any)?.[dim] ?? 0
                        return (
                          <div key={c.candidateId} className="flex-1">
                            <div className="h-2 bg-surface-tertiary rounded-full overflow-hidden">
                              <motion.div
                                className="h-full bg-brand-500 rounded-full"
                                initial={{ width: 0 }}
                                animate={{ width: `${Math.min(100, val * 100)}%` }}
                                transition={{ duration: 0.5 }}
                              />
                            </div>
                            <p className="text-[10px] text-text-dim mt-0.5 text-right">
                              {c.candidateId.slice(-4)}: {(val * 100).toFixed(0)}%
                            </p>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Skills comparison */}
          <div className="grid-auto-responsive gap-4 mt-4">
            {candidates.map((c) => (
              <Card key={c.candidateId}>
                <CardHeader>
                  <CardTitle className="text-sm">{c.candidateId} Skills</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-1.5">
                    {(c.skills || []).map((skill) => (
                      <span
                        key={skill}
                        className="inline-flex px-2 py-1 rounded-[6px] text-[11px] font-medium bg-brand-50 text-brand-700 border border-brand-100"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </motion.div>
      )}

      {selectedIds.length < 2 && !comparing && (
        <div className="text-center py-16">
          <div className="w-16 h-16 rounded-[16px] bg-surface-secondary flex items-center justify-center mx-auto mb-4">
            <GitCompare className="w-6 h-6 text-text-dim" />
          </div>
          <h3 className="text-base font-semibold text-text-primary mb-1">Select at least 2 candidates</h3>
          <p className="text-sm text-text-muted max-w-sm mx-auto">
            Click on candidate chips above to add them to the comparison.
          </p>
        </div>
      )}
    </div>
  )
}
