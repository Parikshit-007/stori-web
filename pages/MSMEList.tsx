"use client"
import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { Search, Building2, Upload, Plus, X, Loader2, Zap, Eye } from "lucide-react"
import { MSMEBusiness, MSMEFeatures, msmeApi, MSMEScoreResponse } from "@/lib/msmeApi"
import { parseCSVToMSMEs, MSME_FEATURE_CATEGORIES, createEmptyMSME } from "@/data/msmeData"
import { getValidScore, saveScore, StoredScore } from "@/lib/scoreStorage"
import ScoreResultModal from "@/components/msme/ScoreResultModal"

const segments = ["All", "micro_new", "micro_established", "small_trading", "small_manufacturing", "small_services", "medium_enterprise"]
const riskCategories = ["All", "Very Low", "Low", "Medium", "High", "Very High"]

export default function MSMEList() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [msmes, setMsmes] = useState<MSMEBusiness[]>([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedSegment, setSelectedSegment] = useState("All")
  const [selectedRisk, setSelectedRisk] = useState("All")
  const [currentPage, setCurrentPage] = useState(1)
  
  // Form state
  const [showAddForm, setShowAddForm] = useState(false)
  const [formData, setFormData] = useState<Partial<MSMEFeatures>>(createEmptyMSME())
  const [businessName, setBusinessName] = useState("")
  const [formSegment, setFormSegment] = useState("micro_established")
  
  // Scoring state
  const [scoringId, setScoringId] = useState<string | null>(null)
  const [scoringLoading, setScoringLoading] = useState(false)
  
  // Modal state
  const [showScoreModal, setShowScoreModal] = useState(false)
  const [currentScoreResult, setCurrentScoreResult] = useState<MSMEScoreResponse | null>(null)
  const [currentBusinessName, setCurrentBusinessName] = useState("")

  const itemsPerPage = 10

  // Load CSV data and stored scores on mount
  useEffect(() => {
    loadCSVData()
  }, [])

  const loadCSVData = async () => {
    setLoading(true)
    try {
      const response = await fetch('/api/msme-data')
      if (response.ok) {
        const data = await response.json()
        
        // Apply stored scores to loaded data
        const msmesWithScores = data.map((msme: MSMEBusiness) => {
          const storedScore = getValidScore(msme.id, msme.features)
          if (storedScore) {
            return {
              ...msme,
              currentScore: storedScore.score,
              riskBucket: storedScore.riskCategory,
              prob_default_90dpd: storedScore.probDefault,
              category_contributions: storedScore.categoryContributions,
              summary: {
                financialHealthScore: storedScore.score,
                riskGrade: storedScore.riskCategory,
                maxLoanAmount: calculateMaxLoan(storedScore.score, msme.features.monthly_gtv || 0),
                probabilityOfDefault: storedScore.probDefault * 100,
                recommendation: storedScore.recommendation
              },
              scoreResponse: storedScore.scoreResponse
            }
          }
          return msme
        })
        
        setMsmes(msmesWithScores)
      }
    } catch (error) {
      console.log("No pre-loaded data, starting with empty list")
    } finally {
      setLoading(false)
    }
  }

  // Filter MSMEs - only filter by score if they have a score
  const filteredMSMEs = msmes.filter(m => {
    if (searchQuery) {
      const q = searchQuery.toLowerCase()
      if (!m.businessName.toLowerCase().includes(q) &&
          !m.email?.toLowerCase().includes(q) &&
          !m.phone?.includes(q) &&
          !m.gstin?.toLowerCase().includes(q)) {
        return false
      }
    }
    if (selectedSegment !== "All" && m.businessSegment !== selectedSegment) return false
    if (selectedRisk !== "All") {
      // Only filter by risk if MSME has been scored
      if (!m.riskBucket) return false
      if (m.riskBucket !== selectedRisk) return false
    }
    return true
  })

  const paginatedMSMEs = filteredMSMEs.slice((currentPage - 1) * itemsPerPage, currentPage * itemsPerPage)
  const totalPages = Math.ceil(filteredMSMEs.length / itemsPerPage)

  // Handle CSV upload
  const handleCSVUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setLoading(true)
    try {
      const text = await file.text()
      const parsedMSMEs = parseCSVToMSMEs(text)
      setMsmes(prev => [...prev, ...parsedMSMEs])
      alert(`Successfully loaded ${parsedMSMEs.length} MSME businesses!`)
    } catch (error) {
      console.error("Error parsing CSV:", error)
      alert("Error parsing CSV file. Please check the format.")
    } finally {
      setLoading(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  // Handle form input change
  const handleFormChange = (key: string, value: any) => {
    setFormData(prev => ({ ...prev, [key]: value }))
  }

  // Add new MSME from form
  const handleAddMSME = () => {
    if (!businessName.trim()) {
      alert("Please enter a business name")
      return
    }

    const newMSME: MSMEBusiness = {
      id: `msme-manual-${Date.now()}`,
      businessName: businessName,
      businessSegment: formSegment,
      industry: formData.industry_code || 'trading',
      features: formData as MSMEFeatures,
      lastUpdated: new Date().toISOString().split('T')[0],
      // NO score - must generate
    }

    setMsmes(prev => [newMSME, ...prev])
    setShowAddForm(false)
    setFormData(createEmptyMSME())
    setBusinessName("")
    setFormSegment("micro_established")
  }

  // Generate score for MSME
  const handleGenerateScore = async (msme: MSMEBusiness) => {
    setScoringId(msme.id)
    setScoringLoading(true)
    setCurrentBusinessName(msme.businessName)
    setCurrentScoreResult(null)
    setShowScoreModal(true)
    
    try {
      const result = await msmeApi.scoreBusiness({
        features: msme.features,
        business_segment: msme.businessSegment,
        alpha: 0.7,
        include_explanation: true
      })

      // Save score to localStorage
      saveScore(msme.id, result, msme.features)
      
      setCurrentScoreResult(result)

      // Update the MSME with the score
      setMsmes(prev => prev.map(m => {
        if (m.id === msme.id) {
          return {
            ...m,
            currentScore: result.score,
            riskBucket: result.risk_category,
            prob_default_90dpd: result.prob_default_90dpd,
            summary: {
              financialHealthScore: result.score,
              riskGrade: result.risk_category,
              maxLoanAmount: calculateMaxLoan(result.score, msme.features.monthly_gtv || 0),
              probabilityOfDefault: result.prob_default_90dpd * 100,
              recommendation: result.recommended_decision
            },
            category_contributions: result.category_contributions,
            scoreResponse: result
          }
        }
        return m
      }))

    } catch (error) {
      console.error("Error generating score:", error)
      
      // Fallback: Generate score locally if API fails
      const localScore = generateLocalScore(msme.features)
      const localResult: MSMEScoreResponse = {
        score: localScore.score,
        prob_default_90dpd: localScore.probDefault,
        risk_category: localScore.riskBucket,
        recommended_decision: localScore.recommendation,
        model_version: 'local_fallback_v1',
        business_segment: msme.businessSegment,
        component_scores: { local_calculation: 1.0 },
        category_contributions: {
          A_business_identity: 0.10,
          B_revenue_performance: 0.20,
          C_cashflow_banking: 0.25,
          D_credit_repayment: 0.22,
          E_compliance_taxation: 0.12,
          F_fraud_verification: 0.07,
          G_external_signals: 0.04
        },
        timestamp: new Date().toISOString()
      }
      
      // Save local score too
      saveScore(msme.id, localResult, msme.features)
      
      setCurrentScoreResult(localResult)
      
      setMsmes(prev => prev.map(m => {
        if (m.id === msme.id) {
          return {
            ...m,
            currentScore: localScore.score,
            riskBucket: localScore.riskBucket,
            summary: {
              financialHealthScore: localScore.score,
              riskGrade: localScore.riskGrade,
              maxLoanAmount: calculateMaxLoan(localScore.score, msme.features.monthly_gtv || 0),
              probabilityOfDefault: localScore.probDefault * 100,
              recommendation: localScore.recommendation
            },
            category_contributions: localResult.category_contributions
          }
        }
        return m
      }))
    } finally {
      setScoringId(null)
      setScoringLoading(false)
    }
  }

  // View existing score
  const handleViewScore = (msme: MSMEBusiness) => {
    if (msme.scoreResponse) {
      setCurrentScoreResult(msme.scoreResponse)
      setCurrentBusinessName(msme.businessName)
      setShowScoreModal(true)
    } else {
      // Try to get from storage
      const stored = getValidScore(msme.id, msme.features)
      if (stored) {
        setCurrentScoreResult(stored.scoreResponse)
        setCurrentBusinessName(msme.businessName)
        setShowScoreModal(true)
      }
    }
  }

  // Local scoring fallback
  const generateLocalScore = (features: MSMEFeatures) => {
    let score = 550

    if (features.business_age_years && features.business_age_years > 3) score += 20
    if (features.gstin_verified) score += 15
    if (features.pan_verified) score += 15
    if (features.weekly_gtv && features.weekly_gtv > 100000) score += 30
    if (features.profit_margin && features.profit_margin > 0.1) score += 20
    if (features.revenue_growth_rate_mom && features.revenue_growth_rate_mom > 0) score += 25
    if (features.inventory_turnover_ratio && features.inventory_turnover_ratio > 2) score += 25
    if (features.weekly_inflow_outflow_ratio && features.weekly_inflow_outflow_ratio > 1.2) score += 40
    if (features.cash_buffer_days && features.cash_buffer_days > 30) score += 30
    if (features.negative_balance_days === 0) score += 30
    if (features.overdraft_repayment_ontime_ratio && features.overdraft_repayment_ontime_ratio > 0.9) score += 40
    if (features.bounced_cheques_count === 0) score += 30
    if (features.previous_defaults_count === 0) score += 30
    if (features.gst_filing_regularity && features.gst_filing_regularity > 0.9) score += 25
    if (features.itr_filed) score += 25

    if (features.previous_defaults_count && features.previous_defaults_count > 0) score -= 50
    if (features.bounced_cheques_count && features.bounced_cheques_count > 3) score -= 30
    if (features.negative_balance_days && features.negative_balance_days > 10) score -= 20
    if (features.legal_proceedings_flag) score -= 40

    score = Math.max(300, Math.min(900, score))
    const probDefault = Math.max(0.01, Math.min(0.5, (900 - score) / 1200))

    return {
      score,
      probDefault,
      riskBucket: score >= 750 ? 'Very Low' : score >= 650 ? 'Low' : score >= 550 ? 'Medium' : score >= 450 ? 'High' : 'Very High',
      riskGrade: score >= 750 ? 'A' : score >= 650 ? 'B' : score >= 550 ? 'C' : score >= 450 ? 'D' : 'E',
      recommendation: score >= 750 ? 'Fast Track Approval' : score >= 650 ? 'Approve' : score >= 550 ? 'Conditional Approval' : score >= 450 ? 'Manual Review' : 'Decline'
    }
  }

  const calculateMaxLoan = (score: number, monthlyGTV: number) => {
    const multiplier = score >= 750 ? 3 : score >= 650 ? 2.5 : score >= 550 ? 2 : score >= 450 ? 1.5 : 1
    return Math.round(monthlyGTV * multiplier)
  }

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "Very Low":
      case "Low":
        return "bg-green-100 text-green-700"
      case "Medium":
        return "bg-yellow-100 text-yellow-700"
      case "High":
      case "Very High":
        return "bg-red-100 text-red-700"
      default:
        return "bg-gray-100 text-gray-700"
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 750) return "text-green-600"
    if (score >= 650) return "text-green-600"
    if (score >= 550) return "text-yellow-600"
    if (score >= 450) return "text-orange-600"
    return "text-red-600"
  }

  // Count only scored MSMEs
  const scoredCount = msmes.filter(m => m.currentScore !== undefined).length
  const lowRiskCount = msmes.filter(m => m.riskBucket === 'Low' || m.riskBucket === 'Very Low').length
  const highRiskCount = msmes.filter(m => m.riskBucket === 'High' || m.riskBucket === 'Very High').length

  return (
    <div className="space-y-6">
      {/* Score Result Modal */}
      <ScoreResultModal
        isOpen={showScoreModal}
        onClose={() => setShowScoreModal(false)}
        result={currentScoreResult}
        businessName={currentBusinessName}
        isLoading={scoringLoading}
      />

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">MSME Businesses</h1>
          <p className="text-gray-600 mt-1">Manage and score MSME credit profiles</p>
        </div>
        <div className="flex gap-3">
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleCSVUpload}
            accept=".csv"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            className="inline-flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition font-medium"
          >
            <Upload className="w-4 h-4" />
            Upload CSV
          </button>
          <button
            onClick={() => setShowAddForm(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
          >
            <Plus className="w-4 h-4" />
            Add MSME
          </button>
        </div>
      </div>

      {/* Search & Filters */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 space-y-6">
        <div>
          <div className="relative">
            <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search by business name, GSTIN, email, or phone..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Business Segment</label>
            <select
              value={selectedSegment}
              onChange={(e) => setSelectedSegment(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {segments.map((seg) => (
                <option key={seg} value={seg}>
                  {seg === "All" ? "All Segments" : seg.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Risk Category (Scored Only)</label>
            <select
              value={selectedRisk}
              onChange={(e) => setSelectedRisk(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {riskCategories.map((risk) => (
                <option key={risk} value={risk}>
                  {risk === "All" ? "All Risks" : risk}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Total MSMEs</p>
          <p className="text-2xl font-bold text-gray-900">{msmes.length}</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Scored</p>
          <p className="text-2xl font-bold text-blue-600">{scoredCount}</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <p className="text-sm text-gray-600">Low Risk</p>
          <p className="text-2xl font-bold text-green-600">{lowRiskCount}</p>
        </div>
        <div className="bg-white rounded-xl p-4 border border-gray-200">
          <p className="text-sm text-gray-600">High Risk</p>
          <p className="text-2xl font-bold text-red-600">{highRiskCount}</p>
        </div>
      </div>

      {/* MSME Table */}
      {loading ? (
        <div className="flex items-center justify-center h-96">
          <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          <span className="ml-2 text-gray-500">Loading MSMEs...</span>
        </div>
      ) : (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Business
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Segment
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Industry
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Score
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Risk
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {paginatedMSMEs.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                      {msmes.length === 0 ? (
                        <div className="space-y-2">
                          <Building2 className="w-12 h-12 mx-auto text-gray-300" />
                          <p>No MSMEs added yet</p>
                          <p className="text-sm">Upload a CSV file or add MSMEs manually</p>
                        </div>
                      ) : (
                        "No MSMEs match your filters"
                      )}
                    </td>
                  </tr>
                ) : (
                  paginatedMSMEs.map((msme) => (
                    <tr key={msme.id} className="hover:bg-gray-50 transition">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-semibold text-gray-900">{msme.businessName}</p>
                          <p className="text-sm text-gray-500">ID: {msme.id}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                          {msme.businessSegment?.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase())}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <span className="text-sm text-gray-600 capitalize">{msme.industry}</span>
                      </td>
                      <td className="px-6 py-4">
                        {msme.currentScore !== undefined ? (
                          <span className={`text-lg font-bold ${getScoreColor(msme.currentScore)}`}>
                            {msme.currentScore}
                          </span>
                        ) : (
                          <span className="text-gray-400 text-sm italic">Not scored</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        {msme.riskBucket ? (
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${getRiskColor(msme.riskBucket)}`}>
                            {msme.riskBucket}
                          </span>
                        ) : (
                          <span className="text-gray-400 text-sm">-</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleGenerateScore(msme)}
                            disabled={scoringLoading && scoringId === msme.id}
                            className="px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-medium disabled:opacity-50 flex items-center gap-1"
                          >
                            {scoringLoading && scoringId === msme.id ? (
                              <Loader2 className="w-4 h-4 animate-spin" />
                            ) : (
                              <Zap className="w-4 h-4" />
                            )}
                            {msme.currentScore !== undefined ? 'Re-Score' : 'Score'}
                          </button>
                          {msme.currentScore !== undefined && (
                            <button
                              onClick={() => handleViewScore(msme)}
                              className="px-3 py-1.5 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition text-sm font-medium flex items-center gap-1"
                            >
                              <Eye className="w-4 h-4" />
                              View
                            </button>
                          )}
                          <button
                            onClick={() => router.push(`/msmes/${msme.id}`)}
                            className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-medium"
                          >
                            Details
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
              <div className="text-sm text-gray-600">
                Showing {(currentPage - 1) * itemsPerPage + 1} to {Math.min(currentPage * itemsPerPage, filteredMSMEs.length)} of {filteredMSMEs.length} businesses
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Previous
                </button>
                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Add MSME Modal */}
      {showAddForm && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
            <div className="p-6 border-b border-gray-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900">Add New MSME</h2>
              <button onClick={() => setShowAddForm(false)} className="p-2 hover:bg-gray-100 rounded-lg">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 overflow-y-auto flex-1">
              {/* Basic Info */}
              <div className="mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Business Name *</label>
                    <input
                      type="text"
                      value={businessName}
                      onChange={(e) => setBusinessName(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter business name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Business Segment</label>
                    <select
                      value={formSegment}
                      onChange={(e) => setFormSegment(e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      {segments.filter(s => s !== 'All').map(seg => (
                        <option key={seg} value={seg}>
                          {seg.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase())}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>

              {/* Feature Categories */}
              {Object.entries(MSME_FEATURE_CATEGORIES).map(([catKey, category]) => (
                <div key={catKey} className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">{category.label}</h3>
                  <div className="grid grid-cols-3 gap-4">
                    {category.fields.map(field => (
                      <div key={field.key}>
                        <label className="block text-sm font-medium text-gray-700 mb-1">{field.label}</label>
                        {field.type === 'select' ? (
                          <select
                            value={(formData as any)[field.key] || ''}
                            onChange={(e) => handleFormChange(field.key, e.target.value)}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                          >
                            {field.options?.map(opt => (
                              <option key={opt} value={opt}>{opt.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</option>
                            ))}
                          </select>
                        ) : field.type === 'binary' ? (
                          <select
                            value={(formData as any)[field.key] || 0}
                            onChange={(e) => handleFormChange(field.key, parseInt(e.target.value))}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                          >
                            <option value={0}>No</option>
                            <option value={1}>Yes</option>
                          </select>
                        ) : field.type === 'percent' ? (
                          <input
                            type="number"
                            value={((formData as any)[field.key] || 0) * 100}
                            onChange={(e) => handleFormChange(field.key, parseFloat(e.target.value) / 100)}
                            min={field.min || 0}
                            max={field.max || 100}
                            step="1"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                            placeholder="%"
                          />
                        ) : field.type === 'currency' ? (
                          <input
                            type="number"
                            value={(formData as any)[field.key] || ''}
                            onChange={(e) => handleFormChange(field.key, parseFloat(e.target.value) || 0)}
                            min={0}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                            placeholder="₹"
                          />
                        ) : (
                          <input
                            type="number"
                            value={(formData as any)[field.key] || ''}
                            onChange={(e) => handleFormChange(field.key, parseFloat(e.target.value) || 0)}
                            min={field.min}
                            max={field.max}
                            step={field.max && field.max <= 5 ? "0.1" : "1"}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                          />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={() => setShowAddForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleAddMSME}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
              >
                Add MSME
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
