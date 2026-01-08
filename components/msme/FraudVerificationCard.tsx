"use client"

import { Shield, CheckCircle, XCircle, AlertTriangle, Smartphone } from "lucide-react"

interface FraudVerificationCardProps {
  msme: any
}

export default function FraudVerificationCard({ msme }: FraudVerificationCardProps) {
  const features = msme.features || {}
  const fraud = msme.fraud || {}

  const formatPercent = (val: number) => {
    return `${(val * 100).toFixed(1)}%`
  }

  const getVerificationBadge = (verified: number | boolean) => {
    const isVerified = typeof verified === 'boolean' ? verified : verified === 1
    return isVerified ? (
      <CheckCircle className="w-4 h-4 text-green-600" />
    ) : (
      <XCircle className="w-4 h-4 text-red-600" />
    )
  }

  const kycScore = features.kyc_completion_score || fraud.kyc_completion_score || 0
  const kycAttempts = features.kyc_attempts_count || fraud.kyc_attempts_count || 1
  const deviceConsistency = features.device_consistency_score || fraud.device_consistency_score || 0
  const ipStability = features.ip_stability_score || fraud.ip_stability_score || 0
  const panMismatch = features.pan_address_bank_mismatch || fraud.pan_address_bank_mismatch || 0
  const reportingErrorRate = features.reporting_error_rate || fraud.reporting_error_rate || 0

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Shield className="w-5 h-5 text-red-600" />
        <h3 className="text-lg font-semibold text-gray-900">F. Fraud & Verification (7%)</h3>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className={`bg-gradient-to-br rounded-xl p-4 ${kycScore >= 0.9 ? 'from-green-50 to-emerald-50' : kycScore >= 0.7 ? 'from-yellow-50 to-amber-50' : 'from-red-50 to-rose-50'}`}>
          <p className="text-xs font-semibold uppercase">KYC Completion Score</p>
          <p className={`text-2xl font-bold mt-1 ${kycScore >= 0.9 ? 'text-green-600' : kycScore >= 0.7 ? 'text-yellow-600' : 'text-red-600'}`}>
            {formatPercent(kycScore)}
          </p>
          <p className="text-xs text-gray-600 mt-1">Attempts: {kycAttempts}</p>
        </div>
        <div className={`bg-gradient-to-br rounded-xl p-4 ${deviceConsistency >= 0.9 ? 'from-green-50 to-emerald-50' : deviceConsistency >= 0.7 ? 'from-yellow-50 to-amber-50' : 'from-red-50 to-rose-50'}`}>
          <p className="text-xs font-semibold uppercase">Device Consistency</p>
          <p className={`text-2xl font-bold mt-1 ${deviceConsistency >= 0.9 ? 'text-green-600' : deviceConsistency >= 0.7 ? 'text-yellow-600' : 'text-red-600'}`}>
            {formatPercent(deviceConsistency)}
          </p>
        </div>
      </div>

      {/* Risk Indicators */}
      {(panMismatch === 1 || reportingErrorRate > 0.1 || kycAttempts > 3) && (
        <div className="mb-6">
          <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            Risk Indicators
          </h4>
          <div className="space-y-2">
            {panMismatch === 1 && (
              <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                <p className="text-red-900 text-xs mb-1">⚠️ PAN-Address-Bank Mismatch Detected</p>
              </div>
            )}
            {reportingErrorRate > 0.1 && (
              <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                <p className="text-red-900 text-xs mb-1">High Reporting Error Rate</p>
                <p className="text-xl font-bold text-red-600">{formatPercent(reportingErrorRate)}</p>
              </div>
            )}
            {kycAttempts > 3 && (
              <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
                <p className="text-yellow-900 text-xs">Multiple KYC Attempts: {kycAttempts}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Verification Status */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
          <Shield className="w-4 h-4 text-gray-500" />
          Verification Status
        </h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex items-center justify-between bg-gray-50 rounded-lg p-2">
            <span className="text-gray-600">Image OCR Verified</span>
            {getVerificationBadge(features.image_ocr_verified ?? fraud.image_ocr_verified ?? false)}
          </div>
          <div className="flex items-center justify-between bg-gray-50 rounded-lg p-2">
            <span className="text-gray-600">Shop Image Verified</span>
            {getVerificationBadge(features.shop_image_verified ?? fraud.shop_image_verified ?? false)}
          </div>
        </div>
      </div>

      {/* Additional Scores */}
      <div className="space-y-2 text-sm">
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">IP Stability Score</span>
          <span className="font-semibold">{formatPercent(ipStability)}</span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Incoming Funds Verified</span>
          <span className="font-semibold">
            {formatPercent(features.incoming_funds_verified || fraud.incoming_funds_verified || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Insurance Coverage Score</span>
          <span className="font-semibold">
            {formatPercent(features.insurance_coverage_score || fraud.insurance_coverage_score || 0)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Insurance Premium Paid Ratio</span>
          <span className="font-semibold">
            {formatPercent(features.insurance_premium_paid_ratio || fraud.insurance_premium_paid_ratio || 0)}
          </span>
        </div>
      </div>
    </div>
  )
}



