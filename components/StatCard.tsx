import type { LucideIcon } from "lucide-react"

interface StatCardProps {
  icon: LucideIcon
  label: string
  value: string | number
  color: "blue" | "purple" | "green" | "red"
}

export default function StatCard({ icon: Icon, label, value, color }: StatCardProps) {
  const colors = {
    blue: "bg-blue-50 text-blue-600",
    purple: "bg-purple-50 text-purple-600",
    green: "bg-green-50 text-green-600",
    red: "bg-red-50 text-red-600",
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
      <div className={`w-12 h-12 rounded-lg ${colors[color]} flex items-center justify-center mb-4`}>
        <Icon className="w-6 h-6" />
      </div>
      <p className="text-gray-600 text-sm font-medium mb-1">{label}</p>
      <p className="text-3xl font-bold text-gray-900">{value}</p>
    </div>
  )
}
