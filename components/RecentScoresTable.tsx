interface RecentScoresTableProps {
  data: Array<any>
}

export default function RecentScoresTable({ data }: RecentScoresTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 font-semibold text-gray-900">Consumer</th>
            <th className="text-left py-3 px-4 font-semibold text-gray-900">Time</th>
            <th className="text-left py-3 px-4 font-semibold text-gray-900">Score</th>
            <th className="text-left py-3 px-4 font-semibold text-gray-900">Risk</th>
            <th className="text-left py-3 px-4 font-semibold text-gray-900">Action</th>
          </tr>
        </thead>
        <tbody>
          {data.map((record) => (
            <tr key={record.id} className="border-b border-gray-100 hover:bg-gray-50 transition">
              <td className="py-3 px-4 text-gray-900 font-medium">{record.consumerName}</td>
              <td className="py-3 px-4 text-gray-600">{record.timestamp}</td>
              <td className="py-3 px-4 font-semibold text-gray-900">{record.score}</td>
              <td className="py-3 px-4">
                <span
                  className={`px-2 py-1 rounded text-xs font-semibold ${
                    record.riskBucket === "Low"
                      ? "bg-green-100 text-green-800"
                      : record.riskBucket === "Medium"
                        ? "bg-yellow-100 text-yellow-800"
                        : "bg-red-100 text-red-800"
                  }`}
                >
                  {record.riskBucket}
                </span>
              </td>
              <td className="py-3 px-4 text-blue-600 font-semibold">{record.action}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
