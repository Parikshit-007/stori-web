// MSME Data loaded from CSV
import { MSMEBusiness, MSMEFeatures } from "@/lib/msmeApi"

// CSV columns mapping
export const MSME_CSV_COLUMNS = [
  'business_segment', 'industry_code', 'legal_entity_type', 'business_age_years', 'business_address_verified',
  'geolocation_verified', 'industry_risk_score', 'num_business_locations', 'employees_count', 'gstin_verified',
  'pan_verified', 'msme_registered', 'msme_category', 'business_structure', 'licenses_certificates_score',
  'weekly_gtv', 'monthly_gtv', 'transaction_count_daily', 'avg_transaction_value', 'revenue_concentration_score',
  'peak_day_dependency', 'revenue_growth_rate_mom', 'revenue_growth_rate_qoq', 'profit_margin', 'profit_margin_trend',
  'inventory_turnover_ratio', 'total_assets_value', 'operational_leverage_ratio', 'avg_bank_balance', 'bank_balance_trend',
  'weekly_inflow_outflow_ratio', 'overdraft_days_count', 'overdraft_amount_avg', 'cash_buffer_days', 'avg_daily_closing_balance',
  'cash_balance_std_dev', 'negative_balance_days', 'daily_min_balance_pattern', 'consistent_deposits_score', 'cashflow_regularity_score',
  'receivables_aging_days', 'payables_aging_days', 'bounced_cheques_count', 'bounced_cheques_rate', 'historical_loan_utilization',
  'overdraft_repayment_ontime_ratio', 'previous_defaults_count', 'previous_writeoffs_count', 'current_loans_outstanding', 'total_debt_amount',
  'utility_payment_ontime_ratio', 'utility_payment_days_before_due', 'mobile_recharge_regularity', 'mobile_recharge_ontime_ratio',
  'rent_payment_regularity', 'rent_payment_ontime_ratio', 'supplier_payment_regularity', 'supplier_payment_ontime_ratio',
  'gst_filing_regularity', 'gst_filing_ontime_ratio', 'gst_vs_platform_sales_mismatch', 'outstanding_taxes_amount', 'outstanding_dues_flag',
  'itr_filed', 'itr_income_declared', 'gst_r1_vs_itr_mismatch', 'tax_payment_regularity', 'tax_payment_ontime_ratio',
  'refund_chargeback_rate', 'kyc_completion_score', 'kyc_attempts_count', 'device_consistency_score', 'ip_stability_score',
  'pan_address_bank_mismatch', 'image_ocr_verified', 'shop_image_verified', 'reporting_error_rate', 'incoming_funds_verified',
  'insurance_coverage_score', 'insurance_premium_paid_ratio', 'local_economic_health_score', 'customer_concentration_risk',
  'legal_proceedings_flag', 'legal_disputes_count', 'social_media_presence_score', 'social_media_sentiment_score', 'online_reviews_score',
  'default_90dpd', 'default_probability_true', 'application_date'
]

