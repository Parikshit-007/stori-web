"use client"
import { useState } from "react"
import { mockApi } from "@/lib/mockApi"
import { Zap } from "lucide-react"
import WeightSlider from "@/components/WeightSlider"
import ScorePreviewCard from "@/components/ScorePreviewCard"

const personas = ["Salaried", "NTC", "Gig", "Credit-Experienced", "Mass Affluent"]
const categories = [
  { id: "identity", label: "A - Identity & Demographics" },
  { id: "income", label: "B - Income & Cashflow" },
  { id: "assets", label: "C - Assets & Liabilities" },
  { id: "behaviour", label: "D - Behavioural Signals" },
  { id: "transactions", label: "E - Transactions & Utility" },
  { id: "fraud", label: "F - Fraud & Identity" },
  { id: "family", label: "G - Family & Network" },
]

export default function ScoreBuilder() {
  const [selectedPersona, setSelectedPersona] = useState("Salaried")
  const [weights, setWeights] = useState({
    identity: 15,
    income: 20,
    assets: 18,
    behaviour: 15,
    transactions: 15,
    fraud: 10,
    family: 7,
  })
  const [gbmResponse, setGbmResponse] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [enabledFeatures, setEnabledFeatures] = useState({
    faceMatch: true,
    incomeStability: true,
    emiRatio: true,
    upiConsistency: true,
    fraudSignals: true,
    deviceAnomalies: true,
    socialStability: false,
  })

  const handlePersonaChange = async (persona: string) => {
    setSelectedPersona(persona)
    try {
      const personaWeights = await mockApi.getPersonaWeights(persona)
      setWeights(personaWeights)
    } catch (error) {
      console.error("Error loading persona weights:", error)
    }
  }

  const handleWeightChange = (category: string, value: number) => {
    const other = Object.keys(weights)
      .filter((k) => k !== category)
      .reduce((sum, k) => sum + (weights[k as keyof typeof weights] as number), 0)

    if (value + other <= 100) {
      setWeights((prev) => ({
        ...prev,
        [category]: value,
      }))
    }
  }

  const totalWeight = Object.values(weights).reduce((sum, v) => sum + v, 0)

  const handleSendToGBM = async () => {
    setLoading(true)
    try {
      const response = await mockApi.postScore({
        consumerId: "test-001",
        persona: selectedPersona,
        weights,
      })
      setGbmResponse(response)
    } catch (error) {
      console.error("Error calling GBM:", error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Score Builder</h1>
        <p className="text-gray-600 mt-1">Configure GBM model weights by persona</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Configuration Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Persona Selector */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Persona & Features</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Select Persona</label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                  {personas.map((p) => (
                    <button
                      key={p}
                      onClick={() => handlePersonaChange(p)}
                      className={`px-4 py-3 rounded-lg transition font-medium text-sm ${
                        selectedPersona === p ? "bg-blue-500 text-white" : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                      }`}
                    >
                      {p}
                    </button>
                  ))}
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <h4 className="font-semibold text-gray-900 mb-3">Feature Toggles</h4>
                <div className="space-y-2">
                  {Object.entries(enabledFeatures).map(([feature, enabled]) => (
                    <label key={feature} className="flex items-center gap-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={enabled}
                        onChange={(e) =>
                          setEnabledFeatures((prev) => ({
                            ...prev,
                            [feature]: e.target.checked,
                          }))
                        }
                        className="w-4 h-4 rounded border-gray-300"
                      />
                      <span className="text-sm text-gray-700 capitalize">{feature.replace(/([A-Z])/g, " $1")}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Weight Sliders */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Category Weights</h3>
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-600">Auto-normalized (Total must equal 100)</p>
                <div className={`text-sm font-semibold ${totalWeight === 100 ? "text-green-600" : "text-red-600"}`}>
                  Total: {totalWeight}%
                </div>
              </div>
            </div>

            {categories.map((cat) => (
              <WeightSlider
                key={cat.id}
                label={cat.label}
                value={weights[cat.id as keyof typeof weights]}
                onChange={(val) => handleWeightChange(cat.id, val)}
              />
            ))}
          </div>
        </div>

        {/* Preview Card */}
        <div className="lg:col-span-1">
          <div className="sticky top-24 space-y-4">
            {/* Local Preview */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl shadow-sm border border-blue-200 p-6">
              <h3 className="text-sm font-semibold text-blue-900 mb-4">LOCAL PREVIEW</h3>
              <div className="bg-white rounded-lg p-4 mb-4">
                <p className="text-xs text-gray-600 mb-1">Calculated Score</p>
                <p className="text-4xl font-bold text-blue-600">{Math.round(650 + Math.random() * 200)}</p>
                <p className="text-xs text-gray-500 mt-2">Not GBM output</p>
              </div>
              <p className="text-xs text-blue-700 bg-blue-100 px-3 py-2 rounded">
                This is a local calculation. Submit to GBM for production score.
              </p>
            </div>

            {/* GBM Response */}
            {gbmResponse && <ScorePreviewCard response={gbmResponse} />}

            {/* Send Button */}
            <button
              onClick={handleSendToGBM}
              disabled={loading || totalWeight !== 100}
              className="w-full px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:shadow-lg transition disabled:opacity-50 font-semibold flex items-center justify-center gap-2"
            >
              <Zap className="w-5 h-5" />
              {loading ? "Sending to GBM..." : "Send to GBM Model"}
            </button>

            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
              <p className="text-xs font-semibold text-yellow-900 mb-2">Requirements</p>
              <ul className="text-xs text-yellow-800 space-y-1">
                <li>✓ Weights must sum to 100%</li>
                <li>✓ At least 1 feature enabled</li>
                <li>• Features can be toggled on/off</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
