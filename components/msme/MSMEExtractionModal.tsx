"use client"

import { CheckCircle, Database, FileText, Shield, TrendingUp, Server, Brain } from "lucide-react"

interface MSMEExtractionModalProps {
  businessName: string
  progress: number
  completedSources: number[]
}

const dataSources = [
  { name: "Bank Statements", icon: FileText, delay: 0 },
  { name: "GST & Tax Filings", icon: Shield, delay: 4000 },
  { name: "Transaction Analysis", icon: TrendingUp, delay: 8000 },
  { name: "Business Verification", icon: Database, delay: 12000 },
  { name: "ML Model Scoring", icon: Brain, delay: 16000 },
]

export default function MSMEExtractionModal({ businessName, progress, completedSources }: MSMEExtractionModalProps) {
  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-lg w-full mx-4 animate-in fade-in zoom-in duration-300">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
            <Server className="w-10 h-10 text-white" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Generating Credit Score</h2>
          <p className="text-gray-600">{businessName}</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-medium text-gray-700">Processing...</span>
            <span className="text-sm font-bold text-blue-600">{Math.round(progress)}%</span>
          </div>
          <div className="h-3 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 transition-all duration-300 ease-out rounded-full"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Data Sources */}
        <div className="space-y-3">
          {dataSources.map((source, index) => {
            const Icon = source.icon
            const isCompleted = completedSources.includes(index)
            const isActive = !isCompleted && completedSources.includes(index - 1)

            return (
              <div
                key={index}
                className={`flex items-center gap-3 p-3 rounded-lg border transition-all duration-300 ${
                  isCompleted
                    ? 'bg-green-50 border-green-200'
                    : isActive
                    ? 'bg-blue-50 border-blue-200 animate-pulse'
                    : 'bg-gray-50 border-gray-200'
                }`}
              >
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    isCompleted
                      ? 'bg-green-500'
                      : isActive
                      ? 'bg-blue-500'
                      : 'bg-gray-300'
                  }`}
                >
                  {isCompleted ? (
                    <CheckCircle className="w-5 h-5 text-white" />
                  ) : (
                    <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-gray-500'}`} />
                  )}
                </div>
                <div className="flex-1">
                  <p
                    className={`font-medium ${
                      isCompleted
                        ? 'text-green-700'
                        : isActive
                        ? 'text-blue-700'
                        : 'text-gray-600'
                    }`}
                  >
                    {source.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {isCompleted ? 'Completed' : isActive ? 'Processing...' : 'Pending'}
                  </p>
                </div>
              </div>
            )
          })}
        </div>

        <div className="mt-6 text-center text-sm text-gray-500">
          Analyzing business data with ML models...
        </div>
      </div>
    </div>
  )
}

