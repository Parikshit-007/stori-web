// Mock MSME Data - Fallback when CSV is not available
import { MSMEBusiness, MSMEFeatures } from './msmeApi'

// Generate mock MSME businesses for development
export function generateMockMSMEs(count: number = 50): MSMEBusiness[] {
  const segments = ['micro_new', 'micro_established', 'small_trading', 'small_manufacturing', 'small_services', 'medium_enterprise']
  const industries = ['manufacturing', 'trading', 'services', 'retail', 'logistics', 'agriculture']
  const entities = ['proprietorship', 'partnership', 'llp', 'private_limited']
  
  const businesses: MSMEBusiness[] = []
  
  for (let i = 1; i <= count; i++) {
    const segment = segments[i % segments.length]
    const industry = industries[i % industries.length]
    const entity = entities[i % entities.length]
    
    const features: MSMEFeatures = {
      business_age_years: 1 + (i % 10),
      legal_entity_type: entity,
      industry_code: industry,
      business_address_verified: i % 2,
      geolocation_verified: i % 3 === 0 ? 1 : 0,
      gstin_verified: i % 2,
      pan_verified: 1,
      msme_registered: i % 3 === 0 ? 1 : 0,
      msme_category: i % 2 === 0 ? 'micro' : 'small',
      business_structure: 'shop',
      
      weekly_gtv: 100000 + (i * 50000),
      monthly_gtv: 400000 + (i * 200000),
      transaction_count_daily: 10 + (i % 100),
      avg_transaction_value: 1000 + (i * 100),
      
      revenue_growth_rate_mom: 0.05 + (i % 10) * 0.01,
      revenue_growth_rate_qoq: 0.1 + (i % 10) * 0.02,
      profit_margin: 0.05 + (i % 20) * 0.01,
      
      avg_bank_balance: 100000 + (i * 10000),
      cash_buffer_days: 30 + (i % 60),
      negative_balance_days: i % 5,
      weekly_inflow_outflow_ratio: 1.0 + (i % 10) * 0.1,
      
      overdraft_repayment_ontime_ratio: 0.8 + (i % 20) * 0.01,
      bounced_cheques_count: i % 3,
      previous_defaults_count: i % 4 === 0 ? 1 : 0,
      current_loans_outstanding: i % 2,
      
      gst_filing_regularity: 0.8 + (i % 20) * 0.01,
      gst_filing_ontime_ratio: 0.85 + (i % 15) * 0.01,
      itr_filed: i % 2,
      
      kyc_completion_score: 0.8 + (i % 20) * 0.01,
      device_consistency_score: 0.7 + (i % 30) * 0.01,
      ip_stability_score: 0.75 + (i % 25) * 0.01,
    }
    
    const businessNames = [
      'Precision Industries', 'Global Trading Co.', 'Pro Services', 'Quality Manufacturing',
      'Super Mart', 'Swift Logistics', 'Green Farms', 'Tech Solutions', 'Care Hospital',
      'Build Constructions', 'Royal Hotels', 'Metro Retail', 'Express Transport',
      'Standard Products', 'Prime Consultants', 'National Imports', 'Smart Systems',
      'Elite Enterprises', 'Quick Store', 'Daily Bazaar', 'Regional Traders',
      'Expert Associates', 'Premier Works', 'City Commerce', 'Speed Carriers',
      'Harvest Foods', 'Digital Labs', 'Life Clinic', 'Foundation Builders'
    ]
    
    businesses.push({
      id: `msme-${i}`,
      businessName: `${businessNames[i % businessNames.length]} ${Math.floor(i / businessNames.length) + 1}`,
      businessSegment: segment,
      industry: industry,
      lastUpdated: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      features: features,
      // No scores - must be generated
      currentScore: undefined,
      riskBucket: undefined,
      prob_default_90dpd: undefined,
      summary: undefined,
      category_contributions: undefined,
      scoreResponse: undefined
    })
  }
  
  return businesses
}

// For use in API route when CSV fails
export const FALLBACK_MSME_COUNT = 100

