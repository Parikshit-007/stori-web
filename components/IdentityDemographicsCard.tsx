"use client"

import { Shield, Smartphone, Home, Users, CheckCircle, User, MapPin, Phone } from "lucide-react"

interface IdentityDemographicsCardProps {
  consumer: any
}

export default function IdentityDemographicsCard({ consumer }: IdentityDemographicsCardProps) {
  const { identity } = consumer

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-600 bg-emerald-50"
    if (score >= 60) return "text-amber-600 bg-amber-50"
    return "text-red-600 bg-red-50"
  }

  const getSocialCapitalLevel = (score: number) => {
    if (score >= 75) return "High"
    if (score >= 50) return "Medium"
    return "Low"
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Shield className="w-5 h-5 text-indigo-600" />
        <h3 className="text-lg font-semibold text-gray-900">1. Identity & Demographics</h3>
      </div>

      {/* Basic Info */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl p-4">
          <p className="text-xs font-semibold text-indigo-900 uppercase">Face Match</p>
          <p className="text-2xl font-bold text-indigo-600 mt-1">{identity.faceMatch}%</p>
        </div>
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl p-4">
          <p className="text-xs font-semibold text-green-900 uppercase">Name Match</p>
          <p className="text-lg font-bold text-green-600 mt-1 flex items-center gap-1">
            <CheckCircle className="w-4 h-4" /> {identity.nameMatch}
          </p>
        </div>
      </div>

      {/* Personal Details */}
      <div className="mb-6 space-y-2 text-sm">
        <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
          <User className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600">Age:</span>
          <span className="font-semibold ml-auto">{consumer.age || Math.floor((new Date().getTime() - new Date(consumer.dob).getTime()) / (365.25 * 24 * 60 * 60 * 1000))} years</span>
        </div>
        <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
          <MapPin className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600">Address:</span>
          <span className="font-semibold ml-auto text-right text-xs">{identity.address}</span>
        </div>
        <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
          <Phone className="w-4 h-4 text-gray-400" />
          <span className="text-gray-600">Phone:</span>
          <span className="font-semibold ml-auto">{consumer.phone}</span>
        </div>
        <div className="flex items-center gap-2 p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">PAN:</span>
          <span className="font-semibold ml-auto">{identity.pan || 'Not Available'}</span>
        </div>
      </div>

      {/* Digital Identity Trust Score */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Smartphone className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(A) Digital Identity Trust Score</h4>
          <span className={`ml-auto px-2 py-1 rounded-full text-xs font-bold ${getScoreColor(identity.digitalIdentity?.overallTrustScore || 0)}`}>
            {identity.digitalIdentity?.overallTrustScore || 0}/100
          </span>
        </div>
        <div className="grid grid-cols-3 gap-2 text-sm mb-2">
          <div className="bg-gray-50 rounded-lg p-2 text-center">
            <p className="text-gray-500 text-xs">Device Age</p>
            <p className="font-semibold">{identity.digitalIdentity?.deviceAge || 0} mo</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-2 text-center">
            <p className="text-gray-500 text-xs">SIM Age</p>
            <p className="font-semibold">{identity.digitalIdentity?.simAge || 0} mo</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-2 text-center">
            <p className="text-gray-500 text-xs">Email Age</p>
            <p className="font-semibold">{identity.digitalIdentity?.emailAge || 0} mo</p>
          </div>
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="flex justify-between bg-gray-50 rounded-lg p-2">
            <span className="text-gray-500 text-xs">Platform Consistency</span>
            <span className="font-semibold text-xs">{identity.digitalIdentity?.platformConsistency || 0}%</span>
          </div>
          <div className="flex justify-between bg-gray-50 rounded-lg p-2">
            <span className="text-gray-500 text-xs">Aadhaar-PAN</span>
            <span className="font-semibold text-xs">{identity.digitalIdentity?.aadhaarPanMatchStability || 'N/A'}</span>
          </div>
        </div>
        {identity.digitalIdentity?.lowAgeFlag && (
          <p className="text-xs text-amber-600 mt-1">⚠️ Low age flag detected</p>
        )}
      </div>

      {/* Life Stability Index */}
      <div className="mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Home className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(B) Life Stability Index</h4>
          <span className={`ml-auto px-2 py-1 rounded-full text-xs font-bold ${getScoreColor(identity.lifeStability?.overallScore || 0)}`}>
            {identity.lifeStability?.overallScore || 0}/100
          </span>
        </div>
        <div className="space-y-2 text-sm">
          <div className="p-2 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Job Stability</span>
              <span className={`font-bold ${(identity.lifeStability?.jobStability?.score || 0) >= 70 ? 'text-green-600' : 'text-amber-600'}`}>
                {identity.lifeStability?.jobStability?.score || 0}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              Avg Duration: {identity.lifeStability?.jobStability?.avgEmploymentDuration || 0}y • 
              Salary Hikes: {identity.lifeStability?.jobStability?.salaryHikes || 0}
              {identity.lifeStability?.jobStability?.currentEmployer && ` • ${identity.lifeStability.jobStability.currentEmployer}`}
            </p>
          </div>
          <div className="p-2 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Residence Stability</span>
              <span className={`font-bold ${(identity.lifeStability?.residenceStability?.score || 0) >= 70 ? 'text-green-600' : 'text-amber-600'}`}>
                {identity.lifeStability?.residenceStability?.score || 0}
              </span>
            </div>
            <p className="text-xs text-gray-400 mt-1">
              {identity.lifeStability?.residenceStability?.yearsAtCurrentAddress || 0}y at address • 
              Landlord: {identity.lifeStability?.residenceStability?.landlordVerified ? '✓ Verified' : 'Not Verified'} • 
              Rent: {identity.lifeStability?.residenceStability?.rentPaymentPattern || 'N/A'}
            </p>
          </div>
          <div className="p-2 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="text-gray-600 font-medium">Household Stability</span>
              <span className={`font-bold ${(identity.lifeStability?.householdStability?.score || 0) >= 70 ? 'text-green-600' : 'text-amber-600'}`}>
                {identity.lifeStability?.householdStability?.status || 'N/A'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Social Capital Proxy */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <Users className="w-4 h-4 text-gray-500" />
          <h4 className="font-semibold text-gray-800 text-sm">(C) Social Capital Proxy</h4>
          <span className={`ml-auto px-2 py-1 rounded-full text-xs font-bold ${
            (identity.socialCapital?.level || getSocialCapitalLevel(identity.socialCapital?.overallScore || 0)) === 'High' 
              ? 'bg-green-100 text-green-700' 
              : (identity.socialCapital?.level || getSocialCapitalLevel(identity.socialCapital?.overallScore || 0)) === 'Medium'
                ? 'bg-amber-100 text-amber-700'
                : 'bg-red-100 text-red-700'
          }`}>
            {identity.socialCapital?.level || getSocialCapitalLevel(identity.socialCapital?.overallScore || 0)}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs">Regular Peer Transactions</p>
            <p className="font-bold text-lg">{identity.socialCapital?.regularPeerTransactions || 0}%</p>
          </div>
          <div className="bg-gray-50 rounded-lg p-3">
            <p className="text-gray-500 text-xs">Professional Network</p>
            <p className="font-bold text-lg">{identity.socialCapital?.professionalNetworkPayments || 0}%</p>
          </div>
        </div>
      </div>
    </div>
  )
}
