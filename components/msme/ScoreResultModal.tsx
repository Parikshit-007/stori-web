"use client"

import { X, TrendingUp, TrendingDown, CheckCircle, XCircle, AlertTriangle, BarChart3, Loader2 } from "lucide-react"
import { MSMEScoreResponse } from "@/lib/msmeApi"
import SHAPWaterfall from "@/components/SHAPWaterfall"

interface ScoreResultModalProps {
  isOpen: boolean
  onClose: () => void
  result: MSMEScoreResponse | null
  businessName: string
  isLoading?: boolean
}

export default function ScoreResultModal({ isOpen, onClose, result, businessName, isLoading }: ScoreResultModalProps) {
  if (!isOpen) return null

  const getRiskColor = (risk: string) => {
    if (risk.includes('Very Low') || risk.includes('Low')) return 'text-green-600 bg-green-50 border-green-200'
    if (risk.includes('Medium')) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  const getDecisionStyle = (decision: string) => {
    if (decision.includes('Fast Track') || decision.includes('Approve')) {
      return { bg: 'bg-green-50', border: 'border-green-300', text: 'text-green-700', icon: CheckCircle }
    }
    if (decision.includes('Conditional') || decision.includes('Review')) {
      return { bg: 'bg-yellow-50', border: 'border-yellow-300', text: 'text-yellow-700', icon: AlertTriangle }
    }
    return { bg: 'bg-red-50', border: 'border-red-300', text: 'text-red-700', icon: XCircle }
  }

  const categoryLabels: Record<string, string> = {
    'A_business_identity': 'Business Identity',
    'B_revenue_performance': 'Revenue & Performance',
    'C_cashflow_banking': 'Cash Flow & Banking',
    'D_credit_repayment': 'Credit & Repayment',
    'E_compliance_taxation': 'Compliance & Taxation',
    'F_fraud_verification': 'Fraud & Verification',
    'G_external_signals': 'External Signals'
  }

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      'A_business_identity': 'bg-blue-500',
      'B_revenue_performance': 'bg-green-500',
      'C_cashflow_banking': 'bg-purple-500',
      'D_credit_repayment': 'bg-orange-500',
      'E_compliance_taxation': 'bg-teal-500',
      'F_fraud_verification': 'bg-red-500',
      'G_external_signals': 'bg-indigo-500'
    }
    return colors[category] || 'bg-gray-500'
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-purple-600">
          <div>
            <h2 className="text-2xl font-bold text-white">Credit Score Result</h2>
            <p className="text-blue-100">{businessName}</p>
          </div>
          <button onClick={onClose} className="text-white hover:bg-white/20 rounded-full p-2 transition">
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[calc(90vh-120px)]">
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20">
              <Loader2 className="w-16 h-16 text-blue-600 animate-spin mb-4" />
              <p className="text-lg font-medium text-gray-600">Generating Credit Score...</p>
              <p className="text-sm text-gray-500">Analyzing business profile and features</p>
            </div>
          ) : result ? (
            <div className="space-y-6">
              {/* Score Overview */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {/* Main Score */}
                <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 text-center border border-blue-200">
                  <div className="relative inline-flex items-center justify-center mb-3">
                    <svg className="w-24 h-24 transform -rotate-90">
                      <circle cx="48" cy="48" r="42" stroke="#e5e7eb" strokeWidth="8" fill="none" />
                      <circle
                        cx="48" cy="48" r="42"
                        stroke={result.score >= 650 ? '#10b981' : result.score >= 550 ? '#f59e0b' : '#ef4444'}
                        strokeWidth="8" fill="none"
                        strokeDasharray={`${((result.score - 300) / 600) * 264} 264`}
                        strokeLinecap="round"
                      />
                    </svg>
                    <span className="absolute text-3xl font-bold text-gray-900">{result.score}</span>
                  </div>
                  <p className="text-sm font-semibold text-blue-700">Credit Score</p>
                  <p className="text-xs text-blue-600">Range: 300-900</p>
                </div>

                {/* Risk Category */}
                <div className={`rounded-xl p-6 text-center border ${getRiskColor(result.risk_category)}`}>
                  <p className="text-4xl font-bold mb-2">{result.risk_category}</p>
                  <p className="text-sm font-semibold">Risk Category</p>
                </div>

                {/* Default Probability */}
                <div className="bg-orange-50 rounded-xl p-6 text-center border border-orange-200">
                  <p className="text-4xl font-bold text-orange-600 mb-2">
                    {(result.prob_default_90dpd * 100).toFixed(2)}%
                  </p>
                  <p className="text-sm font-semibold text-orange-700">90-Day Default Prob</p>
                </div>

                {/* Model Version */}
                <div className="bg-gray-50 rounded-xl p-6 text-center border border-gray-200">
                  <p className="text-lg font-mono text-gray-700 mb-2">{result.model_version}</p>
                  <p className="text-sm font-semibold text-gray-600">Model Version</p>
                  <p className="text-xs text-gray-500">{result.business_segment.replace(/_/g, ' ')}</p>
                </div>
              </div>

              {/* Recommendation */}
              {(() => {
                const decisionStyle = getDecisionStyle(result.recommended_decision)
                const DecisionIcon = decisionStyle.icon
                return (
                  <div className={`${decisionStyle.bg} ${decisionStyle.border} border-2 rounded-xl p-6 flex items-center gap-6`}>
                    <DecisionIcon className={`w-16 h-16 ${decisionStyle.text}`} />
                    <div>
                      <p className={`font-bold text-2xl ${decisionStyle.text}`}>{result.recommended_decision}</p>
                      <p className={`${decisionStyle.text} opacity-80`}>
                        {result.recommended_decision.includes("Fast Track") && "Excellent business profile - Fast track approval recommended"}
                        {result.recommended_decision.includes("Approve") && !result.recommended_decision.includes("Fast") && "Good business profile - Standard approval processing"}
                        {result.recommended_decision.includes("Conditional") && "Additional documentation or verification may be required"}
                        {result.recommended_decision.includes("Review") && "Manual assessment by underwriting team required"}
                        {result.recommended_decision.includes("Decline") && "High risk - Not eligible for credit at this time"}
                      </p>
                    </div>
                  </div>
                )
              })()}

              {/* Category Contributions */}
              <div className="bg-white rounded-xl border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5 text-blue-600" />
                  Category Contributions
                </h3>
                <div className="space-y-3">
                  {Object.entries(result.category_contributions).map(([category, value]) => (
                    <div key={category} className="flex items-center gap-3">
                      <div className="w-40 text-sm font-medium text-gray-700">
                        {categoryLabels[category] || category}
                      </div>
                      <div className="flex-1 bg-gray-200 rounded-full h-4 overflow-hidden">
                        <div
                          className={`h-full ${getCategoryColor(category)} transition-all duration-500`}
                          style={{ width: `${Math.min(value * 100 * 4, 100)}%` }}
                        />
                      </div>
                      <div className="w-16 text-right text-sm font-semibold text-gray-900">
                        {(value * 100).toFixed(1)}%
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Component Scores */}
              {result.component_scores && (
                <div className="bg-gray-50 rounded-xl border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Component Scores</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {Object.entries(result.component_scores).map(([key, value]) => (
                      <div key={key} className="bg-white rounded-lg p-4 border border-gray-200">
                        <p className="text-sm text-gray-600 capitalize">{key.replace(/_/g, ' ')}</p>
                        <p className="text-xl font-bold text-gray-900">
                          {typeof value === 'number' ? value.toFixed(4) : value}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* SHAP Explanation */}
              {result.explanation && (
                <>
                  {/* SHAP Waterfall Visualization */}
                  <div className="bg-white rounded-xl border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <BarChart3 className="w-5 h-5 text-blue-600" />
                      SHAP Waterfall Visualization
                    </h3>
                    <p className="text-sm text-gray-600 mb-4">
                      Feature contributions to credit score. Values show approximate score point impacts.
                    </p>
                    {(() => {
                      // Transform SHAP data to waterfall format
                      const SCORE_SCALING_FACTOR = 1000 // Convert probability SHAP to approximate score points
                      const waterfallData: Array<{ feature: string; value: number; impact: "positive" | "negative" }> = []
                      
                      // Add positive features (decreases risk = increases score)
                      if (result.explanation.top_positive_features) {
                        result.explanation.top_positive_features.forEach((feat) => {
                          waterfallData.push({
                            feature: feat.feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                            value: Math.round(feat.shap_value * SCORE_SCALING_FACTOR),
                            impact: "positive"
                          })
                        })
                      }
                      
                      // Add negative features (increases risk = decreases score)
                      if (result.explanation.top_negative_features) {
                        result.explanation.top_negative_features.forEach((feat) => {
                          waterfallData.push({
                            feature: feat.feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                            value: Math.round(feat.shap_value * SCORE_SCALING_FACTOR),
                            impact: "negative"
                          })
                        })
                      }
                      
                      // Sort by absolute value descending
                      waterfallData.sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
                      
                      // Calculate base value
                      const totalShap = waterfallData.reduce((sum, item) => sum + item.value, 0)
                      const baseValue = result.score - totalShap
                      
                      return waterfallData.length > 0 ? (
                        <SHAPWaterfall 
                          data={waterfallData} 
                          baseScore={Math.round(baseValue)}
                          finalScore={result.score}
                        />
                      ) : (
                        <p className="text-sm text-gray-500 text-center py-4">No SHAP data available</p>
                      )
                    })()}
                  </div>

                  {/* Detailed Feature Lists */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Top Positive Features */}
                    {result.explanation.top_positive_features && result.explanation.top_positive_features.length > 0 && (
                      <div className="bg-green-50 rounded-xl border border-green-200 p-6">
                        <h3 className="text-lg font-semibold text-green-800 mb-4 flex items-center gap-2">
                          <TrendingUp className="w-5 h-5" />
                          Top Positive Factors
                        </h3>
                        <div className="space-y-3">
                          {result.explanation.top_positive_features.slice(0, 5).map((feat, idx) => (
                            <div key={idx} className="flex justify-between items-center bg-white rounded-lg p-3 border border-green-200">
                              <div>
                                <p className="font-medium text-gray-800 capitalize">
                                  {feat.feature.replace(/_/g, ' ')}
                                </p>
                                <p className="text-sm text-gray-500">Value: {feat.feature_value}</p>
                              </div>
                              <span className="text-green-600 font-bold">+{feat.shap_value.toFixed(3)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Top Negative Features */}
                    {result.explanation.top_negative_features && result.explanation.top_negative_features.length > 0 && (
                      <div className="bg-red-50 rounded-xl border border-red-200 p-6">
                        <h3 className="text-lg font-semibold text-red-800 mb-4 flex items-center gap-2">
                          <TrendingDown className="w-5 h-5" />
                          Top Negative Factors
                        </h3>
                        <div className="space-y-3">
                          {result.explanation.top_negative_features.slice(0, 5).map((feat, idx) => (
                            <div key={idx} className="flex justify-between items-center bg-white rounded-lg p-3 border border-red-200">
                              <div>
                                <p className="font-medium text-gray-800 capitalize">
                                  {feat.feature.replace(/_/g, ' ')}
                                </p>
                                <p className="text-sm text-gray-500">Value: {feat.feature_value}</p>
                              </div>
                              <span className="text-red-600 font-bold">{feat.shap_value.toFixed(3)}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}

              {/* Timestamp */}
              <div className="text-center text-sm text-gray-500">
                Score generated at: {new Date(result.timestamp).toLocaleString()}
              </div>
            </div>
          ) : (
            <div className="text-center py-10 text-gray-500">
              No score result available
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-gray-200 bg-gray-50 flex justify-end gap-3">
          <button
            onClick={onClose}
            className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition font-medium"
          >
            Close
          </button>
          {result && (
            <button
              onClick={() => {
                // Could implement download functionality
                console.log('Download score report')
              }}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
            >
              Download Report
            </button>
          )}
        </div>
      </div>
    </div>
  )
}



