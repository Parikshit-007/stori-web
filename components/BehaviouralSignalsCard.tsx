"use client"

import { Brain, Sparkles, AlertTriangle, Receipt, CreditCard, Clock, Calendar, TrendingUp, Heart, Target } from "lucide-react"

interface BehaviouralSignalsCardProps {
  consumer: any
}

export default function BehaviouralSignalsCard({ consumer }: BehaviouralSignalsCardProps) {
  const { behaviour, income } = consumer

  const getArchetypeColor = (type: string) => {
    const colors: Record<string, string> = {
      "Disciplined Saver": "bg-green-100 text-green-700 border-green-200",
      "Experience Seeker": "bg-purple-100 text-purple-700 border-purple-200",
      "Avoider": "bg-red-100 text-red-700 border-red-200",
      "Impulse Spender": "bg-orange-100 text-orange-700 border-orange-200",
      "Risk-taker": "bg-amber-100 text-amber-700 border-amber-200",
      "Family-centered": "bg-blue-100 text-blue-700 border-blue-200",
    }
    return colors[type] || "bg-gray-100 text-gray-700 border-gray-200"
  }

  const getStressColor = (level: string) => {
    if (level === "Very Low" || level === "Low") return "text-green-600 bg-green-50"
    if (level === "Moderate") return "text-amber-600 bg-amber-50"
    return "text-red-600 bg-red-50"
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Brain className="w-5 h-5 text-pink-600" />
        <h3 className="text-lg font-semibold text-gray-900">4. Behavioural & Psychological Signals</h3>
      </div>

      {/* (A) Spending Archetype */}
      <div className="mb-5">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(A) Spending Personality Archetype</h4>
        </div>
        <div className={`p-3 rounded-xl border ${getArchetypeColor(behaviour.spendingArchetype?.type || '')}`}>
          <div className="flex justify-between items-start">
            <div>
              <p className="font-bold text-lg">{behaviour.spendingArchetype?.type || 'N/A'}</p>
              <p className="text-sm opacity-80">{behaviour.spendingArchetype?.confidence || 0}% confidence</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-1 mt-2">
            {behaviour.spendingArchetype?.traits?.map((trait: string, idx: number) => (
              <span key={idx} className="px-2 py-0.5 bg-white/50 rounded text-xs">{trait}</span>
            ))}
          </div>
        </div>
      </div>

      {/* (B) Financial Stress & Bill Payment */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <div>
          <div className="flex items-center gap-1 mb-2">
            <AlertTriangle className="w-3 h-3 text-gray-500" />
            <h4 className="font-semibold text-gray-800 text-xs">(B) Financial Stress</h4>
          </div>
          <div className={`p-2 rounded-lg ${getStressColor(behaviour.financialStress?.stressLevel || 'Low')}`}>
            <p className="font-bold text-sm">{behaviour.financialStress?.stressLevel || 'Low'}</p>
            <p className="text-xs mt-0.5">ATM: {behaviour.financialStress?.atmWithdrawalTrend || 'Stable'}</p>
            <p className="text-xs">Micro-UPI: {behaviour.financialStress?.microUpiPayments || 'Low'}</p>
          </div>
        </div>
        <div>
          <div className="flex items-center gap-1 mb-2">
            <Receipt className="w-3 h-3 text-gray-500" />
            <h4 className="font-semibold text-gray-800 text-xs">(C) Bill Payment</h4>
          </div>
          <div className={`p-2 rounded-lg ${(behaviour.billPayment?.overallScore || 0) >= 80 ? 'bg-green-50 text-green-700' : (behaviour.billPayment?.overallScore || 0) >= 60 ? 'bg-amber-50 text-amber-700' : 'bg-red-50 text-red-700'}`}>
            <p className="font-bold text-sm">{behaviour.billPayment?.behaviour || 'N/A'}</p>
            <p className="text-xs mt-0.5">Score: {behaviour.billPayment?.overallScore || 0}/100</p>
            <p className="text-xs">{behaviour.billPayment?.autoDebitEnabled ? '✓ Auto-debit' : '✗ No auto-debit'}</p>
          </div>
        </div>
      </div>

      {/* Late Payments Table */}
      <div className="mb-5 p-2 bg-gray-50 rounded-lg">
        <p className="text-xs font-semibold text-gray-600 mb-2">Late Payments (Last 6 Months)</p>
        <div className="grid grid-cols-4 gap-2 text-center">
          <div>
            <p className={`font-bold ${(behaviour.billPayment?.latePaymentsLast6Months?.utility || 0) === 0 ? 'text-green-600' : 'text-red-600'}`}>
              {behaviour.billPayment?.latePaymentsLast6Months?.utility || 0}
            </p>
            <p className="text-xs text-gray-500">Utility</p>
          </div>
          <div>
            <p className={`font-bold ${(behaviour.billPayment?.latePaymentsLast6Months?.recharges || 0) === 0 ? 'text-green-600' : 'text-red-600'}`}>
              {behaviour.billPayment?.latePaymentsLast6Months?.recharges || 0}
            </p>
            <p className="text-xs text-gray-500">Recharge</p>
          </div>
          <div>
            <p className={`font-bold ${(behaviour.billPayment?.latePaymentsLast6Months?.rent || 0) === 0 ? 'text-green-600' : 'text-red-600'}`}>
              {behaviour.billPayment?.latePaymentsLast6Months?.rent || 0}
            </p>
            <p className="text-xs text-gray-500">Rent</p>
          </div>
          <div>
            <p className={`font-bold ${(behaviour.billPayment?.latePaymentsLast6Months?.subscriptions || 0) === 0 ? 'text-green-600' : 'text-red-600'}`}>
              {behaviour.billPayment?.latePaymentsLast6Months?.subscriptions || 0}
            </p>
            <p className="text-xs text-gray-500">Subs</p>
          </div>
        </div>
      </div>

      {/* (D) Subscriptions, (E) Micro-commitment, (F) Emotional, (G) Impulse */}
      <div className="grid grid-cols-4 gap-2 mb-5">
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-xs font-semibold text-gray-600">(D) Subscriptions</p>
          <p className="text-lg font-bold">{behaviour.subscriptions?.active || 0}</p>
          <p className="text-xs text-gray-500">Late/yr: {behaviour.subscriptions?.latePaymentsLastYear || 0}</p>
          {behaviour.subscriptions?.downgradingPatterns && (
            <p className="text-xs text-amber-600">⚠️ Downgrading</p>
          )}
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-xs font-semibold text-gray-600">(E) Micro-commit</p>
          <p className="text-lg font-bold">{behaviour.microCommitment?.consistencyScore || 0}</p>
          <p className="text-xs text-gray-500">Consistency</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-xs font-semibold text-gray-600">(F) Emotional</p>
          <p className={`text-sm font-bold ${behaviour.emotionalPurchasing?.pattern === 'Routine-driven' ? 'text-green-600' : behaviour.emotionalPurchasing?.pattern === 'Social behaviour' ? 'text-blue-600' : 'text-red-600'}`}>
            {behaviour.emotionalPurchasing?.level || behaviour.emotionalPurchasing?.pattern || 'N/A'}
          </p>
          <p className="text-xs text-gray-500">Late night: {behaviour.emotionalPurchasing?.lateNightSpending || 0}%</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-xs font-semibold text-gray-600">(G) Impulse</p>
          <p className={`text-lg font-bold ${(income?.salaryRetention?.impulseScore || 0) <= 30 ? 'text-green-600' : (income?.salaryRetention?.impulseScore || 0) <= 50 ? 'text-amber-600' : 'text-red-600'}`}>
            {income?.salaryRetention?.impulseScore || 0}
          </p>
          <p className="text-xs text-gray-500">{income?.salaryRetention?.impatienceLevel || ((income?.salaryRetention?.impulseScore || 0) <= 30 ? 'Low' : (income?.salaryRetention?.impulseScore || 0) <= 50 ? 'Medium' : 'High')}</p>
        </div>
      </div>

      {/* (H) Savings Consistency */}
      <div className="mb-5">
        <div className="flex items-center gap-1 mb-2">
          <TrendingUp className="w-3 h-3 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-xs">(H) Savings Consistency</h4>
        </div>
        <div className="grid grid-cols-4 gap-2 text-center bg-gray-50 rounded-lg p-2">
          <div>
            <p className="text-xs text-gray-500">Active SIPs</p>
            <p className="font-bold">{behaviour.savingsConsistency?.activeSips || 0}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Value/mo</p>
            <p className="font-bold">₹{((behaviour.savingsConsistency?.totalSipValue || 0) / 1000).toFixed(0)}K</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">SIP on Hike</p>
            <p className={`font-bold ${behaviour.savingsConsistency?.sipIncreaseOnHike ? 'text-green-600' : 'text-gray-600'}`}>
              {behaviour.savingsConsistency?.sipIncreaseOnHike ? 'Yes ✓' : 'No'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Consistency</p>
            <p className="font-bold">{behaviour.savingsConsistency?.sipPaymentConsistency || 0}%</p>
          </div>
        </div>
      </div>

      {/* (H) Money Personality & (I) Risk Appetite */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gray-50 rounded-lg p-2">
          <div className="flex items-center gap-1 mb-1">
            <Heart className="w-3 h-3 text-gray-500" />
            <p className="text-xs font-semibold text-gray-600">(H) Financial Stability</p>
          </div>
          <p className={`font-bold ${behaviour.moneyPersonalityStability?.stability === 'Very Stable' || behaviour.moneyPersonalityStability?.stability === 'Stable' ? 'text-green-600' : 'text-amber-600'}`}>
            {behaviour.moneyPersonalityStability?.stability || 'N/A'}
          </p>
          <p className="text-xs text-gray-500">{behaviour.moneyPersonalityStability?.behaviourChanges || 0} changes/yr</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <div className="flex items-center gap-1 mb-1">
            <Target className="w-3 h-3 text-gray-500" />
            <p className="text-xs font-semibold text-gray-600">(I) Risk Appetite</p>
          </div>
          <p className={`font-bold ${behaviour.riskAppetite?.segment === 'Conservative' ? 'text-blue-600' : behaviour.riskAppetite?.segment === 'Moderate' ? 'text-green-600' : 'text-red-600'}`}>
            {behaviour.riskAppetite?.segment || 'N/A'}
          </p>
          <p className="text-xs text-gray-500">
            {behaviour.riskAppetite?.cryptoActivity !== 'None' ? `Crypto: ${behaviour.riskAppetite?.cryptoActivity}` : 'No crypto'}
          </p>
        </div>
      </div>
    </div>
  )
}
