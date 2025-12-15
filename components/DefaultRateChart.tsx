import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

interface DefaultRateChartProps {
  data: Array<{ persona: string; defaultProb: number }>
}

export default function DefaultRateChart({ data }: DefaultRateChartProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis dataKey="persona" stroke="#9ca3af" />
        <YAxis stroke="#9ca3af" />
        <Tooltip
          contentStyle={{ backgroundColor: "#fff", border: "1px solid #e5e7eb", borderRadius: "8px" }}
          formatter={(value) => [`${(value * 100).toFixed(2)}%`, "Default Prob"]}
        />
        <Bar dataKey="defaultProb" fill="#ef4444" radius={[8, 8, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
