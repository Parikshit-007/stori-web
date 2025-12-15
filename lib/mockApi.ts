import { mockConsumers, mockPortfolioStats, featureImportances, personaWeights } from "@/data/mockConsumers"

export interface ScoringRequest {
  consumerId: string
  persona: string
  weights: Record<string, number>
}

export interface ScoringResponse {
  score: number
  prob_default_90dpd: number
  explanation: {
    top_positive: string[]
    top_negative: string[]
  }
  model_version: string
}

export const mockApi = {
  // Get all consumers with optional filters
  getConsumers: async (filters?: {
    search?: string
    persona?: string
    scoreRange?: [number, number]
    riskCategory?: string
  }) => {
    await new Promise((r) => setTimeout(r, 300))

    let results = [...mockConsumers]

    if (filters?.search) {
      const q = filters.search.toLowerCase()
      results = results.filter(
        (c) => c.name.toLowerCase().includes(q) || c.email.toLowerCase().includes(q) || c.phone.includes(q),
      )
    }

    if (filters?.persona) {
      results = results.filter((c) => c.persona === filters.persona)
    }

    if (filters?.scoreRange) {
      const [min, max] = filters.scoreRange
      results = results.filter((c) => {
        // Include unscored consumers (currentScore = 0) if min is 300
        if (c.currentScore === 0) return min <= 300
        return c.currentScore >= min && c.currentScore <= max
      })
    }

    if (filters?.riskCategory) {
      results = results.filter((c) => c.riskBucket === filters.riskCategory)
    }

    return results
  },

  // Get single consumer
  getConsumerById: async (id: string) => {
    await new Promise((r) => setTimeout(r, 200))
    return mockConsumers.find((c) => c.id === id)
  },

  // Send scoring request to GBM model
  // TODO: Replace with real GBM model API
  postScore: async (request: ScoringRequest): Promise<ScoringResponse> => {
    await new Promise((r) => setTimeout(r, 500))

    // Mock GBM response
    return {
      score: Math.round(700 + Math.random() * 200),
      prob_default_90dpd: Math.random() * 0.15,
      explanation: {
        top_positive: ["income_stability", "avg_balance", "good_repayment_history"],
        top_negative: ["high_emi_burden", "recent_inquiries"],
      },
      model_version: "gbm-v1.2.3",
    }
  },

  // Portfolio statistics
  getPortfolioStats: async () => {
    await new Promise((r) => setTimeout(r, 200))
    return mockPortfolioStats
  },

  // Feature importance
  getFeatureImportances: async () => {
    await new Promise((r) => setTimeout(r, 200))
    return featureImportances
  },

  // Persona weights
  getPersonaWeights: async (persona: string) => {
    await new Promise((r) => setTimeout(r, 150))
    return personaWeights[persona as keyof typeof personaWeights]
  },
}
