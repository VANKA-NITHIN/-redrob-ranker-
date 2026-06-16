import { useState, useMemo } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn, formatScore } from "@/lib/utils"
import {
  Search,
  SlidersHorizontal,
  X,
  MapPin,
  Briefcase,
  Building2,
  GraduationCap,
  Star,
  ExternalLink,
} from "lucide-react"

interface SearchResult {
  id: string
  rank: number
  score: number
  title: string
  company: string
  location: string
  experience: number
  skills: string[]
  badge: "verified" | "suspicious" | "honeypot"
  education: string
  snippet: string
}

const mockResults: SearchResult[] = Array.from({ length: 25 }, (_, i) => ({
  id: `CAND_${String(i + 1).padStart(7, "0")}`,
  rank: i + 1,
  score: 0.95 - i * 0.015,
  title: ["ML Engineer", "Senior AI Engineer", "Data Scientist", "Software Engineer", "Research Scientist"][i % 5],
  company: ["Zomato", "Google", "Microsoft", "Amazon", "LinkedIn", "Uber", "Flipkart", "Razorpay"][i % 8],
  location: ["Bengaluru", "Noida", "Pune", "Hyderabad", "Mumbai", "Delhi"][i % 6],
  experience: 3 + (i % 12),
  skills: [
    ["Python", "PyTorch", "NLP"],
    ["Python", "TensorFlow", "ML Pipelines"],
    ["Python", "Scikit-learn", "Statistics"],
    ["Java", "Python", "System Design"],
    ["Python", "Transformers", "LLMs"],
    ["Python", "PyTorch", "Recommendation Systems"],
    ["Python", "NLP", "Search"],
    ["Python", "Computer Vision", "Deep Learning"],
  ][i % 8],
  badge: i < 20 ? "verified" as const : "suspicious" as const,
  education: ["IIT", "NIT", "IIIT", "BITS Pilani", "DTU", "VIT"][i % 6],
  snippet: `${i % 2 === 0 ? "Built" : "Led"} ${["retrieval", "ranking", "search", "recommendation", "ML"][i % 5]} systems with proven impact on ${["user engagement", "relevance metrics", "search quality", "conversion rates", "model performance"][i % 5]}.`,
}))

const allSkills = Array.from(new Set(mockResults.flatMap((r) => r.skills))).sort()
const allLocations = Array.from(new Set(mockResults.map((r) => r.location))).sort()
const allCompanies = Array.from(new Set(mockResults.map((r) => r.company))).sort()
const allTitles = Array.from(new Set(mockResults.map((r) => r.title))).sort()

