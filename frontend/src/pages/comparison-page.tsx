import { useState } from "react"
import { motion } from "framer-motion"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn, formatScore } from "@/lib/utils"
import { GitCompare, ArrowUpDown, BarChart3 } from "lucide-react"

interface CandidateCompare {
  id: string
  title: string
  company: string
  experience: number
  score: number
  badge: "verified" | "suspicious" | "honeypot"
  skills: string[]
  location: string
}

const mockCandidates: CandidateCompare[] = [
  {
    id: "CAND_0000010",
    title: "ML Engineer",
    company: "Zomato",
    experience: 7,
    score: 0.1496,
    badge: "verified",
    skills: ["Python", "PyTorch", "Ranking", "Recommendation Systems", "FAISS"],
    location: "Bengaluru",
  },
  {
    id: "CAND_0000048",
    title: "ML Engineer",
    company: "Microsoft",
    experience: 5,
    score: 0.1151,
    badge: "verified",
    skills: ["Python", "TensorFlow", "ML Pipelines", "Azure", "A/B Testing"],
    location: "Hyderabad",
  },
]

export function ComparisonPage() {
  const [candidates] = useState<CandidateCompare[]>(mockCandidates)

  return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6">
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
      >
        <h2 className="text-fluid-section font-semibold text-text-primary">
          Candidate Comparison
        </h2>
        <p className="text-fluid-small text-text-muted mt-0.5">
          Side-by-side comparison of shortlisted candidates
        </p>
      </motion.div>

      {/* Compare bar */}
      {candidates.length === 2 && (
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
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 items-center">
                {/* Candidate 1 */}
                <div className="space-y-3">
                  <div className="text-center">
                    <p className="font-mono font-bold text-text-primary">
                      {candidates[0].id}
                    </p>
                    <Badge variant={candidates[0].badge} className="mt-1" />
                  </div>
                  <div className="space-y-2">
                    {[
                      { label: "Score", value: formatScore(candidates[0].score), color: "text-brand-600" },
                      { label: "Experience", value: `${candidates[0].experience}yrs`, color: "text-text-primary" },
                      { label: "Location", value: candidates[0].location, color: "text-text-muted" },
                    ].map((stat) => (
                      <div key={stat.label} className="flex justify-between text-xs">
                        <span className="text-text-muted">{stat.label}</span>
                        <span className={cn("font-semibold", stat.color)}>{stat.value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Delta */}
                <div className="text-center space-y-2">
                  <ArrowUpDown className="w-6 h-6 mx-auto text-text-dim" />
                  <div className="text-sm font-bold">
                    <span className="text-success">
                      +{formatScore(candidates[0].score - candidates[1].score)}
                    </span>
                  </div>
                  <BarChart3 className="w-5 h-5 mx-auto text-brand-400" />
                </div>

                {/* Candidate 2 */}
                <div className="space-y-3">
                  <div className="text-center">
                    <p className="font-mono font-bold text-text-primary">
                      {candidates[1].id}
                    </p>
                    <Badge variant={candidates[1].badge} className="mt-1" />
                  </div>
                  <div className="space-y-2">
                    {[
                      { label: "Score", value: formatScore(candidates[1].score), color: "text-brand-600" },
                      { label: "Experience", value: `${candidates[1].experience}yrs`, color: "text-text-primary" },
                      { label: "Location", value: candidates[1].location, color: "text-text-muted" },
                    ].map((stat) => (
                      <div key={stat.label} className="flex justify-between text-xs">
                        <span className="text-text-muted">{stat.label}</span>
                        <span className={cn("font-semibold", stat.color)}>{stat.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Skills comparison */}
          <div className="grid-auto-responsive gap-4 mt-4">
            {candidates.map((c, i) => (
              <Card key={c.id}>
                <CardHeader>
                  <CardTitle className="text-sm">{c.id} Skills</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-1.5">
                    {c.skills.map((skill) => (
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
    </div>
  )
}
