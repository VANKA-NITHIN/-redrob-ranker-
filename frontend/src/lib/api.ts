import type {
  RankingEntry,
  CandidateDetails,
  DashboardMetrics,
  ScoreBreakdown,
  AnalyticsData,
  HoneypotData,
} from "@/types"

const BASE_URL = "/api"

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
