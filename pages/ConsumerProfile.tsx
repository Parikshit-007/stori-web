"use client"
import { useState, useEffect } from "react"
import { useParams } from "next/navigation"
import { mockApi } from "@/lib/mockApi"
import { ArrowLeft, Download, FileText } from "lucide-react"
import Link from "next/link"
import IdentityDemographicsCard from "@/components/IdentityDemographicsCard"
import IncomeCashflowCard from "@/components/IncomeCashflowCard"
import AssetsLiabilitiesCard from "@/components/AssetsLiabilitiesCard"
import BehaviouralSignalsCard from "@/components/BehaviouralSignalsCard"
import FraudIdentityCard from "@/components/FraudIdentityCard"
import TransactionsUtilityCard from "@/components/TransactionsUtilityCard"
import SummaryCard from "@/components/SummaryCard"
import { downloadPDF } from "@/components/PDFReport"

export default function ConsumerProfile() {
  const params = useParams<{ id: string }>()
  const id = params?.id
  const [consumer, setConsumer] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchConsumer = async () => {
      try {
        const data = await mockApi.getConsumerById(id as string)
        setConsumer(data)
      } catch (error) {
        console.error("Error fetching consumer:", error)
      } finally {
        setLoading(false)
      }
    }
    if (id) fetchConsumer()
  }, [id])

  if (loading) return <div className="flex items-center justify-center h-96">Loading...</div>
  if (!consumer) return <div className="flex items-center justify-center h-96">Consumer not found</div>

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case "Low":
        return "bg-green-50 border-green-200 text-green-800"
      case "Medium":
        return "bg-yellow-50 border-yellow-200 text-yellow-800"
      case "High":
        return "bg-red-50 border-red-200 text-red-800"
      default:
        return "bg-gray-50 border-gray-200 text-gray-800"
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <Link href="/consumers" className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4">
            <ArrowLeft className="w-4 h-4" />
            Back to Consumers
          </Link>
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-2xl">
              {consumer.name.charAt(0)}
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{consumer.name}</h1>
              <p className="text-gray-600">
                {consumer.persona} • {consumer.email}
              </p>
            </div>
          </div>
        </div>
        <div className="flex flex-col items-end gap-2">
          {/* PAN Number */}
          <div className="bg-gray-100 border border-gray-300 px-4 py-2 rounded-lg">
            <p className="text-xs font-semibold text-gray-600">PAN NUMBER</p>
            <p className="text-lg font-bold text-gray-900 tracking-wider">{consumer.identity?.pan || "ABCDE1234F"}</p>
          </div>
          {/* Key Metrics Row */}
          <div className="flex gap-3">
            <div className="bg-blue-50 border border-blue-200 px-4 py-2 rounded-lg text-center">
              <p className="text-2xl font-bold text-blue-900">{consumer.summary?.financialHealthScore || 82}</p>
              <p className="text-xs font-semibold text-blue-700">Financial Health Score</p>
            </div>
            <div className={`px-4 py-2 rounded-lg border text-center ${getRiskColor(consumer.riskBucket)}`}>
              <p className="text-2xl font-bold">{consumer.summary?.riskGrade || "B"}</p>
              <p className="text-xs font-semibold">Risk Grade</p>
            </div>
            <div className="bg-green-50 border border-green-200 px-4 py-2 rounded-lg text-center">
              <p className="text-2xl font-bold text-green-900">
                ₹{consumer.summary?.maxLoanAmount >= 10000000 
                  ? `${(consumer.summary.maxLoanAmount / 10000000).toFixed(1)}Cr` 
                  : consumer.summary?.maxLoanAmount >= 100000 
                    ? `${(consumer.summary.maxLoanAmount / 100000).toFixed(1)}L`
                    : `${((consumer.summary?.maxLoanAmount || 1500000) / 1000).toFixed(0)}K`}
              </p>
              <p className="text-xs font-semibold text-green-700">Max Loan Amount</p>
            </div>
            <div className="bg-orange-50 border border-orange-200 px-4 py-2 rounded-lg text-center">
              <p className="text-2xl font-bold text-orange-900">{consumer.summary?.probabilityOfDefault || "3.2"}%</p>
              <p className="text-xs font-semibold text-orange-700">Default Probability</p>
            </div>
          </div>
          <button 
            onClick={() => downloadPDF(consumer)}
            className="mt-2 inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
          >
            <FileText className="w-4 h-4" />
            Download Summary
          </button>
        </div>
      </div>

      {/* Summary Card - Full Width */}
      <SummaryCard consumer={consumer} />

      {/* 1. Identity (Left) + 2. Income (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <IdentityDemographicsCard consumer={consumer} />
        <IncomeCashflowCard consumer={consumer} />
      </div>

      {/* 3. Assets & Liabilities (Left) + 4. Behavioural (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AssetsLiabilitiesCard consumer={consumer} />
        <BehaviouralSignalsCard consumer={consumer} />
      </div>

      {/* 5. Fraud (Left) + 6. Transactions & Utility (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <FraudIdentityCard consumer={consumer} />
        <TransactionsUtilityCard consumer={consumer} />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full px-4 py-3 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition font-medium">
              Re-Score with Current GBM
            </button>
            <button className="w-full px-4 py-3 bg-purple-50 text-purple-600 rounded-lg hover:bg-purple-100 transition font-medium">
              Generate Full Report
            </button>
            <button className="w-full px-4 py-3 bg-gray-50 text-gray-600 rounded-lg hover:bg-gray-100 transition font-medium">
              Request Manual Review
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
