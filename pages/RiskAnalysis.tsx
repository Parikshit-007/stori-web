"use client"
import { useState, useEffect } from "react"
import { mockApi } from "@/lib/mockApi"
import { AlertTriangle, TrendingDown, Zap } from "lucide-react"
import RiskSegmentationChart from "@/components/RiskSegmentationChart"
import RiskAlertsList from "@/components/RiskAlertsList"

export default function RiskAnalysis() {
  const [stats, setStats] = useState<any>(null)
  const [highRiskConsumers, setHighRiskConsumers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsData = await mockApi.getPortfolioStats()
        setStats(statsData)
        const consumers = await mockApi.getConsumers({ riskCategory: "High" })
        setHighRiskConsumers(consumers)
      } catch (error) {
        console.error("Error fetching risk data:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [])

  if (loading) return <div className="flex items-center justify-center h-96">Loading...</div>

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Risk Analysis</h1>
        <p className="text-gray-600 mt-1">Portfolio-level risk signals and anomalies</p>
      </div>

      {/* Alert Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-semibold text-red-900">HIGH RISK CONSUMERS</p>
            <AlertTriangle className="w-5 h-5 text-red-600" />
          </div>
          <p className="text-3xl font-bold text-red-600">{stats.riskDistribution.high.count}</p>
          <p className="text-xs text-red-700 mt-2">Require immediate attention</p>
        </div>

        <div className="bg-orange-50 border border-orange-200 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-semibold text-orange-900">FALLING BALANCES</p>
            <TrendingDown className="w-5 h-5 text-orange-600" />
          </div>
          <p className="text-3xl font-bold text-orange-600">23</p>
          <p className="text-xs text-orange-700 mt-2">Down 20%+ in last 30 days</p>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm font-semibold text-yellow-900">HIGH EMI BURDEN</p>
            <Zap className="w-5 h-5 text-yellow-600" />
          </div>
          <p className="text-3xl font-bold text-yellow-600">18</p>
          <p className="text-xs text-yellow-700 mt-2">FOIR &gt; 50%</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Segmentation</h2>
          <RiskSegmentationChart data={stats.riskDistribution} />
        </div>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Persona Risk Profiles</h2>
          <div className="space-y-3">
            {stats.defaultProbabilityByPersona.map((item: any) => (
              <div key={item.persona}>
                <div className="flex justify-between mb-1">
                  <span className="text-sm font-medium text-gray-700">{item.persona}</span>
                  <span className="text-sm font-semibold text-gray-900">{(item.defaultProb * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${
                      item.defaultProb > 0.15
                        ? "bg-red-500"
                        : item.defaultProb > 0.05
                          ? "bg-yellow-500"
                          : "bg-green-500"
                    }`}
                    style={{ width: `${Math.min(item.defaultProb * 1000, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* High Risk Consumer List */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">High Risk Consumers</h2>
        <RiskAlertsList consumers={highRiskConsumers} />
      </div>
    </div>
  )
}
