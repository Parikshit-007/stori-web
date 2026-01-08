"use client"
import { useState, useEffect } from "react"
import { mockApi } from "@/lib/mockApi"
import { consumerApi, ConsumerFeatures } from "@/lib/consumerApi"
import { Download, Info, RefreshCw, AlertCircle } from "lucide-react"
import FeatureImportanceChart from "@/components/FeatureImportanceChart"
import SHAPWaterfall from "@/components/SHAPWaterfall"

// Helper function to convert mock consumer to API features format
function convertConsumerToFeatures(consumer: any): ConsumerFeatures {
  return {
    // Identity & Demographics
    name_dob_verified: consumer.identity?.faceMatch ? 1 : 0,
    phone_verified: consumer.identity?.mobileVerified ? 1 : 0,
    phone_age_months: consumer.identity?.digitalIdentity?.simAge || 0,
    email_verified: 1,
    email_age_months: consumer.identity?.digitalIdentity?.emailAge || 0,
    location_stability_score: consumer.identity?.lifeStability?.residenceStability?.score ? consumer.identity.lifeStability.residenceStability.score / 100 : 0.8,
    education_level: 3, // Default
    employment_tenure_months: consumer.identity?.lifeStability?.jobStability?.avgEmploymentDuration ? consumer.identity.lifeStability.jobStability.avgEmploymentDuration * 12 : 0,
    employment_type: consumer.persona === "Salaried" ? "salaried" : "other",
    
    // Income & Cashflow
    monthly_income: consumer.income?.monthlyIncome || 0,
    avg_account_balance: consumer.income?.totalBalance || 0,
    min_account_balance: consumer.income?.accountBalances?.reduce((min: number, acc: any) => Math.min(min, acc.balance || 0), Infinity) || 0,
    income_stability_score: consumer.income?.incomeStabilityScore ? consumer.income.incomeStabilityScore / 100 : 0.8,
    itr_filed: consumer.assets?.itrFiled ? 1 : 0,
    itr_income_declared: consumer.income?.monthlyIncome ? consumer.income.monthlyIncome * 12 : 0,
    
    // Assets & Liabilities
    total_assets_value: consumer.assets?.totalAssets || 0,
    total_liabilities: consumer.liabilities?.activeLoans?.reduce((sum: number, loan: any) => sum + (loan.outstanding || 0), 0) || 0,
    debt_to_income_ratio: consumer.liabilities?.activeLoans ? 
      consumer.liabilities.activeLoans.reduce((sum: number, loan: any) => sum + (loan.outstanding || 0), 0) / (consumer.income?.monthlyIncome || 1) : 0,
    emi_burden_ratio: consumer.saturation?.emiToIncome ? consumer.saturation.emiToIncome / 100 : 0,
    
    // Behavioral Signals
    budgeting_score: consumer.behaviour?.spendingArchetype?.confidence ? consumer.behaviour.spendingArchetype.confidence / 100 : 0.7,
    savings_rate: consumer.income?.monthlyIncome ? (consumer.income.monthlyIncome - (consumer.saturation?.totalSaturation || 0) * consumer.income.monthlyIncome / 100) / consumer.income.monthlyIncome : 0.3,
    
    // Credit & Repayment
    repayment_ontime_ratio: consumer.liabilities?.loanRepaymentHistory === "Excellent" ? 1.0 : 0.8,
    credit_card_utilization: 0.35, // Default
    num_credit_inquiries_6m: consumer.liabilities?.creditEnquiries || 0,
    default_history_count: consumer.liabilities?.defaultHistory === "None" ? 0 : 1,
    
    // Fraud & Verification
    face_match_score: consumer.identity?.faceMatch ? consumer.identity.faceMatch / 100 : 0.9,
    kyc_completion_score: 0.95,
    device_consistency_score: consumer.identity?.digitalIdentity?.platformConsistency ? consumer.identity.digitalIdentity.platformConsistency / 100 : 0.9,
    
    // Transactions & Utility
    utility_payment_ontime_ratio: consumer.behaviour?.billPayment?.overallScore ? consumer.behaviour.billPayment.overallScore / 100 : 0.9,
    utility_payment_days_before_due: consumer.behaviour?.billPayment?.avgDaysBeforeDue || 0,
    mobile_recharge_regularity: 0.9,
    mobile_recharge_ontime_ratio: 0.95,
    rent_payment_regularity: consumer.identity?.lifeStability?.residenceStability?.rentPaymentPattern === "On-time" ? 1.0 : 0.8,
    rent_payment_ontime_ratio: consumer.identity?.lifeStability?.residenceStability?.rentPaymentPattern === "On-time" ? 1.0 : 0.8,
  }
}