// Feature categories for form organization
export const MSME_FEATURE_CATEGORIES = {
  business_identity: {
    label: 'A. Business Identity & Registration (10%)',
    fields: [
      { key: 'legal_entity_type', label: 'Legal Entity Type', type: 'select', options: ['proprietorship', 'partnership', 'llp', 'private_limited', 'public_limited', 'trust', 'society'] },
      { key: 'business_age_years', label: 'Business Age (Years)', type: 'number', min: 0, max: 50 },
      { key: 'business_address_verified', label: 'Address Verified', type: 'binary' },
      { key: 'geolocation_verified', label: 'Geolocation Verified', type: 'binary' },
      { key: 'industry_code', label: 'Industry', type: 'select', options: ['manufacturing', 'trading', 'services', 'agriculture', 'construction', 'retail', 'hospitality', 'logistics', 'technology', 'healthcare'] },
      { key: 'industry_risk_score', label: 'Industry Risk Score', type: 'percent' },
      { key: 'num_business_locations', label: 'Number of Locations', type: 'number', min: 1, max: 100 },
      { key: 'employees_count', label: 'Employee Count', type: 'number', min: 0, max: 500 },
      { key: 'gstin_verified', label: 'GSTIN Verified', type: 'binary' },
      { key: 'pan_verified', label: 'PAN Verified', type: 'binary' },
      { key: 'msme_registered', label: 'MSME Registered', type: 'binary' },
      { key: 'msme_category', label: 'MSME Category', type: 'select', options: ['micro', 'small', 'medium', 'not_registered'] },
      { key: 'business_structure', label: 'Business Structure', type: 'select', options: ['home_based', 'shop', 'warehouse', 'office', 'factory', 'multiple'] },
      { key: 'licenses_certificates_score', label: 'Licenses Score', type: 'percent' },
    ]
  },
  revenue_performance: {
    label: 'B. Revenue & Business Performance (20%)',
    fields: [
      { key: 'weekly_gtv', label: 'Weekly GTV (₹)', type: 'currency' },
      { key: 'monthly_gtv', label: 'Monthly GTV (₹)', type: 'currency' },
      { key: 'transaction_count_daily', label: 'Daily Transactions', type: 'number', min: 0, max: 10000 },
      { key: 'avg_transaction_value', label: 'Avg Transaction Value (₹)', type: 'currency' },
      { key: 'revenue_concentration_score', label: 'Revenue Concentration', type: 'percent' },
      { key: 'peak_day_dependency', label: 'Peak Day Dependency', type: 'percent' },
      { key: 'revenue_growth_rate_mom', label: 'MoM Growth Rate', type: 'percent', min: -100, max: 200 },
      { key: 'revenue_growth_rate_qoq', label: 'QoQ Growth Rate', type: 'percent', min: -100, max: 300 },
      { key: 'profit_margin', label: 'Profit Margin', type: 'percent', min: -50, max: 80 },
      { key: 'profit_margin_trend', label: 'Profit Margin Trend', type: 'percent', min: -100, max: 100 },
      { key: 'inventory_turnover_ratio', label: 'Inventory Turnover', type: 'number', min: 0, max: 50 },
      { key: 'total_assets_value', label: 'Total Assets (₹)', type: 'currency' },
      { key: 'operational_leverage_ratio', label: 'Operational Leverage', type: 'number', min: 0, max: 5 },
    ]
  },
  cashflow_banking: {
    label: 'C. Cash Flow & Banking (25%)',
    fields: [
      { key: 'avg_bank_balance', label: 'Avg Bank Balance (₹)', type: 'currency' },
      { key: 'bank_balance_trend', label: 'Balance Trend', type: 'percent', min: -100, max: 100 },
      { key: 'weekly_inflow_outflow_ratio', label: 'Inflow/Outflow Ratio', type: 'number', min: 0, max: 5 },
      { key: 'overdraft_days_count', label: 'Overdraft Days', type: 'number', min: 0, max: 90 },
      { key: 'overdraft_amount_avg', label: 'Avg Overdraft (₹)', type: 'currency' },
      { key: 'cash_buffer_days', label: 'Cash Buffer Days', type: 'number', min: 0, max: 180 },
      { key: 'avg_daily_closing_balance', label: 'Avg Daily Closing (₹)', type: 'currency' },
      { key: 'cash_balance_std_dev', label: 'Balance Std Dev (₹)', type: 'currency' },
      { key: 'negative_balance_days', label: 'Negative Balance Days', type: 'number', min: 0, max: 90 },
      { key: 'daily_min_balance_pattern', label: 'Daily Min Balance (₹)', type: 'currency' },
      { key: 'consistent_deposits_score', label: 'Consistent Deposits', type: 'percent' },
      { key: 'cashflow_regularity_score', label: 'Cash Flow Regularity', type: 'percent' },
      { key: 'receivables_aging_days', label: 'Receivables Aging (Days)', type: 'number', min: 0, max: 180 },
      { key: 'payables_aging_days', label: 'Payables Aging (Days)', type: 'number', min: 0, max: 180 },
    ]
  },
  credit_repayment: {
    label: 'D. Credit & Repayment Behavior (22%)',
    fields: [
      { key: 'bounced_cheques_count', label: 'Bounced Cheques', type: 'number', min: 0, max: 50 },
      { key: 'bounced_cheques_rate', label: 'Bounce Rate', type: 'percent' },
      { key: 'historical_loan_utilization', label: 'Loan Utilization', type: 'percent' },
      { key: 'overdraft_repayment_ontime_ratio', label: 'On-Time Repayment', type: 'percent' },
      { key: 'previous_defaults_count', label: 'Previous Defaults', type: 'number', min: 0, max: 10 },
      { key: 'previous_writeoffs_count', label: 'Previous Write-offs', type: 'number', min: 0, max: 10 },
      { key: 'current_loans_outstanding', label: 'Current Loans', type: 'number', min: 0, max: 20 },
      { key: 'total_debt_amount', label: 'Total Debt (₹)', type: 'currency' },
      { key: 'utility_payment_ontime_ratio', label: 'Utility On-Time', type: 'percent' },
      { key: 'utility_payment_days_before_due', label: 'Utility Days Before Due', type: 'number', min: -30, max: 30 },
      { key: 'mobile_recharge_regularity', label: 'Mobile Regularity', type: 'percent' },
      { key: 'mobile_recharge_ontime_ratio', label: 'Mobile On-Time', type: 'percent' },
      { key: 'rent_payment_regularity', label: 'Rent Regularity', type: 'percent' },
      { key: 'rent_payment_ontime_ratio', label: 'Rent On-Time', type: 'percent' },
      { key: 'supplier_payment_regularity', label: 'Supplier Regularity', type: 'percent' },
      { key: 'supplier_payment_ontime_ratio', label: 'Supplier On-Time', type: 'percent' },
    ]
  },
  compliance_taxation: {
    label: 'E. Compliance & Taxation (12%)',
    fields: [
      { key: 'gst_filing_regularity', label: 'GST Filing Regularity', type: 'percent' },
      { key: 'gst_filing_ontime_ratio', label: 'GST On-Time', type: 'percent' },
      { key: 'gst_vs_platform_sales_mismatch', label: 'GST Mismatch', type: 'percent' },
      { key: 'outstanding_taxes_amount', label: 'Outstanding Taxes (₹)', type: 'currency' },
      { key: 'outstanding_dues_flag', label: 'Outstanding Dues', type: 'binary' },
      { key: 'itr_filed', label: 'ITR Filed', type: 'binary' },
      { key: 'itr_income_declared', label: 'ITR Income (₹)', type: 'currency' },
      { key: 'gst_r1_vs_itr_mismatch', label: 'GST-ITR Mismatch', type: 'percent' },
      { key: 'tax_payment_regularity', label: 'Tax Regularity', type: 'percent' },
      { key: 'tax_payment_ontime_ratio', label: 'Tax On-Time', type: 'percent' },
      { key: 'refund_chargeback_rate', label: 'Refund Rate', type: 'percent' },
    ]
  },
  fraud_verification: {
    label: 'F. Fraud & Verification (7%)',
    fields: [
      { key: 'kyc_completion_score', label: 'KYC Score', type: 'percent' },
      { key: 'kyc_attempts_count', label: 'KYC Attempts', type: 'number', min: 1, max: 10 },
      { key: 'device_consistency_score', label: 'Device Consistency', type: 'percent' },
      { key: 'ip_stability_score', label: 'IP Stability', type: 'percent' },
      { key: 'pan_address_bank_mismatch', label: 'PAN Mismatch', type: 'binary' },
      { key: 'image_ocr_verified', label: 'Image OCR Verified', type: 'binary' },
      { key: 'shop_image_verified', label: 'Shop Image Verified', type: 'binary' },
      { key: 'reporting_error_rate', label: 'Reporting Error Rate', type: 'percent' },
      { key: 'incoming_funds_verified', label: 'Funds Verified', type: 'percent' },
      { key: 'insurance_coverage_score', label: 'Insurance Score', type: 'percent' },
      { key: 'insurance_premium_paid_ratio', label: 'Premium Paid Ratio', type: 'percent' },
    ]
  },
  external_signals: {
    label: 'G. External Signals (4%)',
    fields: [
      { key: 'local_economic_health_score', label: 'Local Economic Health', type: 'percent' },
      { key: 'customer_concentration_risk', label: 'Customer Concentration', type: 'percent' },
      { key: 'legal_proceedings_flag', label: 'Legal Proceedings', type: 'binary' },
      { key: 'legal_disputes_count', label: 'Legal Disputes', type: 'number', min: 0, max: 10 },
      { key: 'social_media_presence_score', label: 'Social Media Presence', type: 'percent' },
      { key: 'social_media_sentiment_score', label: 'Social Sentiment', type: 'percent' },
      { key: 'online_reviews_score', label: 'Online Reviews', type: 'number', min: 0, max: 5 },
    ]
  }
}

