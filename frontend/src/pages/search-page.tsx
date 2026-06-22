import { useState, useEffect, useMemo, useCallback } from "react"
import { PageHeader } from "@/components/layout/page-header"
import { motion, AnimatePresence } from "framer-motion"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn, formatScore } from "@/lib/utils"
import { searchCandidates, type SearchResponse } from "@/lib/api"
import type { RankingEntry } from "@/types"
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
  Loader2,
} from "lucide-react"

export function SearchPage() {
  const [query, setQuery] = useState("")
  const [showFilters, setShowFilters] = useState(false)
  const [selectedSkills, setSelectedSkills] = useState<string[]>([])
  const [selectedLocations, setSelectedLocations] = useState<string[]>([])
  const [selectedTitles, setSelectedTitles] = useState<string[]>([])
  const [minScore, setMinScore] = useState(0)
  const [minExperience, setMinExperience] = useState(0)
  const [sortBy, setSortBy] = useState<"score" | "experience" | "name">("score")
  const [results, setResults] = useState<RankingEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [totalResults, setTotalResults] = useState(0)

  // Debounce search
  const [debouncedQuery, setDebouncedQuery] = useState("")
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedQuery(query), 300)
    return () => clearTimeout(timer)
  }, [query])

  // Fetch data from API
  const doSearch = useCallback(async () => {
    setLoading(true)
    try {
      const resp = await searchCandidates({
        q: debouncedQuery || undefined,
        skills: selectedSkills.length ? selectedSkills.join(",") : undefined,
        location: selectedLocations.length ? selectedLocations[0] : undefined,
        title: selectedTitles.length ? selectedTitles[0] : undefined,
        min_score: minScore > 0 ? minScore / 100 : undefined,
        min_experience: minExperience > 0 ? minExperience : undefined,
        sort: sortBy,
      })
      setResults(resp.results)
      setTotalResults(resp.totalResults)
    } catch (err) {
      console.error("Search failed:", err)
    } finally {
      setLoading(false)
    }
  }, [debouncedQuery, selectedSkills, selectedLocations, selectedTitles, minScore, minExperience, sortBy])

  useEffect(() => {
    doSearch()
  }, [doSearch])

  // Extract unique values for filter chips from results
  const allSkills = useMemo(() => {
    const s = new Set<string>()
    results.forEach(r => (r.skills || []).forEach(sk => s.add(sk)))
    return Array.from(s).sort()
  }, [results])

  const allLocations = useMemo(() => {
    const s = new Set<string>()
    results.forEach(r => { if (r.location) s.add(r.location) })
    return Array.from(s).sort()
  }, [results])

  const allTitles = useMemo(() => {
    const s = new Set<string>()
    results.forEach(r => { if (r.title) s.add(r.title) })
    return Array.from(s).sort()
  }, [results])

  const toggleFilter = (arr: string[], val: string, setter: (v: string[]) => void) => {
    if (arr.includes(val)) setter(arr.filter((v) => v !== val))
    else setter([...arr, val])
  }

  const activeFilterCount = selectedSkills.length + selectedLocations.length + selectedTitles.length + (minScore > 0 ? 1 : 0) + (minExperience > 0 ? 1 : 0)

  return (
    <div className="relative space-y-6 max-w-[2200px] mx-auto min-h-[calc(100vh-3.5rem)] px-[clamp(1rem,3vw,3rem)] py-[clamp(1rem,3vw,2rem)]">
      {/* Background glow */}
      <div className="absolute top-0 right-1/4 w-1/3 h-64 bg-brand-500/10 blur-[120px] rounded-full pointer-events-none -z-10" />

      <PageHeader 
        title="Search & Discovery"
        description="Find candidates across all dimensions and signals."
      />

      {/* Search bar */}
      <motion.div
        className="flex flex-col sm:flex-row gap-3"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
      >
        <div className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-text-dim" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by candidate ID, title, company, skills, or keywords..."
            className="w-full h-12 pl-12 pr-10 rounded-xl border border-border-light bg-surface-secondary/80 backdrop-blur-md text-[14px] text-text-primary placeholder:text-text-dim focus:outline-none focus:border-brand-500/50 shadow-sm transition-all"
          />
          {query && (
            <button
              onClick={() => setQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 w-6 h-6 flex items-center justify-center rounded-full bg-surface-tertiary text-text-dim hover:text-text-primary hover:bg-white/10 transition-colors"
              aria-label="Clear search"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
        <Button
          variant="outline"
          onClick={() => setShowFilters(!showFilters)}
          className={cn("h-12 px-5 bg-surface-secondary/80 backdrop-blur-md border-border-light", activeFilterCount > 0 && "border-brand-500/50 text-brand-400")}
        >
          <SlidersHorizontal className="w-4 h-4 mr-2" />
          Filters
          {activeFilterCount > 0 && (
            <span className="ml-2 w-5 h-5 rounded-full bg-brand-500/20 text-brand-400 text-[10px] font-bold flex items-center justify-center">
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
            <div className="rounded-xl border border-border-light bg-surface/40 backdrop-blur-xl shadow-premium p-5 sm:p-6 space-y-5">
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
                          "px-2.5 py-1.5 rounded-lg text-[11px] font-medium border transition-all duration-200",
                          selectedSkills.includes(skill)
                            ? "bg-brand-500/20 text-brand-300 border-brand-500/30"
                            : "bg-surface-secondary/50 text-text-muted border-transparent hover:bg-white/5 hover:text-text-primary"
                        )}
                      >
                        {skill}
                      </button>
                    ))}
                    {allSkills.length === 0 && <span className="text-[11px] text-text-dim">No skills available</span>}
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
                          "px-2.5 py-1.5 rounded-lg text-[11px] font-medium border transition-all duration-200",
                          selectedLocations.includes(loc)
                            ? "bg-brand-500/20 text-brand-300 border-brand-500/30"
                            : "bg-surface-secondary/50 text-text-muted border-transparent hover:bg-white/5 hover:text-text-primary"
                        )}
                      >
                        {loc}
                      </button>
                    ))}
                    {allLocations.length === 0 && <span className="text-[11px] text-text-dim">No locations</span>}
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
                          "px-2.5 py-1.5 rounded-lg text-[11px] font-medium border transition-all duration-200",
                          selectedTitles.includes(title)
                            ? "bg-brand-500/20 text-brand-300 border-brand-500/30"
                            : "bg-surface-secondary/50 text-text-muted border-transparent hover:bg-white/5 hover:text-text-primary"
                        )}
                      >
                        {title}
                      </button>
                    ))}
                    {allTitles.length === 0 && <span className="text-[11px] text-text-dim">No titles</span>}
                  </div>
                </div>

                {/* Range filters */}
                <div className="space-y-3">
                  <div>
                    <h4 className="text-[11px] font-semibold uppercase tracking-wider text-text-muted mb-2">
                      Min Score: <span className="text-brand-400">{minScore}%</span>
                    </h4>
                    <input
                      type="range"
                      min={0}
                      max={100}
                      step={5}
                      value={minScore}
                      onChange={(e) => setMinScore(Number(e.target.value))}
                      className="w-full h-1.5 rounded-full bg-surface-secondary appearance-none cursor-pointer accent-brand-500"
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
          {loading ? (
            <span className="flex items-center gap-2">
              <Loader2 className="w-3.5 h-3.5 animate-spin" /> Searching...
            </span>
          ) : (
            <>
              <span className="font-semibold text-text-primary">{totalResults}</span> candidates found
              {query && <span> for "<span className="font-medium">{query}</span>"</span>}
            </>
          )}
        </p>
        <div className="flex items-center gap-2">
          <span className="text-[11px] text-text-dim uppercase tracking-wider">Sort:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as typeof sortBy)}
            className="h-8 px-2 rounded-[8px] border border-border-light bg-surface-secondary/80 text-[12px] text-text-primary focus:outline-none focus:border-brand-500/50 shadow-sm transition-all"
          >
            <option value="score">Match Score</option>
            <option value="experience">Experience</option>
            <option value="name">Candidate ID</option>
          </select>
        </div>
      </div>

      {/* Results grid */}
      <div className="grid-auto-responsive gap-3">
        {results.map((result, i) => (
          <motion.div
            key={result.candidateId}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.25, delay: i * 0.02 }}
          >
            <Card hover>
              <CardContent className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="font-mono text-xs font-semibold text-text-muted shrink-0">#{result.rank}</span>
                    <span className="font-mono text-sm font-semibold text-text-primary truncate">{result.candidateId}</span>
                    <Badge variant={result.badge} />
                  </div>
                  <span className="font-mono text-sm font-bold text-brand-600 shrink-0 ml-2">
                    {formatScore(result.score)}
                  </span>
                </div>

                <h4 className="text-sm font-semibold text-text-primary truncate">{result.title || "Candidate"}</h4>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 mt-1 text-xs text-text-muted">
                  {result.company && <span className="flex items-center gap-1"><Building2 className="w-3 h-3" /> {result.company}</span>}
                  {result.location && <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> {result.location}</span>}
                  {result.experience != null && result.experience > 0 && <span className="flex items-center gap-1"><Briefcase className="w-3 h-3" /> {result.experience}yrs</span>}
                  {result.education && <span className="flex items-center gap-1"><GraduationCap className="w-3 h-3" /> {result.education}</span>}
                </div>

                <p className="text-xs text-text-muted mt-2 line-clamp-2">{result.reasoning}</p>

                <div className="flex flex-wrap gap-1 mt-2.5">
                  {(result.skills || []).slice(0, 5).map((skill) => (
                    <span key={skill} className="px-1.5 py-0.5 rounded-[6px] text-[10px] font-medium bg-surface-secondary text-text-muted border border-border-light">
                      {skill}
                    </span>
                  ))}
                </div>

                <div className="flex items-center gap-2 mt-4 pt-3 border-t border-border-light/50">
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

      {!loading && results.length === 0 && (
        <div className="text-center py-24">
          <div className="w-16 h-16 rounded-[16px] bg-surface/50 backdrop-blur-md shadow-premium border border-border-light flex items-center justify-center mx-auto mb-5">
            <Search className="w-6 h-6 text-text-dim" />
          </div>
          <h3 className="text-lg font-bold text-text-primary mb-1">No candidates match your search</h3>
          <p className="text-sm text-text-muted max-w-sm mx-auto">
            Try adjusting your filters, expanding your criteria, or clearing search terms to discover more talent.
          </p>
        </div>
      )}
    </div>
  )
}
