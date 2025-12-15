interface ScorePreviewCardProps {
  response: any
}

export default function ScorePreviewCard({ response }: ScorePreviewCardProps) {
  return (
    <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl shadow-sm border border-green-200 p-6">
      <h3 className="text-sm font-semibold text-green-900 mb-4">GBM MODEL RESPONSE</h3>

      <div className="space-y-4">
        <div className="bg-white rounded-lg p-4">
          <p className="text-xs text-gray-600 mb-1">Credit Score</p>
          <p className="text-3xl font-bold text-green-600">{response.score}</p>
          <p className="text-xs text-gray-500 mt-1">
            90DPD Probability: {(response.prob_default_90dpd * 100).toFixed(2)}%
          </p>
        </div>

        <div className="bg-white rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 text-sm mb-2">Top Positive Factors</h4>
          <ul className="space-y-1">
            {response.explanation.top_positive.map((factor: string) => (
              <li key={factor} className="text-xs text-green-700 flex items-center gap-2">
                <span className="text-green-600">✓</span>
                {factor.replace(/_/g, " ")}
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white rounded-lg p-4">
          <h4 className="font-semibold text-gray-900 text-sm mb-2">Top Negative Factors</h4>
          <ul className="space-y-1">
            {response.explanation.top_negative.map((factor: string) => (
              <li key={factor} className="text-xs text-red-700 flex items-center gap-2">
                <span className="text-red-600">✗</span>
                {factor.replace(/_/g, " ")}
              </li>
            ))}
          </ul>
        </div>

        <p className="text-xs text-gray-500 text-center">{response.model_version}</p>
      </div>
    </div>
  )
}
