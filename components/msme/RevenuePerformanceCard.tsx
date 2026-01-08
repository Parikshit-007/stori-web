"use client"

import { TrendingUp, DollarSign, BarChart3, TrendingDown } from "lucide-react"

interface RevenuePerformanceCardProps {
  msme: any
}

export default function RevenuePerformanceCard({ msme }: RevenuePerformanceCardProps) {
  const features = msme.features || {}
  const revenue = msme.revenue || {}

  const formatCurrency = (amount: number) => {
    if (!amount) return '₹0'
    if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)}Cr`
    if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`
    if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`
    return `₹${amount.toFixed(0)}`
  }

  const formatPercent = (val: number) => {
    return `${(val * 100).toFixed(1)}%`
  }

  const weeklyGTV = features.weekly_gtv || revenue.weekly_gtv || 0
  const monthlyGTV = features.monthly_gtv || revenue.monthly_gtv || weeklyGTV * 4
  const profitMargin = features.profit_margin || revenue.profit_margin || 0
  const revenueGrowthMoM = features.revenue_growth_rate_mom || revenue.revenue_growth_rate_mom || 0
  const revenueGrowthQoQ = features.revenue_growth_rate_qoq || revenue.revenue_growth_rate_qoq || 0

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <TrendingUp className="w-5 h-5 text-green-600" />
        <h3 className="text-lg font-semibold text-gray-900">B. Revenue & Business Performance (20%)</h3>
      </div>

      {/* Key Revenue Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4">
          <p className="text-xs font-semibold text-green-900 uppercase">Weekly GTV</p>
          <p className="text-2xl font-bold text-green-600 mt-1">{formatCurrency(weeklyGTV)}</p>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4">
          <p className="text-xs font-semibold text-blue-900 uppercase">Monthly GTV</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">{formatCurrency(monthlyGTV)}</p>
        </div>
      </div>

      {/* Transaction Metrics */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <p className="text-gray-500 text-xs">Daily Transactions</p>
          <p className="font-bold text-lg">
            {features.transaction_count_daily || revenue.transaction_count_daily || 0}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <p className="text-gray-500 text-xs">Avg Transaction</p>
          <p className="font-bold text-lg">
            {formatCurrency(features.avg_transaction_value || revenue.avg_transaction_value || 0)}
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3 text-center">
          <p className="text-gray-500 text-xs">Profit Margin</p>
          <p className={`font-bold text-lg ${profitMargin >= 0.1 ? 'text-green-600' : profitMargin >= 0 ? 'text-yellow-600' : 'text-red-600'}`}>
            {formatPercent(profitMargin)}
          </p>
        </div>
      </div>

      {/* Growth Metrics */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-gray-500" />
          Growth Trends
        </h4>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-gray-600 text-sm">MoM Growth</span>
              {revenueGrowthMoM >= 0 ? (
                <TrendingUp className="w-4 h-4 text-green-600" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-600" />
              )}
            </div>
            <p className={`text-xl font-bold ${revenueGrowthMoM >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercent(revenueGrowthMoM)}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-gray-600 text-sm">QoQ Growth</span>
              {revenueGrowthQoQ >= 0 ? (
                <TrendingUp className="w-4 h-4 text-green-600" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-600" />
              )}
            </div>
            <p className={`text-xl font-bold ${revenueGrowthQoQ >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercent(revenueGrowthQoQ)}
            </p>
          </div>
        </div>
      </div>

      {/* Performance Indicators */}
      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Revenue Concentration</span>
          <span className="font-semibold">
            {formatPercent(features.revenue_concentration_score || revenue.revenue_concentration_score || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Peak Day Dependency</span>
          <span className="font-semibold">
            {formatPercent(features.peak_day_dependency || revenue.peak_day_dependency || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Inventory Turnover</span>
          <span className="font-semibold">
            {(features.inventory_turnover_ratio || revenue.inventory_turnover_ratio || 0).toFixed(1)}x
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Total Assets</span>
          <span className="font-semibold">
            {formatCurrency(features.total_assets_value || revenue.total_assets_value || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Operational Leverage</span>
          <span className="font-semibold">
            {(features.operational_leverage_ratio || revenue.operational_leverage_ratio || 0).toFixed(2)}x
          </span>
        </div>
      </div>
    </div>
  )
}



