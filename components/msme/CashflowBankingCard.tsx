"use client"

import { Wallet, TrendingUp, TrendingDown, Clock, AlertCircle, Building } from "lucide-react"

interface CashflowBankingCardProps {
  msme: any
}

export default function CashflowBankingCard({ msme }: CashflowBankingCardProps) {
  const features = msme.features || {}
  const cashflow = msme.cashflow || {}
  
  // Mock bank accounts data
  const bankAccounts = [
    { bank: 'HDFC Bank', accountType: 'Current', balance: features.avg_bank_balance * 0.6 || 0, status: 'Active' },
    { bank: 'ICICI Bank', accountType: 'Current', balance: features.avg_bank_balance * 0.3 || 0, status: 'Active' },
    { bank: 'Axis Bank', accountType: 'Savings', balance: features.avg_bank_balance * 0.1 || 0, status: 'Active' }
  ]

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

  const avgBalance = features.avg_bank_balance || cashflow.avg_bank_balance || 0
  const balanceTrend = features.bank_balance_trend || cashflow.bank_balance_trend || 0
  const inflowOutflowRatio = features.weekly_inflow_outflow_ratio || cashflow.weekly_inflow_outflow_ratio || 0
  const cashBufferDays = features.cash_buffer_days || cashflow.cash_buffer_days || 0
  const overdraftDays = features.overdraft_days_count || cashflow.overdraft_days_count || 0
  const negativeBalanceDays = features.negative_balance_days || cashflow.negative_balance_days || 0

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Wallet className="w-5 h-5 text-blue-600" />
        <h3 className="text-lg font-semibold text-gray-900">C. Cash Flow & Banking (25%)</h3>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4">
          <p className="text-xs font-semibold text-blue-900 uppercase">Avg Bank Balance</p>
          <p className="text-2xl font-bold text-blue-600 mt-1">{formatCurrency(avgBalance)}</p>
        </div>
        <div className={`bg-gradient-to-br rounded-xl p-4 ${balanceTrend >= 0 ? 'from-green-50 to-emerald-50' : 'from-red-50 to-rose-50'}`}>
          <p className="text-xs font-semibold uppercase">Balance Trend</p>
          <div className="flex items-center gap-2 mt-1">
            {balanceTrend >= 0 ? (
              <TrendingUp className="w-5 h-5 text-green-600" />
            ) : (
              <TrendingDown className="w-5 h-5 text-red-600" />
            )}
            <p className={`text-2xl font-bold ${balanceTrend >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatPercent(Math.abs(balanceTrend))}
            </p>
          </div>
        </div>
      </div>

      {/* Bank Accounts */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
          <Building className="w-4 h-4 text-gray-500" />
          Connected Bank Accounts
        </h4>
        <div className="space-y-2">
          {bankAccounts.map((account, idx) => (
            <div key={idx} className="bg-gray-50 rounded-lg p-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white font-bold text-sm">
                  {account.bank.substring(0, 2).toUpperCase()}
                </div>
                <div>
                  <p className="font-semibold text-gray-900 text-sm">{account.bank}</p>
                  <p className="text-xs text-gray-500">{account.accountType} Account</p>
                </div>
              </div>
              <div className="text-right">
                <p className="font-bold text-gray-900">{formatCurrency(account.balance)}</p>
                <p className="text-xs text-green-600">{account.status}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Cash Flow Health */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
          <Wallet className="w-4 h-4 text-gray-500" />
          Cash Flow Health
        </h4>
        <div className="grid grid-cols-2 gap-3">
          <div className={`bg-gray-50 rounded-lg p-3 ${inflowOutflowRatio >= 1.2 ? 'border-2 border-green-500' : inflowOutflowRatio >= 1.0 ? 'border-2 border-yellow-500' : 'border-2 border-red-500'}`}>
            <p className="text-gray-600 text-xs mb-1">Inflow/Outflow Ratio</p>
            <p className={`text-2xl font-bold ${inflowOutflowRatio >= 1.2 ? 'text-green-600' : inflowOutflowRatio >= 1.0 ? 'text-yellow-600' : 'text-red-600'}`}>
              {inflowOutflowRatio.toFixed(2)}x
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {inflowOutflowRatio >= 1.2 ? 'Excellent' : inflowOutflowRatio >= 1.0 ? 'Good' : 'Needs Attention'}
            </p>
          </div>
          <div className={`bg-gray-50 rounded-lg p-3 ${cashBufferDays >= 60 ? 'border-2 border-green-500' : cashBufferDays >= 30 ? 'border-2 border-yellow-500' : 'border-2 border-red-500'}`}>
            <p className="text-gray-600 text-xs mb-1">Cash Buffer Days</p>
            <p className={`text-2xl font-bold ${cashBufferDays >= 60 ? 'text-green-600' : cashBufferDays >= 30 ? 'text-yellow-600' : 'text-red-600'}`}>
              {cashBufferDays.toFixed(0)} days
            </p>
          </div>
        </div>
      </div>

      {/* Risk Indicators */}
      {(overdraftDays > 0 || negativeBalanceDays > 0) && (
        <div className="mb-6">
          <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
            <AlertCircle className="w-4 h-4 text-red-500" />
            Risk Indicators
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {overdraftDays > 0 && (
              <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                <p className="text-red-900 text-xs mb-1">Overdraft Days</p>
                <p className="text-xl font-bold text-red-600">{overdraftDays} days</p>
                <p className="text-xs text-red-700 mt-1">
                  Avg: {formatCurrency(features.overdraft_amount_avg || cashflow.overdraft_amount_avg || 0)}
                </p>
              </div>
            )}
            {negativeBalanceDays > 0 && (
              <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                <p className="text-red-900 text-xs mb-1">Negative Balance Days</p>
                <p className="text-xl font-bold text-red-600">{negativeBalanceDays} days</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Banking Details */}
      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Avg Daily Closing Balance</span>
          <span className="font-semibold">
            {formatCurrency(features.avg_daily_closing_balance || cashflow.avg_daily_closing_balance || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Daily Min Balance Pattern</span>
          <span className="font-semibold">
            {formatCurrency(features.daily_min_balance_pattern || cashflow.daily_min_balance_pattern || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Cash Flow Regularity</span>
          <span className="font-semibold">
            {formatPercent(features.cashflow_regularity_score || cashflow.cashflow_regularity_score || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Consistent Deposits Score</span>
          <span className="font-semibold">
            {formatPercent(features.consistent_deposits_score || cashflow.consistent_deposits_score || 0)}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 mt-2">
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
            <span className="text-gray-600 text-xs">Receivables Aging</span>
            <span className="font-semibold text-xs">
              {(features.receivables_aging_days || cashflow.receivables_aging_days || 0).toFixed(0)} days
            </span>
          </div>
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
            <span className="text-gray-600 text-xs">Payables Aging</span>
            <span className="font-semibold text-xs">
              {(features.payables_aging_days || cashflow.payables_aging_days || 0).toFixed(0)} days
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}