// Parse CSV row to MSMEFeatures
export function parseCSVRowToFeatures(row: string[], headers: string[]): MSMEFeatures {
  const features: MSMEFeatures = {}
  
  headers.forEach((header, index) => {
    const value = row[index]
    if (value === '' || value === undefined || value === null) return
    
    // Parse numeric values
    const numericFields = [
      'business_age_years', 'industry_risk_score', 'num_business_locations', 'employees_count',
      'licenses_certificates_score', 'weekly_gtv', 'monthly_gtv', 'transaction_count_daily',
      'avg_transaction_value', 'revenue_concentration_score', 'peak_day_dependency',
      'revenue_growth_rate_mom', 'revenue_growth_rate_qoq', 'profit_margin', 'profit_margin_trend',
      'inventory_turnover_ratio', 'total_assets_value', 'operational_leverage_ratio',
      'avg_bank_balance', 'bank_balance_trend', 'weekly_inflow_outflow_ratio', 'overdraft_days_count',
      'overdraft_amount_avg', 'cash_buffer_days', 'avg_daily_closing_balance', 'cash_balance_std_dev',
      'negative_balance_days', 'daily_min_balance_pattern', 'consistent_deposits_score',
      'cashflow_regularity_score', 'receivables_aging_days', 'payables_aging_days',
      'bounced_cheques_count', 'bounced_cheques_rate', 'historical_loan_utilization',
      'overdraft_repayment_ontime_ratio', 'previous_defaults_count', 'previous_writeoffs_count',
      'current_loans_outstanding', 'total_debt_amount', 'utility_payment_ontime_ratio',
      'utility_payment_days_before_due', 'mobile_recharge_regularity', 'mobile_recharge_ontime_ratio',
      'rent_payment_regularity', 'rent_payment_ontime_ratio', 'supplier_payment_regularity',
      'supplier_payment_ontime_ratio', 'gst_filing_regularity', 'gst_filing_ontime_ratio',
      'gst_vs_platform_sales_mismatch', 'outstanding_taxes_amount', 'itr_income_declared',
      'gst_r1_vs_itr_mismatch', 'tax_payment_regularity', 'tax_payment_ontime_ratio',
      'refund_chargeback_rate', 'kyc_completion_score', 'kyc_attempts_count',
      'device_consistency_score', 'ip_stability_score', 'reporting_error_rate',
      'incoming_funds_verified', 'insurance_coverage_score', 'insurance_premium_paid_ratio',
      'local_economic_health_score', 'customer_concentration_risk', 'legal_disputes_count',
      'social_media_presence_score', 'social_media_sentiment_score', 'online_reviews_score',
      'default_probability_true'
    ]
    
    const binaryFields = [
      'business_address_verified', 'geolocation_verified', 'gstin_verified', 'pan_verified',
      'msme_registered', 'outstanding_dues_flag', 'itr_filed', 'pan_address_bank_mismatch',
      'image_ocr_verified', 'shop_image_verified', 'legal_proceedings_flag', 'default_90dpd'
    ]
    
    const stringFields = [
      'business_segment', 'industry_code', 'legal_entity_type', 'msme_category', 
      'business_structure', 'application_date'
    ]
    
    if (numericFields.includes(header)) {
      const num = parseFloat(value)
      if (!isNaN(num)) {
        (features as any)[header] = num
      }
    } else if (binaryFields.includes(header)) {
      (features as any)[header] = value === '1' || value === '1.0' ? 1 : 0
    } else if (stringFields.includes(header)) {
      (features as any)[header] = value
    }
  })
  
  return features
}

