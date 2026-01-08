// Consumer API Service - Connects to Consumer Credit Scoring Backend
const CONSUMER_API_BASE_URL = process.env.NEXT_PUBLIC_CONSUMER_API_URL || 'http://localhost:8000'
const CONSUMER_API_TOKEN = process.env.NEXT_PUBLIC_CONSUMER_API_TOKEN || 'dev_token_12345'

// Feature input interface matching backend FeatureInput model
export interface ConsumerFeatures {
  // Identity & Demographics
  name_dob_verified?: number
  phone_verified?: number
  phone_age_months?: number
  email_verified?: number
  email_age_months?: number
  location_stability_score?: number
  location_tier?: string
  education_level?: number
  employment_tenure_months?: number
  employment_type?: string
  
  // Income & Cashflow
  monthly_income?: number
  income_growth_rate?: number
  avg_account_balance?: number
  min_account_balance?: number
  income_stability_score?: number
  income_variance_coefficient?: number
  itr_filed?: number
  itr_income_declared?: number
  employability_score?: number
  ppf_balance?: number
  gov_schemes_enrolled?: number
  
  // Assets & Liabilities
  total_assets_value?: number
  liquid_assets_ratio?: number
  property_ownership?: number
  vehicle_ownership?: number
  gold_holdings_value?: number
  total_liabilities?: number
  debt_to_income_ratio?: number
  emi_burden_ratio?: number
  
  // Behavioral Signals
  transaction_frequency?: number
  avg_transaction_amount?: number
  savings_rate?: number
  budgeting_score?: number
  spending_regularity?: number
  cash_vs_digital_ratio?: number
  
  // Credit & Repayment
  credit_history_length_months?: number
  num_active_loans?: number
  num_closed_loans?: number
  repayment_ontime_ratio?: number
  credit_card_utilization?: number
  num_credit_inquiries_6m?: number
  num_credit_inquiries_12m?: number
  default_history_count?: number
  
  // Fraud & Verification
  kyc_completion_score?: number
  device_consistency_score?: number
  ip_stability_score?: number
  pan_address_bank_mismatch?: number
  face_match_score?: number
  
  // Transactions & Utility
  utility_payment_ontime_ratio?: number
  utility_payment_days_before_due?: number
  mobile_recharge_regularity?: number
  mobile_recharge_ontime_ratio?: number
  rent_payment_regularity?: number
  rent_payment_ontime_ratio?: number
  
  // Family & Dependents
  marital_status?: string
  num_dependents?: number
  family_income?: number
  spouse_employment?: number
}

export interface ExplainRequest {
  features: ConsumerFeatures
  persona?: string
  top_n?: number
}

export interface ExplainResponse {
  score: number
  top_positive_features: Array<{ feature: string; shap_value: number; feature_value: number }>
  top_negative_features: Array<{ feature: string; shap_value: number; feature_value: number }>
  category_contributions: Record<string, number>
  persona_details: {
    name: string
    category_weights: Record<string, number>
  }
  timestamp: string
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const response = await fetch(`${CONSUMER_API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${CONSUMER_API_TOKEN}`,
        ...options.headers,
      },
    })

    if (!response.ok) {
      const errorText = await response.text()
      console.error('API Error Response:', errorText)
      throw new Error(`API error: ${response.status} - ${errorText}`)
    }

    return await response.json()
  } catch (error) {
    console.error('Consumer API request failed:', error)
    throw error
  }
}

export const consumerApi = {
  // Health check
  healthCheck: async () => {
    return apiRequest<{ status: string; model_loaded: boolean; model_version: string }>('/api/health')
  },

  // Get SHAP explanation for a consumer
  explainScore: async (request: ExplainRequest): Promise<ExplainResponse> => {
    const payload = {
      features: request.features,
      persona: request.persona || 'salaried_professional',
      top_n: request.top_n || 10
    }
    
    return apiRequest<ExplainResponse>('/api/explain', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },

  // Get model info
  getModelInfo: async () => {
    return apiRequest<{
      model_version: string
      api_version: string
      available_personas: string[]
      category_weights: Record<string, number>
      score_range: { min: number; max: number }
      alpha_default: number
    }>('/api/model/info')
  },
}

