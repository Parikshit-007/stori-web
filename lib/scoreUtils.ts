// Score Utility Functions - Convert between different scoring scales

/**
 * Convert MSME score from 300-900 scale to 0-100 scale
 * @param score Score on 300-900 scale
 * @returns Score on 0-100 scale
 */
export function convertScoreTo100(score: number): number {
  if (score < 300) return 0
  if (score > 900) return 100
  
  // Linear interpolation: 300-900 → 0-100
  // Formula: (score - 300) / (900 - 300) * 100
  return Math.round(((score - 300) / 600) * 100)
}

/**
 * Convert score from 0-100 scale to 300-900 scale
 * @param score Score on 0-100 scale
 * @returns Score on 300-900 scale
 */
export function convertScoreFrom100(score: number): number {
  if (score < 0) return 300
  if (score > 100) return 900
  
  // Linear interpolation: 0-100 → 300-900
  // Formula: (score / 100) * 600 + 300
  return Math.round((score / 100) * 600 + 300)
}

/**
 * Get risk category from 0-100 score
 * @param score Score on 0-100 scale
 * @returns Risk category string
 */
export function getRiskCategoryFrom100Score(score: number): string {
  if (score >= 85) return 'Very Low'
  if (score >= 70) return 'Low'
  if (score >= 50) return 'Medium'
  if (score >= 30) return 'High'
  return 'Very High'
}

/**
 * Get risk category from 300-900 score
 * @param score Score on 300-900 scale
 * @returns Risk category string
 */
export function getRiskCategoryFrom900Score(score: number): string {
  if (score >= 750) return 'Very Low'
  if (score >= 650) return 'Low'
  if (score >= 550) return 'Medium'
  if (score >= 450) return 'High'
  return 'Very High'
}

/**
 * Get recommendation based on 0-100 score
 * @param score Score on 0-100 scale
 * @returns Recommendation string
 */
export function getRecommendation(score: number): string {
  if (score >= 80) return 'Approve'
  if (score >= 60) return 'Approve with Conditions'
  if (score >= 40) return 'Manual Review'
  if (score >= 20) return 'High Risk - Detailed Review Required'
  return 'Reject'
}

/**
 * Get score color class based on 0-100 score
 * @param score Score on 0-100 scale
 * @returns Tailwind CSS color class
 */
export function getScoreColor(score: number): string {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-blue-600'
  if (score >= 40) return 'text-yellow-600'
  if (score >= 20) return 'text-orange-600'
  return 'text-red-600'
}

/**
 * Get score background color class based on 0-100 score
 * @param score Score on 0-100 scale
 * @returns Tailwind CSS background color class
 */
export function getScoreBgColor(score: number): string {
  if (score >= 80) return 'bg-green-50 border-green-200'
  if (score >= 60) return 'bg-blue-50 border-blue-200'
  if (score >= 40) return 'bg-yellow-50 border-yellow-200'
  if (score >= 20) return 'bg-orange-50 border-orange-200'
  return 'bg-red-50 border-red-200'
}

