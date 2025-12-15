import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts"

interface RiskDistributionChartProps {
  data: {
    low: { count: number; percentage: number }
    medium: { count: number; percentage: number }
    high: { count: number; percentage: number }
  }
}

export default function RiskDistributionChart({ data }: RiskDistributionChartProps) {
  const chartData = [
    { name: "Low Risk", value: data.low.percentage },
    { name: "Medium Risk", value: data.medium.percentage },
    { name: "High Risk", value: data.high.percentage },
  ]

  const colors = ["#10b981", "#f59e0b", "#ef4444"]

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index]} />
          ))}
        </Pie>
        <Tooltip formatter={(value) => `${value.toFixed(1)}%`} />
      </PieChart>
    </ResponsiveContainer>
  )
}
