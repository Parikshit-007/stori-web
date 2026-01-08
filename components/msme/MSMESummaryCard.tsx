"use client"

import { BarChart3, CircleDollarSign, TrendingUp, CheckCircle, XCircle, AlertTriangle, Activity } from "lucide-react"
import { MSMEBusiness } from "@/lib/msmeApi"
import { convertScoreTo100, getRiskCategoryFrom100Score, getScoreColor } from "@/lib/scoreUtils"

interface MSMESummaryCardProps {
  msme: MSMEBusiness
}

export default function MSMESummaryCard({ msme }: MSMESummaryCardProps) {
  const summary = msme.summary
  const score900 = msme.currentScore || summary?.financialHealthScore || 0
  const score = convertScoreTo100(score900) // Convert to 0-100 scale
  const probDefault = summary?.probabilityOfDefault || (msme.prob_default_90dpd || 0) * 100 || 0
  const maxLoanAmount = summary?.maxLoanAmount || 0
  const riskCategory = msme.riskBucket || summary?.riskGrade || 'Medium'
  const recommendation = summary?.recommendation || 'Manual Review'
  const categoryContributions = msme.category_contributions || {}

  const getRiskGrade = (score: number) => {
    // Score is now 0-100
    if (score >= 85) return { grade: 'A', cibil: '800+', color: 'text-green-600' }
    if (score >= 70) return { grade: 'B', cibil: '740-800', color: 'text-green-600' }
    if (score >= 50) return { grade: 'C', cibil: '700-740', color: 'text-yellow-600' }
    if (score >= 30) return { grade: 'D', cibil: '650-699', color: 'text-orange-600' }
    return { grade: 'E', cibil: '<650', color: 'text-red-600' }
  }

  const risk = getRiskGrade(score)

  const getRecommendationStyle = (rec: string) => {
    if (rec.includes("Approve") || rec.includes("Fast Track")) return { bg: "bg-green-50", border: "border-green-200", text: "text-green-700", icon: CheckCircle }
    if (rec.includes("Conditional") || rec.includes("Review")) return { bg: "bg-yellow-50", border: "border-yellow-200", text: "text-yellow-700", icon: AlertTriangle }
    return { bg: "bg-red-50", border: "border-red-200", text: "text-red-700", icon: XCircle }
  }

  const recStyle = getRecommendationStyle(recommendation)
  const RecIcon = recStyle.icon

  const gradeTable = [
    { cibil: '800+', score: '85-100', grade: 'A' },
    { cibil: '740-800', score: '70-84', grade: 'B' },
    { cibil: '700-740', score: '50-69', grade: 'C' },
    { cibil: '650-699', score: '30-49', grade: 'D' },
    { cibil: '<650', score: '0-29', grade: 'E' },
  ]

  const categoryLabels: Record<string, string> = {
    'A_business_identity': 'Business Identity',
    'B_revenue_performance': 'Revenue Performance',
    'C_cashflow_banking': 'Cash Flow & Banking',
    'D_credit_repayment': 'Credit & Repayment',
    'E_compliance_taxation': 'Compliance & Tax',
    'F_fraud_verification': 'Fraud & Verification',
    'G_external_signals': 'External Signals'
  }

  const getCategoryColor = (idx: number) => {
    const colors = ['bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-orange-500', 'bg-teal-500', 'bg-red-500', 'bg-indigo-500']
    return colors[idx % colors.length]
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <BarChart3 className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">Credit Score Summary</h3>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Key Metrics */}
        <div className="grid grid-cols-2 gap-4">
          {/* Credit Score */}
          <div className="bg-gray-50 rounded-xl p-4 text-center">
            <div className="relative inline-flex items-center justify-center mb-3">
              <svg className="w-20 h-20 transform -rotate-90">
                <circle cx="40" cy="40" r="35" stroke="#e5e7eb" strokeWidth="6" fill="none" />
                <circle
                  cx="40" cy="40" r="35"
                  stroke={score >= 70 ? '#10b981' : score >= 50 ? '#f59e0b' : '#ef4444'}
                  strokeWidth="6" fill="none"
                  strokeDasharray={`${(score / 100) * 220} 220`}
                  strokeLinecap="round"
                />
              </svg>
              <span className="absolute text-xl font-bold text-gray-900">{score}</span>
            </div>
            <p className="text-sm font-medium text-gray-600">Credit Score</p>
            <p className="text-xs text-gray-400 mt-1">Out of 100</p>
          </div>

          {/* Risk Grade */}
          <div className="bg-gray-50 rounded-xl p-4 text-center flex flex-col justify-center">
            <p className={`text-5xl font-bold ${risk.color}`}>{risk.grade}</p>
            <p className="text-sm text-gray-500 mt-1">Risk Grade</p>
            <p className="text-xs text-gray-400">≈ CIBIL {risk.cibil}</p>
          </div>

          {/* Max Loan Amount */}
          <div className="bg-gray-50 rounded-xl p-4 text-center flex flex-col justify-center">
            <CircleDollarSign className="w-6 h-6 mx-auto mb-2 text-green-600" />
            <p className="text-2xl font-bold text-green-600">
              ₹{maxLoanAmount >= 10000000 
                ? `${(maxLoanAmount / 10000000).toFixed(1)}Cr` 
                : maxLoanAmount >= 100000 
                  ? `${(maxLoanAmount / 100000).toFixed(1)}L`
                  : `${(maxLoanAmount / 1000).toFixed(0)}K`}
            </p>
            <p className="text-sm font-medium text-gray-600">Max Loan</p>
          </div>

          {/* Default Probability */}
          <div className="bg-gray-50 rounded-xl p-4 text-center flex flex-col justify-center">
            <TrendingUp className={`w-6 h-6 mx-auto mb-2 ${probDefault <= 5 ? 'text-green-600' : probDefault <= 15 ? 'text-yellow-600' : 'text-red-600'}`} />
            <p className={`text-2xl font-bold ${probDefault <= 5 ? 'text-green-600' : probDefault <= 15 ? 'text-yellow-600' : 'text-red-600'}`}>
              {probDefault.toFixed(1)}%
            </p>
            <p className="text-sm font-medium text-gray-600">Default Prob</p>
          </div>
        </div>

        {/* Middle: Category Contributions */}
        <div className="space-y-3">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="w-4 h-4 text-purple-600" />
            <p className="text-sm font-semibold text-gray-700">Category Contributions</p>
          </div>
          {Object.keys(categoryContributions).length > 0 ? (
            <div className="space-y-2">
              {Object.entries(categoryContributions).map(([category, value], idx) => (
                <div key={category} className="flex items-center gap-2">
                  <div className="w-24 text-xs font-medium text-gray-600 truncate" title={categoryLabels[category] || category}>
                    {categoryLabels[category]?.split(' ')[0] || category}
                  </div>
                  <div className="flex-1 bg-gray-200 rounded-full h-3 overflow-hidden">
                    <div
                      className={`h-full ${getCategoryColor(idx)} transition-all duration-500`}
                      style={{ width: `${Math.min(value * 100 * 4, 100)}%` }}
                    />
                  </div>
                  <div className="w-12 text-right text-xs font-semibold text-gray-900">
                    {(value * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <p className="text-sm text-gray-500">Generate score to see category breakdown</p>
            </div>
          )}
        </div>

        {/* Right: Grade Table & Recommendation */}
        <div className="space-y-4">
          {/* Risk Grade Table */}
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-sm font-semibold text-gray-700 mb-3">Score Range</p>
            <table className="w-full text-xs">
              <thead>
                <tr className="text-gray-500">
                  <th className="text-left py-1">CIBIL</th>
                  <th className="text-center py-1">Score</th>
                  <th className="text-right py-1">Grade</th>
                </tr>
              </thead>
              <tbody>
                {gradeTable.map((row, idx) => (
                  <tr 
                    key={idx}
                    className={risk.grade === row.grade ? 'bg-blue-500 text-white rounded' : 'text-gray-700'}
                  >
                    <td className="py-1.5 px-2 rounded-l-md">{row.cibil}</td>
                    <td className="py-1.5 px-2 text-center">{row.score}</td>
                    <td className="py-1.5 px-2 text-right font-bold rounded-r-md">{row.grade}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Recommendation */}
          <div className={`${recStyle.bg} ${recStyle.border} border rounded-xl p-4 flex items-center gap-3`}>
            <RecIcon className={`w-8 h-8 ${recStyle.text}`} />
            <div>
              <p className={`font-bold text-sm ${recStyle.text}`}>{recommendation}</p>
              <p className={`text-xs ${recStyle.text} opacity-80`}>
                {recommendation.includes("Fast Track") && "Fast track approval"}
                {recommendation.includes("Approve") && !recommendation.includes("Fast") && "Standard processing"}
                {recommendation.includes("Conditional") && "Verification needed"}
                {recommendation.includes("Decline") && "Not eligible"}
                {recommendation.includes("Review") && "Manual assessment"}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
