import { NextResponse } from 'next/server'
import fs from 'fs'
import path from 'path'
import { MSMEBusiness, MSMEFeatures } from '@/lib/msmeApi'

// Parse CSV row to features - ALL columns from CSV
function parseCSVRowToFeatures(row: string[], headers: string[]): MSMEFeatures {
  const features: MSMEFeatures = {}
  
  // All numeric fields from CSV
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
    'social_media_presence_score', 'social_media_sentiment_score', 'online_reviews_score'
  ]
  
  // Binary fields (0 or 1)
  const binaryFields = [
    'business_address_verified', 'geolocation_verified', 'gstin_verified', 'pan_verified',
    'msme_registered', 'outstanding_dues_flag', 'itr_filed', 'pan_address_bank_mismatch',
    'image_ocr_verified', 'shop_image_verified', 'legal_proceedings_flag'
  ]
  
  // String/categorical fields
  const stringFields = ['legal_entity_type', 'industry_code', 'msme_category', 'business_structure']
  
  headers.forEach((header, index) => {
    const value = row[index]
    if (value === '' || value === undefined || value === null) return
    
    // Skip non-feature columns
    if (['default_90dpd', 'default_probability_true', 'application_date', 'business_segment'].includes(header)) {
      return
    }
    
    if (numericFields.includes(header)) {
      const num = parseFloat(value)
      if (!isNaN(num)) {
        (features as any)[header] = num
      }
    } else if (binaryFields.includes(header)) {
      (features as any)[header] = value === '1' || value === '1.0' || parseFloat(value) >= 0.5 ? 1 : 0
    } else if (stringFields.includes(header)) {
      (features as any)[header] = value
    }
  })
  
  return features
}

// Parse CSV line handling quotes
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

// Generate business name
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

export async function GET() {
  try {
    // Try to read the CSV file
    const csvPath = path.join(process.cwd(), 'credit_scoring_pipeline', 'msme', 'msme_synthetic_data.csv')
    
    if (!fs.existsSync(csvPath)) {
      return NextResponse.json([])
    }
    
    const csvContent = fs.readFileSync(csvPath, 'utf-8')
    const lines = csvContent.trim().split('\n')
    
    if (lines.length < 2) {
      return NextResponse.json([])
    }
    
    const headers = parseCSVLine(lines[0])
    const msmes: MSMEBusiness[] = []
    
    // Load first 100 rows for performance
    const maxRows = Math.min(lines.length, 101)
    
    for (let i = 1; i < maxRows; i++) {
      const row = parseCSVLine(lines[i])
      if (row.length !== headers.length) continue
      
      const features = parseCSVRowToFeatures(row, headers)
      
      const businessSegmentIdx = headers.indexOf('business_segment')
      const industryIdx = headers.indexOf('industry_code')
      const applicationDateIdx = headers.indexOf('application_date')
      
      // DON'T pre-calculate scores - leave them undefined
      // Scores should only come from actual API call
      const msme: MSMEBusiness = {
        id: `msme-${i}`,
        businessName: generateBusinessName(row[businessSegmentIdx], row[industryIdx], i),
        businessSegment: row[businessSegmentIdx] || 'micro_established',
        industry: row[industryIdx] || 'trading',
        // NO currentScore - will be undefined until scored
        // NO riskBucket - will be undefined until scored
        // NO summary - will be undefined until scored
        lastUpdated: row[applicationDateIdx] || new Date().toISOString().split('T')[0],
        features: features,
      }
      
      msmes.push(msme)
    }
    
    return NextResponse.json(msmes)
  } catch (error) {
    console.error('Error loading MSME data:', error)
    return NextResponse.json([])
  }
}