// Example features for demonstration
const exampleFeatures: ConsumerFeatures = {
  name_dob_verified: 1,
  phone_verified: 1,
  phone_age_months: 48,
  email_verified: 1,
  email_age_months: 84,
  location_stability_score: 0.92,
  education_level: 3,
  employment_tenure_months: 54,
  employment_type: "salaried",
  monthly_income: 85000,
  avg_account_balance: 450000,
  min_account_balance: 35000,
  income_stability_score: 0.92,
  itr_filed: 1,
  itr_income_declared: 1020000,
  total_assets_value: 2950000,
  total_liabilities: 3320000,
  debt_to_income_ratio: 39.06,
  emi_burden_ratio: 0.706,
  budgeting_score: 0.85,
  savings_rate: 0.26,
  repayment_ontime_ratio: 1.0,
  credit_card_utilization: 0.35,
  num_credit_inquiries_6m: 2,
  default_history_count: 0,
  face_match_score: 0.985,
  kyc_completion_score: 0.95,
  device_consistency_score: 0.95,
  utility_payment_ontime_ratio: 0.94,
  utility_payment_days_before_due: 2,
  mobile_recharge_regularity: 0.9,
  mobile_recharge_ontime_ratio: 0.95,
  rent_payment_regularity: 1.0,
  rent_payment_ontime_ratio: 1.0,
}

