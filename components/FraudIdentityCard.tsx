"use client"

import { ShieldAlert, Fingerprint, FileWarning, UserX, CheckCircle, XCircle, AlertTriangle, MapPin } from "lucide-react"

interface FraudIdentityCardProps {
  consumer: any
}

export default function FraudIdentityCard({ consumer }: FraudIdentityCardProps) {
  const { fraud } = consumer

  const getRiskColor = (probability: number) => {
    if (probability <= 5) return "text-green-600 bg-green-50 border-green-200"
    if (probability <= 15) return "text-amber-600 bg-amber-50 border-amber-200"
    return "text-red-600 bg-red-50 border-red-200"
  }

  const getCheckStatus = (status: string) => {
    if (status === "Pass") return { icon: CheckCircle, color: "text-green-600" }
    if (status === "Minor Issues") return { icon: AlertTriangle, color: "text-amber-600" }
    return { icon: XCircle, color: "text-red-600" }
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <ShieldAlert className="w-5 h-5 text-red-600" />
        <h3 className="text-lg font-semibold text-gray-900">5. Fraud & Identity Strength</h3>
        {(fraud.historicalFraudSignals || 0) > 0 && (
          <span className="ml-auto px-2 py-1 rounded bg-red-100 text-red-700 text-xs font-bold">
            {fraud.historicalFraudSignals} Historical Signal(s)
          </span>
        )}
      </div>

      {/* (A) Identity Matching */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Fingerprint className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(A) Identity Matching</h4>
          <span className={`ml-auto px-2 py-1 rounded-full text-xs font-bold ${(fraud.identityMatching?.overallScore || 0) >= 90 ? 'bg-green-100 text-green-700' : (fraud.identityMatching?.overallScore || 0) >= 75 ? 'bg-amber-100 text-amber-700' : 'bg-red-100 text-red-700'}`}>
            {fraud.identityMatching?.overallScore || 0}%
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 mb-2">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">Name Match (Platforms)</p>
            <p className={`font-bold text-lg ${(fraud.identityMatching?.nameMatchAcrossPlatforms || 0) >= 90 ? 'text-green-600' : 'text-amber-600'}`}>
              {fraud.identityMatching?.nameMatchAcrossPlatforms || 0}%
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">Email/Phone Consistency</p>
            <p className={`font-bold text-lg ${(fraud.identityMatching?.emailPhoneConsistency || 0) >= 90 ? 'text-green-600' : 'text-amber-600'}`}>
              {fraud.identityMatching?.emailPhoneConsistency || 0}%
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">Geo-Location Match</p>
            <p className={`font-bold text-lg ${(fraud.identityMatching?.geoLocationMatch || 0) >= 90 ? 'text-green-600' : 'text-amber-600'}`}>
              {fraud.identityMatching?.geoLocationMatch || 0}%
            </p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-xs text-gray-500">Social Media Match</p>
            <p className={`font-bold text-lg ${(fraud.identityMatching?.socialMediaMatch || 0) >= 90 ? 'text-green-600' : 'text-amber-600'}`}>
              {fraud.identityMatching?.socialMediaMatch || 0}%
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
          <MapPin className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-600">Pin Code Risk:</span>
          <span className={`ml-auto px-2 py-1 rounded text-xs font-bold ${fraud.pinCodeRisk === 'Low Risk' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
            {fraud.pinCodeRisk || 'Low Risk'}
          </span>
        </div>
      </div>

      {/* (B) Bank Statement Manipulation */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <FileWarning className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(B) Bank Statement Manipulation</h4>
        </div>
        <div className={`p-4 rounded-xl border ${getRiskColor(fraud.statementManipulation?.probability || 0)}`}>
          <div className="flex justify-between items-center mb-3">
            <span className="font-semibold">Manipulation Probability</span>
            <span className="text-2xl font-bold">{fraud.statementManipulation?.probability || 0}%</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            {[
              { label: "Pixel Structure", value: fraud.statementManipulation?.pixelStructureCheck },
              { label: "Font Variation", value: fraud.statementManipulation?.fontVariationCheck },
              { label: "Duplicate Template", value: fraud.statementManipulation?.duplicateTemplateCheck },
              { label: "OCR Consistency", value: fraud.statementManipulation?.ocrConsistency },
            ].map((check, idx) => {
              const status = getCheckStatus(check.value || 'Pass')
              const Icon = status.icon
              return (
                <div key={idx} className="flex items-center gap-2 bg-white/50 rounded p-2">
                  <Icon className={`w-4 h-4 ${status.color}`} />
                  <span className="text-gray-700">{check.label}</span>
                </div>
              )
            })}
          </div>
          <div className="mt-2 pt-2 border-t border-current/20 flex justify-between items-center">
            <span className="text-xs">Salary-to-UPI Ratio:</span>
            <span className={`text-xs font-semibold px-2 py-1 rounded ${fraud.statementManipulation?.salaryToUpiRatio === 'Normal' ? 'bg-green-200 text-green-800' : 'bg-amber-200 text-amber-800'}`}>
              {fraud.statementManipulation?.salaryToUpiRatio || 'Normal'}
            </span>
          </div>
        </div>
      </div>

      {/* (C) Synthetic Identity */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <UserX className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(C) Synthetic Identity Detection</h4>
        </div>
        <div className={`p-4 rounded-xl border ${getRiskColor(fraud.syntheticIdentity?.probability || 0)}`}>
          <div className="flex justify-between items-center mb-2">
            <span className="font-semibold">Synthetic ID Probability</span>
            <span className="text-2xl font-bold">{fraud.syntheticIdentity?.probability || 0}%</span>
          </div>
          <div className="flex justify-between items-center text-sm mb-2">
            <span>Name/DOB Similarity Check</span>
            <span className="font-semibold">{fraud.syntheticIdentity?.nameDobSimilarity || 'No Match'}</span>
          </div>
          <div className="pt-2 border-t border-current/20 flex justify-between">
            <span className="text-xs">Risk Level</span>
            <span className={`px-2 py-0.5 rounded text-xs font-bold ${
              fraud.syntheticIdentity?.riskLevel === 'Very Low' ? 'bg-green-200 text-green-800' : 
              fraud.syntheticIdentity?.riskLevel === 'Low' ? 'bg-green-100 text-green-700' : 
              fraud.syntheticIdentity?.riskLevel === 'Medium' ? 'bg-amber-100 text-amber-700' : 
              'bg-red-100 text-red-700'
            }`}>
              {fraud.syntheticIdentity?.riskLevel || 'Low'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
