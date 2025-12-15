"use client"
import { useState, useEffect } from "react"
import { mockApi } from "@/lib/mockApi"
import { Download, Info } from "lucide-react"
import FeatureImportanceChart from "@/components/FeatureImportanceChart"
import SHAPWaterfall from "@/components/SHAPWaterfall"

export default function Explainability() {
  const [importances, setImportances] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

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

  if (loading) return <div className="flex items-center justify-center h-96">Loading...</div>

  const mockSHAPData = [
    { feature: "Income Stability", value: 85, impact: "positive" },
    { feature: "Average Balance", value: 72, impact: "positive" },
    { feature: "EMI Burden", value: -45, impact: "negative" },
    { feature: "Face Match %", value: 58, impact: "positive" },
    { feature: "Recent Inquiries", value: -28, impact: "negative" },
    { feature: "Budgeting Score", value: 65, impact: "positive" },
  ]

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
        <h2 className="text-lg font-semibold text-gray-900 mb-4">SHAP Values (Example Consumer)</h2>
        <p className="text-sm text-gray-600 mb-6">Shows positive and negative feature contributions to final score</p>
        <SHAPWaterfall data={mockSHAPData} />
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
