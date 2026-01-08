"use client"

import { Activity, TrendingUp, Zap, CheckCircle, AlertTriangle } from "lucide-react"

interface TransactionsUtilityCardProps {
  consumer: any
}

export default function TransactionsUtilityCard({ consumer }: TransactionsUtilityCardProps) {
  const { transactions } = consumer

  const getStatusColor = (status: string) => {
    if (status === "Normal" || status === "Verified") return "bg-green-100 text-green-700 border-green-200"
    if (status === "Monitor" || status.includes("Variable")) return "bg-amber-100 text-amber-700 border-amber-200"
    return "bg-red-100 text-red-700 border-red-200"
  }

  const getConsistencyColor = (val: number) => {
    if (val >= 90) return "text-green-600 bg-green-50"
    if (val >= 75) return "text-amber-600 bg-amber-50"
    return "text-red-600 bg-red-50"
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Activity className="w-5 h-5 text-cyan-600" />
        <h3 className="text-lg font-semibold text-gray-900">6. Transactions & Utility Signals</h3>
      </div>

      {/* (A) Spike Detector */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Zap className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(A) Spike Detector</h4>
          <span className={`ml-auto px-3 py-1 rounded-full text-xs font-bold border ${getStatusColor(transactions.spikeDetector?.status || 'Normal')}`}>
            {transactions.spikeDetector?.status || 'Normal'}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">UPI Volume Change</p>
            <p className={`text-xl font-bold ${(transactions.spikeDetector?.upiVolumeChange || 0) <= 10 ? 'text-green-600' : (transactions.spikeDetector?.upiVolumeChange || 0) <= 20 ? 'text-amber-600' : 'text-red-600'}`}>
              {(transactions.spikeDetector?.upiVolumeChange || 0) > 0 ? '+' : ''}{transactions.spikeDetector?.upiVolumeChange || 0}%
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">Balance Drop Alert</p>
            <p className={`text-xl font-bold flex items-center gap-1 ${transactions.spikeDetector?.balanceDropAlert ? 'text-red-600' : 'text-green-600'}`}>
              {transactions.spikeDetector?.balanceDropAlert ? (
                <><AlertTriangle className="w-5 h-5" /> Yes</>
              ) : (
                <><CheckCircle className="w-5 h-5" /> No</>
              )}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">New Merchants Added</p>
            <p className={`text-xl font-bold ${(transactions.spikeDetector?.newMerchantsAdded || 0) <= 5 ? 'text-green-600' : 'text-amber-600'}`}>
              {transactions.spikeDetector?.newMerchantsAdded || 0}
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">EMI Failures</p>
            <p className={`text-xl font-bold ${(transactions.spikeDetector?.emiFailures || 0) === 0 ? 'text-green-600' : 'text-red-600'}`}>
              {transactions.spikeDetector?.emiFailures || 0}
            </p>
          </div>
        </div>
      </div>

      {/* (B) Income Authenticity */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <TrendingUp className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(B) Income Authenticity</h4>
          <span className={`ml-auto px-3 py-1 rounded-full text-xs font-bold border ${getStatusColor(transactions.incomeAuthenticity?.status || 'N/A')}`}>
            {transactions.incomeAuthenticity?.status || 'N/A'}
          </span>
        </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">Inflow Time Consistency</p>
            <p className={`text-xl font-bold ${(transactions.incomeAuthenticity?.inflowTimeConsistency || 0) >= 90 ? 'text-green-600' : (transactions.incomeAuthenticity?.inflowTimeConsistency || 0) >= 75 ? 'text-amber-600' : 'text-red-600'}`}>
              {transactions.incomeAuthenticity?.inflowTimeConsistency || 0}%
            </p>
            <p className="text-xs text-gray-400">Salary on same date</p>
        </div>
      </div>

      {/* (C) Utility Payments Table */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <CheckCircle className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(C) Utility Payment Consistency</h4>
          <span className={`ml-auto px-3 py-1 rounded-full text-xs font-bold ${(transactions.utilityPayments?.overallScore || 0) >= 90 ? 'bg-green-100 text-green-700' : (transactions.utilityPayments?.overallScore || 0) >= 75 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}`}>
            Overall: {transactions.utilityPayments?.overallScore || 0}%
          </span>
        </div>
        
        {/* Table Format */}
        <div className="overflow-hidden rounded-lg border border-gray-200">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-50">
                <th className="px-4 py-2 text-left font-semibold text-gray-700">Utility Type</th>
                <th className="px-4 py-2 text-right font-semibold text-gray-700">Consistency</th>
                <th className="px-4 py-2 text-center font-semibold text-gray-700">Status</th>
              </tr>
            </thead>
            <tbody>
              {[
                { label: "Recharge", value: transactions.utilityPayments?.rechargeConsistency },
                { label: "Electricity", value: transactions.utilityPayments?.electricityConsistency },
                { label: "Rent", value: transactions.utilityPayments?.rentConsistency },
                { label: "Subscriptions", value: transactions.utilityPayments?.subscriptionConsistency },
              ].map((item, idx) => (
                <tr key={idx} className="border-t border-gray-100">
                  <td className="px-4 py-3 text-gray-700">{item.label}</td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <div className="w-20 bg-gray-200 rounded-full h-1.5">
                        <div 
                          className={`h-1.5 rounded-full ${(item.value || 0) >= 90 ? 'bg-green-500' : (item.value || 0) >= 75 ? 'bg-amber-500' : 'bg-red-500'}`}
                          style={{ width: `${item.value || 0}%` }}
                        />
                      </div>
                      <span className="font-bold w-12">{item.value || 0}%</span>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-center">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${getConsistencyColor(item.value || 0)}`}>
                      {(item.value || 0) >= 90 ? 'Excellent' : (item.value || 0) >= 75 ? 'Good' : 'Needs Review'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
