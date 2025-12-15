import { AlertCircle } from "lucide-react"

interface RiskAlertsListProps {
  consumers: Array<any>
}

export default function RiskAlertsList({ consumers }: RiskAlertsListProps) {
  if (consumers.length === 0) {
    return <p className="text-gray-500 text-center py-8">No high-risk consumers at this time</p>
  }

  return (
    <div className="space-y-3">
      {consumers.map((consumer) => (
        <div key={consumer.id} className="flex items-start gap-4 p-4 border border-red-200 bg-red-50 rounded-lg">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <p className="font-semibold text-gray-900">{consumer.name}</p>
              <span className="text-lg font-bold text-red-600">{consumer.currentScore}</span>
            </div>
            <p className="text-sm text-gray-600 mb-2">{consumer.email}</p>
            <div className="flex flex-wrap gap-2">
              <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-semibold">High Risk</span>
              <span className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">{consumer.persona}</span>
              <span className="px-2 py-1 bg-orange-100 text-orange-700 rounded text-xs">
                FOIR: {(consumer.transactions?.emiRepaymentRatio * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
