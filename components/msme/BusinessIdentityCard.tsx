"use client"

import { Building2, MapPin, Users, CheckCircle, XCircle, Shield } from "lucide-react"

interface BusinessIdentityCardProps {
  msme: any
}

export default function BusinessIdentityCard({ msme }: BusinessIdentityCardProps) {
  const features = msme.features || {}
  const identity = msme.identity || {}

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`
    return num?.toString() || '0'
  }

  const getVerificationBadge = (verified: number | boolean) => {
    const isVerified = typeof verified === 'boolean' ? verified : verified === 1
    return isVerified ? (
      <CheckCircle className="w-4 h-4 text-green-600" />
    ) : (
      <XCircle className="w-4 h-4 text-red-600" />
    )
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Building2 className="w-5 h-5 text-indigo-600" />
        <h3 className="text-lg font-semibold text-gray-900">A. Business Identity & Registration (10%)</h3>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-4">
          <p className="text-xs font-semibold text-indigo-900 uppercase">Business Age</p>
          <p className="text-2xl font-bold text-indigo-600 mt-1">
            {features.business_age_years?.toFixed(1) || identity.business_age_years?.toFixed(1) || '0'} years
          </p>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-xl p-4">
          <p className="text-xs font-semibold text-blue-900 uppercase">Legal Entity</p>
          <p className="text-lg font-bold text-blue-600 mt-1 capitalize">
            {features.legal_entity_type || identity.legal_entity_type || 'N/A'}
          </p>
        </div>
      </div>

      {/* Business Details */}
      <div className="mb-6 space-y-2 text-sm">
        <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
          <Building2 className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600">Industry:</span>
          <span className="font-semibold ml-auto capitalize">
            {features.industry_code || identity.industry_code || msme.industry || 'N/A'}
          </span>
        </div>
        <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
          <Users className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600">Employees:</span>
          <span className="font-semibold ml-auto">
            {formatNumber(features.employees_count || identity.employees_count || 0)}
          </span>
        </div>
        <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
          <MapPin className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600">Locations:</span>
          <span className="font-semibold ml-auto">
            {features.num_business_locations || identity.num_business_locations || 1}
          </span>
        </div>
        <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">MSME Category:</span>
          <span className="font-semibold ml-auto capitalize">
            {features.msme_category || identity.msme_category || msme.msme_category || 'N/A'}
          </span>
        </div>
        <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Business Structure:</span>
          <span className="font-semibold ml-auto capitalize">
            {features.business_structure || identity.business_structure || 'N/A'}
          </span>
        </div>
      </div>

      {/* Verification Status */}
      <div className="mb-6">
        <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
          <Shield className="w-4 h-4 text-gray-500" />
          Verification Status
        </h4>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex items-center justify-between bg-gray-50 rounded-lg p-2">
            <span className="text-gray-600">PAN Verified</span>
            {getVerificationBadge(features.pan_verified ?? identity.pan_verified ?? false)}
          </div>
          <div className="flex items-center justify-between bg-gray-50 rounded-lg p-2">
            <span className="text-gray-600">GSTIN Verified</span>
            {getVerificationBadge(features.gstin_verified ?? identity.gstin_verified ?? false)}
          </div>
          <div className="flex items-center justify-between bg-gray-50 rounded-lg p-2">
            <span className="text-gray-600">Address Verified</span>
            {getVerificationBadge(features.business_address_verified ?? identity.business_address_verified ?? false)}
          </div>
          <div className="flex items-center justify-between bg-gray-50 rounded-lg p-2">
            <span className="text-gray-600">Geolocation Verified</span>
            {getVerificationBadge(features.geolocation_verified ?? identity.geolocation_verified ?? false)}
          </div>
          <div className="flex items-center justify-between bg-gray-50 rounded-lg p-2">
            <span className="text-gray-600">MSME Registered</span>
            {getVerificationBadge(features.msme_registered ?? identity.msme_registered ?? false)}
          </div>
        </div>
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-gray-500 text-xs">Industry Risk Score</p>
          <p className="font-bold text-lg">
            {((features.industry_risk_score || identity.industry_risk_score || 0) * 100).toFixed(0)}%
          </p>
        </div>
        <div className="bg-gray-50 rounded-lg p-3">
          <p className="text-gray-500 text-xs">Licenses Score</p>
          <p className="font-bold text-lg">
            {((features.licenses_certificates_score || identity.licenses_certificates_score || 0) * 100).toFixed(0)}%
          </p>
        </div>
      </div>
    </div>
  )
}