// Parse full CSV to MSME businesses
export function parseCSVToMSMEs(csvContent: string): MSMEBusiness[] {
  const lines = csvContent.trim().split('\n')
  if (lines.length < 2) return []
  
  const headers = lines[0].split(',')
  const msmes: MSMEBusiness[] = []
  
  for (let i = 1; i < lines.length; i++) {
    const row = parseCSVLine(lines[i])
    if (row.length !== headers.length) continue
    
    const features = parseCSVRowToFeatures(row, headers)
    const businessSegmentIdx = headers.indexOf('business_segment')
    const industryIdx = headers.indexOf('industry_code')
    const defaultProbIdx = headers.indexOf('default_probability_true')
    const applicationDateIdx = headers.indexOf('application_date')
    
    const defaultProb = parseFloat(row[defaultProbIdx]) || 0
    const score = Math.round(300 + (1 - defaultProb) * 600) // Convert probability to score
    
    const msme: MSMEBusiness = {
      id: `msme-${i}`,
      businessName: generateBusinessName(row[businessSegmentIdx], row[industryIdx], i),
      businessSegment: row[businessSegmentIdx] || 'micro_established',
      industry: row[industryIdx] || 'trading',
      currentScore: score,
      riskBucket: getRiskBucket(score),
      lastUpdated: row[applicationDateIdx] || new Date().toISOString().split('T')[0],
      features: features,
      prob_default_90dpd: defaultProb,
      summary: {
        financialHealthScore: score,
        riskGrade: getRiskGrade(score),
        maxLoanAmount: calculateMaxLoan(score, features.monthly_gtv || 0),
        probabilityOfDefault: defaultProb * 100,
        recommendation: getRecommendation(score)
      }
    }
    
    msmes.push(msme)
  }
  
  return msmes
}

