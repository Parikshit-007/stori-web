"use client"

import { Globe, AlertTriangle, Star, TrendingUp } from "lucide-react"

interface ExternalSignalsCardProps {
  msme: any
}

export default function ExternalSignalsCard({ msme }: ExternalSignalsCardProps) {
  const features = msme.features || {}
  const external = msme.external || {}

  const formatPercent = (val: number) => {
    return `${(val * 100).toFixed(1)}%`
  }

  const localEconomicHealth = features.local_economic_health_score || external.local_economic_health_score || 0
  const customerConcentration = features.customer_concentration_risk || external.customer_concentration_risk || 0
  const legalProceedings = features.legal_proceedings_flag || external.legal_proceedings_flag || 0
  const legalDisputes = features.legal_disputes_count || external.legal_disputes_count || 0
  const socialMediaPresence = features.social_media_presence_score || external.social_media_presence_score || 0
  const socialMediaSentiment = features.social_media_sentiment_score || external.social_media_sentiment_score || 0
  const onlineReviews = features.online_reviews_score || external.online_reviews_score || 0

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className="flex items-center gap-2 mb-6">
        <Globe className="w-5 h-5 text-teal-600" />
        <h3 className="text-lg font-semibold text-gray-900">G. External Signals (4%)</h3>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className={`bg-gradient-to-br rounded-xl p-4 ${localEconomicHealth >= 0.7 ? 'from-green-50 to-emerald-50' : localEconomicHealth >= 0.5 ? 'from-yellow-50 to-amber-50' : 'from-red-50 to-rose-50'}`}>
          <p className="text-xs font-semibold uppercase">Local Economic Health</p>
          <p className={`text-2xl font-bold mt-1 ${localEconomicHealth >= 0.7 ? 'text-green-600' : localEconomicHealth >= 0.5 ? 'text-yellow-600' : 'text-red-600'}`}>
            {formatPercent(localEconomicHealth)}
          </p>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4">
          <p className="text-xs font-semibold uppercase">Online Reviews</p>
          <div className="flex items-center gap-1 mt-1">
            <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
            <p className="text-2xl font-bold text-blue-600">{onlineReviews.toFixed(1)}</p>
            <span className="text-xs text-gray-500">/5.0</span>
          </div>
        </div>
      </div>

      {/* Risk Indicators */}
      {(legalProceedings === 1 || legalDisputes > 0 || customerConcentration > 0.7) && (
        <div className="mb-6">
          <h4 className="font-semibold text-gray-800 text-sm mb-3 flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-500" />
            Risk Indicators
          </h4>
          <div className="space-y-2">
            {legalProceedings === 1 && (
              <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                <p className="text-red-900 text-xs mb-1">⚠️ Legal Proceedings Flag Active</p>
                {legalDisputes > 0 && (
                  <p className="text-red-700 text-sm">Disputes: {legalDisputes}</p>
                )}
              </div>
            )}
            {customerConcentration > 0.7 && (
              <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
                <p className="text-yellow-900 text-xs mb-1">High Customer Concentration Risk</p>
                <p className="text-xl font-bold text-yellow-600">{formatPercent(customerConcentration)}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Social Media & Online Presence */}
      <div className="space-y-2 text-sm">
        <h4 className="font-semibold text-gray-800 text-sm mb-2">Online Presence</h4>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Social Media Presence</span>
          <span className="font-semibold">{formatPercent(socialMediaPresence)}</span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Social Media Sentiment</span>
          <span className={`font-semibold ${socialMediaSentiment >= 0.7 ? 'text-green-600' : socialMediaSentiment >= 0.5 ? 'text-yellow-600' : 'text-red-600'}`}>
            {formatPercent(socialMediaSentiment)}
          </span>
        </div>
        <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
          <span className="text-gray-600">Customer Concentration Risk</span>
          <span className={`font-semibold ${customerConcentration < 0.3 ? 'text-green-600' : customerConcentration < 0.7 ? 'text-yellow-600' : 'text-red-600'}`}>
            {formatPercent(customerConcentration)}
          </span>
        </div>
      </div>
    </div>
  )
}



