import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts"

interface RiskSegmentationChartProps {
  data: any
}

export default function RiskSegmentationChart({ data }: RiskSegmentationChartProps) {
  const chartData = [
    { name: `Low (${data.low.count})`, value: data.low.percentage },
    { name: `Medium (${data.medium.count})`, value: data.medium.percentage },
    { name: `High (${data.high.count})`, value: data.high.percentage },
  ]

  const colors = ["#10b981", "#f59e0b", "#ef4444"]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie data={chartData} cx="50%" cy="50%" outerRadius={100} fill="#8884d8" dataKey="value">
          {colors.map((color, index) => (
            <Cell key={`cell-${index}`} fill={color} />
          ))}
        </Pie>
        <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  )
}
