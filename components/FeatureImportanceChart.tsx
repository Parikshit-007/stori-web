import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

interface FeatureImportanceChartProps {
  data: Array<{ feature: string; importance: number }>
}

export default function FeatureImportanceChart({ data }: FeatureImportanceChartProps) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={data} layout="vertical" margin={{ left: 200, right: 30 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis type="number" stroke="#9ca3af" />
        <YAxis dataKey="feature" type="category" width={195} stroke="#9ca3af" tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
          formatter={(value: number) => `${value.toFixed(2)}%`}
        />
        <Bar dataKey="importance" fill="#6366f1" radius={[0, 8, 8, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