export function SearchPage() {
  const [query, setQuery] = useState("")
  const [showFilters, setShowFilters] = useState(false)
  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  const [selectedLocations, setSelectedLocations] = useState<string[]>([])
  const [selectedTitles, setSelectedTitles] = useState<string[]>([])
  const [minScore, setMinScore] = useState(0)
  const [minExperience, setMinExperience] = useState(0)
  const [sortBy, setSortBy] = useState<"score" | "experience" | "name">("score")

  const filtered = useMemo(() => {
    return mockResults
      .filter((r) => {
        if (query) {
          const q = query.toLowerCase()
          if (!r.id.toLowerCase().includes(q) &&
              !r.title.toLowerCase().includes(q) &&
              !r.company.toLowerCase().includes(q) &&
              !r.skills.some((s) => s.toLowerCase().includes(q)) &&
              !r.snippet.toLowerCase().includes(q)) return false
        }
        if (selectedSkills.length && !selectedSkills.some((s) => r.skills.includes(s))) return false
        if (selectedLocations.length && !selectedLocations.includes(r.location)) return false
        if (selectedTitles.length && !selectedTitles.includes(r.title)) return false
        if (r.score < minScore / 100) return false
        if (r.experience < minExperience) return false
        return true
      })
      .sort((a, b) => {
        if (sortBy === "score") return b.score - a.score
        if (sortBy === "experience") return b.experience - a.experience
        return a.id.localeCompare(b.id)
      })
  }, [query, selectedSkills, selectedLocations, selectedTitles, minScore, minExperience, sortBy])

  const toggleFilter = (arr: string[], val: string, setter: (v: string[]) => void) => {
    if (arr.includes(val)) setter(arr.filter((v) => v !== val))
    else setter([...arr, val])
  }

  const activeFilterCount = selectedSkills.length + selectedLocations.length + selectedTitles.length + (minScore > 0 ? 1 : 0) + (minExperience > 0 ? 1 : 0)

  return (
    <div className="p-4 sm:p-6 space-y-4 sm:space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}>
        <h2 className="text-fluid-section font-semibold text-text-primary">Search & Discovery</h2>
        <p className="text-fluid-small text-text-muted mt-0.5">Find candidates across all dimensions and signals.</p>
      </motion.div>

      {/* Search bar */}
      <motion.div
        className="flex flex-col sm:flex-row gap-3"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
      >
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-text-dim" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by candidate ID, title, company, skills, or keywords..."
            className="w-full h-11 pl-10 pr-4 rounded-[12px] border border-border/50 bg-surface text-sm text-text-primary placeholder:text-text-dim focus:outline-none focus:border-brand-300 focus:ring-2 focus:ring-brand-100 transition-all"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-text-dim hover:text-text-muted"
              aria-label="Clear search"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>
        <Button
          variant="outline"
          onClick={() => setShowFilters(!showFilters)}
          className={cn("h-11", activeFilterCount > 0 && "border-brand-300 text-brand-600")}
        >
          <SlidersHorizontal className="w-4 h-4 mr-2" />
          Filters
          {activeFilterCount > 0 && (
            <span className="ml-1.5 w-5 h-5 rounded-full bg-brand-600 text-white text-[10px] font-bold flex items-center justify-center">
              {activeFilterCount}
            </span>
          )}
        </Button>
      </motion.div>

      {/* Filter panel */}
      <AnimatePresence>
        {showFilters && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="overflow-hidden"
          >
            <div className="rounded-[14px] border border-border/50 bg-surface p-4 sm:p-5 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-semibold text-text-primary">Advanced Filters</h3>
                <button
                  onClick={() => {
                    setSelectedSkills([])
                    setSelectedLocations([])
                    setSelectedTitles([])
                    setMinScore(0)
                    setMinExperience(0)
                  }}
                  className="text-xs text-brand-600 hover:text-brand-700 font-medium"
                >
                  Clear all
                </button>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Skills filter */}
                <div className="space-y-2">
                  <h4 className="text-[11px] font-semibold uppercase tracking-wider text-text-muted">Skills</h4>
                  <div className="flex flex-wrap gap-1.5 max-h-[120px] overflow-y-auto">
                    {allSkills.map((skill) => (
                      <button
                        key={skill}
                        onClick={() => toggleFilter(selectedSkills, skill, setSelectedSkills)}
                        className={cn(
                          "px-2 py-1 rounded-[6px] text-[11px] font-medium border transition-all",
                          selectedSkills.includes(skill)
                            ? "bg-brand-100 text-brand-700 border-brand-200"
                            : "bg-surface-secondary text-text-muted border-border/30 hover:bg-surface-tertiary"
                        )}
                      >
                        {skill}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Locations filter */}
                <div className="space-y-2">
                  <h4 className="text-[11px] font-semibold uppercase tracking-wider text-text-muted">Location</h4>
                  <div className="flex flex-wrap gap-1.5 max-h-[120px] overflow-y-auto">
                    {allLocations.map((loc) => (
                      <button
                        key={loc}
                        onClick={() => toggleFilter(selectedLocations, loc, setSelectedLocations)}
                        className={cn(
                          "px-2 py-1 rounded-[6px] text-[11px] font-medium border transition-all",
                          selectedLocations.includes(loc)
                            ? "bg-brand-100 text-brand-700 border-brand-200"
                            : "bg-surface-secondary text-text-muted border-border/30 hover:bg-surface-tertiary"
                        )}
                      >
                        {loc}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Titles filter */}
                <div className="space-y-2">
                  <h4 className="text-[11px] font-semibold uppercase tracking-wider text-text-muted">Title</h4>
                  <div className="flex flex-wrap gap-1.5 max-h-[120px] overflow-y-auto">
                    {allTitles.map((title) => (
                      <button
                        key={title}
                        onClick={() => toggleFilter(selectedTitles, title, setSelectedTitles)}
                        className={cn(
                          "px-2 py-1 rounded-[6px] text-[11px] font-medium border transition-all",
                          selectedTitles.includes(title)
                            ? "bg-brand-100 text-brand-700 border-brand-200"
                            : "bg-surface-secondary text-text-muted border-border/30 hover:bg-surface-tertiary"
                        )}
                      >
                        {title}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Range filters */}
                <div className="space-y-3">
                  <div>
                    <h4 className="text-[11px] font-semibold uppercase tracking-wider text-text-muted mb-1.5">
                      Min Score: {minScore}%
                    </h4>
                    <input
                      type="range"
                      min={0}
                      max={100}
                      step={5}
                      value={minScore}
                      onChange={(e) => setMinScore(Number(e.target.value))}
                      className="w-full h-1.5 rounded-full bg-surface-tertiary appearance-none cursor-pointer accent-brand-600"
                      aria-label="Minimum score threshold"
                    />
                  </div>
                  <div>
                    <h4 className="text-[11px] font-semibold uppercase tracking-wider text-text-muted mb-1.5">
                      Min Experience: {minExperience}yrs
                    </h4>
                    <input
                      type="range"
                      min={0}
                      max={15}
                      step={1}
                      value={minExperience}
                      onChange={(e) => setMinExperience(Number(e.target.value))}
                      className="w-full h-1.5 rounded-full bg-surface-tertiary appearance-none cursor-pointer accent-brand-600"
                      aria-label="Minimum experience threshold"
                    />
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <p className="text-sm text-text-muted">
          <span className="font-semibold text-text-primary">{filtered.length}</span> candidates found
          {query && <span> for "<span className="font-medium">{query}</span>"</span>}
        </p>
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-text-dim uppercase tracking-wider">Sort:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="h-8 px-2 rounded-[6px] border border-border/50 bg-surface-secondary text-xs text-text-primary focus:outline-none"
          >
            <option value="score">Score</option>
            <option value="experience">Experience</option>
            <option value="name">Candidate ID</option>
          </select>
        </div>
      </div>

      {/* Results grid */}
      <div className="grid-auto-responsive gap-3">
        {filtered.map((result, i) => (
          <motion.div
            key={result.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, delay: i * 0.02 }}
          >
            <Card hover>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="font-mono text-xs font-semibold text-text-muted shrink-0">#{result.rank}</span>
                    <span className="font-mono text-sm font-semibold text-text-primary truncate">{result.id}</span>
                    <Badge variant={result.badge} />
                  </div>
                  <span className="font-mono text-sm font-bold text-brand-600 shrink-0 ml-2">
                    {formatScore(result.score)}
                  </span>
                </div>

                <h4 className="text-sm font-semibold text-text-primary truncate">{result.title}</h4>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 text-xs text-text-muted">
                  <span className="flex items-center gap-1"><Building2 className="w-3 h-3" /> {result.company}</span>
                  <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {result.location}</span>
                  <span className="flex items-center gap-1"><Briefcase className="w-3 h-3" /> {result.experience}yrs</span>
                  <span className="flex items-center gap-1"><GraduationCap className="w-3 h-3" /> {result.education}</span>
                </div>

                <p className="text-xs text-text-muted mt-2 line-clamp-2">{result.snippet}</p>

                <div className="flex flex-wrap gap-1 mt-2">
                  {result.skills.map((skill) => (
                    <span key={skill} className="px-1.5 py-0.5 rounded-[4px] text-[10px] font-medium bg-brand-50 text-brand-600 border border-brand-100">
                      {skill}
                    </span>
                  ))}
                </div>

                <div className="flex items-center gap-2 mt-3 pt-3 border-t border-border/25">
                  <Button variant="ghost" size="sm" className="h-8 text-xs flex-1">
                    <Star className="w-3 h-3 mr-1" /> Save
                  </Button>
                  <Button variant="ghost" size="sm" className="h-8 text-xs flex-1">
                    <ExternalLink className="w-3 h-3 mr-1" /> View
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      {filtered.length === 0 && (
        <div className="text-center py-16">
          <div className="w-16 h-16 rounded-[16px] bg-surface-secondary flex items-center justify-center mx-auto mb-4">
            <Search className="w-6 h-6 text-text-dim" />
          </div>
          <h3 className="text-base font-semibold text-text-primary mb-1">No candidates match your search</h3>
          <p className="text-sm text-text-muted max-w-sm mx-auto">
            Try adjusting your filters or search terms to discover more candidates.
          </p>
        </div>
      )}
    </div>
  )
}
