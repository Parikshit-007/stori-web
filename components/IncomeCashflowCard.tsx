"use client"

import { TrendingUp, Wallet, PiggyBank, Clock, Tag, AlertCircle } from "lucide-react"

interface IncomeCashflowCardProps {
  consumer: any
}

export default function IncomeCashflowCard({ consumer }: IncomeCashflowCardProps) {
  const { income } = consumer

  const getReliabilityColor = (tag: string) => {
    switch (tag) {
      case "salary": return "bg-green-100 text-green-700"
      case "gig": return "bg-amber-100 text-amber-700"
      case "passive": return "bg-blue-100 text-blue-700"
      default: return "bg-gray-100 text-gray-700"
    }
  }

  const formatAmount = (amt: number) => {
    if (amt >= 100000) return `₹${(amt / 100000).toFixed(1)}L`
    if (amt >= 1000) return `₹${(amt / 1000).toFixed(0)}K`
    return `₹${amt}`
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <TrendingUp className="w-5 h-5 text-green-600" />
        <h3 className="text-lg font-semibold text-gray-900">2. Income & Cashflow Strength</h3>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-3 text-center">
          <p className="text-xs font-semibold text-green-900 uppercase">Monthly Income</p>
          <p className="text-xl font-bold text-green-600 mt-1">{formatAmount(income.monthlyIncome)}</p>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-3 text-center">
          <p className="text-xs font-semibold text-blue-900 uppercase">Monthly Inflow</p>
          <p className="text-xl font-bold text-blue-600 mt-1">{formatAmount(income.monthlyInflow || income.monthlyIncome)}</p>
        </div>
        <div className="bg-gradient-to-br from-red-50 to-rose-50 rounded-xl p-3 text-center">
          <p className="text-xs font-semibold text-red-900 uppercase">Monthly Outflow</p>
          <p className="text-xl font-bold text-red-600 mt-1">{formatAmount(income.monthlyOutflow || income.survivability?.monthlyOutflow)}</p>
        </div>
      </div>

      {/* (A) Account Balances */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Wallet className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(A) Account Balances</h4>
          <span className="ml-auto text-sm font-bold text-green-600">Avg: {formatAmount(income.averageBalance || income.totalBalance)}</span>
        </div>
        <div className="space-y-2 mb-2">
          {income.accountBalances?.map((acc: any, idx: number) => (
            <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded-lg text-sm">
              <div>
                <span className="text-gray-600">{acc.bank}</span>
                {acc.accountNo && <span className="text-gray-400 text-xs ml-2">({acc.accountNo})</span>}
              </div>
              <span className="font-bold">₹{acc.balance?.toLocaleString()}</span>
            </div>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="p-2 bg-blue-50 rounded-lg flex justify-between">
            <span className="text-blue-700 text-xs">Txn Value (excl. P2P)</span>
            <span className="font-bold text-blue-700">{formatAmount(income.transactionValueExcludingP2P)}</span>
          </div>
          <div className={`p-2 rounded-lg flex justify-between ${income.oneOffTransactionInflation ? 'bg-red-50' : 'bg-green-50'}`}>
            <span className={`text-xs ${income.oneOffTransactionInflation ? 'text-red-700' : 'text-green-700'}`}>One-off Inflation</span>
            <span className={`font-bold ${income.oneOffTransactionInflation ? 'text-red-700' : 'text-green-700'}`}>
              {income.oneOffTransactionInflation ? 'Yes ⚠️' : 'No ✓'}
            </span>
          </div>
        </div>
      </div>

      {/* (B) Income Volatility & (C) Survivability */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-50 rounded-xl p-4">
          <p className="text-xs font-semibold text-gray-600 uppercase mb-2">(B) Income Volatility</p>
          <p className={`text-2xl font-bold ${income.incomeVolatility?.volatilityIndex <= 15 ? 'text-green-600' : income.incomeVolatility?.volatilityIndex <= 25 ? 'text-amber-600' : 'text-red-600'}`}>
            {income.incomeVolatility?.volatilityIndex}%
          </p>
          <p className="text-xs text-gray-500 mt-1">Std Dev / Avg Income</p>
        </div>
        <div className="bg-gray-50 rounded-xl p-4">
          <div className="flex items-center gap-1 mb-2">
            <PiggyBank className="w-4 h-4 text-gray-500" />
            <p className="text-xs font-semibold text-gray-600 uppercase">(C) Survivability</p>
          </div>
          <p className={`text-2xl font-bold ${income.survivability?.months >= 12 ? 'text-green-600' : income.survivability?.months >= 6 ? 'text-amber-600' : 'text-red-600'}`}>
            {income.survivability?.months?.toFixed(1)} mo
          </p>
          <p className="text-xs text-gray-500 mt-1">Emergency: {formatAmount(income.survivability?.emergencyFunds || income.totalBalance)}</p>
        </div>
      </div>

      {/* (D) Income Sources */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Tag className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(D) Income Source Reliability</h4>
        </div>
        <div className="space-y-2">
          {income.incomeSources?.map((src: any, idx: number) => (
            <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded-lg text-sm">
              <div className="flex items-center gap-2">
                <span className={`px-2 py-0.5 rounded text-xs font-semibold ${getReliabilityColor(src.tag)}`}>
                  {src.reliability}
                </span>
                <span className="text-gray-600">{src.source}</span>
              </div>
              <span className="font-bold">{formatAmount(src.amount)}</span>
            </div>
          ))}
        </div>
      </div>

      {/* (E) Expense Categories */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 text-sm mb-3">(E) Expense Rigidity Score</h4>
        <div className="space-y-2">
          {Object.entries(income.expenseCategories || {}).map(([key, val]: [string, any]) => (
            <div key={key} className="flex items-center gap-2">
              <div className="flex-1 bg-gray-100 rounded-full h-2 overflow-hidden">
                <div 
                  className={`h-full ${key === 'fixedEssential' ? 'bg-blue-500' : key === 'variableEssential' ? 'bg-green-500' : key === 'entertainment' ? 'bg-purple-500' : key === 'shopping' ? 'bg-pink-500' : 'bg-amber-500'}`}
                  style={{ width: `${val.percentage}%` }}
                />
              </div>
              <span className="text-xs text-gray-600 w-28 capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
              <span className="text-xs font-bold w-16 text-right">{val.percentage}% ({formatAmount(val.amount)})</span>
            </div>
          ))}
        </div>
      </div>

      {/* Salary Retention / Impulse */}
      <div className="bg-gray-50 rounded-xl p-4">
        <div className="flex items-center gap-2 mb-2">
          <Clock className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">Salary Retention (Impulse Check)</h4>
        </div>
        <div className="grid grid-cols-4 gap-2 text-sm">
          <div className="text-center">
            <p className="text-gray-500 text-xs">Week 1 Bal</p>
            <p className="font-bold">{formatAmount(income.salaryRetention?.firstWeekBalance)}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500 text-xs">Week 4 Bal</p>
            <p className="font-bold">{formatAmount(income.salaryRetention?.lastWeekBalance)}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500 text-xs">Days in A/c</p>
            <p className="font-bold">{income.salaryRetention?.daysInAccount || 'N/A'}</p>
          </div>
          <div className="text-center">
            <p className="text-gray-500 text-xs">Impulse Score</p>
            <p className={`font-bold ${(income.salaryRetention?.impulseScore || 0) <= 30 ? 'text-green-600' : (income.salaryRetention?.impulseScore || 0) <= 50 ? 'text-amber-600' : 'text-red-600'}`}>
              {income.salaryRetention?.impulseScore}
            </p>
          </div>
        </div>
        <p className={`text-xs mt-2 font-medium ${income.salaryRetention?.impatienceLevel === 'Low' ? 'text-green-600' : income.salaryRetention?.impatienceLevel === 'Medium' ? 'text-amber-600' : 'text-red-600'}`}>
          Impatience Level: {income.salaryRetention?.impatienceLevel || (income.salaryRetention?.impulseScore <= 30 ? 'Low' : income.salaryRetention?.impulseScore <= 50 ? 'Medium' : 'High')}
        </p>
      </div>
    </div>
  )
}
