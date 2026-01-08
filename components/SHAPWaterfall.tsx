interface SHAPWaterfallProps {
  data: Array<{ feature: string; value: number; impact: "positive" | "negative" }>
  baseScore?: number
  finalScore?: number
}

export default function SHAPWaterfall({ data, baseScore = 700, finalScore }: SHAPWaterfallProps) {
  let cumulativeValue = 0

  return (
    <div className="space-y-3">
      <div className="bg-gray-50 p-4 rounded-lg">
        <p className="text-sm font-semibold text-gray-900">Base Score: {baseScore}</p>
      </div>

      {data.map((item, idx) => {
        cumulativeValue += item.value
        const isPositive = item.impact === "positive"

        return (
          <div key={idx} className="flex items-center gap-4">
            <div className="w-48">
              <p className="text-sm font-medium text-gray-900">{item.feature}</p>
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <div className="w-full bg-gray-200 rounded h-6 relative">
                  <div
                    className={`h-full rounded transition ${isPositive ? "bg-green-500" : "bg-red-500"}`}
                    style={{ width: `${Math.min((Math.abs(item.value) / 100) * 100, 100)}%` }}
                  />
                </div>
                <span
                  className={`text-sm font-semibold w-16 text-right ${isPositive ? "text-green-600" : "text-red-600"}`}
                >
                  {isPositive ? "+" : ""}
                  {item.value}
                </span>
              </div>
            </div>
          </div>
        )
      })}

      <div className="bg-blue-50 p-4 rounded-lg border border-blue-200 mt-4">
        <p className="text-sm font-semibold text-blue-900">
          Final Score: {finalScore !== undefined ? finalScore : baseScore + cumulativeValue}
        </p>
      </div>
    </div>
  )
}
