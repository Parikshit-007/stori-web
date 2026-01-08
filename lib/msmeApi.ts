// MSME API Service - Connects to MSME Credit Scoring Backend
// Using Nginx proxy at https://mycfo.club/stori/api/
const MSME_API_BASE_URL = process.env.NEXT_PUBLIC_MSME_API_URL || 'https://mycfo.club/stori'
const MSME_API_TOKEN = process.env.NEXT_PUBLIC_MSME_API_TOKEN || 'msme_prod_token_67890'

// All features from the CSV - must match backend MSMEFeatureInput model
export interface MSMEFeatures {
  // Business Identity
  legal_entity_type?: string
  business_age_years?: number
  business_address_verified?: number
  geolocation_verified?: number
  industry_code?: string
  industry_risk_score?: number
  num_business_locations?: number
  employees_count?: number
  gstin_verified?: number
  pan_verified?: number
  msme_registered?: number
  msme_category?: string
  business_structure?: string
  licenses_certificates_score?: number
  
  // Revenue & Performance
  weekly_gtv?: number
  monthly_gtv?: number
  transaction_count_daily?: number
  avg_transaction_value?: number
  revenue_concentration_score?: number
  peak_day_dependency?: number
  revenue_growth_rate_mom?: number
  revenue_growth_rate_qoq?: number
  profit_margin?: number
  profit_margin_trend?: number
  inventory_turnover_ratio?: number
  total_assets_value?: number
  operational_leverage_ratio?: number
  
  // Cash Flow & Banking
  avg_bank_balance?: number
  bank_balance_trend?: number
  weekly_inflow_outflow_ratio?: number
  overdraft_days_count?: number
  overdraft_amount_avg?: number
  cash_buffer_days?: number
  avg_daily_closing_balance?: number
  cash_balance_std_dev?: number
  negative_balance_days?: number
  daily_min_balance_pattern?: number
  consistent_deposits_score?: number
  cashflow_regularity_score?: number
  receivables_aging_days?: number
  payables_aging_days?: number
  
  // Credit & Repayment
  bounced_cheques_count?: number
  bounced_cheques_rate?: number
  historical_loan_utilization?: number
  overdraft_repayment_ontime_ratio?: number
  previous_defaults_count?: number
  previous_writeoffs_count?: number
  current_loans_outstanding?: number
  total_debt_amount?: number
  utility_payment_ontime_ratio?: number
  utility_payment_days_before_due?: number
  mobile_recharge_regularity?: number
  mobile_recharge_ontime_ratio?: number
  rent_payment_regularity?: number
  rent_payment_ontime_ratio?: number
  supplier_payment_regularity?: number
  supplier_payment_ontime_ratio?: number
  
  // Compliance & Taxation
  gst_filing_regularity?: number
  gst_filing_ontime_ratio?: number
  gst_vs_platform_sales_mismatch?: number
  outstanding_taxes_amount?: number
  outstanding_dues_flag?: number
  itr_filed?: number
  itr_income_declared?: number
  gst_r1_vs_itr_mismatch?: number
  tax_payment_regularity?: number
  tax_payment_ontime_ratio?: number
  refund_chargeback_rate?: number
  
  // Fraud & Verification
  kyc_completion_score?: number
  kyc_attempts_count?: number
  device_consistency_score?: number
  ip_stability_score?: number
  pan_address_bank_mismatch?: number
  image_ocr_verified?: number
  shop_image_verified?: number
  reporting_error_rate?: number
  incoming_funds_verified?: number
  insurance_coverage_score?: number
  insurance_premium_paid_ratio?: number
  
  // External Signals
  local_economic_health_score?: number
  customer_concentration_risk?: number
  legal_proceedings_flag?: number
  legal_disputes_count?: number
  social_media_presence_score?: number
  social_media_sentiment_score?: number
  online_reviews_score?: number
}

export interface MSMEScoreRequest {
  features: MSMEFeatures
  business_segment?: string
  alpha?: number
  include_explanation?: boolean
}

export interface MSMEScoreResponse {
  score: number
  prob_default_90dpd: number
  risk_category: string
  recommended_decision: string
  model_version: string
  business_segment: string
  component_scores: Record<string, number>
  category_contributions: Record<string, number>
  explanation?: {
    base_value?: number
    top_positive_features?: Array<{ feature: string; shap_value: number; feature_value: number }>
    top_negative_features?: Array<{ feature: string; shap_value: number; feature_value: number }>
    category_contributions?: Record<string, number>
  }
  timestamp: string
}