// Helper function to parse CSV line (handles quoted fields)
function parseCSVLine(line: string): string[] {
  const result: string[] = []
  let current = ''
  let inQuotes = false
  
  for (let i = 0; i < line.length; i++) {
    const char = line[i]
    
    if (char === '"') {
      inQuotes = !inQuotes
    } else if (char === ',' && !inQuotes) {
      result.push(current.trim())
      current = ''
    } else {
      current += char
    }
  }
  result.push(current.trim())
  
  return result
}

// Generate business name from segment and industry
function generateBusinessName(segment: string, industry: string, index: number): string {
  const prefixes: Record<string, string[]> = {
    manufacturing: ['Precision', 'Quality', 'Premier', 'Elite', 'Standard'],
    trading: ['Global', 'National', 'Regional', 'Metro', 'City'],
    services: ['Pro', 'Expert', 'Prime', 'Quick', 'Smart'],
    agriculture: ['Green', 'Farm', 'Agro', 'Harvest', 'Rural'],
    construction: ['Build', 'Construct', 'Foundation', 'Skyline', 'Metro'],
    retail: ['Super', 'Mega', 'Quick', 'Daily', 'Corner'],
    hospitality: ['Grand', 'Royal', 'Golden', 'Classic', 'Heritage'],
    logistics: ['Swift', 'Express', 'Fast', 'Quick', 'Speed'],
    technology: ['Tech', 'Digital', 'Smart', 'Cyber', 'Net'],
    healthcare: ['Care', 'Health', 'Med', 'Life', 'Wellness']
  }
  
  const suffixes: Record<string, string[]> = {
    manufacturing: ['Industries', 'Manufacturing', 'Works', 'Products', 'Enterprises'],
    trading: ['Trading Co.', 'Traders', 'Imports', 'Exports', 'Commerce'],
    services: ['Services', 'Solutions', 'Consultants', 'Associates', 'Partners'],
    agriculture: ['Farms', 'Agri', 'Produce', 'Foods', 'Organics'],
    construction: ['Builders', 'Construction', 'Infra', 'Developers', 'Projects'],
    retail: ['Mart', 'Store', 'Retail', 'Shop', 'Bazaar'],
    hospitality: ['Hotels', 'Resorts', 'Inn', 'Stay', 'Lodge'],
    logistics: ['Logistics', 'Transport', 'Movers', 'Carriers', 'Freight'],
    technology: ['Solutions', 'Systems', 'Soft', 'Labs', 'Tech'],
    healthcare: ['Hospital', 'Clinic', 'Center', 'Labs', 'Diagnostics']
  }
  
  const industryPrefixes = prefixes[industry] || prefixes.trading
  const industrySuffixes = suffixes[industry] || suffixes.trading
  
  const prefix = industryPrefixes[index % industryPrefixes.length]
  const suffix = industrySuffixes[Math.floor(index / industryPrefixes.length) % industrySuffixes.length]
  
  return `${prefix} ${suffix}`
}

