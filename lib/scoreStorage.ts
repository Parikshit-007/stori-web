// Score Storage Service - Uses localStorage to persist scores
import { MSMEScoreResponse } from './msmeApi'

const STORAGE_KEY = 'msme_scores'

export interface StoredScore {
  msmeId: string
  score: number
  riskCategory: string
  probDefault: number
  recommendation: string
  categoryContributions: Record<string, number>
  scoreResponse: MSMEScoreResponse
  scoredAt: string
  featuresHash: string // To detect if features changed
}

// Generate hash from features to detect changes
function generateFeaturesHash(features: Record<string, any>): string {
  const sortedKeys = Object.keys(features).sort()
  const values = sortedKeys.map(k => `${k}:${features[k]}`)
  // Simple hash - in production use a proper hash function
  let hash = 0
  const str = values.join('|')
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // Convert to 32bit integer
  }
  return hash.toString(16)
}

// Get all stored scores
export function getAllStoredScores(): Record<string, StoredScore> {
  if (typeof window === 'undefined') return {}
  
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : {}
  } catch {
    return {}
  }
}

// Get score for specific MSME
export function getStoredScore(msmeId: string): StoredScore | null {
  const scores = getAllStoredScores()
  return scores[msmeId] || null
}

// Check if score is valid (features haven't changed)
export function isScoreValid(msmeId: string, features: Record<string, any>): boolean {
  const stored = getStoredScore(msmeId)
  if (!stored) return false
  
  const currentHash = generateFeaturesHash(features)
  return stored.featuresHash === currentHash
}

// Save score
export function saveScore(
  msmeId: string, 
  scoreResponse: MSMEScoreResponse, 
  features: Record<string, any>
): void {
  if (typeof window === 'undefined') return
  
  const scores = getAllStoredScores()
  
  const storedScore: StoredScore = {
    msmeId,
    score: scoreResponse.score,
    riskCategory: scoreResponse.risk_category,
    probDefault: scoreResponse.prob_default_90dpd,
    recommendation: scoreResponse.recommended_decision,
    categoryContributions: scoreResponse.category_contributions,
    scoreResponse: scoreResponse,
    scoredAt: new Date().toISOString(),
    featuresHash: generateFeaturesHash(features)
  }
  
  scores[msmeId] = storedScore
  
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(scores))
  } catch (e) {
    console.error('Failed to save score:', e)
  }
}

// Remove score (e.g., when features are updated)
export function removeScore(msmeId: string): void {
  if (typeof window === 'undefined') return
  
  const scores = getAllStoredScores()
  delete scores[msmeId]
  
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(scores))
  } catch (e) {
    console.error('Failed to remove score:', e)
  }
}

// Clear all scores
export function clearAllScores(): void {
  if (typeof window === 'undefined') return
  
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (e) {
    console.error('Failed to clear scores:', e)
  }
}

// Get score with validation
export function getValidScore(msmeId: string, features: Record<string, any>): StoredScore | null {
  if (isScoreValid(msmeId, features)) {
    return getStoredScore(msmeId)
  }
  // Features changed, score is no longer valid
  removeScore(msmeId)
  return null
}



