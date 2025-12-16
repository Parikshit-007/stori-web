"use client"

import { BarChart3, CircleDollarSign, TrendingUp, CheckCircle, XCircle, AlertTriangle } from "lucide-react"

interface SummaryCardProps {
  consumer: any
}

export default function SummaryCard({ consumer }: SummaryCardProps) {
  const { summary } = consumer

  const getRiskGrade = (score: number) => {
    if (score >= 85) return { grade: 'A', cibil: '800+', color: 'text-green-600' }
    if (score >= 75) return { grade: 'B', cibil: '740-800', color: 'text-green-600' }
    if (score >= 56) return { grade: 'C', cibil: '700-740', color: 'text-yellow-600' }
    if (score >= 40) return { grade: 'D', cibil: '650-699', color: 'text-orange-600' }
    return { grade: 'E', cibil: '<650', color: 'text-red-600' }
  }

  const risk = getRiskGrade(summary.financialHealthScore)

  const getRecommendationStyle = (rec: string) => {
    if (rec === "Pre-Approved" || rec === "Approved") return { bg: "bg-green-50", border: "border-green-200", text: "text-green-700", icon: CheckCircle }
    if (rec === "Conditional Approval") return { bg: "bg-yellow-50", border: "border-yellow-200", text: "text-yellow-700", icon: AlertTriangle }
    return { bg: "bg-red-50", border: "border-red-200", text: "text-red-700", icon: XCircle }
  }

  const recStyle = getRecommendationStyle(summary.recommendation)
  const RecIcon = recStyle.icon

  const gradeTable = [
    { cibil: '800+', score: '85-100', grade: 'A' },
    { cibil: '740-800', score: '75-84', grade: 'B' },
    { cibil: '700-740', score: '56-74', grade: 'C' },
    { cibil: '650-699', score: '40-55', grade: 'D' },
    { cibil: '<650', score: '0-39', grade: 'E' },
  ]

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <BarChart3 className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">Summary</h3>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left: Key Metrics */}
        <div className="grid grid-cols-2 gap-4">
          {/* Financial Health Score */}
          <div className="bg-gray-50 rounded-xl p-4 text-center">
            <div className="relative inline-flex items-center justify-center mb-3">
              <svg className="w-20 h-20 transform -rotate-90">
                <circle cx="40" cy="40" r="35" stroke="#e5e7eb" strokeWidth="6" fill="none" />
                <circle
                  cx="40" cy="40" r="35"
                  stroke={summary.financialHealthScore >= 75 ? '#10b981' : summary.financialHealthScore >= 50 ? '#f59e0b' : '#ef4444'}
                  strokeWidth="6" fill="none"
                  strokeDasharray={`${summary.financialHealthScore * 2.2} 220`}
                  strokeLinecap="round"
                />
              </svg>
              <span className="absolute text-xl font-bold text-gray-900">{summary.financialHealthScore}</span>
            </div>
            <p className="text-sm font-medium text-gray-600">Financial Health Score</p>
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
              ₹{summary.maxLoanAmount >= 10000000 
                ? `${(summary.maxLoanAmount / 10000000).toFixed(1)}Cr` 
                : summary.maxLoanAmount >= 100000 
                  ? `${(summary.maxLoanAmount / 100000).toFixed(1)}L`
                  : `${(summary.maxLoanAmount / 1000).toFixed(0)}K`}
            </p>
            <p className="text-sm font-medium text-gray-600">Max Loan Amount</p>
          </div>

          {/* Default Probability */}
          <div className="bg-gray-50 rounded-xl p-4 text-center flex flex-col justify-center">
            <TrendingUp className={`w-6 h-6 mx-auto mb-2 ${summary.probabilityOfDefault <= 5 ? 'text-green-600' : summary.probabilityOfDefault <= 15 ? 'text-yellow-600' : 'text-red-600'}`} />
            <p className={`text-2xl font-bold ${summary.probabilityOfDefault <= 5 ? 'text-green-600' : summary.probabilityOfDefault <= 15 ? 'text-yellow-600' : 'text-red-600'}`}>
              {summary.probabilityOfDefault}%
            </p>
            <p className="text-sm font-medium text-gray-600">Default Probability</p>
          </div>
        </div>

        {/* Right: Grade Table & Recommendation */}
        <div className="space-y-4">
          {/* Risk Grade Table */}
          <div className="bg-gray-50 rounded-xl p-4">
            <p className="text-sm font-semibold text-gray-700 mb-3">Proximity to CIBIL</p>
            <table className="w-full text-xs">
              <thead>
                <tr className="text-gray-500">
                  <th className="text-left py-1">CIBIL</th>
                  <th className="text-center py-1">Health Score</th>
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
          <div className={`${recStyle.bg} ${recStyle.border} border rounded-xl p-4 flex items-center gap-4`}>
            <RecIcon className={`w-10 h-10 ${recStyle.text}`} />
            <div>
              <p className={`font-bold text-lg ${recStyle.text}`}>{summary.recommendation}</p>
              <p className={`text-sm ${recStyle.text} opacity-80`}>
                {summary.recommendation === "Pre-Approved" && "Excellent profile - Fast track"}
                {summary.recommendation === "Approved" && "Good profile - Standard processing"}
                {summary.recommendation === "Conditional Approval" && "Additional verification needed"}
                {summary.recommendation === "High Risk - Manual Review" && "Manual assessment required"}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
