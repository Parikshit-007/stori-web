"use client"

import { User, Phone, CreditCard, MapPin, Wallet, TrendingUp, Brain, Sparkles, AlertTriangle, Receipt, Clock, ShoppingBag, Shield, CheckCircle, XCircle } from "lucide-react"

interface DirectorDetailsCardProps {
  msme: any
}

export default function DirectorDetailsCard({ msme }: DirectorDetailsCardProps) {
  const features = msme.features || {}
  const director = msme.director || {}

  const formatCurrency = (amount: number) => {
    if (!amount) return '₹0'
    if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)}Cr`
    if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`
    if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`
    return `₹${amount.toFixed(0)}`
  }

  // Mock director data
  const directorDetails = {
    name: director.name || msme.businessName?.split(' ')[0] + ' Kumar' || 'Rajesh Kumar',
    age: director.age || features.owner_age || 42,
    phone: director.phone || msme.phone || '+91-9876543210',
    pan: director.pan || features.owner_pan || 'ABCDE1234F',
    location: director.location || msme.location || 'Mumbai, Maharashtra',
    avgBalance: director.avg_balance || features.owner_avg_balance || (features.avg_bank_balance || 0) * 0.4,
    individualAssets: director.individual_assets || features.owner_individual_assets || (features.total_assets_value || 0) * 0.6
  }

  const getArchetypeColor = (type: string) => {
    const colors: Record<string, string> = {
      "Conservative": "bg-blue-100 text-blue-700 border-blue-200",
      "Growth-Focused": "bg-green-100 text-green-700 border-green-200",
      "Risk-Taker": "bg-orange-100 text-orange-700 border-orange-200",
      "Cautious Planner": "bg-purple-100 text-purple-700 border-purple-200"
    }
    return colors[type] || "bg-gray-100 text-gray-700 border-gray-200"
  }

  const getStressColor = (level: string) => {
    if (level === "Low") return "text-green-600 bg-green-50"
    if (level === "Moderate") return "text-amber-600 bg-amber-50"
    return "text-red-600 bg-red-50"
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Brain className="w-5 h-5 text-indigo-600" />
        <h3 className="text-lg font-semibold text-gray-900">Director / Promoter Profile & Behavioral Signals</h3>
      </div>

      {/* Director Profile Header */}
      <div className="flex items-start gap-4 mb-6 pb-4 border-b border-gray-200">
        <div className="w-16 h-16 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-2xl">
          {directorDetails.name.charAt(0)}
        </div>
        <div className="flex-1">
          <h4 className="text-xl font-bold text-gray-900">{directorDetails.name}</h4>
          <div className="flex items-center gap-4 mt-1 text-sm text-gray-600">
            <span>{directorDetails.age} years</span>
            <span>•</span>
            <span>{directorDetails.location}</span>
          </div>
          <div className="flex gap-3 mt-2">
            <span className="text-xs bg-blue-50 text-blue-700 px-2 py-1 rounded">📞 {directorDetails.phone}</span>
            <span className="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded tracking-wide">💳 {directorDetails.pan}</span>
          </div>
        </div>
      </div>

      {/* Individual Asset Value & Key Financials */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4 border border-green-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase text-gray-700 mb-1">Individual Asset Value</p>
              <p className="text-3xl font-bold text-green-600">{formatCurrency(directorDetails.individualAssets)}</p>
              <p className="text-xs text-gray-600 mt-1">Personal wealth holdings</p>
            </div>
            <Wallet className="w-8 h-8 text-green-500" />
          </div>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase text-gray-700 mb-1">Average Account Balance</p>
              <p className="text-3xl font-bold text-blue-600">{formatCurrency(directorDetails.avgBalance)}</p>
              <p className="text-xs text-gray-600 mt-1">Personal banking liquidity</p>
            </div>
            <TrendingUp className="w-8 h-8 text-blue-500" />
          </div>
        </div>
      </div>

      {/* Psychological Behaviour Analysis */}
      {/* <div className="mb-6 bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl p-5 border border-purple-200">
        <div className="flex items-center gap-2 mb-4">
          <Brain className="w-5 h-5 text-purple-600" />
          <h4 className="font-semibold text-gray-900 text-base">Psychological Behaviour Analysis</h4>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg p-3 border border-purple-100">
            <p className="text-xs text-gray-600 mb-1">Risk Tolerance</p>
            <p className="text-lg font-bold text-purple-600">{director.risk_tolerance || 'Moderate'}</p>
            <div className="mt-2 bg-gray-100 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full"
                style={{ width: `${director.risk_tolerance_score || 65}%` }}
              />
            </div>
          </div>
          <div className="bg-white rounded-lg p-3 border border-purple-100">
            <p className="text-xs text-gray-600 mb-1">Decision Speed</p>
            <p className="text-lg font-bold text-indigo-600">{director.decision_speed || 'Fast'}</p>
            <p className="text-xs text-gray-500 mt-1">
              {director.decision_time || '2-3'} days avg
            </p>
          </div>
          <div className="bg-white rounded-lg p-3 border border-purple-100">
            <p className="text-xs text-gray-600 mb-1">Stress Handling</p>
            <p className={`text-lg font-bold ${(director.stress_handling_score || 80) >= 75 ? 'text-green-600' : (director.stress_handling_score || 80) >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
              {director.stress_handling || 'Good'}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              Score: {director.stress_handling_score || 80}/100
            </p>
          </div>
        </div>
        <div className="mt-4 pt-4 border-t border-purple-200">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="text-center">
              <p className="text-xs text-gray-600">Financial Literacy</p>
              <p className="text-sm font-bold text-purple-600">{director.financial_literacy || 'High'}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-600">Planning Horizon</p>
              <p className="text-sm font-bold text-indigo-600">{director.planning_horizon || 'Long-term'}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-600">Innovation Mindset</p>
              <p className="text-sm font-bold text-pink-600">{director.innovation_mindset || 'Progressive'}</p>
            </div>
            <div className="text-center">
              <p className="text-xs text-gray-600">Leadership Style</p>
              <p className="text-sm font-bold text-purple-600">{director.leadership_style || 'Collaborative'}</p>
            </div>
          </div>
        </div>
      </div> */}

      {/* (A) Business Decision Making Style */}
      {/* <div className="mb-5">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(A) Business Decision Making Style</h4>
        </div>
        <div className={`p-3 rounded-xl border ${getArchetypeColor(director.decision_style || 'Growth-Focused')}`}>
          <div className="flex justify-between items-start">
            <div>
              <p className="font-bold text-lg">{director.decision_style || 'Growth-Focused'}</p>
              <p className="text-sm opacity-80">{director.decision_confidence || 85}% confidence</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-1 mt-2">
            {(director.traits || ['Data-driven', 'Quick adopter', 'Calculated risk']).map((trait: string, idx: number) => (
              <span key={idx} className="px-2 py-0.5 bg-white/50 rounded text-xs">{trait}</span>
            ))}
          </div>
        </div>
      </div> */}

      {/* (B) Financial Discipline & (C) Payment Behavior */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <div>
          <div className="flex items-center gap-1 mb-2">
            <AlertTriangle className="w-3 h-3 text-gray-500" />
            <h4 className="font-semibold text-gray-800 text-xs">(B) Financial Discipline</h4>
          </div>
          <div className={`p-2 rounded-lg ${getStressColor(director.financial_discipline || 'Low')}`}>
            <p className="font-bold text-sm">{director.financial_discipline_level || 'High'}</p>
            <p className="text-xs mt-0.5">Cash Management: {director.cash_management || 'Excellent'}</p>
            <p className="text-xs">Debt Burden: {director.debt_burden || 'Low'}</p>
          </div>
        </div>
        <div>
          <div className="flex items-center gap-1 mb-2">
            <Receipt className="w-3 h-3 text-gray-500" />
            <h4 className="font-semibold text-gray-800 text-xs">(C) Payment Behavior</h4>
          </div>
          <div className={`p-2 rounded-lg ${(director.payment_score || 85) >= 80 ? 'bg-green-50 text-green-700' : (director.payment_score || 85) >= 60 ? 'bg-amber-50 text-amber-700' : 'bg-red-50 text-red-700'}`}>
            <p className="font-bold text-sm">{director.payment_behavior || 'On-Time Payer'}</p>
            <p className="text-xs mt-0.5">Score: {director.payment_score || 85}/100</p>
            <p className="text-xs">Auto-pay: {director.auto_payment || 'Enabled'}</p>
          </div>
        </div>
      </div>

      {/* Late Payments Table */}
      <div className="mb-5 p-2 bg-gray-50 rounded-lg">
        <p className="text-xs font-semibold text-gray-600 mb-2">Late Payments (Last 6 Months)</p>
        <div className="grid grid-cols-4 gap-2 text-center">
          <div>
            <p className={`font-bold ${(director.late_supplier_payments || 0) === 0 ? 'text-green-600' : 'text-red-600'}`}>
              {director.late_supplier_payments || 0}
            </p>
            <p className="text-xs text-gray-500">Suppliers</p>
          </div>
          <div>
            <p className={`font-bold ${(director.late_loan_payments || 0) === 0 ? 'text-green-600' : 'text-red-600'}`}>
              {director.late_loan_payments || 0}
            </p>
            <p className="text-xs text-gray-500">Loans</p>
          </div>
          <div>
            <p className={`font-bold ${(director.late_rent_payments || 0) === 0 ? 'text-green-600' : 'text-red-600'}`}>
              {director.late_rent_payments || 0}
            </p>
            <p className="text-xs text-gray-500">Rent</p>
          </div>
          <div>
            <p className={`font-bold ${(director.late_utility_payments || 0) === 0 ? 'text-green-600' : 'text-red-600'}`}>
              {director.late_utility_payments || 0}
            </p>
            <p className="text-xs text-gray-500">Utilities</p>
          </div>
        </div>
      </div>

      {/* (D) Utility Payment Consistency */}
      <div className="mb-5">
        <div className="flex items-center gap-1 mb-2">
          <Clock className="w-3 h-3 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-xs">(D) Utility Payment Consistency</h4>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center bg-gray-50 rounded-lg p-2">
          <div>
            <p className="text-xs text-gray-500">Electricity</p>
            <p className={`font-bold ${(director.electricity_payment_consistency || 95) >= 90 ? 'text-green-600' : (director.electricity_payment_consistency || 95) >= 70 ? 'text-amber-600' : 'text-red-600'}`}>
              {director.electricity_payment_consistency || 95}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Water</p>
            <p className={`font-bold ${(director.water_payment_consistency || 92) >= 90 ? 'text-green-600' : (director.water_payment_consistency || 92) >= 70 ? 'text-amber-600' : 'text-red-600'}`}>
              {director.water_payment_consistency || 92}%
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Internet/Phone</p>
            <p className={`font-bold ${(director.telecom_payment_consistency || 98) >= 90 ? 'text-green-600' : (director.telecom_payment_consistency || 98) >= 70 ? 'text-amber-600' : 'text-red-600'}`}>
              {director.telecom_payment_consistency || 98}%
            </p>
          </div>
        </div>
      </div>

      {/* (E) Personal Financial Health */}
      <div className="mb-5">
        <div className="flex items-center gap-1 mb-2">
          <Wallet className="w-3 h-3 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-xs">(E) Personal Financial Health</h4>
        </div>
        <div className="grid grid-cols-2 gap-3 bg-gray-50 rounded-lg p-3">
          <div>
            <p className="text-xs text-gray-500">Personal Account Balance</p>
            <p className="font-bold text-lg text-green-600">{formatCurrency(directorDetails.avgBalance)}</p>
          </div>
          <div>
            <p className="text-xs text-gray-500">Individual Assets</p>
            <p className="font-bold text-lg text-orange-600">{formatCurrency(directorDetails.individualAssets)}</p>
          </div>
        </div>
      </div>

      {/* (F) Spending Personality */}
      <div className="mb-5">
        <div className="flex items-center gap-2 mb-2">
          <ShoppingBag className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(F) Spending Personality & Behavior</h4>
        </div>
        <div className={`p-4 rounded-xl border ${getArchetypeColor(director.spending_archetype || 'Conservative Spender')}`}>
          <div className="flex justify-between items-start mb-2">
            <div>
              <p className="font-bold text-lg">{director.spending_archetype || 'Conservative Spender'}</p>
              <p className="text-sm opacity-80">{director.spending_confidence || 78}% confidence</p>
            </div>
          </div>
          <div className="flex flex-wrap gap-1 mt-2 mb-3">
            {(director.spending_traits || ['Budget-conscious', 'Planned purchases', 'Value-driven']).map((trait: string, idx: number) => (
              <span key={idx} className="px-2 py-0.5 bg-white/50 rounded text-xs">{trait}</span>
            ))}
          </div>
          <div className="grid grid-cols-3 gap-2 text-xs mt-3 pt-3 border-t border-black/10">
            <div className="text-center">
              <p className="text-gray-600 mb-1">Impulse Score</p>
              <p className={`font-bold ${(director.impulse_spending_score || 25) <= 30 ? 'text-green-600' : (director.impulse_spending_score || 25) <= 50 ? 'text-amber-600' : 'text-red-600'}`}>
                {director.impulse_spending_score || 25}/100
              </p>
            </div>
            <div className="text-center">
              <p className="text-gray-600 mb-1">Luxury Tendency</p>
              <p className="font-bold text-purple-600">{director.luxury_spending_tendency || 'Low'}</p>
            </div>
            <div className="text-center">
              <p className="text-gray-600 mb-1">Savings Rate</p>
              <p className="font-bold text-blue-600">{director.personal_savings_rate || 22}%</p>
            </div>
          </div>
        </div>
      </div>

      {/* (G) Fraud & Identity Verification Checks */}
      <div className="mb-5">
        <div className="flex items-center gap-2 mb-3">
          <Shield className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(G) Fraud & Identity Verification</h4>
        </div>
        <div className="space-y-2">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center gap-2">
              <span className="text-gray-700 font-medium text-sm">PAN Verification</span>
            </div>
            <div className="flex items-center gap-2">
              {(director.pan_verified ?? features.owner_pan_verified ?? true) ? (
                <>
                  <span className="text-green-600 font-semibold text-xs">Verified</span>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </>
              ) : (
                <>
                  <span className="text-red-600 font-semibold text-xs">Not Verified</span>
                  <XCircle className="w-5 h-5 text-red-600" />
                </>
              )}
            </div>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center gap-2">
              <span className="text-gray-700 font-medium text-sm">Aadhaar Verification</span>
            </div>
            <div className="flex items-center gap-2">
              {(director.aadhaar_verified ?? features.owner_aadhaar_verified ?? true) ? (
                <>
                  <span className="text-green-600 font-semibold text-xs">Verified</span>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </>
              ) : (
                <>
                  <span className="text-red-600 font-semibold text-xs">Not Verified</span>
                  <XCircle className="w-5 h-5 text-red-600" />
                </>
              )}
            </div>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center gap-2">
              <span className="text-gray-700 font-medium text-sm">Bank Account Verification</span>
            </div>
            <div className="flex items-center gap-2">
              {(director.bank_account_verified ?? features.owner_bank_verified ?? true) ? (
                <>
                  <span className="text-green-600 font-semibold text-xs">Verified</span>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </>
              ) : (
                <>
                  <span className="text-red-600 font-semibold text-xs">Not Verified</span>
                  <XCircle className="w-5 h-5 text-red-600" />
                </>
              )}
            </div>
          </div>
          {/* <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center gap-2">
              <span className="text-gray-700 font-medium text-sm">Credit History Check</span>
            </div>
            <div className="flex items-center gap-2">
              {(director.credit_history_clean ?? true) ? (
                <>
                  <span className="text-green-600 font-semibold text-xs">Clean</span>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </>
              ) : (
                <>
                  <span className="text-red-600 font-semibold text-xs">Issues Found</span>
                  <XCircle className="w-5 h-5 text-red-600" />
                </>
              )}
            </div>
          </div> */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center gap-2">
              <span className="text-gray-700 font-medium text-sm">Address Mismatch Check</span>
            </div>
            <div className="flex items-center gap-2">
              {!(director.address_mismatch ?? features.pan_address_bank_mismatch ?? false) ? (
                <>
                  <span className="text-green-600 font-semibold text-xs">No Mismatch</span>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </>
              ) : (
                <>
                  <span className="text-red-600 font-semibold text-xs">Mismatch Detected</span>
                  <XCircle className="w-5 h-5 text-red-600" />
                </>
              )}
            </div>
          </div>
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border border-gray-200">
            <div className="flex items-center gap-2">
              <span className="text-gray-700 font-medium text-sm">Fraudulent Activity</span>
            </div>
            <div className="flex items-center gap-2">
              {!(director.fraudulent_activity ?? features.fraud_flag ?? false) ? (
                <>
                  <span className="text-green-600 font-semibold text-xs">None Detected</span>
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </>
              ) : (
                <>
                  <span className="text-red-600 font-semibold text-xs">⚠ Detected</span>
                  <XCircle className="w-5 h-5 text-red-600" />
                </>
              )}
            </div>
          </div>
        </div>
      </div>

    </div>
  )
}

