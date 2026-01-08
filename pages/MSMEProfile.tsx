"use client"
import { useState, useEffect } from "react"
import { useParams, useRouter } from "next/navigation"
import { msmeApi, MSMEBusiness, MSMEScoreResponse } from "@/lib/msmeApi"
import { getValidScore, saveScore } from "@/lib/scoreStorage"
import { convertScoreTo100 } from "@/lib/scoreUtils"
import { ArrowLeft, FileText, Zap, Loader2 } from "lucide-react"
import Link from "next/link"
import BusinessIdentityCard from "@/components/msme/BusinessIdentityCard"
import RevenuePerformanceCard from "@/components/msme/RevenuePerformanceCard"
import CashflowBankingCard from "@/components/msme/CashflowBankingCard"
import CreditRepaymentCard from "@/components/msme/CreditRepaymentCard"
import ComplianceTaxationCard from "@/components/msme/ComplianceTaxationCard"
import FraudVerificationCard from "@/components/msme/FraudVerificationCard"
import ExternalSignalsCard from "@/components/msme/ExternalSignalsCard"
import MSMESummaryCard from "@/components/msme/MSMESummaryCard"
import DirectorDetailsCard from "@/components/msme/DirectorDetailsCard"
import { downloadMSMEPDF } from "@/components/msme/MSMEPDFReport"