export interface MSMEBusiness {
  id: string
  businessName: string
  gstin?: string
  pan?: string
  email?: string
  phone?: string
  businessSegment: string
  industry: string
  currentScore?: number
  riskBucket?: string
  lastUpdated?: string
  features: MSMEFeatures
  prob_default_90dpd?: number
  summary?: {
    financialHealthScore: number
    riskGrade: string
    maxLoanAmount: number
    probabilityOfDefault: number
    recommendation: string
  }
  category_contributions?: Record<string, number>
  scoreResponse?: MSMEScoreResponse  // Store full score response for detailed view
}

async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  try {
    const response = await fetch(`${MSME_API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${MSME_API_TOKEN}`,
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
    console.error('MSME API request failed:', error)
    throw error
  }
}

// Valid business segments for the API
const VALID_SEGMENTS = [
  'micro_new', 'micro_established', 'small_trading', 
  'small_manufacturing', 'small_services', 'medium_enterprise'
]

// Normalize segment name to match backend expected values
function normalizeSegment(segment: string): string {
  if (!segment) return 'micro_established'
  
  const normalized = segment.toLowerCase().trim()
  
  // Direct match
  if (VALID_SEGMENTS.includes(normalized)) {
    return normalized
  }
  
  // Try to find partial match
  for (const valid of VALID_SEGMENTS) {
    if (normalized.includes(valid) || valid.includes(normalized)) {
      return valid
    }
  }
  
  // Default fallback
  return 'micro_established'
}

// Helper function to clean features - ONLY numeric fields for the model
// The model only accepts int, float, or bool - NO string fields
function cleanFeatures(features: MSMEFeatures): Record<string, any> {
  const cleaned: Record<string, any> = {}
  
  // ONLY these numeric fields are accepted by the model
  // String fields like industry_code, legal_entity_type, msme_category, business_structure must be EXCLUDED
  const numericFields = [
    'business_age_years', 'business_address_verified', 'geolocation_verified',
    'industry_risk_score', 'num_business_locations', 'employees_count',
    'gstin_verified', 'pan_verified', 'msme_registered', 'licenses_certificates_score',
    'weekly_gtv', 'monthly_gtv', 'transaction_count_daily', 'avg_transaction_value',
    'revenue_concentration_score', 'peak_day_dependency', 'revenue_growth_rate_mom',
    'revenue_growth_rate_qoq', 'profit_margin', 'profit_margin_trend',
    'inventory_turnover_ratio', 'total_assets_value', 'operational_leverage_ratio',
    'avg_bank_balance', 'bank_balance_trend', 'weekly_inflow_outflow_ratio',
    'overdraft_days_count', 'overdraft_amount_avg', 'cash_buffer_days',
    'avg_daily_closing_balance', 'cash_balance_std_dev', 'negative_balance_days',
    'daily_min_balance_pattern', 'consistent_deposits_score', 'cashflow_regularity_score',
    'receivables_aging_days', 'payables_aging_days', 'bounced_cheques_count',
    'bounced_cheques_rate', 'historical_loan_utilization', 'overdraft_repayment_ontime_ratio',
    'previous_defaults_count', 'previous_writeoffs_count', 'current_loans_outstanding',
    'total_debt_amount', 'utility_payment_ontime_ratio', 'utility_payment_days_before_due',
    'mobile_recharge_regularity', 'mobile_recharge_ontime_ratio', 'rent_payment_regularity',
    'rent_payment_ontime_ratio', 'supplier_payment_regularity', 'supplier_payment_ontime_ratio',
    'gst_filing_regularity', 'gst_filing_ontime_ratio', 'gst_vs_platform_sales_mismatch',
    'outstanding_taxes_amount', 'outstanding_dues_flag', 'itr_filed', 'itr_income_declared',
    'gst_r1_vs_itr_mismatch', 'tax_payment_regularity', 'tax_payment_ontime_ratio',
    'refund_chargeback_rate', 'kyc_completion_score', 'kyc_attempts_count',
    'device_consistency_score', 'ip_stability_score', 'pan_address_bank_mismatch',
    'image_ocr_verified', 'shop_image_verified', 'reporting_error_rate',
    'incoming_funds_verified', 'insurance_coverage_score', 'insurance_premium_paid_ratio',
    'local_economic_health_score', 'customer_concentration_risk', 'legal_proceedings_flag',
    'legal_disputes_count', 'social_media_presence_score', 'social_media_sentiment_score',
    'online_reviews_score'
  ]
  
  for (const [key, value] of Object.entries(features)) {
    // ONLY include numeric fields - skip everything else
    if (!numericFields.includes(key)) continue
    
    // Skip undefined, null, empty strings
    if (value === undefined || value === null || value === '') continue
    
    // Convert to number
    const numVal = typeof value === 'string' ? parseFloat(value) : value
    if (!isNaN(numVal)) {
      cleaned[key] = numVal
    }
  }
  
  return cleaned
}

