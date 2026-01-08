"use client"

import { FileText, CheckCircle, XCircle, AlertTriangle, Receipt } from "lucide-react"

interface ComplianceTaxationCardProps {
  msme: any
}

export default function ComplianceTaxationCard({ msme }: ComplianceTaxationCardProps) {
  const features = msme.features || {}
  const compliance = msme.compliance || {}

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

  const gstFilingRegularity = features.gst_filing_regularity || compliance.gst_filing_regularity || 0
  const gstFilingOnTime = features.gst_filing_ontime_ratio || compliance.gst_filing_ontime_ratio || 0
  const itrFiled = features.itr_filed || compliance.itr_filed || 0
  const outstandingTaxes = features.outstanding_taxes_amount || compliance.outstanding_taxes_amount || 0
  const outstandingDuesFlag = features.outstanding_dues_flag || compliance.outstanding_dues_flag || 0

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <FileText className="w-5 h-5 text-orange-600" />
        <h3 className="text-lg font-semibold text-gray-900">E. Compliance & Taxation (12%)</h3>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className={`bg-gradient-to-br rounded-xl p-4 ${gstFilingRegularity >= 0.9 ? 'from-green-50 to-emerald-50' : gstFilingRegularity >= 0.7 ? 'from-yellow-50 to-amber-50' : 'from-red-50 to-rose-50'}`}>
          <p className="text-xs font-semibold uppercase">GST Filing Regularity</p>
          <p className={`text-2xl font-bold mt-1 ${gstFilingRegularity >= 0.9 ? 'text-green-600' : gstFilingRegularity >= 0.7 ? 'text-yellow-600' : 'text-red-600'}`}>
            {formatPercent(gstFilingRegularity)}
          </p>
        </div>
        <div className={`bg-gradient-to-br rounded-xl p-4 ${itrFiled === 1 ? 'from-green-50 to-emerald-50' : 'from-red-50 to-rose-50'}`}>
          <p className="text-xs font-semibold uppercase">ITR Filed</p>
          <div className="flex items-center gap-2 mt-1">
            {itrFiled === 1 ? (
              <CheckCircle className="w-6 h-6 text-green-600" />
            ) : (
              <XCircle className="w-6 h-6 text-red-600" />
            )}
            <p className={`text-lg font-bold ${itrFiled === 1 ? 'text-green-600' : 'text-red-600'}`}>
              {itrFiled === 1 ? 'Yes' : 'No'}
            </p>
          </div>
        </div>
      </div>

      {/* Risk Indicators */}
      {(outstandingTaxes > 0 || outstandingDuesFlag === 1) && (
        <div className="mb-6">
          <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            Outstanding Dues
          </h4>
          <div className="bg-red-50 rounded-lg p-3 border border-red-200">
            <p className="text-red-900 text-xs mb-1">Outstanding Taxes</p>
            <p className="text-xl font-bold text-red-600">{formatCurrency(outstandingTaxes)}</p>
            {outstandingDuesFlag === 1 && (
              <p className="text-xs text-red-700 mt-1">⚠️ Outstanding dues flag active</p>
            )}
          </div>
        </div>
      )}

      {/* GST Compliance */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
          <Receipt className="w-4 h-4 text-gray-500" />
          GST Compliance
        </h4>
        <div className="space-y-2 text-sm">
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
            <span className="text-gray-600">GST Filing On-Time Ratio</span>
            <span className="font-semibold">{formatPercent(gstFilingOnTime)}</span>
          </div>
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
            <span className="text-gray-600">GST vs Platform Sales Mismatch</span>
            <span className={`font-semibold ${(features.gst_vs_platform_sales_mismatch || 0) > 0.1 ? 'text-red-600' : 'text-green-600'}`}>
              {formatPercent(features.gst_vs_platform_sales_mismatch || compliance.gst_vs_platform_sales_mismatch || 0)}
            </span>
          </div>
        </div>
      </div>

      {/* Tax Payment */}
      <div className="space-y-2 text-sm">
        <h4 className="font-semibold text-gray-800 text-sm mb-2">Tax Payment</h4>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Tax Payment Regularity</span>
          <span className="font-semibold">
            {formatPercent(features.tax_payment_regularity || compliance.tax_payment_regularity || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Tax Payment On-Time Ratio</span>
          <span className="font-semibold">
            {formatPercent(features.tax_payment_ontime_ratio || compliance.tax_payment_ontime_ratio || 0)}
          </span>
        </div>
        {features.itr_income_declared > 0 && (
          <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
            <span className="text-gray-600">ITR Income Declared</span>
            <span className="font-semibold">
              {formatCurrency(features.itr_income_declared || compliance.itr_income_declared || 0)}
            </span>
          </div>
        )}
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">GST R1 vs ITR Mismatch</span>
          <span className={`font-semibold ${(features.gst_r1_vs_itr_mismatch || 0) > 0.1 ? 'text-red-600' : 'text-green-600'}`}>
            {formatPercent(features.gst_r1_vs_itr_mismatch || compliance.gst_r1_vs_itr_mismatch || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Refund/Chargeback Rate</span>
          <span className="font-semibold">
            {formatPercent(features.refund_chargeback_rate || compliance.refund_chargeback_rate || 0)}
          </span>
        </div>
      </div>
    </div>
  )
}



