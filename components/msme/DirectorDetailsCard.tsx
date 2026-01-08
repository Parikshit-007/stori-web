"use client"

import { User, Phone, CreditCard, MapPin, Wallet, TrendingUp, Brain, Sparkles, AlertTriangle, Receipt, Target, Heart, Clock } from "lucide-react"

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

      {/* (A) Business Decision Making Style */}
      <div className="mb-5">
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
      </div>

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

      {/* (D) Business Expansion, (E) Investment, (F) Diversification, (G) Liquidity */}
      <div className="grid grid-cols-4 gap-2 mb-5">
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-xs font-semibold text-gray-600">(D) Expansion</p>
          <p className="text-lg font-bold">{director.expansion_appetite || 'Medium'}</p>
          <p className="text-xs text-gray-500">New ventures: {director.new_ventures || 1}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-xs font-semibold text-gray-600">(E) Reinvestment</p>
          <p className="text-lg font-bold">{director.reinvestment_rate || '18'}%</p>
          <p className="text-xs text-gray-500">Of profits</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-xs font-semibold text-gray-600">(F) Diversification</p>
          <p className={`text-sm font-bold ${(director.diversification_score || 65) >= 70 ? 'text-green-600' : 'text-amber-600'}`}>
            {director.diversification_level || 'Moderate'}
          </p>
          <p className="text-xs text-gray-500">Streams: {director.income_streams || 2}</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-xs font-semibold text-gray-600">(G) Liquidity</p>
          <p className={`text-lg font-bold ${(director.liquidity_ratio || 1.5) >= 1.5 ? 'text-green-600' : 'text-red-600'}`}>
            {(director.liquidity_ratio || 1.5).toFixed(1)}x
          </p>
          <p className="text-xs text-gray-500">Current ratio</p>
        </div>
      </div>

      {/* (H) Utility Payment Consistency */}
      <div className="mb-5">
        <div className="flex items-center gap-1 mb-2">
          <Clock className="w-3 h-3 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-xs">(H) Utility Payment Consistency</h4>
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

      {/* (I) Personal Financial Health */}
      <div className="mb-5">
        <div className="flex items-center gap-1 mb-2">
          <Wallet className="w-3 h-3 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-xs">(I) Personal Financial Health</h4>
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

      {/* (J) Financial Stability & (K) Risk Appetite */}
      <div className="grid grid-cols-2 gap-3">
        <div className="bg-gray-50 rounded-lg p-2">
          <div className="flex items-center gap-1 mb-1">
            <Heart className="w-3 h-3 text-gray-500" />
            <p className="text-xs font-semibold text-gray-600">(J) Business Stability</p>
          </div>
          <p className={`font-bold ${director.business_stability === 'Very Stable' || director.business_stability === 'Stable' ? 'text-green-600' : 'text-amber-600'}`}>
            {director.business_stability || 'Stable'}
          </p>
          <p className="text-xs text-gray-500">{director.major_changes || 0} major changes/yr</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <div className="flex items-center gap-1 mb-1">
            <Target className="w-3 h-3 text-gray-500" />
            <p className="text-xs font-semibold text-gray-600">(K) Risk Appetite</p>
          </div>
          <p className={`font-bold ${director.risk_appetite === 'Conservative' ? 'text-blue-600' : director.risk_appetite === 'Moderate' ? 'text-green-600' : 'text-red-600'}`}>
            {director.risk_appetite || 'Moderate'}
          </p>
          <p className="text-xs text-gray-500">
            {director.high_risk_ventures || 0} high-risk ventures
          </p>
        </div>
      </div>
    </div>
  )
}