function getRiskBucket(score: number): string {
  if (score >= 750) return 'Very Low'
  if (score >= 650) return 'Low'
  if (score >= 550) return 'Medium'
  if (score >= 450) return 'High'
  return 'Very High'
}

function getRiskGrade(score: number): string {
  if (score >= 750) return 'A'
  if (score >= 650) return 'B'
  if (score >= 550) return 'C'
  if (score >= 450) return 'D'
  return 'E'
}

function getRecommendation(score: number): string {
  if (score >= 750) return 'Fast Track Approval'
  if (score >= 650) return 'Approve'
  if (score >= 550) return 'Conditional Approval'
  if (score >= 450) return 'Manual Review'
  return 'Decline'
}

function calculateMaxLoan(score: number, monthlyGTV: number): number {
  const multiplier = score >= 750 ? 3 : score >= 650 ? 2.5 : score >= 550 ? 2 : score >= 450 ? 1.5 : 1
  return Math.round(monthlyGTV * multiplier)
}

// Empty MSME template for form
export function createEmptyMSME(): Partial<MSMEFeatures> {
  return {
    legal_entity_type: 'proprietorship',
    business_age_years: 0,
    business_address_verified: 0,
    geolocation_verified: 0,
    industry_code: 'trading',
    industry_risk_score: 0,
    num_business_locations: 1,
    employees_count: 1,
    gstin_verified: 0,
    pan_verified: 0,
    msme_registered: 0,
    msme_category: 'not_registered',
    business_structure: 'shop',
    licenses_certificates_score: 0,
    weekly_gtv: 0,
    monthly_gtv: 0,
    transaction_count_daily: 0,
    avg_transaction_value: 0,
    revenue_concentration_score: 0,
    peak_day_dependency: 0,
    revenue_growth_rate_mom: 0,
    revenue_growth_rate_qoq: 0,
    profit_margin: 0,
    profit_margin_trend: 0,
    inventory_turnover_ratio: 0,
    total_assets_value: 0,
    operational_leverage_ratio: 0,
    avg_bank_balance: 0,
    bank_balance_trend: 0,
    weekly_inflow_outflow_ratio: 1,
    overdraft_days_count: 0,
    overdraft_amount_avg: 0,
    cash_buffer_days: 0,
    avg_daily_closing_balance: 0,
    cash_balance_std_dev: 0,
    negative_balance_days: 0,
    daily_min_balance_pattern: 0,
    consistent_deposits_score: 0,
    cashflow_regularity_score: 0,
    receivables_aging_days: 0,
    payables_aging_days: 0,
    bounced_cheques_count: 0,
    bounced_cheques_rate: 0,
    historical_loan_utilization: 0,
    overdraft_repayment_ontime_ratio: 0,
    previous_defaults_count: 0,
    previous_writeoffs_count: 0,
    current_loans_outstanding: 0,
    total_debt_amount: 0,
    utility_payment_ontime_ratio: 0,
    utility_payment_days_before_due: 0,
    mobile_recharge_regularity: 0,
    mobile_recharge_ontime_ratio: 0,
    rent_payment_regularity: 0,
    rent_payment_ontime_ratio: 0,
    supplier_payment_regularity: 0,
    supplier_payment_ontime_ratio: 0,
    gst_filing_regularity: 0,
    gst_filing_ontime_ratio: 0,
    gst_vs_platform_sales_mismatch: 0,
    outstanding_taxes_amount: 0,
    outstanding_dues_flag: 0,
    itr_filed: 0,
    itr_income_declared: 0,
    gst_r1_vs_itr_mismatch: 0,
    tax_payment_regularity: 0,
    tax_payment_ontime_ratio: 0,
    refund_chargeback_rate: 0,
    kyc_completion_score: 0,
    kyc_attempts_count: 1,
    device_consistency_score: 0,
    ip_stability_score: 0,
    pan_address_bank_mismatch: 0,
    image_ocr_verified: 0,
    shop_image_verified: 0,
    reporting_error_rate: 0,
    incoming_funds_verified: 0,
    insurance_coverage_score: 0,
    insurance_premium_paid_ratio: 0,
    local_economic_health_score: 0,
    customer_concentration_risk: 0,
    legal_proceedings_flag: 0,
    legal_disputes_count: 0,
    social_media_presence_score: 0,
    social_media_sentiment_score: 0,
    online_reviews_score: 0
  }
}



