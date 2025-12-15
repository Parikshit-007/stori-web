"use client"

interface WeightSliderProps {
  label: string
  value: number
  onChange: (value: number) => void
}

export default function WeightSlider({ label, value, onChange }: WeightSliderProps) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        <span className="text-sm font-semibold text-gray-900 bg-gray-100 px-3 py-1 rounded-lg">{value}%</span>
      </div>
      <input
        type="range"
        min="0"
        max="100"
        value={value}
        onChange={(e) => onChange(Number.parseInt(e.target.value))}
        className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
      />
    </div>
  )
}