export default function MSMEProfile() {
  const params = useParams<{ id: string }>()
  const router = useRouter()
  const id = params?.id
  const [msme, setMsme] = useState<MSMEBusiness | null>(null)
  const [loading, setLoading] = useState(true)
  const [scoring, setScoring] = useState(false)
  
  // Debug: Log when msme changes
  useEffect(() => {
    // MSME state tracking for debugging (removed in production)
  }, [msme])

  useEffect(() => {
    const fetchMSME = async () => {
      try {
        // FIRST: Try sessionStorage (fastest, just navigated here)
        const sessionMSME = sessionStorage.getItem('current_msme')
        if (sessionMSME) {
          try {
            const parsed = JSON.parse(sessionMSME)
            if (parsed.id === id) {
              setMsme(parsed)
              setLoading(false)
              return
            }
          } catch (e) {
            console.error('[MSMEProfile] Failed to parse sessionStorage', e)
          }
        }
        
        // SECOND: Try cached businesses from sessionStorage
        const cachedBusinesses = sessionStorage.getItem('msme_businesses')
        if (cachedBusinesses) {
          try {
            const allMsmes = JSON.parse(cachedBusinesses)
            const found = allMsmes.find((m: MSMEBusiness) => m.id === id)
            if (found) {
              // Check for stored score
              const storedScore = getValidScore(found.id, found.features)
              if (storedScore) {
                // Normalize risk category (handle old format with " Risk" suffix)
                const normalizedRisk = storedScore.riskCategory.replace(' Risk', '')
                
                found.currentScore = storedScore.score
                found.riskBucket = normalizedRisk
                found.prob_default_90dpd = storedScore.probDefault
                found.category_contributions = storedScore.categoryContributions
                found.summary = {
                  financialHealthScore: storedScore.score,
                  riskGrade: normalizedRisk,
                  maxLoanAmount: calculateMaxLoan(storedScore.score, found.features.monthly_gtv || 0),
                  probabilityOfDefault: storedScore.probDefault * 100,
                  recommendation: storedScore.recommendation
                }
                found.scoreResponse = storedScore.scoreResponse
              }
              setMsme(found)
              setLoading(false)
              return
            }
          } catch (e) {
            console.error('[MSMEProfile] Failed to parse cached businesses', e)
          }
        }
        
        // THIRD: Try to fetch from API data
        const response = await fetch('/api/msme-data')
        if (response.ok) {
          const allMsmes = await response.json()
          
          if (Array.isArray(allMsmes)) {
          const found = allMsmes.find((m: MSMEBusiness) => m.id === id)
          if (found) {
            // Check for stored score
            const storedScore = getValidScore(found.id, found.features)
            if (storedScore) {
                // Normalize risk category (handle old format with " Risk" suffix)
                const normalizedRisk = storedScore.riskCategory.replace(' Risk', '')
                
              // Apply stored score
              found.currentScore = storedScore.score
                found.riskBucket = normalizedRisk
              found.prob_default_90dpd = storedScore.probDefault
              found.category_contributions = storedScore.categoryContributions
              found.summary = {
                financialHealthScore: storedScore.score,
                  riskGrade: normalizedRisk,
                maxLoanAmount: calculateMaxLoan(storedScore.score, found.features.monthly_gtv || 0),
                probabilityOfDefault: storedScore.probDefault * 100,
                recommendation: storedScore.recommendation
              }
              found.scoreResponse = storedScore.scoreResponse
            }
            setMsme(found)
            setLoading(false)
            return
            }
          } else {
            console.error('[MSMEProfile] API returned error:', allMsmes)
          }
        }

        // FOURTH: Try to get from backend scoring API
        try {
          const featuresData = await msmeApi.getBusinessFeatures(id as string)
          
          const msmeData: MSMEBusiness = {
            id: featuresData.business_id,
            businessName: `Business ${id}`,
            businessSegment: featuresData.business_segment,
            industry: featuresData.features.industry_code || 'trading',
            features: featuresData.features,
          }

          setMsme(msmeData)
        } catch (apiError) {
          console.error("[MSMEProfile] ❌ All fetch methods failed:", apiError)
          alert('MSME not found. Please return to the list and try again.')
        }
      } catch (error) {
        console.error("[MSMEProfile] ❌ Error fetching MSME:", error)
        alert('Failed to load MSME. Please check console for details.')
      } finally {
        setLoading(false)
      }
    }
    if (id) fetchMSME()
  }, [id])

  const handleGenerateScore = async () => {
    if (!msme) return
    if (scoring) return // Prevent double click
    
    setScoring(true)
    
    try {
      // Send ALL features from the MSME data to the backend
      const result = await msmeApi.scoreBusiness({
        features: msme.features,
        business_segment: msme.businessSegment,
        alpha: 0.7,
        include_explanation: true
      })

      // Save to localStorage
      saveScore(msme.id, result, msme.features)
      
      // Normalize risk category (remove " Risk" suffix from backend)
      const normalizedRisk = result.risk_category.replace(' Risk', '')

      // Update MSME state with score results
      setMsme(prev => prev ? {
        ...prev,
        currentScore: result.score,
        riskBucket: normalizedRisk,
        prob_default_90dpd: result.prob_default_90dpd,
        summary: {
          financialHealthScore: result.score,
          riskGrade: normalizedRisk,
          maxLoanAmount: calculateMaxLoan(result.score, prev.features.monthly_gtv || prev.features.weekly_gtv ? (prev.features.weekly_gtv || 0) * 4 : 0),
          probabilityOfDefault: result.prob_default_90dpd * 100,
          recommendation: result.recommended_decision
        },
        category_contributions: result.category_contributions,
        scoreResponse: result
      } : null)

    } catch (error) {
      console.error("Error generating score:", error)
      
      // Fallback: Generate score locally
      const localScore = generateLocalScore(msme.features)
      const localResult: MSMEScoreResponse = {
        score: localScore.score,
        prob_default_90dpd: localScore.probDefault,
        risk_category: localScore.riskBucket,
        recommended_decision: localScore.recommendation,
        model_version: 'local_fallback_v1',
        business_segment: msme.businessSegment,
        component_scores: {
          local_calculation: 1.0
        },
        category_contributions: {
          A_business_identity: 0.10,
          B_revenue_performance: 0.20,
          C_cashflow_banking: 0.25,
          D_credit_repayment: 0.22,
          E_compliance_taxation: 0.12,
          F_fraud_verification: 0.07,
          G_external_signals: 0.04
        },
        timestamp: new Date().toISOString()
      }
      
      // Save local score
      saveScore(msme.id, localResult, msme.features)
      
      const updatedMsme = {
        ...msme,
        currentScore: localScore.score,
        riskBucket: localScore.riskBucket,
        summary: {
          financialHealthScore: localScore.score,
          riskGrade: localScore.riskGrade,
          maxLoanAmount: calculateMaxLoan(localScore.score, msme.features.monthly_gtv || 0),
          probabilityOfDefault: localScore.probDefault * 100,
          recommendation: localScore.recommendation
        },
        category_contributions: localResult.category_contributions
      }
      
      setMsme(updatedMsme)
      sessionStorage.setItem('current_msme', JSON.stringify(updatedMsme))
    } finally {
      setScoring(false)
    }
  }

  const generateLocalScore = (features: any) => {
    let score = 550

    if (features.business_age_years && features.business_age_years > 3) score += 20
    if (features.gstin_verified) score += 15
    if (features.pan_verified) score += 15
    if (features.weekly_gtv && features.weekly_gtv > 100000) score += 30
    if (features.profit_margin && features.profit_margin > 0.1) score += 20
    if (features.revenue_growth_rate_mom && features.revenue_growth_rate_mom > 0) score += 25
    if (features.weekly_inflow_outflow_ratio && features.weekly_inflow_outflow_ratio > 1.2) score += 40
    if (features.cash_buffer_days && features.cash_buffer_days > 30) score += 30
    if (features.negative_balance_days === 0) score += 30
    if (features.overdraft_repayment_ontime_ratio && features.overdraft_repayment_ontime_ratio > 0.9) score += 40
    if (features.bounced_cheques_count === 0) score += 30
    if (features.previous_defaults_count === 0) score += 30
    if (features.gst_filing_regularity && features.gst_filing_regularity > 0.9) score += 25
    if (features.itr_filed) score += 25

    if (features.previous_defaults_count && features.previous_defaults_count > 0) score -= 50
    if (features.bounced_cheques_count && features.bounced_cheques_count > 3) score -= 30
    if (features.negative_balance_days && features.negative_balance_days > 10) score -= 20
    if (features.legal_proceedings_flag) score -= 40

    score = Math.max(300, Math.min(900, score))
    const probDefault = Math.max(0.01, Math.min(0.5, (900 - score) / 1200))

    return {
      score,
      probDefault,
      riskBucket: score >= 750 ? 'Very Low' : score >= 650 ? 'Low' : score >= 550 ? 'Medium' : score >= 450 ? 'High' : 'Very High',
      riskGrade: score >= 750 ? 'A' : score >= 650 ? 'B' : score >= 550 ? 'C' : score >= 450 ? 'D' : 'E',
      recommendation: score >= 750 ? 'Fast Track Approval' : score >= 650 ? 'Approve' : score >= 550 ? 'Conditional Approval' : score >= 450 ? 'Manual Review' : 'Decline'
    }
  }

  const calculateMaxLoan = (score: number, monthlyGTV: number) => {
    const multiplier = score >= 750 ? 3 : score >= 650 ? 2.5 : score >= 550 ? 2 : score >= 450 ? 1.5 : 1
    return Math.round(monthlyGTV * multiplier)
  }

  if (loading) return <div className="flex items-center justify-center h-96">Loading...</div>
  if (!msme) return <div className="flex items-center justify-center h-96">MSME business not found</div>

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "Very Low":
      case "Low":
        return "bg-green-50 border-green-200 text-green-800"
      case "Medium":
        return "bg-yellow-50 border-yellow-200 text-yellow-800"
      case "High":
      case "Very High":
        return "bg-red-50 border-red-200 text-red-800"
      default:
        return "bg-gray-50 border-gray-200 text-gray-800"
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link href="/msmes" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to MSMEs
          </Link>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-2xl">
              {msme.businessName.charAt(0)}
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{msme.businessName}</h1>
              <p className="text-gray-600">
                {msme.businessSegment?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())} • {msme.industry}
              </p>
            </div>
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          {/* Key Metrics Row - Only show if scored */}
          <div className="flex gap-3">
            {msme.currentScore !== undefined ? (
              <>
                <div className="bg-blue-50 border border-blue-200 px-4 py-2 rounded-lg text-center">
                  <p className="text-2xl font-bold text-blue-900">{convertScoreTo100(msme.currentScore)}</p>
                  <p className="text-xs font-semibold text-blue-700">Credit Score</p>
                  <p className="text-xs text-blue-600">Out of 100</p>
                </div>
                {msme.riskBucket && (
                  <div className={`px-4 py-2 rounded-lg border text-center ${getRiskColor(msme.riskBucket)}`}>
                    <p className="text-2xl font-bold">{msme.riskBucket}</p>
                    <p className="text-xs font-semibold">Risk Category</p>
                  </div>
                )}
                {msme.summary?.maxLoanAmount !== undefined && (
                  <div className="bg-green-50 border border-green-200 px-4 py-2 rounded-lg text-center">
                    <p className="text-2xl font-bold text-green-900">
                      ₹{msme.summary.maxLoanAmount >= 10000000 
                        ? `${(msme.summary.maxLoanAmount / 10000000).toFixed(1)}Cr` 
                        : msme.summary.maxLoanAmount >= 100000 
                          ? `${(msme.summary.maxLoanAmount / 100000).toFixed(1)}L`
                          : `${(msme.summary.maxLoanAmount / 1000).toFixed(0)}K`}
                    </p>
                    <p className="text-xs font-semibold text-green-700">Max Loan Amount</p>
                  </div>
                )}
                {msme.prob_default_90dpd !== undefined && (
                  <div className="bg-orange-50 border border-orange-200 px-4 py-2 rounded-lg text-center">
                    <p className="text-2xl font-bold text-orange-900">
                      {(msme.prob_default_90dpd * 100).toFixed(1)}%
                    </p>
                    <p className="text-xs font-semibold text-orange-700">Default Probability</p>
                  </div>
                )}
              </>
            ) : (
              <div className="bg-gray-50 border border-gray-200 px-6 py-3 rounded-lg text-center">
                <p className="text-sm text-gray-500 italic">Click "Generate Score" to score this business</p>
              </div>
            )}
          </div>
          <div className="flex gap-2">
            <button 
              onClick={handleGenerateScore}
              disabled={scoring}
              className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium disabled:opacity-50"
            >
              {scoring ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
              {scoring ? 'Scoring...' : msme.currentScore !== undefined ? 'Re-Score' : 'Generate Score'}
            </button>
            <button 
              onClick={() => downloadMSMEPDF(msme)}
              className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!msme.currentScore && !msme.scoreResponse}
              title={!msme.currentScore && !msme.scoreResponse ? 'Generate a score first to download summary' : 'Download one-page PDF summary'}
            >
              <FileText className="w-4 h-4" />
              Download Summary
            </button>
          </div>
        </div>
      </div>

      {/* Summary Card - Full Width (always shown if scored) */}
      {(msme.currentScore !== undefined || msme.scoreResponse) && (
        <MSMESummaryCard msme={msme} />
      )}

      {/* Director/Promoter Details - Full Width */}
      <DirectorDetailsCard msme={msme} />

      {/* 1. Business Identity (Left) + 2. Revenue Performance (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BusinessIdentityCard msme={msme} />
        <RevenuePerformanceCard msme={msme} />
      </div>

      {/* 3. Cashflow & Banking (Left) + 4. Credit & Repayment (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <CashflowBankingCard msme={msme} />
        <CreditRepaymentCard msme={msme} />
      </div>

      {/* 5. Compliance & Taxation (Left) + 6. Fraud & Verification (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <ComplianceTaxationCard msme={msme} />
        <FraudVerificationCard msme={msme} />
      </div>

      {/* 7. External Signals (Full Width) */}
      <div className="grid grid-cols-1 gap-6">
        <ExternalSignalsCard msme={msme} />
      </div>

      {/* Category Contributions (shown when scored) */}
      {msme.category_contributions && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Score Category Breakdown</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
            {Object.entries(msme.category_contributions).map(([category, value]) => {
              const labels: Record<string, string> = {
                'A_business_identity': 'Identity',
                'B_revenue_performance': 'Revenue',
                'C_cashflow_banking': 'Cashflow',
                'D_credit_repayment': 'Credit',
                'E_compliance_taxation': 'Compliance',
                'F_fraud_verification': 'Fraud',
                'G_external_signals': 'External'
              }
              return (
                <div key={category} className="bg-gray-50 rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-gray-900">{(value * 100).toFixed(1)}%</p>
                  <p className="text-xs text-gray-600">{labels[category] || category}</p>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* SHAP Explanation (shown when scored) */}
      {msme.scoreResponse?.explanation && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-6 flex items-center gap-2">
            <Zap className="w-5 h-5 text-purple-600" />
            Score Explanation (SHAP Analysis)
          </h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Top Positive Features */}
            {msme.scoreResponse.explanation.top_positive_features && msme.scoreResponse.explanation.top_positive_features.length > 0 && (
              <div className="space-y-3">
                <h4 className="font-semibold text-green-700 flex items-center gap-2">
                  <span className="text-2xl">📈</span>
                  Positive Impact Factors
                </h4>
                <div className="space-y-2">
                  {msme.scoreResponse.explanation.top_positive_features.map((feature, idx) => (
                    <div key={idx} className="bg-green-50 border border-green-200 rounded-lg p-3">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium text-gray-700">
                          {feature.feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                        <span className="text-xs font-bold text-green-700">
                          +{feature.shap_value.toFixed(3)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-green-200 rounded-full h-2 overflow-hidden">
                          <div
                            className="h-full bg-green-600"
                            style={{ width: `${Math.min(Math.abs(feature.shap_value) * 100, 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600">
                          Value: {typeof feature.feature_value === 'number' ? feature.feature_value.toFixed(2) : feature.feature_value}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Top Negative Features */}
            {msme.scoreResponse.explanation.top_negative_features && msme.scoreResponse.explanation.top_negative_features.length > 0 && (
          <div className="space-y-3">
                <h4 className="font-semibold text-red-700 flex items-center gap-2">
                  <span className="text-2xl">📉</span>
                  Negative Impact Factors
                </h4>
                <div className="space-y-2">
                  {msme.scoreResponse.explanation.top_negative_features.map((feature, idx) => (
                    <div key={idx} className="bg-red-50 border border-red-200 rounded-lg p-3">
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm font-medium text-gray-700">
                          {feature.feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                        <span className="text-xs font-bold text-red-700">
                          {feature.shap_value.toFixed(3)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-red-200 rounded-full h-2 overflow-hidden">
                          <div
                            className="h-full bg-red-600"
                            style={{ width: `${Math.min(Math.abs(feature.shap_value) * 100, 100)}%` }}
                          />
                        </div>
                        <span className="text-xs text-gray-600">
                          Value: {typeof feature.feature_value === 'number' ? feature.feature_value.toFixed(2) : feature.feature_value}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {msme.scoreResponse.explanation.base_value !== undefined && (
            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">
                <span className="font-semibold">Base Value:</span> {msme.scoreResponse.explanation.base_value.toFixed(2)}
                <span className="ml-4 text-xs text-gray-500">
                  (Average prediction across all businesses)
                </span>
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
