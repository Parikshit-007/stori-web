interface ScoringHistoryCardProps {
  consumer: any
}

export default function ScoringHistoryCard({ consumer }: ScoringHistoryCardProps) {
  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Scoring History</h3>
      <div className="space-y-3">
        {consumer.scoringHistory.map((record: any, idx: number) => (
          <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p className="font-semibold text-gray-900">{record.date}</p>
              <p className="text-xs text-gray-500">{record.method}</p>
            </div>
            <span className="text-lg font-bold text-blue-600">{record.score}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
