"use client"

import { CreditCard, CheckCircle, XCircle, AlertTriangle, Clock } from "lucide-react"

interface CreditRepaymentCardProps {
  msme: any
}

export default function CreditRepaymentCard({ msme }: CreditRepaymentCardProps) {
  const features = msme.features || {}
  const credit = msme.credit || {}

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

  const overdraftRepaymentRatio = features.overdraft_repayment_ontime_ratio || credit.overdraft_repayment_ontime_ratio || 0
  const bouncedChequesCount = features.bounced_cheques_count || credit.bounced_cheques_count || 0
  const bouncedChequesRate = features.bounced_cheques_rate || credit.bounced_cheques_rate || 0
  const previousDefaults = features.previous_defaults_count || credit.previous_defaults_count || 0
  const currentLoans = features.current_loans_outstanding || credit.current_loans_outstanding || 0
  const totalDebt = features.total_debt_amount || credit.total_debt_amount || 0

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <CreditCard className="w-5 h-5 text-purple-600" />
        <h3 className="text-lg font-semibold text-gray-900">D. Credit & Repayment Behavior (22%)</h3>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className={`bg-gradient-to-br rounded-xl p-4 ${overdraftRepaymentRatio >= 0.9 ? 'from-green-50 to-emerald-50' : overdraftRepaymentRatio >= 0.7 ? 'from-yellow-50 to-amber-50' : 'from-red-50 to-rose-50'}`}>
          <p className="text-xs font-semibold uppercase">On-Time Repayment Ratio</p>
          <p className={`text-2xl font-bold mt-1 ${overdraftRepaymentRatio >= 0.9 ? 'text-green-600' : overdraftRepaymentRatio >= 0.7 ? 'text-yellow-600' : 'text-red-600'}`}>
            {formatPercent(overdraftRepaymentRatio)}
          </p>
        </div>
        <div className={`bg-gradient-to-br rounded-xl p-4 ${bouncedChequesCount === 0 ? 'from-green-50 to-emerald-50' : bouncedChequesCount <= 2 ? 'from-yellow-50 to-amber-50' : 'from-red-50 to-rose-50'}`}>
          <p className="text-xs font-semibold uppercase">Bounced Cheques</p>
          <p className={`text-2xl font-bold mt-1 ${bouncedChequesCount === 0 ? 'text-green-600' : bouncedChequesCount <= 2 ? 'text-yellow-600' : 'text-red-600'}`}>
            {bouncedChequesCount}
          </p>
          {bouncedChequesRate > 0 && (
            <p className="text-xs text-gray-600 mt-1">Rate: {formatPercent(bouncedChequesRate)}</p>
          )}
        </div>
      </div>

      {/* Risk Indicators */}
      {(previousDefaults > 0 || bouncedChequesCount > 0) && (
        <div className="mb-6">
          <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            Risk Indicators
          </h4>
          <div className="grid grid-cols-2 gap-3">
            {previousDefaults > 0 && (
              <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                <p className="text-red-900 text-xs mb-1">Previous Defaults</p>
                <p className="text-xl font-bold text-red-600">{previousDefaults}</p>
              </div>
            )}
            {features.previous_writeoffs_count > 0 && (
              <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                <p className="text-red-900 text-xs mb-1">Write-offs</p>
                <p className="text-xl font-bold text-red-600">
                  {features.previous_writeoffs_count || credit.previous_writeoffs_count || 0}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Payment History - Last 6 Months */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
          <Clock className="w-4 h-4 text-gray-500" />
          Last 6 Months Payment History
        </h4>
        <div className="flex items-center gap-2 p-4 bg-gray-50 rounded-lg">
          {[...Array(6)].map((_, idx) => {
            // Mock data: alternating good/bad payments based on features
            const monthDefaults = idx === 2 || idx === 4 ? (previousDefaults > 0 || bouncedChequesCount > idx) : false
            return (
              <div key={idx} className="flex-1">
                <div 
                  className={`h-12 rounded-lg flex items-center justify-center text-white font-bold text-sm ${
                    monthDefaults ? 'bg-red-500' : 'bg-green-500'
                  }`}
                  title={monthDefaults ? 'Default/Delay' : 'On-Time'}
                >
                  {monthDefaults ? (
                    <XCircle className="w-5 h-5" />
                  ) : (
                    <CheckCircle className="w-5 h-5" />
                  )}
                </div>
                <p className="text-center text-xs text-gray-500 mt-1">
                  {['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'][idx]}
                </p>
              </div>
            )
          })}
        </div>
        <div className="mt-3 flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-green-500"></div>
            <span className="text-gray-600">On-Time Payment</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded bg-red-500"></div>
            <span className="text-gray-600">Default/Delay</span>
          </div>
        </div>
      </div>

      {/* Current Debt Status */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
          <CreditCard className="w-4 h-4 text-gray-500" />
          Current Debt Status
        </h4>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-600 text-xs mb-1">Loans Outstanding</p>
            <p className="text-xl font-bold">{currentLoans}</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-600 text-xs mb-1">Total Debt</p>
            <p className="text-xl font-bold">{formatCurrency(totalDebt)}</p>
          </div>
        </div>
      </div>

      {/* Payment Discipline */}
      <div className="space-y-2 text-sm">
        <h4 className="font-semibold text-gray-800 text-sm mb-2">Payment Discipline</h4>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Utility Payment On-Time</span>
          <span className="font-semibold">
            {formatPercent(features.utility_payment_ontime_ratio || credit.utility_payment_ontime_ratio || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Mobile Recharge Regularity</span>
          <span className="font-semibold">
            {formatPercent(features.mobile_recharge_regularity || credit.mobile_recharge_regularity || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Rent Payment Regularity</span>
          <span className="font-semibold">
            {formatPercent(features.rent_payment_regularity || credit.rent_payment_regularity || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Supplier Payment Regularity</span>
          <span className="font-semibold">
            {formatPercent(features.supplier_payment_regularity || credit.supplier_payment_regularity || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Historical Loan Utilization</span>
          <span className="font-semibold">
            {formatPercent(features.historical_loan_utilization || credit.historical_loan_utilization || 0)}
          </span>
        </div>
      </div>
    </div>
  )
}