export const msmeApi = {
  // Health check
  healthCheck: async () => {
    return apiRequest<{ status: string; model_loaded: boolean; model_version: string }>('/api/health')
  },

  // Score a business - sends ALL features to backend
  scoreBusiness: async (request: MSMEScoreRequest): Promise<MSMEScoreResponse> => {
    const cleanedFeatures = cleanFeatures(request.features)
    const segment = normalizeSegment(request.business_segment || 'micro_established')
    
    const payload = {
      features: cleanedFeatures,
      business_segment: segment,
      alpha: request.alpha || 0.7,
      include_explanation: request.include_explanation ?? true
    }
    
    return apiRequest<MSMEScoreResponse>('/api/score', {
      method: 'POST',
      body: JSON.stringify(payload),
    })
  },

  // Get business features (stub endpoint)
  getBusinessFeatures: async (businessId: string) => {
    return apiRequest<{ business_id: string; features: MSMEFeatures; business_segment: string }>(
      `/api/features/${businessId}`
    )
  },

  // Get business segments
  getSegments: async () => {
    return apiRequest<{ segments: Record<string, any>; default: string }>('/api/segments')
  },

  // Get categories
  getCategories: async () => {
    return apiRequest<{ categories: Record<string, number>; description: Record<string, string> }>('/api/categories')
  },

  // Get model info
  getModelInfo: async () => {
    return apiRequest<{
      model_version: string
      api_version: string
      available_segments: string[]
      category_weights: Record<string, number>
      score_range: { min: number; max: number }
      risk_buckets: Array<{ range: string; risk: string; decision: string }>
    }>('/api/model/info')
  },

  // Get SHAP explanation for MSME
  explainScore: async (request: MSMEScoreRequest) => {
    const cleanedFeatures = cleanFeatures(request.features)
    const segment = normalizeSegment(request.business_segment || 'micro_established')
    
    return apiRequest<{
      score: number
      risk_category: string
      recommended_decision: string
      top_positive_features: Array<{ feature: string; shap_value: number; feature_value: number }>
      top_negative_features: Array<{ feature: string; shap_value: number; feature_value: number }>
      category_contributions: Record<string, number>
      segment_details: {
        name: string
        weights: Record<string, number>
      }
      timestamp: string
    }>('/api/explain', {
      method: 'POST',
      body: JSON.stringify({
        features: cleanedFeatures,
        business_segment: segment,
        alpha: request.alpha || 0.7,
        include_explanation: true
      }),
    })
  },

  // Score with overdraft recommendation
  scoreWithOverdraft: async (request: MSMEScoreRequest) => {
    const cleanedFeatures = cleanFeatures(request.features)
    const segment = normalizeSegment(request.business_segment || 'micro_established')
    
    return apiRequest<{
      credit_assessment: MSMEScoreResponse
      overdraft_recommendation: {
        eligibility: string
        risk_tier: string
        recommended_limit: number
        interest_rate: number
        tenure_months: number
        emi_amount?: number
        collateral_required: boolean
        collateral_value: number
        processing_fee: number
        dscr: number
        calculation_methods: Record<string, number>
        conditions: string[]
        recommendations: string[]
      }
      timestamp: string
    }>('/api/score-with-overdraft', {
      method: 'POST',
      body: JSON.stringify({
        features: cleanedFeatures,
        business_segment: segment,
        alpha: request.alpha || 0.7,
        include_explanation: request.include_explanation ?? true
      }),
    })
  },
}
