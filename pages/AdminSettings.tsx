"use client"
import { useState } from "react"
import { Save, Plus, Trash2, Eye, EyeOff } from "lucide-react"

export default function AdminSettings() {
  const [scoreScale, setScoreScale] = useState("300-900")
  const [showApiKey, setShowApiKey] = useState(false)
  const [apiKey] = useState("sk_live_xxxxxxxxxxxxxxxxxxx")
  const [users, setUsers] = useState([
    { id: 1, name: "John Doe", email: "john@company.com", role: "Admin" },
    { id: 2, name: "Jane Smith", email: "jane@company.com", role: "Analyst" },
    { id: 3, name: "Bob Wilson", email: "bob@company.com", role: "Viewer" },
  ])

  const personaTemplates = [
    {
      id: 1,
      name: "Salaried",
      weights: { identity: 15, income: 20, assets: 18, behaviour: 15, transactions: 15, fraud: 10, family: 7 },
    },
    {
      id: 2,
      name: "NTC",
      weights: { identity: 28, income: 22, assets: 12, behaviour: 18, transactions: 12, fraud: 8, family: 0 },
    },
    {
      id: 3,
      name: "Gig",
      weights: { identity: 20, income: 25, assets: 15, behaviour: 15, transactions: 15, fraud: 8, family: 2 },
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Admin & Settings</h1>
        <p className="text-gray-600 mt-1">Configuration and internal settings</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* Score Scale */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Scoring Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Score Scale</label>
                <select
                  value={scoreScale}
                  onChange={(e) => setScoreScale(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="300-900">300 - 900 (CIBIL-like)</option>
                  <option value="0-1000">0 - 1000 (Linear)</option>
                  <option value="0-100">0 - 100 (Percentage)</option>
                </select>
              </div>
              <button className="inline-flex items-center gap-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition">
                <Save className="w-4 h-4" />
                Save Configuration
              </button>
            </div>
          </div>

          {/* Persona Templates */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Persona Weight Templates</h3>
              <button className="inline-flex items-center gap-2 px-3 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition text-sm font-medium">
                <Plus className="w-4 h-4" />
                New Template
              </button>
            </div>
            <div className="space-y-3">
              {personaTemplates.map((template) => (
                <div key={template.id} className="p-4 border border-gray-200 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="font-semibold text-gray-900">{template.name}</h4>
                    <button className="p-1 text-gray-400 hover:text-red-600 transition">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="grid grid-cols-4 gap-2 text-sm">
                    {Object.entries(template.weights).map(([cat, weight]: [string, any]) => (
                      <div key={cat} className="bg-gray-50 px-2 py-1 rounded">
                        <p className="text-gray-600 text-xs capitalize">{cat}</p>
                        <p className="font-semibold text-gray-900">{weight}%</p>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* API Keys */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">API Configuration</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">GBM Model API Key</label>
                <div className="flex gap-2">
                  <input
                    type={showApiKey ? "text" : "password"}
                    value={apiKey}
                    readOnly
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
                  />
                  <button
                    onClick={() => setShowApiKey(!showApiKey)}
                    className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
                  >
                    {showApiKey ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                  </button>
                </div>
              </div>
              <p className="text-xs text-gray-500">TODO: Connect to your GBM model backend API</p>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* User Management */}
          <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">User Roles</h3>
              <button className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 text-green-600 rounded text-xs font-medium">
                <Plus className="w-3 h-3" />
                Add
              </button>
            </div>
            <div className="space-y-3">
              {users.map((user) => (
                <div key={user.id} className="p-3 border border-gray-200 rounded-lg">
                  <p className="font-medium text-gray-900 text-sm">{user.name}</p>
                  <p className="text-xs text-gray-600">{user.email}</p>
                  <span className="inline-block mt-2 px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-semibold">
                    {user.role}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Stats */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-2xl p-6">
            <h3 className="font-semibold text-blue-900 mb-4">System Info</h3>
            <div className="space-y-2 text-sm">
              <div>
                <p className="text-blue-700">Model Version</p>
                <p className="font-semibold text-blue-900">GBM v1.2.3</p>
              </div>
              <div>
                <p className="text-blue-700">Last Sync</p>
                <p className="font-semibold text-blue-900">Jan 15, 2025</p>
              </div>
              <div>
                <p className="text-blue-700">Scoring Calls</p>
                <p className="font-semibold text-blue-900">12,847</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Logs */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Scoring Events Log</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {[...Array(10)].map((_, i) => (
            <div key={i} className="flex items-center justify-between p-3 border border-gray-200 rounded text-sm">
              <div>
                <p className="font-medium text-gray-900">Consumer ID: {1000 + i}</p>
                <p className="text-gray-600">2025-01-15 14:{(30 + i * 5).toString().padStart(2, "0")}</p>
              </div>
              <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">Success</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