export default function Explainability() {
  const [importances, setImportances] = useState<any[]>([])
  const [shapData, setShapData] = useState<Array<{ feature: string; value: number; impact: "positive" | "negative" }>>([])
  const [shapScore, setShapScore] = useState<number | null>(null)
  const [shapBaseValue, setShapBaseValue] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)
  const [shapLoading, setShapLoading] = useState(false)
  const [shapError, setShapError] = useState<string | null>(null)
  const [persona, setPersona] = useState<string>("salaried_professional")

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await mockApi.getFeatureImportances()
        setImportances(data)
      } catch (error) {
        console.error("Error fetching importances:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  useEffect(() => {
    // Fetch SHAP data on mount
    fetchSHAPData(exampleFeatures)
  }, [persona])

  const fetchSHAPData = async (features: ConsumerFeatures) => {
    setShapLoading(true)
    setShapError(null)
    try {
      const response = await consumerApi.explainScore({
        features,
        persona,
        top_n: 15
      })

      // Transform API response to SHAPWaterfall format
      // SHAP values are in probability space. To convert to approximate score impact:
      // Around prob 0.05-0.10 (score 600-700), a 0.01 change in prob ≈ 10-20 score points
      // We'll use a scaling factor of 1000 to make contributions visible
      const SCORE_SCALING_FACTOR = 1000
      
      const transformedData: Array<{ feature: string; value: number; impact: "positive" | "negative" }> = []
      
      // Add positive features (convert SHAP values to approximate score points)
      // Positive SHAP = decreases probability = increases score
      response.top_positive_features.forEach((feat) => {
        transformedData.push({
          feature: feat.feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          value: Math.round(feat.shap_value * SCORE_SCALING_FACTOR), // Scale SHAP value to score points
          impact: "positive"
        })
      })

      // Add negative features
      // Negative SHAP = increases probability = decreases score
      response.top_negative_features.forEach((feat) => {
        transformedData.push({
          feature: feat.feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          value: Math.round(feat.shap_value * SCORE_SCALING_FACTOR), // Already negative, scale to score points
          impact: "negative"
        })
      })

      // Sort by absolute value descending
      transformedData.sort((a, b) => Math.abs(b.value) - Math.abs(a.value))

      setShapData(transformedData)
      setShapScore(response.score)
      // Calculate base value from score and SHAP contributions
      const totalShap = transformedData.reduce((sum, item) => sum + item.value, 0)
      setShapBaseValue(response.score - totalShap)
    } catch (error: any) {
      console.error("Error fetching SHAP data:", error)
      setShapError(error.message || "Failed to fetch SHAP explanation. Make sure the API is running.")
    } finally {
      setShapLoading(false)
    }
  }

  const handleRefresh = () => {
    fetchSHAPData(exampleFeatures)
  }

  const personaWeights = {
    Salaried: { identity: 15, income: 20, assets: 18, behaviour: 15, transactions: 15, fraud: 10, family: 7 },
    NTC: { identity: 28, income: 22, assets: 12, behaviour: 18, transactions: 12, fraud: 8, family: 0 },
    Gig: { identity: 20, income: 25, assets: 15, behaviour: 15, transactions: 15, fraud: 8, family: 2 },
    "Credit-Experienced": {
      identity: 12,
      income: 18,
      assets: 22,
      behaviour: 18,
      transactions: 15,
      fraud: 10,
      family: 5,
    },
    "Mass Affluent": { identity: 10, income: 15, assets: 30, behaviour: 20, transactions: 12, fraud: 8, family: 5 },
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Model Explainability</h1>
          <p className="text-gray-600 mt-1">Understand what drives the GBM credit score</p>
        </div>
        <button className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
          <Download className="w-4 h-4" />
          Export PDF
        </button>
      </div>

      {/* Model Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-2xl p-6">
        <div className="flex gap-4">
          <Info className="w-6 h-6 text-blue-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-2">Current Model Configuration</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-blue-800">
              <div>
                <span className="font-semibold">Model Version:</span> GBM v1.2.3
              </div>
              <div>
                <span className="font-semibold">Calibration Date:</span> Jan 10, 2025
              </div>
              <div>
                <span className="font-semibold">Score Range:</span> 300-900
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Feature Importance */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Global Feature Importance</h2>
        <FeatureImportanceChart data={importances} />
      </div>

      {/* SHAP Waterfall */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">SHAP Values (Real Data)</h2>
            <p className="text-sm text-gray-600 mt-1">
              Shows positive and negative feature contributions to final score. 
              Values are approximate score point impacts derived from probability contributions.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <select
              value={persona}
              onChange={(e) => setPersona(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="salaried_professional">Salaried Professional</option>
              <option value="new_to_credit">New to Credit</option>
              <option value="gig_worker">Gig Worker</option>
              <option value="credit_experienced">Credit Experienced</option>
              <option value="mass_affluent">Mass Affluent</option>
            </select>
            <button
              onClick={handleRefresh}
              disabled={shapLoading}
              className="inline-flex items-center gap-2 px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <RefreshCw className={`w-4 h-4 ${shapLoading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>
        
        {shapError ? (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
            <div>
              <p className="text-sm font-medium text-red-800">Error loading SHAP data</p>
              <p className="text-sm text-red-600 mt-1">{shapError}</p>
            </div>
          </div>
        ) : shapLoading ? (
          <div className="flex items-center justify-center py-12">
            <div className="flex flex-col items-center gap-3">
              <RefreshCw className="w-8 h-8 text-blue-600 animate-spin" />
              <p className="text-sm text-gray-600">Loading SHAP explanation...</p>
            </div>
          </div>
        ) : shapData.length > 0 ? (
          <SHAPWaterfall 
            data={shapData} 
            baseScore={shapBaseValue || undefined}
            finalScore={shapScore || undefined}
          />
        ) : (
          <div className="text-center py-8 text-gray-500">
            No SHAP data available. Click Refresh to load.
          </div>
        )}
      </div>

      {/* Persona Weights */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Category Weights by Persona</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {Object.entries(personaWeights).map(([persona, weights]: [string, any]) => (
            <div key={persona} className="border border-gray-200 rounded-xl p-4">
              <h4 className="font-semibold text-gray-900 mb-3 text-center">{persona}</h4>
              <div className="space-y-2 text-sm">
                {Object.entries(weights).map(([cat, weight]: [string, any]) => (
                  <div key={cat} className="flex justify-between">
                    <span className="text-gray-600 capitalize">{cat}</span>
                    <span className="font-semibold text-gray-900">{weight}%</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Partial Dependency Plots */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Income vs Default Risk</h3>
          <div className="h-48 flex items-center justify-center bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500">Partial Dependency Plot (Mock)</p>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Balance vs Credit Score</h3>
          <div className="h-48 flex items-center justify-center bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-500">Partial Dependency Plot (Mock)</p>
          </div>
        </div>
      </div>
    </div>
  )
}
