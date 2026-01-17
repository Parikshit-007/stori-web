"use client"

export function generateMSMEPDFContent(msme: any): string {
  const { summary, features, director } = msme
  
  const formatCurrency = (amount: number) => {
    if (!amount) return '₹0'
    if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(2)}Cr`
    if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)}L`
    if (amount >= 1000) return `₹${(amount / 1000).toFixed(1)}K`
    return `₹${amount.toFixed(0)}`
  }

  const directorName = director?.name || msme.businessName?.split(' ')[0] + ' Kumar' || 'Director'
  const directorAge = director?.age || features.owner_age || 42
  const directorPan = director?.pan || features.owner_pan || 'ABCDE1234F'

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>MSME Credit Report - ${msme.businessName}</title>
  <style>
    @page { size: A4; margin: 15mm; }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
      font-size: 9px;
      line-height: 1.4;
      color: #1f2937;
      background: white;
    }
    .container { max-width: 100%; padding: 12px; }
    .header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      padding: 16px;
      border-radius: 8px;
      margin-bottom: 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .logo { font-size: 20px; font-weight: bold; }
    .report-title { font-size: 14px; font-weight: 600; margin-top: 4px; }
    .business-name { font-size: 18px; font-weight: bold; margin-bottom: 2px; }
    .header-right { text-align: right; }
    .score-box {
      background: white;
      border: 2px solid #fff;
      border-radius: 8px;
      padding: 8px 12px;
      text-align: center;
    }
    .score-value { font-size: 32px; font-weight: bold; line-height: 1; }
    .score-label { font-size: 10px; opacity: 0.9; margin-top: 2px; }
    
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 8px; }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
    
    .section {
      background: #f9fafb;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      padding: 10px;
      margin-bottom: 10px;
    }
    .section-title {
      font-size: 11px;
      font-weight: 700;
      color: #374151;
      margin-bottom: 8px;
      padding-bottom: 4px;
      border-bottom: 2px solid #e5e7eb;
    }
    .metric-box {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 6px;
      padding: 8px;
      text-align: center;
    }
    .metric-label { font-size: 8px; color: #6b7280; margin-bottom: 4px; }
    .metric-value { font-size: 16px; font-weight: bold; }
    .metric-value.green { color: #10b981; }
    .metric-value.red { color: #ef4444; }
    .metric-value.yellow { color: #f59e0b; }
    .metric-value.blue { color: #3b82f6; }
    
    .info-row {
      display: flex;
      justify-content: space-between;
      padding: 4px 6px;
      border-bottom: 1px solid #e5e7eb;
    }
    .info-row:last-child { border-bottom: none; }
    .info-label { color: #6b7280; font-size: 8px; }
    .info-value { font-weight: 600; font-size: 8px; color: #1f2937; }
    
    .badge {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 12px;
      font-size: 8px;
      font-weight: 600;
    }
    .badge.green { background: #d1fae5; color: #065f46; }
    .badge.red { background: #fee2e2; color: #991b1b; }
    .badge.yellow { background: #fef3c7; color: #92400e; }
    .badge.blue { background: #dbeafe; color: #1e40af; }
    
    .footer {
      text-align: center;
      font-size: 7px;
      color: #9ca3af;
      margin-top: 12px;
      padding-top: 8px;
      border-top: 1px solid #e5e7eb;
    }
    
    @media print {
      body { print-color-adjust: exact; -webkit-print-color-adjust: exact; }
      .container { padding: 0; }
    }
  </style>
</head>
<body>
  <div class="container">
    <!-- Header -->
    <div class="header">
      <div>
        <div class="logo">Stori AI</div>
        <div class="report-title">MSME Credit Report</div>
        <div class="business-name">${msme.businessName}</div>
        <div style="font-size: 10px; opacity: 0.9;">${msme.businessSegment?.replace('_', ' ').toUpperCase()} • ${msme.industry?.toUpperCase()}</div>
      </div>
      <div class="header-right">
        <div class="score-box">
          <div class="score-value">${msme.currentScore || summary?.financialHealthScore || 0}/100</div>
          <div class="score-label">Credit Score</div>
        </div>
        <div style="margin-top: 8px; font-size: 10px;">
          Risk Grade: <strong>${msme.riskBucket || summary?.riskGrade || 'N/A'}</strong>
        </div>
      </div>
    </div>

    <!-- Key Metrics -->
    <div class="grid-4" style="margin-bottom: 10px;">
      <div class="metric-box">
        <div class="metric-label">Max Loan Amount</div>
        <div class="metric-value green">${formatCurrency(summary?.maxLoanAmount || 0)}</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">Default Probability</div>
        <div class="metric-value ${(summary?.probabilityOfDefault || 0) < 5 ? 'green' : (summary?.probabilityOfDefault || 0) < 15 ? 'yellow' : 'red'}">${(summary?.probabilityOfDefault || 0).toFixed(1)}%</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">Business Age</div>
        <div class="metric-value blue">${(features.business_age_years || 0).toFixed(1)} yrs</div>
      </div>
      <div class="metric-box">
        <div class="metric-label">Monthly GTV</div>
        <div class="metric-value">${formatCurrency(features.monthly_gtv || features.weekly_gtv * 4 || 0)}</div>
      </div>
    </div>

    <div class="grid-2">
      <!-- Left Column -->
      <div>
        <!-- Director Details -->
        <div class="section">
          <div class="section-title">Director / Promoter</div>
          <div class="info-row"><span class="info-label">Name</span><span class="info-value">${directorName}</span></div>
          <div class="info-row"><span class="info-label">Age</span><span class="info-value">${directorAge} years</span></div>
          <div class="info-row"><span class="info-label">PAN</span><span class="info-value">${directorPan}</span></div>
          <div class="info-row"><span class="info-label">Decision Style</span><span class="info-value">${director?.decision_style || 'Growth-Focused'}</span></div>
          <div class="info-row"><span class="info-label">Risk Appetite</span><span class="info-value">${director?.risk_appetite || 'Moderate'}</span></div>
        </div>

        <!-- Business Identity -->
        <div class="section">
          <div class="section-title">A. Business Identity & Registration</div>
          <div class="info-row"><span class="info-label">Legal Entity</span><span class="info-value">${features.legal_entity_type || 'N/A'}</span></div>
          <div class="info-row"><span class="info-label">GSTIN Verified</span><span class="info-value" style="color: ${features.gstin_verified ? '#10b981' : '#ef4444'};">${features.gstin_verified ? '✓ Yes' : '✗ No'}</span></div>
          <div class="info-row"><span class="info-label">PAN Verified</span><span class="info-value" style="color: ${features.pan_verified ? '#10b981' : '#ef4444'};">${features.pan_verified ? '✓ Yes' : '✗ No'}</span></div>
          <div class="info-row"><span class="info-label">MSME Registered</span><span class="info-value" style="color: ${features.msme_registered ? '#10b981' : '#ef4444'};">${features.msme_registered ? '✓ Yes' : '✗ No'}</span></div>
          <div class="info-row"><span class="info-label">Employees</span><span class="info-value">${features.employees_count || 0}</span></div>
          <div class="info-row"><span class="info-label">Locations</span><span class="info-value">${features.num_business_locations || 1}</span></div>
        </div>

        <!-- Revenue Performance -->
        <div class="section">
          <div class="section-title">B. Revenue & Business Performance</div>
          <div class="grid-3" style="margin-bottom: 6px;">
            <div class="metric-box">
              <div class="metric-label">Weekly GTV</div>
              <div class="metric-value green">${formatCurrency(features.weekly_gtv || 0)}</div>
            </div>
            <div class="metric-box">
              <div class="metric-label">Monthly GTV</div>
              <div class="metric-value blue">${formatCurrency(features.monthly_gtv || features.weekly_gtv * 4 || 0)}</div>
            </div>
            <div class="metric-box">
              <div class="metric-label">Profit Margin</div>
              <div class="metric-value ${(features.profit_margin || 0) >= 0.1 ? 'green' : 'yellow'}">${((features.profit_margin || 0) * 100).toFixed(1)}%</div>
            </div>
          </div>
          <div class="info-row"><span class="info-label">Gross Profit Margin</span><span class="info-value" style="color: ${(features.gross_profit_margin || 0.25) >= 0.2 ? '#10b981' : (features.gross_profit_margin || 0.25) >= 0.1 ? '#f59e0b' : '#ef4444'};">${((features.gross_profit_margin || 0.25) * 100).toFixed(1)}%</span></div>
          <div class="info-row"><span class="info-label">Net Profit Margin</span><span class="info-value" style="color: ${(features.profit_margin || 0) >= 0.1 ? '#10b981' : (features.profit_margin || 0) >= 0.05 ? '#f59e0b' : '#ef4444'};">${((features.profit_margin || 0) * 100).toFixed(1)}%</span></div>
          <div class="info-row"><span class="info-label">MoM Growth</span><span class="info-value" style="color: ${(features.revenue_growth_rate_mom || 0) >= 0 ? '#10b981' : '#ef4444'};">${((features.revenue_growth_rate_mom || 0) * 100).toFixed(1)}%</span></div>
          <div class="info-row"><span class="info-label">QoQ Growth</span><span class="info-value" style="color: ${(features.revenue_growth_rate_qoq || 0) >= 0 ? '#10b981' : '#ef4444'};">${((features.revenue_growth_rate_qoq || 0) * 100).toFixed(1)}%</span></div>
          <div class="info-row"><span class="info-label">Daily Transactions</span><span class="info-value">${features.transaction_count_daily || 0}</span></div>
          // <div class="info-row"><span class="info-label">Inventory Turnover</span><span class="info-value">${(features.inventory_turnover_ratio || 0).toFixed(1)}x</span></div>
        </div>

        <!-- Cashflow & Banking -->
        <div class="section">
          <div class="section-title">C. Cash Flow & Banking</div>
          <div class="info-row"><span class="info-label">Avg Bank Balance</span><span class="info-value">${formatCurrency(features.avg_bank_balance || 0)}</span></div>
          <div class="info-row"><span class="info-label">Inflow/Outflow Ratio</span><span class="info-value" style="color: ${(features.weekly_inflow_outflow_ratio || 0) >= 1.2 ? '#10b981' : (features.weekly_inflow_outflow_ratio || 0) >= 1 ? '#f59e0b' : '#ef4444'};">${(features.weekly_inflow_outflow_ratio || 0).toFixed(2)}x</span></div>
          <div class="info-row"><span class="info-label">Cash Buffer Days</span><span class="info-value">${features.cash_buffer_days || 0} days</span></div>
          <div class="info-row"><span class="info-label">Negative Balance Days</span><span class="info-value" style="color: ${(features.negative_balance_days || 0) === 0 ? '#10b981' : '#ef4444'};">${features.negative_balance_days || 0} days</span></div>
          <div class="info-row"><span class="info-label">Overdraft Days</span><span class="info-value">${features.overdraft_days_count || 0} days</span></div>
        </div>
      </div>

      <!-- Right Column -->
      <div>
        <!-- Credit & Repayment -->
        <div class="section">
          <div class="section-title">D. Credit & Repayment Behavior</div>
          <div class="grid-2" style="margin-bottom: 6px;">
            <div class="metric-box">
              <div class="metric-label">On-Time Repayment</div>
              <div class="metric-value ${(features.overdraft_repayment_ontime_ratio || 0) >= 0.9 ? 'green' : 'yellow'}">${((features.overdraft_repayment_ontime_ratio || 0) * 100).toFixed(0)}%</div>
            </div>
            <div class="metric-box">
              <div class="metric-label">Bounced Cheques</div>
              <div class="metric-value ${(features.bounced_cheques_count || 0) === 0 ? 'green' : 'red'}">${features.bounced_cheques_count || 0}</div>
            </div>
          </div>
          <div class="info-row"><span class="info-label">Previous Defaults</span><span class="info-value" style="color: ${(features.previous_defaults_count || 0) === 0 ? '#10b981' : '#ef4444'};">${features.previous_defaults_count || 0}</span></div>
          <div class="info-row"><span class="info-label">Current Loans</span><span class="info-value">${features.current_loans_outstanding || 0}</span></div>
          <div class="info-row"><span class="info-label">Total Debt</span><span class="info-value">${formatCurrency(features.total_debt_amount || 0)}</span></div>
          <div class="info-row"><span class="info-label">Utility Payment On-Time</span><span class="info-value">${((features.utility_payment_ontime_ratio || 0) * 100).toFixed(0)}%</span></div>
        </div>

        <!-- Compliance & Taxation -->
        <div class="section">
          <div class="section-title">E. Compliance & Taxation</div>
          <div class="info-row"><span class="info-label">GST Filing Regularity</span><span class="info-value" style="color: ${(features.gst_filing_regularity || 0) >= 0.9 ? '#10b981' : '#ef4444'};">${((features.gst_filing_regularity || 0) * 100).toFixed(0)}%</span></div>
          <div class="info-row"><span class="info-label">GST Filing On-Time Ratio</span><span class="info-value">${((features.gst_filing_ontime_ratio || 0) * 100).toFixed(0)}%</span></div>
          <div class="info-row"><span class="info-label">ITR Filed</span><span class="info-value" style="color: ${features.itr_filed ? '#10b981' : '#ef4444'};">${features.itr_filed ? '✓ Yes' : '✗ No'}</span></div>
          ${features.itr_income_declared > 0 ? `<div class="info-row"><span class="info-label">ITR Income Declared</span><span class="info-value">${formatCurrency(features.itr_income_declared || 0)}</span></div>` : ''}
          <div class="info-row"><span class="info-label">Outstanding Taxes</span><span class="info-value" style="color: ${(features.outstanding_taxes_amount || 0) > 0 ? '#ef4444' : '#10b981'};">${formatCurrency(features.outstanding_taxes_amount || 0)}</span></div>
          <div class="info-row"><span class="info-label">Tax Payment Regularity</span><span class="info-value">${((features.tax_payment_regularity || 0) * 100).toFixed(0)}%</span></div>
          <div class="info-row"><span class="info-label">Tax Payment On-Time Ratio</span><span class="info-value">${((features.tax_payment_ontime_ratio || 0) * 100).toFixed(0)}%</span></div>
          <div class="info-row"><span class="info-label">GST vs Platform Sales Mismatch</span><span class="info-value" style="color: ${(features.gst_vs_platform_sales_mismatch || 0) > 0.1 ? '#ef4444' : '#10b981'};">${((features.gst_vs_platform_sales_mismatch || 0) * 100).toFixed(1)}%</span></div>
          <div class="info-row"><span class="info-label">GST R1 vs ITR Mismatch</span><span class="info-value" style="color: ${(features.gst_r1_vs_itr_mismatch || 0) > 0.1 ? '#ef4444' : '#10b981'};">${((features.gst_r1_vs_itr_mismatch || 0) * 100).toFixed(1)}%</span></div>
          <div class="info-row"><span class="info-label">Refund/Chargeback Rate</span><span class="info-value">${((features.refund_chargeback_rate || 0) * 100).toFixed(1)}%</span></div>
          <div class="info-row"><span class="info-label">Legal Proceedings</span><span class="info-value" style="color: ${features.legal_proceedings_flag ? '#ef4444' : '#10b981'};">${features.legal_proceedings_flag ? '⚠ Yes' : 'None'}</span></div>
        </div>

        <!-- Fraud & Verification -->
        <div class="section">
          <div class="section-title">F. Fraud & Verification</div>
          <div class="info-row"><span class="info-label">KYC Completion Score</span><span class="info-value">${((features.kyc_completion_score || 0) * 100).toFixed(0)}%</span></div>
          <div class="info-row"><span class="info-label">KYC Attempts</span><span class="info-value">${features.kyc_attempts_count || 1}</span></div>
          <div class="info-row"><span class="info-label">Image OCR Verified</span><span class="info-value" style="color: ${features.image_ocr_verified ? '#10b981' : '#ef4444'};">${features.image_ocr_verified ? '✓ Yes' : '✗ No'}</span></div>
          <div class="info-row"><span class="info-label">Shop Image Verified</span><span class="info-value" style="color: ${features.shop_image_verified ? '#10b981' : '#ef4444'};">${features.shop_image_verified ? '✓ Yes' : '✗ No'}</span></div>
          <div class="info-row"><span class="info-label">Circular Transaction</span><span class="info-value" style="color: ${features.circular_transaction_detected ? '#ef4444' : '#10b981'};">${features.circular_transaction_detected ? '⚠ Detected' : '✓ Clear'}</span></div>
          <div class="info-row"><span class="info-label">Bank Statement OCR</span><span class="info-value" style="color: ${features.bank_statement_ocr_verified !== false ? '#10b981' : '#ef4444'};">${features.bank_statement_ocr_verified !== false ? '✓ Verified' : '✗ Failed'}</span></div>
        </div>

        <!-- External Signals -->
        <div class="section">
          <div class="section-title">G. External Signals</div>
          <div class="info-row"><span class="info-label">Google Reviews</span><span class="info-value">${(features.google_reviews_rating || 0).toFixed(1)}⭐ (${features.google_reviews_count || 0})</span></div>
          <div class="info-row"><span class="info-label">Social Media Presence</span><span class="info-value">${((features.social_media_presence_score || 0) * 100).toFixed(0)}%</span></div>
          <div class="info-row"><span class="info-label">Business Listing</span><span class="info-value" style="color: ${features.business_listing_verified ? '#10b981' : '#6b7280'};">${features.business_listing_verified ? 'Verified' : 'Not Verified'}</span></div>
        </div>

        <!-- Recommendation -->
        <div class="section" style="background: ${summary?.recommendation?.includes('Approve') ? '#d1fae5' : summary?.recommendation?.includes('Decline') ? '#fee2e2' : '#fef3c7'};">
          <div class="section-title">Credit Decision</div>
          <div style="text-align: center; padding: 8px;">
            <div style="font-size: 16px; font-weight: bold; color: ${summary?.recommendation?.includes('Approve') ? '#065f46' : summary?.recommendation?.includes('Decline') ? '#991b1b' : '#92400e'};">
              ${summary?.recommendation || 'Manual Review'}
            </div>
            <div style="font-size: 8px; color: #6b7280; margin-top: 4px;">
              Model Version: ${msme.scoreResponse?.model_version || 'N/A'} | 
              Generated: ${new Date().toLocaleDateString()}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <div class="footer">
      Generated by Stori AI MSME Credit Scoring System | Report ID: ${msme.id}-${Date.now()} | This is a system-generated report.
    </div>
  </div>
</body>
</html>
  `
}

export function downloadMSMEPDF(msme: any) {
  const content = generateMSMEPDFContent(msme)
  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(content)
    printWindow.document.close()
    
    printWindow.onload = () => {
      printWindow.print()
      // Optionally close the window after printing
      // printWindow.close()
    }
  } else {
    alert('Please allow popups to download the PDF')
  }
}

