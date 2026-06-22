import type {
  RankingEntry,
  CandidateDetails,
  DashboardMetrics,
  ScoreBreakdown,
  AnalyticsData,
  HoneypotData,
} from "@/types"

// Point to the deployed backend API on HuggingFace
const BASE_URL = "https://vankanithin-redrob-ranker.hf.space/api"

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`)
  if (!res.ok) {
    throw new Error(`API error: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

export interface RankingResponse {
  rankings: RankingEntry[]
  metrics: DashboardMetrics
}

export async function getRankings(): Promise<RankingResponse> {
  return fetchJSON<RankingResponse>("/rankings")
}

export async function getCandidateDetails(
  id: string
): Promise<CandidateDetails> {
  return fetchJSON<CandidateDetails>(`/candidates/${id}`)
}

export async function getScoreBreakdown(
  id: string
): Promise<ScoreBreakdown> {
  return fetchJSON<ScoreBreakdown>(`/candidates/${id}/breakdown`)
}

export async function getAnalytics(): Promise<AnalyticsData> {
  return fetchJSON<AnalyticsData>("/analytics")
}

export async function runRanking(source?: string): Promise<RankingResponse> {
  const params = source ? `?source=${encodeURIComponent(source)}` : ""
  return fetchJSON<RankingResponse>(`/run${params}`)
}

export async function getHoneypotData(): Promise<HoneypotData> {
  return fetchJSON<HoneypotData>("/honeypot")
}

export interface SearchParams {
  q?: string
  skills?: string
  location?: string
  title?: string
  min_score?: number
  min_experience?: number
  sort?: "score" | "experience" | "name"
}

export interface SearchResponse {
  results: RankingEntry[]
  totalResults: number
}

export async function searchCandidates(params: SearchParams): Promise<SearchResponse> {
  const searchParams = new URLSearchParams()
  if (params.q) searchParams.set("q", params.q)
  if (params.skills) searchParams.set("skills", params.skills)
  if (params.location) searchParams.set("location", params.location)
  if (params.title) searchParams.set("title", params.title)
  if (params.min_score) searchParams.set("min_score", String(params.min_score))
  if (params.min_experience) searchParams.set("min_experience", String(params.min_experience))
  if (params.sort) searchParams.set("sort", params.sort)
  const qs = searchParams.toString()
  return fetchJSON<SearchResponse>(`/search${qs ? `?${qs}` : ""}`)
}

export interface CompareResponse {
  candidates: Array<{
    candidateId: string
    rank: number
    score: number
    badge: string
    title: string
    company: string
    location: string
    experience: number
    skills: string[]
    breakdown: ScoreBreakdown
    profile: CandidateDetails["profile"]
  }>
}

export async function compareCandidates(ids: string[]): Promise<CompareResponse> {
  return fetchJSON<CompareResponse>(`/compare?ids=${ids.join(",")}`)
}

export async function getHealth(): Promise<{ status: string; version: string }> {
  return fetchJSON<{ status: string; version: string }>("/health")
}
