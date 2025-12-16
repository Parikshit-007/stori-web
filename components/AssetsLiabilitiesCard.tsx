"use client"

import { Building, Shield, CreditCard, Gauge } from "lucide-react"

interface AssetsLiabilitiesCardProps {
  consumer: any
}

export default function AssetsLiabilitiesCard({ consumer }: AssetsLiabilitiesCardProps) {
  const { assets, insurance, liabilities, saturation } = consumer

  const formatAmount = (amt: number) => {
    if (amt >= 10000000) return `₹${(amt / 10000000).toFixed(1)}Cr`
    if (amt >= 100000) return `₹${(amt / 100000).toFixed(1)}L`
    if (amt >= 1000) return `₹${(amt / 1000).toFixed(0)}K`
    return `₹${amt}`
  }

  const getSaturationColor = (val: number) => {
    if (val <= 30) return "text-green-600"
    if (val <= 50) return "text-amber-600"
    return "text-red-600"
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Building className="w-5 h-5 text-purple-600" />
        <h3 className="text-lg font-semibold text-gray-900">3. Assets & Liabilities</h3>
      </div>

      {/* (A) Assets */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-semibold text-gray-800 text-sm">(A) Assets</h4>
          <div className="flex items-center gap-2">
            <span className={`px-2 py-1 rounded text-xs font-semibold ${assets.itrFiled ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              ITR: {assets.itrFiled ? (assets.itrYear || 'Filed') : 'Not Filed'}
            </span>
            <span className="font-bold text-purple-600">Total: {formatAmount(assets.totalAssets)}</span>
          </div>
        </div>
        <div className="grid grid-cols-3 gap-2 text-sm">
          {[
            { key: 'mutualFunds', label: 'Mutual Funds' },
            { key: 'stocks', label: 'Stocks' },
            { key: 'corporateBonds', label: 'Corp Bonds' },
            { key: 'governmentSecurities', label: 'Govt Securities' },
            { key: 'nps', label: 'NPS' },
            { key: 'epf', label: 'EPF' },
            { key: 'ppf', label: 'PPF' },
            { key: 'fd', label: 'FD' },
            { key: 'rd', label: 'RD' },
          ].map(({ key, label }) => (
            <div key={key} className="bg-gray-50 rounded-lg p-2 text-center">
              <p className="text-gray-500 text-xs">{label}</p>
              <p className={`font-semibold ${assets.investments?.[key] > 0 ? 'text-gray-900' : 'text-gray-400'}`}>
                {assets.investments?.[key] > 0 ? formatAmount(assets.investments[key]) : '—'}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* (B) Insurance */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Shield className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(B) Insurance</h4>
        </div>
        {insurance.policies?.length > 0 ? (
          <>
            <div className="space-y-2 mb-2">
              {insurance.policies.map((policy: any, idx: number) => (
                <div key={idx} className="flex justify-between items-center p-2 bg-gray-50 rounded-lg text-sm">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-blue-100 text-blue-700 text-xs font-semibold">{policy.type}</span>
                    <span className="text-gray-600">{policy.provider}</span>
                    {policy.sumAssured && <span className="text-gray-400 text-xs">(Cover: {formatAmount(policy.sumAssured)})</span>}
                  </div>
                  <span className="font-semibold">₹{policy.premium?.toLocaleString()}/yr</span>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="p-2 bg-green-50 rounded-lg">
                <p className="text-green-700 text-xs">Payment: {insurance.paymentBehaviour?.avgDaysBeforeDue}d before due</p>
              </div>
              <div className={`p-2 rounded-lg ${insurance.paymentBehaviour?.latePaymentsLast6Months === 0 ? 'bg-green-50' : 'bg-red-50'}`}>
                <p className={`text-xs ${insurance.paymentBehaviour?.latePaymentsLast6Months === 0 ? 'text-green-700' : 'text-red-700'}`}>
                  Late (6mo): {insurance.paymentBehaviour?.latePaymentsLast6Months}
                </p>
              </div>
            </div>
          </>
        ) : (
          <p className="text-gray-500 text-sm italic p-3 bg-gray-50 rounded-lg">No insurance policies found</p>
        )}
      </div>

      {/* (C) Liabilities */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <CreditCard className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(C) Liabilities</h4>
          {!liabilities.available && (
            <span className="ml-auto px-2 py-1 rounded bg-amber-100 text-amber-700 text-xs font-semibold">Not Available (NTC)</span>
          )}
        </div>
        {liabilities.available ? (
          <>
            {liabilities.activeLoans?.length > 0 ? (
              <div className="space-y-2 mb-3">
                {liabilities.activeLoans.map((loan: any, idx: number) => (
                  <div key={idx} className="p-2 bg-gray-50 rounded-lg text-sm">
                    <p className="text-gray-800 font-medium mb-1">{loan.type}({loan.bank})</p>
                    <div className="flex justify-between items-center">
                      <span className="font-semibold">{formatAmount(loan.outstanding)}</span>
                      <span className="text-gray-600">EMI: {formatAmount(loan.emi)}</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-sm mb-3 p-2 bg-gray-50 rounded-lg">No active loans</p>
            )}
            <div className="space-y-2 mb-3">
              <div className="p-2 bg-gray-50 rounded-lg text-sm">
                <p className="text-gray-500 text-xs mb-1">Loan Repayment</p>
                <p className={`font-semibold ${liabilities.loanRepaymentHistory === 'Excellent' ? 'text-green-600' : liabilities.loanRepaymentHistory === 'Good' ? 'text-amber-600' : 'text-gray-900'}`}>
                  {liabilities.loanRepaymentHistory === 'Excellent' ? '10/10 paid on time' : 
                   liabilities.loanRepaymentHistory === 'Good' ? '8/10 paid on time' : 
                   liabilities.loanRepaymentHistory || 'N/A'}
                </p>
              </div>
              <div className="p-2 bg-gray-50 rounded-lg text-sm">
                <p className="text-gray-500 text-xs mb-1">Credit Card</p>
                <p className={`font-semibold ${liabilities.creditCardRepaymentHistory === 'Excellent' ? 'text-green-600' : liabilities.creditCardRepaymentHistory === 'Good' ? 'text-amber-600' : 'text-gray-900'}`}>
                  {liabilities.creditCardRepaymentHistory === 'Excellent' ? '10/10 paid on time' : 
                   liabilities.creditCardRepaymentHistory === 'Good' ? '8/10 paid on time' : 
                   liabilities.creditCardRepaymentHistory || 'N/A'}
                </p>
              </div>
              <div className="p-2 bg-gray-50 rounded-lg text-sm">
                <p className="text-gray-500 text-xs mb-1">Credit Enquiries</p>
                <p className="font-semibold">{liabilities.creditEnquiries}</p>
              </div>
              <div className="p-2 bg-gray-50 rounded-lg text-sm">
                <p className="text-gray-500 text-xs mb-1">Default History</p>
                <p className={`font-semibold ${liabilities.defaultHistory === 'None' || liabilities.defaultHistory === 'Not Available' ? 'text-green-600' : 'text-red-600'}`}>
                  {liabilities.defaultHistory}
                </p>
              </div>
            </div>
            <div className="mb-3 p-2 bg-gray-50 rounded-lg text-sm">
              <p className="text-gray-500 text-xs mb-1">BNPL History</p>
              <p className="font-semibold">{liabilities.bnplHistory?.repaymentStatus || 'N/A'} (Active: {liabilities.bnplHistory?.active || 0})</p>
            </div>
          </>
        ) : (
          <div className="bg-amber-50 rounded-lg p-4 text-center text-amber-700 text-sm border border-amber-200">
            <p className="font-medium">Credit history not available</p>
            <p className="text-xs mt-1">New to Credit (NTC) - No bureau record</p>
          </div>
        )}
      </div>

      {/* (D) Saturation Levels */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Gauge className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(D) Saturation Levels</h4>
          <span className={`ml-auto px-2 py-1 rounded text-xs font-bold ${saturation.totalSaturation <= 40 ? 'bg-green-100 text-green-700' : saturation.totalSaturation <= 60 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}`}>
            {saturation.status}
          </span>
        </div>
        <div className="space-y-3">
          <div className="p-2 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-600">EMI ÷ Income</span>
              <span className={`font-semibold text-sm ${getSaturationColor(saturation.emiToIncome)}`}>{saturation.emiToIncome}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className={`h-2 rounded-full ${saturation.emiToIncome <= 40 ? 'bg-green-500' : saturation.emiToIncome <= 60 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${Math.min(saturation.emiToIncome, 100)}%` }} />
            </div>
          </div>
          <div className="p-2 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-600">Rent ÷ Income</span>
              <span className={`font-semibold text-sm ${getSaturationColor(saturation.rentToIncome)}`}>{saturation.rentToIncome}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className={`h-2 rounded-full ${saturation.rentToIncome <= 30 ? 'bg-green-500' : saturation.rentToIncome <= 45 ? 'bg-amber-500' : 'bg-red-500'}`} style={{ width: `${Math.min(saturation.rentToIncome, 100)}%` }} />
            </div>
          </div>
          <div className="p-2 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-600">Utility ÷ Income</span>
              <span className="font-semibold text-sm text-green-600">{saturation.utilityToIncome}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div className="h-2 rounded-full bg-green-500" style={{ width: `${Math.min(saturation.utilityToIncome * 5, 100)}%` }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
