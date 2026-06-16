export interface RankingEntry {
  rank: number
  score: number
  candidateId: string
  reasoning: string
  penalty: number
  issues: string[]
}

export interface CandidateProfile {
  anonymizedName: string
  headline: string
  summary: string
  location: string
  country: string
  yearsOfExperience: number
  currentTitle: string
  currentCompany: string
  currentCompanySize: string
  currentIndustry: string
}

export interface CareerEntry {
  company: string
  title: string
  startDate: string
  endDate: string | null
  durationMonths: number
  isCurrent: boolean
  industry: string
  companySize: string
  description: string
}

export interface EducationEntry {
  institution: string
  degree: string
  fieldOfStudy: string
  startYear: number
  endYear: number
  grade: string
  tier: string
}

export interface SkillEntry {
  name: string
  proficiency: string
  endorsements: number
  durationMonths?: number
}

export interface RedrobSignals {
  profileCompletenessScore: number
  signupDate: string
  lastActiveDate: string
  openToWorkFlag: boolean
  profileViewsReceived30d: number
  applicationsSubmitted30d: number
  recruiterResponseRate: number
  avgResponseTimeHours: number
  connectionCount: number
  endorsementsReceived: number
  noticePeriodDays: number
  expectedSalaryRangeInrLpa: { min: number; max: number }
  preferredWorkMode: string
  willingToRelocate: boolean
  githubActivityScore: number
  searchAppearance30d: number
  savedByRecruiters30d: number
  interviewCompletionRate: number
  offerAcceptanceRate: number
  verifiedEmail: boolean
  verifiedPhone: boolean
  linkedinConnected: boolean
}

export interface CandidateDetails {
  candidateId: string
  profile: CandidateProfile
  careerHistory: CareerEntry[]
  education: EducationEntry[]
  skills: SkillEntry[]
  certifications?: { name: string; issuer: string }[]
  languages?: { language: string; proficiency: string }[]
  redrobSignals: RedrobSignals
}

export interface DashboardMetrics {
  totalCandidates: number
  processingTime: number
  topScore: number
  bottomScore: number
  honeypotCount: number
  suspiciousCount: number
  verifiedCount: number
  source: string
}

export interface ScoreBreakdown {
  careerRelevance: number
  roleRelevance: number
  productionAiEvidence: number
  retrievalRankingExperience: number
  experienceFit: number
  skillsMatch: number
  educationScore: number
  careerProgression: number
  coherence: number
  companyQuality: number
  latentRole: number
  recruiterAttractiveness: number
  startupFit: number
  behavioralMultiplier: number
  locationBonus: number
  noticeBonus: number
  negativePenalty: number
  honeypotPenalty: number
}

export interface AnalyticsData {
  scoreDistribution: { range: string; count: number }[]
  penaltyDistribution: { range: string; count: number }[]
  experienceDistribution: { range: string; count: number }[]
  topSkills: { skill: string; count: number }[]
  educationTiers: { tier: string; count: number }[]
  issueBreakdown: { issue: string; count: number }[]
  countryDistribution: { country: string; count: number }[]
}

export interface HoneypotData {
  totalDetected: number
  totalFlags: number
  cleanProfiles: number
  detectionRate: number
  violationBreakdown: { name: string; count: number; color: string }[]
  riskDistribution: { name: string; value: number; color: string }[]
  multiHitDistribution: { hits: string; count: number }[]
}

export type BadgeType = 'verified' | 'suspicious' | 'honeypot'
