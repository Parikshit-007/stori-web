'use client';

import React from 'react';
import { Building2, TrendingUp, CheckCircle2, PieChart } from 'lucide-react';

interface VendorPaymentsCardProps {
  msme: any;
}

const VendorPaymentsCard: React.FC<VendorPaymentsCardProps> = ({ msme }) => {
  // Mock data for vendor payments - in production, this would come from the API
  const vendorData = {
    paymentConsistency: msme.vendor_payment_consistency || 85,
    verifiedVendors: msme.verified_vendors || 12,
    vendorVerificationRate: msme.vendor_verification_rate || 75,
    totalVendors: msme.total_vendors || 16,
  };

  const expenseBreakdown = msme.expense_breakdown || [
    { category: 'Raw Materials', amount: 450000, percentage: 45 },
    { category: 'Operational Costs', amount: 250000, percentage: 25 },
    { category: 'Employee Salaries', amount: 180000, percentage: 18 },
    { category: 'Marketing & Sales', amount: 70000, percentage: 7 },
    { category: 'Other Expenses', amount: 50000, percentage: 5 },
  ];

  const getConsistencyColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConsistencyBg = (score: number) => {
    if (score >= 80) return 'bg-green-50 border-green-200';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200';
    return 'bg-red-50 border-red-200';
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-blue-600 px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
            <Building2 className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Vendor Payments and Expenses</h3>
            <p className="text-purple-100 text-sm">Vendor relationships & expense management</p>
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {/* Payment Consistency */}
          <div className={`border rounded-lg p-4 ${getConsistencyBg(vendorData.paymentConsistency)}`}>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-1">Vendor Payment Consistency</p>
                <p className={`text-2xl font-bold ${getConsistencyColor(vendorData.paymentConsistency)}`}>
                  {vendorData.paymentConsistency}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  {vendorData.paymentConsistency >= 80 ? 'Excellent' : vendorData.paymentConsistency >= 60 ? 'Good' : 'Needs Improvement'}
                </p>
              </div>
              <TrendingUp className={`w-5 h-5 ${getConsistencyColor(vendorData.paymentConsistency)}`} />
            </div>
          </div>

          {/* Number of Verified Vendors */}
          <div className="border border-blue-200 bg-blue-50 rounded-lg p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-1">Verified Vendors</p>
                <p className="text-2xl font-bold text-blue-600">
                  {vendorData.verifiedVendors}
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  of {vendorData.totalVendors} total vendors
                </p>
              </div>
              <CheckCircle2 className="w-5 h-5 text-blue-600" />
            </div>
          </div>

          {/* Verification Rate */}
          <div className="border border-purple-200 bg-purple-50 rounded-lg p-4">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-1">Verification Rate</p>
                <p className="text-2xl font-bold text-purple-600">
                  {vendorData.vendorVerificationRate}%
                </p>
                <p className="text-xs text-gray-500 mt-1">
                  Vendor verification status
                </p>
              </div>
              <PieChart className="w-5 h-5 text-purple-600" />
            </div>
          </div>
        </div>

        {/* Expense Breakdown */}
        <div>
          <h4 className="text-sm font-semibold text-gray-900 mb-4 flex items-center gap-2">
            <PieChart className="w-4 h-4 text-purple-600" />
            Business Expense Breakdown
          </h4>
          
          <div className="space-y-3">
            {expenseBreakdown.map((expense, index) => (
              <div key={index} className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">{expense.category}</span>
                  <div className="text-right">
                    <span className="text-sm font-semibold text-gray-900">
                      ₹{expense.amount.toLocaleString('en-IN')}
                    </span>
                    <span className="text-xs text-gray-500 ml-2">({expense.percentage}%)</span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-purple-600 to-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${expense.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          {/* Total Expenses */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold text-gray-900">Total Monthly Expenses</span>
              <span className="text-lg font-bold text-purple-600">
                ₹{expenseBreakdown.reduce((sum, exp) => sum + exp.amount, 0).toLocaleString('en-IN')}
              </span>
            </div>
          </div>
        </div>

        {/* Additional Insights */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <h4 className="text-sm font-semibold text-gray-900 mb-3">Payment Insights</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <p className="text-xs text-gray-600">Average Payment Cycle</p>
              <p className="text-lg font-semibold text-blue-600 mt-1">30 days</p>
            </div>
            <div className="bg-green-50 border border-green-200 rounded-lg p-3">
              <p className="text-xs text-gray-600">On-Time Payments</p>
              <p className="text-lg font-semibold text-green-600 mt-1">92%</p>
            </div>
            <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
              <p className="text-xs text-gray-600">Long-term Vendors</p>
              <p className="text-lg font-semibold text-purple-600 mt-1">8 vendors</p>
            </div>
            <div className="bg-orange-50 border border-orange-200 rounded-lg p-3">
              <p className="text-xs text-gray-600">Average Transaction Value</p>
              <p className="text-lg font-semibold text-orange-600 mt-1">₹62,500</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VendorPaymentsCard;


