"use client"
import { useState, useEffect } from "react"
import { mockApi } from "@/lib/mockApi"
import { AlertCircle, TrendingUp, Users, Zap } from "lucide-react"
import StatCard from "@/components/StatCard"
import ScoreTrendChart from "@/components/ScoreTrendChart"
import DefaultRateChart from "@/components/DefaultRateChart"
import RiskDistributionChart from "@/components/RiskDistributionChart"
import RecentScoresTable from "@/components/RecentScoresTable"

export default function Dashboard() {
  const [stats, setStats] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await mockApi.getPortfolioStats()
        setStats(data)
      } catch (error) {
        console.error("Error fetching stats:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchStats()
  }, [])

  if (loading) {
    return <div className="flex items-center justify-center h-96">Loading...</div>
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Portfolio-level credit scoring metrics & insights</p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard icon={Users} label="Total Consumers Scored" value={stats.totalUsersScored} color="blue" />
        <StatCard icon={Zap} label="Average Credit Score" value={stats.averageScore} color="purple" />
        <StatCard
          icon={TrendingUp}
          label="Low Risk %"
          value={`${stats.riskDistribution.low.percentage.toFixed(1)}%`}
          color="green"
        />
        <StatCard icon={AlertCircle} label="High Risk Count" value={stats.riskDistribution.high.count} color="red" />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Average Score Trend (30 days)</h2>
          <ScoreTrendChart data={stats.averageScoreTrend} />
        </div>
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Default Probability by Persona</h2>
          <DefaultRateChart data={stats.defaultProbabilityByPersona} />
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Risk Distribution</h2>
          <RiskDistributionChart data={stats.riskDistribution} />
        </div>
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Scoring Events</h2>
          <RecentScoresTable data={stats.recentScoringEvents} />
        </div>
      </div>

      {/* Alerts Section */}
      <div className="bg-red-50 border border-red-200 rounded-2xl p-6">
        <div className="flex gap-4">
          <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="font-semibold text-red-900 mb-2">Active Alerts</h3>
            <ul className="space-y-1 text-sm text-red-700">
              <li>• 3 consumers with rapidly falling balances</li>
              <li>• 5 fraud signals detected in last 24 hours</li>
              <li>• 2 users with EMI-to-income ratio exceeding safe limits</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}
