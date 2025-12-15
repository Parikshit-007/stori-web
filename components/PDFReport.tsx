"use client"

export function generatePDFContent(consumer: any): string {
  const { summary, identity, income, assets, insurance, liabilities, saturation, behaviour, fraud, transactions } = consumer

  const getRiskGrade = (score: number) => {
    if (score >= 85) return 'A'
    if (score >= 75) return 'B'
    if (score >= 56) return 'C'
    if (score >= 40) return 'D'
    return 'E'
  }

  const formatAmount = (amt: number) => {
    if (amt >= 10000000) return `₹${(amt / 10000000).toFixed(1)}Cr`
    if (amt >= 100000) return `₹${(amt / 100000).toFixed(1)}L`
    if (amt >= 1000) return `₹${(amt / 1000).toFixed(0)}K`
    return `₹${amt}`
  }

  return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Credit Report - ${consumer.name}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 9px; color: #1f2937; line-height: 1.4; padding: 20px; }
    .header { display: flex; justify-content: space-between; align-items: start; border-bottom: 2px solid #3b82f6; padding-bottom: 10px; margin-bottom: 15px; }
    .logo { font-size: 18px; font-weight: bold; color: #1e40af; }
    .report-title { font-size: 14px; color: #6b7280; }
    .customer-info { text-align: right; }
    .customer-name { font-size: 14px; font-weight: bold; }
    .section { margin-bottom: 12px; }
    .section-title { font-size: 11px; font-weight: bold; color: #1e40af; border-bottom: 1px solid #e5e7eb; padding-bottom: 3px; margin-bottom: 8px; }
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
    .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
    .grid-4 { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 6px; }
    .metric-box { background: #f9fafb; padding: 8px; border-radius: 6px; text-align: center; }
    .metric-label { font-size: 7px; color: #6b7280; text-transform: uppercase; margin-bottom: 2px; }
    .metric-value { font-size: 14px; font-weight: bold; }
    .metric-value.green { color: #10b981; }
    .metric-value.yellow { color: #f59e0b; }
    .metric-value.red { color: #ef4444; }
    .metric-value.blue { color: #3b82f6; }
    .info-row { display: flex; justify-content: space-between; padding: 3px 0; border-bottom: 1px solid #f3f4f6; }
    .info-label { color: #6b7280; }
    .info-value { font-weight: 600; }
    .badge { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 8px; font-weight: 600; }
    .badge-green { background: #d1fae5; color: #065f46; }
    .badge-yellow { background: #fef3c7; color: #92400e; }
    .badge-red { background: #fee2e2; color: #991b1b; }
    .badge-blue { background: #dbeafe; color: #1e40af; }
    table { width: 100%; border-collapse: collapse; font-size: 8px; }
    th, td { padding: 4px 6px; text-align: left; border: 1px solid #e5e7eb; }
    th { background: #f9fafb; font-weight: 600; }
    .grade-table tr.highlight { background: #3b82f6; color: white; }
    .summary-box { background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%); color: white; padding: 15px; border-radius: 8px; margin-bottom: 15px; }
    .summary-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; text-align: center; }
    .summary-metric { background: rgba(255,255,255,0.1); padding: 10px; border-radius: 6px; }
    .summary-value { font-size: 20px; font-weight: bold; }
    .summary-label { font-size: 8px; opacity: 0.8; margin-top: 2px; }
    .page-break { page-break-before: always; }
    .footer { margin-top: 20px; padding-top: 10px; border-top: 1px solid #e5e7eb; font-size: 7px; color: #9ca3af; text-align: center; }
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
    .compact-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; }
    .mini-box { background: #f9fafb; padding: 4px 6px; border-radius: 4px; text-align: center; }
    .mini-label { font-size: 6px; color: #9ca3af; }
    .mini-value { font-size: 9px; font-weight: 600; }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="logo">Kaj NBFC</div>
      <div class="report-title">Alternative Data Credit Report</div>
    </div>
    <div class="customer-info">
      <div class="customer-name">${consumer.name}</div>
      <div>Report Date: ${consumer.reportDate || consumer.lastUpdated}</div>
      <div>PAN: ${identity.pan}</div>
    </div>
  </div>

  <div class="summary-box">
    <div class="summary-grid">
      <div class="summary-metric">
        <div class="summary-value">${summary.financialHealthScore}</div>
        <div class="summary-label">Financial Health Score</div>
      </div>
      <div class="summary-metric">
        <div class="summary-value">${getRiskGrade(summary.financialHealthScore)}</div>
        <div class="summary-label">Risk Grade</div>
      </div>
      <div class="summary-metric">
        <div class="summary-value">${formatAmount(summary.maxLoanAmount)}</div>
        <div class="summary-label">Max Loan Amount</div>
      </div>
      <div class="summary-metric">
        <div class="summary-value">${summary.probabilityOfDefault}%</div>
        <div class="summary-label">Default Probability</div>
      </div>
    </div>
  </div>

  <div class="two-col">
    <div>
      <div class="section">
        <div class="section-title">1. Identity & Demographics</div>
        <div class="grid-3" style="margin-bottom: 8px;">
          <div class="metric-box">
            <div class="metric-label">Digital Trust Score</div>
            <div class="metric-value blue">${identity.digitalIdentity?.overallTrustScore || 'N/A'}</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Life Stability</div>
            <div class="metric-value blue">${identity.lifeStability?.overallScore || 'N/A'}</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Social Capital</div>
            <div class="metric-value blue">${identity.socialCapital?.level || (identity.socialCapital?.overallScore >= 70 ? 'High' : identity.socialCapital?.overallScore >= 50 ? 'Medium' : 'Low')}</div>
          </div>
        </div>
        <div class="info-row"><span class="info-label">Address</span><span class="info-value">${identity.address}</span></div>
        <div class="info-row"><span class="info-label">Device Age</span><span class="info-value">${identity.digitalIdentity?.deviceAge} months</span></div>
        <div class="info-row"><span class="info-label">SIM Age</span><span class="info-value">${identity.digitalIdentity?.simAge} months</span></div>
        <div class="info-row"><span class="info-label">Job Stability</span><span class="info-value">${identity.lifeStability?.jobStability?.avgEmploymentDuration}y avg, ${identity.lifeStability?.jobStability?.salaryHikes} hikes</span></div>
        <div class="info-row"><span class="info-label">Residence</span><span class="info-value">${identity.lifeStability?.residenceStability?.yearsAtCurrentAddress}y, ${identity.lifeStability?.residenceStability?.rentPaymentPattern}</span></div>
      </div>

      <div class="section">
        <div class="section-title">2. Income & Cashflow</div>
        <div class="grid-3" style="margin-bottom: 8px;">
          <div class="metric-box">
            <div class="metric-label">Monthly Income</div>
            <div class="metric-value green">${formatAmount(income.monthlyIncome)}</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Avg Balance</div>
            <div class="metric-value green">${formatAmount(income.averageBalance || income.totalBalance)}</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Survivability</div>
            <div class="metric-value ${income.survivability?.months >= 6 ? 'green' : 'yellow'}">${income.survivability?.months?.toFixed(1)} mo</div>
          </div>
        </div>
        <div class="info-row"><span class="info-label">Monthly Inflow</span><span class="info-value">${formatAmount(income.monthlyInflow || income.monthlyIncome)}</span></div>
        <div class="info-row"><span class="info-label">Monthly Outflow</span><span class="info-value">${formatAmount(income.monthlyOutflow || income.survivability?.monthlyOutflow)}</span></div>
        <div class="info-row"><span class="info-label">Volatility Index</span><span class="info-value">${income.incomeVolatility?.volatilityIndex}%</span></div>
        <div class="info-row"><span class="info-label">Emergency Funds</span><span class="info-value">${formatAmount(income.survivability?.emergencyFunds || income.totalBalance)}</span></div>
        <div class="info-row"><span class="info-label">One-off Inflation</span><span class="info-value">${income.oneOffTransactionInflation ? 'Yes' : 'No'}</span></div>
        <div class="info-row"><span class="info-label">Impulse Score</span><span class="info-value">${income.salaryRetention?.impulseScore} (${income.salaryRetention?.impatienceLevel || (income.salaryRetention?.impulseScore <= 30 ? 'Low' : 'Medium')})</span></div>
      </div>

      <div class="section">
        <div class="section-title">3. Assets & Liabilities</div>
        <div class="info-row"><span class="info-label">Total Assets</span><span class="info-value">${formatAmount(assets.totalAssets)}</span></div>
        <div class="compact-grid" style="margin: 6px 0;">
          ${assets.investments.mutualFunds > 0 ? `<div class="mini-box"><div class="mini-label">MF</div><div class="mini-value">${formatAmount(assets.investments.mutualFunds)}</div></div>` : ''}
          ${assets.investments.stocks > 0 ? `<div class="mini-box"><div class="mini-label">Stocks</div><div class="mini-value">${formatAmount(assets.investments.stocks)}</div></div>` : ''}
          ${assets.investments.epf > 0 ? `<div class="mini-box"><div class="mini-label">EPF</div><div class="mini-value">${formatAmount(assets.investments.epf)}</div></div>` : ''}
          ${assets.investments.ppf > 0 ? `<div class="mini-box"><div class="mini-label">PPF</div><div class="mini-value">${formatAmount(assets.investments.ppf)}</div></div>` : ''}
          ${assets.investments.rd > 0 ? `<div class="mini-box"><div class="mini-label">RD</div><div class="mini-value">${formatAmount(assets.investments.rd)}</div></div>` : ''}
        </div>
        <div class="info-row"><span class="info-label">ITR Filed</span><span class="info-value">${assets.itrFiled ? `Yes (${assets.itrYear || 'Available'})` : 'No'}</span></div>
        <div class="info-row"><span class="info-label">Insurance</span><span class="info-value">${insurance.policies?.map((p: any) => p.type).join(', ') || 'None'}</span></div>
        <div class="info-row"><span class="info-label">Premium Payment</span><span class="info-value">${insurance.paymentBehaviour?.avgDaysBeforeDue}d before due</span></div>
        <div class="info-row"><span class="info-label">Liabilities</span><span class="info-value">${liabilities.available ? `${liabilities.activeLoans?.length || 0} active` : 'Not Available (NTC)'}</span></div>
        <div class="info-row"><span class="info-label">Credit Enquiries</span><span class="info-value">${liabilities.creditEnquiries}</span></div>
        <div style="margin-top: 6px; font-weight: 600;">Saturation Levels:</div>
        <div class="info-row"><span class="info-label">EMI ÷ Income</span><span class="info-value">${saturation.emiToIncome}%</span></div>
        <div class="info-row"><span class="info-label">Rent ÷ Income</span><span class="info-value">${saturation.rentToIncome}%</span></div>
        <div class="info-row"><span class="info-label">Utility ÷ Income</span><span class="info-value">${saturation.utilityToIncome}%</span></div>
      </div>
    </div>

    <div>
      <div class="section">
        <div class="section-title">4. Behavioural Signals</div>
        <div class="grid-3" style="margin-bottom: 8px;">
          <div class="metric-box">
            <div class="metric-label">Archetype</div>
            <div class="metric-value blue" style="font-size: 9px;">${behaviour.spendingArchetype?.type}</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Micro-commit</div>
            <div class="metric-value blue">${behaviour.microCommitment?.consistencyScore}</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Emotional</div>
            <div class="metric-value blue">${behaviour.emotionalPurchasing?.level || behaviour.emotionalPurchasing?.pattern}</div>
          </div>
        </div>
        <div class="info-row"><span class="info-label">Bill Payment Score</span><span class="info-value">${behaviour.billPayment?.overallScore}/100</span></div>
        <div class="info-row"><span class="info-label">Auto-debit</span><span class="info-value">${behaviour.billPayment?.autoDebitEnabled ? 'Enabled' : 'Disabled'}</span></div>
        <div class="info-row"><span class="info-label">Late (6mo)</span><span class="info-value">Util: ${behaviour.billPayment?.latePaymentsLast6Months?.utility}, Rent: ${behaviour.billPayment?.latePaymentsLast6Months?.rent}, Subs: ${behaviour.billPayment?.latePaymentsLast6Months?.subscriptions}</span></div>
        <div class="info-row"><span class="info-label">Active SIPs</span><span class="info-value">${behaviour.savingsConsistency?.activeSips} (${formatAmount(behaviour.savingsConsistency?.totalSipValue)}/mo)</span></div>
        <div class="info-row"><span class="info-label">SIP on Hike</span><span class="info-value">${behaviour.savingsConsistency?.sipIncreaseOnHike ? 'Yes' : 'No'}</span></div>
        <div class="info-row"><span class="info-label">Risk Appetite</span><span class="info-value">${behaviour.riskAppetite?.segment}</span></div>
      </div>

      <div class="section">
        <div class="section-title">5. Fraud & Identity Strength</div>
        <div class="grid-3" style="margin-bottom: 8px;">
          <div class="metric-box">
            <div class="metric-label">Identity Match</div>
            <div class="metric-value green">${fraud.identityMatching?.overallScore}%</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Manipulation</div>
            <div class="metric-value ${fraud.statementManipulation?.probability <= 5 ? 'green' : 'red'}">${fraud.statementManipulation?.probability}%</div>
          </div>
          <div class="metric-box">
            <div class="metric-label">Synthetic ID</div>
            <div class="metric-value ${fraud.syntheticIdentity?.probability <= 5 ? 'green' : 'red'}">${fraud.syntheticIdentity?.probability}%</div>
          </div>
        </div>
        <div class="info-row"><span class="info-label">Pin Code Risk</span><span class="info-value">${fraud.pinCodeRisk || 'Low Risk'}</span></div>
        <div class="info-row"><span class="info-label">Historical Signals</span><span class="info-value">${fraud.historicalFraudSignals}</span></div>
      </div>

      <div class="section">
        <div class="section-title">6. Transactions & Utility</div>
        <div class="info-row"><span class="info-label">Income Authenticity</span><span class="info-value">${transactions.incomeAuthenticity?.status}</span></div>
        <div class="info-row"><span class="info-label">Inflow Consistency</span><span class="info-value">${transactions.incomeAuthenticity?.inflowTimeConsistency}%</span></div>
        <div class="info-row"><span class="info-label">Salary:UPI Ratio</span><span class="info-value">${transactions.incomeAuthenticity?.salaryToUpiRatio}x</span></div>
        <table style="margin-top: 8px;">
          <thead>
            <tr>
              <th>Utility Type</th>
              <th>Consistency</th>
            </tr>
          </thead>
          <tbody>
            <tr><td>Recharge</td><td>${transactions.utilityPayments?.rechargeConsistency}%</td></tr>
            <tr><td>Electricity</td><td>${transactions.utilityPayments?.electricityConsistency}%</td></tr>
            <tr><td>Rent</td><td>${transactions.utilityPayments?.rentConsistency}%</td></tr>
            <tr><td>Subscriptions</td><td>${transactions.utilityPayments?.subscriptionConsistency}%</td></tr>
          </tbody>
        </table>
      </div>

      <div class="section">
        <div class="section-title">CIBIL Proximity</div>
        <table class="grade-table">
          <thead>
            <tr><th>CIBIL</th><th>Health Score</th><th>Grade</th></tr>
          </thead>
          <tbody>
            <tr ${getRiskGrade(summary.financialHealthScore) === 'A' ? 'class="highlight"' : ''}><td>800+</td><td>85-100</td><td>A</td></tr>
            <tr ${getRiskGrade(summary.financialHealthScore) === 'B' ? 'class="highlight"' : ''}><td>740-800</td><td>75-84</td><td>B</td></tr>
            <tr ${getRiskGrade(summary.financialHealthScore) === 'C' ? 'class="highlight"' : ''}><td>700-740</td><td>56-74</td><td>C</td></tr>
            <tr ${getRiskGrade(summary.financialHealthScore) === 'D' ? 'class="highlight"' : ''}><td>650-699</td><td>40-55</td><td>D</td></tr>
            <tr ${getRiskGrade(summary.financialHealthScore) === 'E' ? 'class="highlight"' : ''}><td>&lt;650</td><td>0-39</td><td>E</td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="footer">
    Generated by Kaj NBFC Alternative Data Credit Scoring System | Report ID: ${consumer.id}-${Date.now()} | This is a system-generated report.
  </div>
</body>
</html>
  `
}

export function downloadPDF(consumer: any) {
  const content = generatePDFContent(consumer)
  const printWindow = window.open('', '_blank')
  if (printWindow) {
    printWindow.document.write(content)
    printWindow.document.close()
    setTimeout(() => {
      printWindow.print()
    }, 250)
  }
}

