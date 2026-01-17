"use client"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Search, Database, Loader2, CheckCircle, Server, FileText, Shield, TrendingUp } from "lucide-react"
import { mockApi } from "@/lib/mockApi"

const personas = ["All", "Salaried", "Credit-Experienced", "Mass Affluent", "Gig", "NTC", "Credit Invisible"]
const riskCategories = ["All", "Low", "Medium", "High", "Unscored"]

const dataSources = [
  { name: "Bank Statements", icon: FileText, delay: 0 },
  { name: "Identity Verification", icon: Shield, delay: 3000 },
  { name: "Transaction Analysis", icon: TrendingUp, delay: 6000 },
  { name: "Digital Footprint", icon: Server, delay: 9000 },
  { name: "Behavioural Signals", icon: Database, delay: 12000 },
]

export default function ConsumerList() {
  const router = useRouter()
  const [consumers, setConsumers] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedPersona, setSelectedPersona] = useState("All")
  const [selectedRisk, setSelectedRisk] = useState("All")
  const [scoreRange, setScoreRange] = useState<[number, number]>([0, 100])
  const [currentPage, setCurrentPage] = useState(1)
  
  // Extraction state
  const [extracting, setExtracting] = useState(false)
  const [extractingConsumerId, setExtractingConsumerId] = useState<string | null>(null)
  const [extractionProgress, setExtractionProgress] = useState(0)
  const [completedSources, setCompletedSources] = useState<number[]>([])

  const itemsPerPage = 10

  useEffect(() => {
    const fetchConsumers = async () => {
      try {
        const data = await mockApi.getConsumers({
          search: searchQuery,
          persona: selectedPersona !== "All" ? selectedPersona : undefined,
          riskCategory: selectedRisk !== "All" ? selectedRisk : undefined,
          scoreRange,
        })
        setConsumers(data)
        setCurrentPage(1)
      } catch (error) {
        console.error("Error fetching consumers:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchConsumers()
  }, [searchQuery, selectedPersona, selectedRisk, scoreRange])

  const handleExtractData = (consumerId: string) => {
    setExtracting(true)
    setExtractingConsumerId(consumerId)
    setExtractionProgress(0)
    setCompletedSources([])

    // Progress animation
    const progressInterval = setInterval(() => {
      setExtractionProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval)
          return 100
        }
        return prev + (100 / 300) // 30 seconds = 300 intervals of 100ms
      })
    }, 100)

    // Mark sources as completed
    dataSources.forEach((_, index) => {
      setTimeout(() => {
        setCompletedSources(prev => [...prev, index])
      }, (index + 1) * 5000) // Each source completes every 5 seconds
    })

    // Navigate after 30 seconds
    setTimeout(() => {
      clearInterval(progressInterval)
      setExtracting(false)
      setExtractingConsumerId(null)
      router.push(`/consumers/${consumerId}`)
    }, 30000)
  }

  const paginatedConsumers = consumers.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
  const totalPages = Math.ceil(consumers.length / itemsPerPage)

  return (
    <>
      {/* Extraction Preloader Modal */}
      {extracting && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="bg-white rounded-2xl shadow-2xl p-8 max-w-lg w-full mx-4 animate-in fade-in zoom-in duration-300">
            {/* Header */}
            <div className="text-center mb-8">
              <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                <Database className="w-10 h-10 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Extracting Data</h2>
              <p className="text-gray-600">Gathering information from multiple sources...</p>
              <p className="text-sm text-gray-400 mt-1">Please wait while we analyze the profile</p>
            </div>

            {/* Progress Bar */}
            <div className="mb-8">
              <div className="flex justify-between text-sm mb-2">
                <span className="font-medium text-gray-700">Progress</span>
                <span className="font-bold text-blue-600">{Math.round(extractionProgress)}%</span>
              </div>
              <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full transition-all duration-100 ease-out"
                  style={{ width: `${extractionProgress}%` }}
                />
              </div>
            </div>

            {/* Data Sources */}
            <div className="space-y-3">
              {dataSources.map((source, index) => {
                const Icon = source.icon
                const isCompleted = completedSources.includes(index)
                const isActive = !isCompleted && (completedSources.length === index || (index === 0 && completedSources.length === 0))
                
                return (
                  <div 
                    key={index}
                    className={`flex items-center gap-3 p-3 rounded-lg transition-all duration-300 ${
                      isCompleted 
                        ? 'bg-green-50 border border-green-200' 
                        : isActive 
                          ? 'bg-blue-50 border border-blue-200' 
                          : 'bg-gray-50 border border-gray-200'
                    }`}
                  >
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                      isCompleted 
                        ? 'bg-green-500' 
                        : isActive 
                          ? 'bg-blue-500' 
                          : 'bg-gray-300'
                    }`}>
                      {isCompleted ? (
                        <CheckCircle className="w-5 h-5 text-white" />
                      ) : isActive ? (
                        <Loader2 className="w-5 h-5 text-white animate-spin" />
                      ) : (
                        <Icon className="w-5 h-5 text-white" />
                      )}
                    </div>
                    <div className="flex-1">
                      <p className={`font-medium ${
                        isCompleted 
                          ? 'text-green-700' 
                          : isActive 
                            ? 'text-blue-700' 
                            : 'text-gray-500'
                      }`}>
                        {source.name}
                      </p>
                      <p className={`text-xs ${
                        isCompleted 
                          ? 'text-green-600' 
                          : isActive 
                            ? 'text-blue-600' 
                            : 'text-gray-400'
                      }`}>
                        {isCompleted ? 'Completed' : isActive ? 'Extracting...' : 'Pending'}
                      </p>
                    </div>
                    {isActive && (
                      <div className="flex gap-1">
                        <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                        <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                        <span className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                      </div>
                    )}
                  </div>
                )
              })}
            </div>

            {/* Footer */}
            <div className="mt-8 text-center">
              <p className="text-xs text-gray-400">
                This process typically takes 30 seconds
              </p>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Consumers</h1>
          <p className="text-gray-600 mt-1">Search and manage consumer credit profiles</p>
        </div>

        {/* Search & Filters */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-6">
          <div>
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search by name, email, or phone..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Persona</label>
              <select
                value={selectedPersona}
                onChange={(e) => setSelectedPersona(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {personas.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Risk Category</label>
              <select
                value={selectedRisk}
                onChange={(e) => setSelectedRisk(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {riskCategories.map((r) => (
                  <option key={r} value={r}>
                    {r}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Score Range</label>
              <input
                type="text"
                value={`${scoreRange[0]} - ${scoreRange[1]}`}
                readOnly
                className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
            </div>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200 bg-gray-50">
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Name</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Persona</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Contact</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Score</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Risk</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Updated</th>
                  <th className="px-6 py-4 text-left text-sm font-semibold text-gray-900">Action</th>
                </tr>
              </thead>
              <tbody>
                {paginatedConsumers.map((consumer) => (
                  <tr key={consumer.id} className="border-b border-gray-200 hover:bg-gray-50 transition">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{consumer.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{consumer.persona}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{consumer.phone}</td>
                    <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                      {consumer.currentScore || consumer.summary?.financialHealthScore || '—'}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          consumer.riskBucket === "Low"
                            ? "bg-green-100 text-green-800"
                            : consumer.riskBucket === "Medium"
                              ? "bg-yellow-100 text-yellow-800"
                              : consumer.riskBucket === "High"
                                ? "bg-red-100 text-red-800"
                                : "bg-gray-100 text-gray-800"
                        }`}
                      >
                        {consumer.riskBucket}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{consumer.lastUpdated}</td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => handleExtractData(consumer.id)}
                        disabled={extracting}
                        className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg hover:from-blue-600 hover:to-indigo-700 transition font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
                      >
                        <Database className="w-4 h-4" />
                        Extract Data
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
            <div className="text-sm text-gray-600">
              Showing {paginatedConsumers.length > 0 ? (currentPage - 1) * itemsPerPage + 1 : 0} to{" "}
              {Math.min(currentPage * itemsPerPage, consumers.length)} of {consumers.length}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 disabled:opacity-50 hover:bg-gray-50"
              >
                Previous
              </button>
              <div className="flex items-center gap-1">
                {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition ${
                      currentPage === page
                        ? "bg-blue-500 text-white"
                        : "border border-gray-300 text-gray-700 hover:bg-gray-50"
                    }`}
                  >
                    {page}
                  </button>
                ))}
              </div>
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 disabled:opacity-50 hover:bg-gray-50"
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}
