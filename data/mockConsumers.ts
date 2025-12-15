export const mockConsumers = [
  {
    id: "1",
    name: "Rajesh Kumar",
    phone: "+91-XXXX006789",
    email: "rajesh.kumar@email.com",
    persona: "Salaried",
    currentScore: 745,
    riskBucket: "Low",
    lastUpdated: "2025-01-15",
    dob: "1990-05-15",

    // 1. Identity & Demographics
    identity: {
      faceMatch: 98.5,
      nameMatch: "Verified",
      address: "Bangalore, Karnataka",
      pan: "XXXX1234K",
      aadhaar: "XXXX1234",
      mobileVerified: true,
      // Digital Identity Trust Score
      digitalIdentity: {
        deviceAge: 36, // months
        simAge: 48, // months
        emailAge: 84, // months
        overallTrustScore: 92,
        platformConsistency: 95, // consistency across platforms
        aadhaarPanMatchStability: "Stable",
      },
      // Life Stability Index
      lifeStability: {
        jobStability: {
          avgEmploymentDuration: 4.5, // years
          salaryHikes: 3, // number of hikes in last 3 years
          score: 88,
        },
        residenceStability: {
          yearsAtCurrentAddress: 5,
          landlordVerified: true,
          rentPaymentPattern: "On-time",
          score: 92,
        },
        householdStability: {
          status: "Strong",
          score: 85,
        },
        overallScore: 88,
      },
      // Social Capital Proxy
      socialCapital: {
        regularPeerTransactions: 78, // percentage
        professionalNetworkPayments: 85, // consistency percentage
        overallScore: 82,
      },
    },

    // 2. Income & Cashflow Strength
    income: {
      monthlyIncome: 85000,
      incomeStabilityScore: 92,
      // Account Balances
      accountBalances: [
        { bank: "HDFC Savings", balance: 285000 },
        { bank: "ICICI Savings", balance: 125000 },
        { bank: "SBI Salary", balance: 40000 },
      ],
      totalBalance: 450000,
      transactionValueExcludingP2P: 65000,
      // Income Volatility Index
      incomeVolatility: {
        stdDeviation: 8500,
        avgIncome: 85000,
        volatilityIndex: 10, // percentage
      },
      // Future Cashflow Survivability
      survivability: {
        totalSavings: 1800000, // PPF + Assets + Bank
        monthlyOutflow: 42000,
        months: 42.8,
      },
      // Income Source Reliability Tags
      incomeSources: [
        { source: "Salary - TCS", amount: 85000, reliability: "Verified", tag: "salary" },
      ],
      // Expense Rigidity Score
      expenseCategories: {
        fixedEssential: { amount: 18000, percentage: 43, items: ["Rent", "EMIs", "Groceries"] },
        variableEssential: { amount: 8000, percentage: 19, items: ["Utilities", "Transport"] },
        entertainment: { amount: 5000, percentage: 12, items: ["OTT", "Dining"] },
        shopping: { amount: 6000, percentage: 14, items: ["Clothing", "Electronics"] },
        lifestyle: { amount: 5000, percentage: 12, items: ["Gym", "Events"] },
      },
      salaryRetention: {
        firstWeekBalance: 78000,
        lastWeekBalance: 35000,
        adjustedForInvestments: 15000,
        impulseScore: 25, // lower is better
      },
    },

    // 3. Assets & Liabilities
    assets: {
      investments: {
        mutualFunds: 500000,
        stocks: 350000,
        corporateBonds: 0,
        governmentSecurities: 100000,
        nps: 200000,
        epf: 450000,
        ppf: 800000,
        fd: 500000,
        rd: 50000,
      },
      itrFiled: true,
      totalAssets: 2950000,
    },
    insurance: {
      policies: [
        { type: "Health", provider: "Star Health", premium: 25000, status: "Active" },
        { type: "Life", provider: "LIC", premium: 48000, status: "Active" },
        { type: "Vehicle", provider: "ICICI Lombard", premium: 12000, status: "Active" },
      ],
      paymentBehaviour: {
        avgDaysBeforeDue: 5,
        latePaymentsLast6Months: 0,
      },
    },
    liabilities: {
      available: true,
      activeLoans: [
        { type: "Home Loan", outstanding: 3200000, emi: 45000, bank: "HDFC" },
        { type: "Car Loan", outstanding: 120000, emi: 15000, bank: "ICICI" },
      ],
      loanRepaymentHistory: "Excellent",
      creditCardRepaymentHistory: "Excellent",
      creditEnquiries: 2,
      goodDebtVsBadDebt: {
        goodDebt: 3200000, // home loan
        badDebt: 120000, // car loan
        index: 0.96, // higher is better
      },
      defaultHistory: "None",
      bnplHistory: {
        active: 0,
        totalUsed: 2,
        repaymentStatus: "All Cleared",
      },
    },
    saturation: {
      emiToIncome: 70.6, // percentage
      rentToIncome: 0, // owns home
      utilityToIncome: 3.5,
      totalSaturation: 74.1,
      status: "Moderate",
    },

    // 4. Behavioural & Psychological Signals
    behaviour: {
      // Spending Personality Archetype
      spendingArchetype: {
        type: "Disciplined Saver",
        confidence: 85,
        traits: ["Low lifestyle spend", "Stable categories", "Regular savings"],
      },
      // Financial Stress Indicator
      financialStress: {
        atmWithdrawalTrend: "Stable",
        microUpiPayments: "Low",
        stressLevel: "Low",
        warningSignals: [],
      },
      // Bill Payment Behaviour Index
      billPayment: {
        avgDaysBeforeDue: 2,
        behaviour: "High Discipline",
        autoDebitEnabled: true,
        latePaymentsLast6Months: {
          utility: 0,
          recharges: 0,
          rent: 0,
          subscriptions: 0,
        },
        overallScore: 94,
      },
      // Subscription
      subscriptions: {
        active: 5,
        latePaymentsLastYear: 1,
        downgradingPatterns: false,
        list: ["Netflix", "Spotify", "Swiggy One", "Amazon Prime", "Gym"],
      },
      // Micro-commitment Score
      microCommitment: {
        consistencyScore: 88,
        dailySpendPatterns: ["Coffee - ₹150", "Parking - ₹50", "Metro - ₹60"],
      },
      // Emotional Purchasing Window
      emotionalPurchasing: {
        lateNightSpending: 8, // percentage of total
        weekendSpending: 25,
        weekdaySpending: 67,
        pattern: "Routine-driven",
      },
      // Savings Consistency
      savingsConsistency: {
        sipIncreaseOnHike: true,
        activeSips: 3,
        totalSipValue: 25000,
        sipPaymentConsistency: 100,
        sipWithdrawalTrend: "None",
      },
      // Money Personality Stability
      moneyPersonalityStability: {
        behaviourChanges: 1, // in last year
        stability: "Stable",
      },
      // Risk Appetite Segmentation
      riskAppetite: {
        tradingAppInflows: 15000,
        cryptoActivity: "None",
        lotteryGamingSpends: 0,
        segment: "Moderate",
      },
    },

    // 5. Fraud & Identity Strength
    fraud: {
      historicalFraudSignals: 0,
      // Identity Matching
      identityMatching: {
        nameMatchAcrossPlatforms: 98,
        emailPhoneConsistency: 100,
        geoLocationMatch: 95,
        overallScore: 97,
      },
      // Bank Statement Manipulation
      statementManipulation: {
        probability: 2, // percentage
        pixelStructureCheck: "Pass",
        fontVariationCheck: "Pass",
        duplicateTemplateCheck: "Pass",
        ocrConsistency: "Pass",
        salaryToUpiRatio: "Normal",
      },
      // Synthetic Identity Probability
      syntheticIdentity: {
        probability: 1, // percentage
        nameDobSimilarity: "No Match in Fraud DB",
        riskLevel: "Very Low",
      },
    },

    // 6. Transactions & Utility Signals
    transactions: {
      // Spike Detector
      spikeDetector: {
        upiVolumeChange: 5, // percentage change
        balanceDropAlert: false,
        newMerchantsAdded: 2,
        emiFailures: 0,
        status: "Normal",
      },
      // Income Authenticity
      incomeAuthenticity: {
        inflowTimeConsistency: 98, // salary on same date
        salaryToUpiRatio: 1.2, // normal range
        status: "Verified",
      },
      // Utility Payments
      utilityPayments: {
        rechargeConsistency: 100,
        electricityConsistency: 98,
        rentConsistency: 100,
        subscriptionConsistency: 95,
        overallScore: 98,
      },
    },

    // Summary
    summary: {
      financialHealthScore: 82,
      maxLoanAmount: 1500000,
      probabilityOfDefault: 3.2,
      recommendation: "Approved",
    },

    scoringHistory: [
      { date: "2025-01-15", score: 745, method: "GBM v1.2.3" },
      { date: "2025-01-08", score: 742, method: "GBM v1.2.2" },
      { date: "2024-12-15", score: 738, method: "GBM v1.2.2" },
    ],
  },
  {
    id: "2",
    name: "Priya Sharma",
    phone: "+91-XXXX112345",
    email: "priya.sharma@email.com",
    persona: "Gig",
    currentScore: 658,
    riskBucket: "Medium",
    lastUpdated: "2025-01-12",
    dob: "1992-08-22",

    identity: {
      faceMatch: 95.2,
      nameMatch: "Verified",
      address: "Delhi, NCR",
      pan: "XXXX5678P",
      aadhaar: "XXXX5678",
      mobileVerified: true,
      digitalIdentity: {
        deviceAge: 18,
        simAge: 24,
        emailAge: 60,
        overallTrustScore: 72,
        platformConsistency: 78,
        aadhaarPanMatchStability: "Stable",
      },
      lifeStability: {
        jobStability: {
          avgEmploymentDuration: 1.2,
          salaryHikes: 0,
          score: 55,
        },
        residenceStability: {
          yearsAtCurrentAddress: 2,
          landlordVerified: false,
          rentPaymentPattern: "Mostly On-time",
          score: 68,
        },
        householdStability: {
          status: "Moderate",
          score: 65,
        },
        overallScore: 63,
      },
      socialCapital: {
        regularPeerTransactions: 65,
        professionalNetworkPayments: 55,
        overallScore: 60,
      },
    },

    income: {
      monthlyIncome: 65000,
      incomeStabilityScore: 65,
      accountBalances: [
        { bank: "Kotak Savings", balance: 125000 },
        { bank: "Paytm Payments", balance: 55000 },
      ],
      totalBalance: 180000,
      transactionValueExcludingP2P: 45000,
      incomeVolatility: {
        stdDeviation: 19500,
        avgIncome: 65000,
        volatilityIndex: 30,
      },
      survivability: {
        totalSavings: 650000,
        monthlyOutflow: 38000,
        months: 17.1,
      },
      incomeSources: [
        { source: "Freelance - Design", amount: 45000, reliability: "Medium", tag: "gig" },
        { source: "Freelance - Consulting", amount: 20000, reliability: "Variable", tag: "gig" },
      ],
      expenseCategories: {
        fixedEssential: { amount: 15000, percentage: 39, items: ["Rent", "Groceries"] },
        variableEssential: { amount: 6000, percentage: 16, items: ["Utilities", "Transport"] },
        entertainment: { amount: 8000, percentage: 21, items: ["OTT", "Dining", "Events"] },
        shopping: { amount: 5000, percentage: 13, items: ["Clothing"] },
        lifestyle: { amount: 4000, percentage: 11, items: ["Fitness", "Travel"] },
      },
      salaryRetention: {
        firstWeekBalance: 55000,
        lastWeekBalance: 18000,
        adjustedForInvestments: 5000,
        impulseScore: 58,
      },
    },

    assets: {
      investments: {
        mutualFunds: 100000,
        stocks: 80000,
        corporateBonds: 0,
        governmentSecurities: 0,
        nps: 0,
        epf: 0,
        ppf: 200000,
        fd: 100000,
        rd: 20000,
      },
      itrFiled: true,
      totalAssets: 500000,
    },
    insurance: {
      policies: [
        { type: "Health", provider: "HDFC Ergo", premium: 15000, status: "Active" },
      ],
      paymentBehaviour: {
        avgDaysBeforeDue: 1,
        latePaymentsLast6Months: 2,
      },
    },
    liabilities: {
      available: true,
      activeLoans: [
        { type: "Personal Loan", outstanding: 125000, emi: 8500, bank: "Bajaj" },
      ],
      loanRepaymentHistory: "Good",
      creditCardRepaymentHistory: "Good",
      creditEnquiries: 5,
      goodDebtVsBadDebt: {
        goodDebt: 0,
        badDebt: 125000,
        index: 0,
      },
      defaultHistory: "None",
      bnplHistory: {
        active: 2,
        totalUsed: 8,
        repaymentStatus: "1 Pending",
      },
    },
    saturation: {
      emiToIncome: 13.1,
      rentToIncome: 23.1,
      utilityToIncome: 4.6,
      totalSaturation: 40.8,
      status: "Low",
    },

    behaviour: {
      spendingArchetype: {
        type: "Experience Seeker",
        confidence: 72,
        traits: ["High travel", "Food enthusiast", "Entertainment focused"],
      },
      financialStress: {
        atmWithdrawalTrend: "Slightly Increasing",
        microUpiPayments: "Moderate",
        stressLevel: "Moderate",
        warningSignals: ["Increasing cash withdrawals"],
      },
      billPayment: {
        avgDaysBeforeDue: 0,
        behaviour: "Neutral",
        autoDebitEnabled: false,
        latePaymentsLast6Months: {
          utility: 2,
          recharges: 1,
          rent: 1,
          subscriptions: 3,
        },
        overallScore: 72,
      },
      subscriptions: {
        active: 8,
        latePaymentsLastYear: 5,
        downgradingPatterns: true,
        list: ["Netflix", "Spotify", "Zomato Pro", "Amazon Prime", "Cult.fit", "YouTube Premium", "Notion", "Figma"],
      },
      microCommitment: {
        consistencyScore: 65,
        dailySpendPatterns: ["Coffee - ₹200", "Uber - ₹300", "Lunch - ₹250"],
      },
      emotionalPurchasing: {
        lateNightSpending: 22,
        weekendSpending: 45,
        weekdaySpending: 33,
        pattern: "Social behaviour",
      },
      savingsConsistency: {
        sipIncreaseOnHike: false,
        activeSips: 1,
        totalSipValue: 5000,
        sipPaymentConsistency: 85,
        sipWithdrawalTrend: "Occasional",
      },
      moneyPersonalityStability: {
        behaviourChanges: 4,
        stability: "Volatile",
      },
      riskAppetite: {
        tradingAppInflows: 25000,
        cryptoActivity: "Moderate",
        lotteryGamingSpends: 2000,
        segment: "Aggressive",
      },
    },

    fraud: {
      historicalFraudSignals: 0,
      identityMatching: {
        nameMatchAcrossPlatforms: 92,
        emailPhoneConsistency: 95,
        geoLocationMatch: 88,
        overallScore: 92,
      },
      statementManipulation: {
        probability: 5,
        pixelStructureCheck: "Pass",
        fontVariationCheck: "Pass",
        duplicateTemplateCheck: "Pass",
        ocrConsistency: "Pass",
        salaryToUpiRatio: "Slightly High",
      },
      syntheticIdentity: {
        probability: 3,
        nameDobSimilarity: "No Match in Fraud DB",
        riskLevel: "Low",
      },
    },

    transactions: {
      spikeDetector: {
        upiVolumeChange: 15,
        balanceDropAlert: false,
        newMerchantsAdded: 8,
        emiFailures: 0,
        status: "Monitor",
      },
      incomeAuthenticity: {
        inflowTimeConsistency: 65,
        salaryToUpiRatio: 0.8,
        status: "Variable - Gig Income",
      },
      utilityPayments: {
        rechargeConsistency: 90,
        electricityConsistency: 85,
        rentConsistency: 92,
        subscriptionConsistency: 78,
        overallScore: 86,
      },
    },

    summary: {
      financialHealthScore: 62,
      maxLoanAmount: 400000,
      probabilityOfDefault: 12.8,
      recommendation: "Conditional Approval",
    },

    scoringHistory: [{ date: "2025-01-12", score: 658, method: "GBM v1.2.3" }],
  },
  {
    id: "3",
    name: "Amit Patel",
    phone: "+91-XXXX223456",
    email: "amit.patel@email.com",
    persona: "Mass Affluent",
    currentScore: 812,
    riskBucket: "Low",
    lastUpdated: "2025-01-14",
    dob: "1985-03-10",

    identity: {
      faceMatch: 99.8,
      nameMatch: "Verified",
      address: "Mumbai, Maharashtra",
      pan: "XXXX9012A",
      aadhaar: "XXXX9012",
      mobileVerified: true,
      digitalIdentity: {
        deviceAge: 48,
        simAge: 96,
        emailAge: 144,
        overallTrustScore: 98,
        platformConsistency: 99,
        aadhaarPanMatchStability: "Stable",
      },
      lifeStability: {
        jobStability: {
          avgEmploymentDuration: 7.5,
          salaryHikes: 6,
          score: 96,
        },
        residenceStability: {
          yearsAtCurrentAddress: 8,
          landlordVerified: true,
          rentPaymentPattern: "Owns Property",
          score: 98,
        },
        householdStability: {
          status: "Very Strong",
          score: 95,
        },
        overallScore: 96,
      },
      socialCapital: {
        regularPeerTransactions: 85,
        professionalNetworkPayments: 92,
        overallScore: 89,
      },
    },

    income: {
      monthlyIncome: 250000,
      incomeStabilityScore: 96,
      accountBalances: [
        { bank: "HDFC Savings", balance: 1200000 },
        { bank: "ICICI Priority", balance: 800000 },
        { bank: "Kotak 811", balance: 500000 },
      ],
      totalBalance: 2500000,
      transactionValueExcludingP2P: 180000,
      incomeVolatility: {
        stdDeviation: 12500,
        avgIncome: 250000,
        volatilityIndex: 5,
      },
      survivability: {
        totalSavings: 11500000,
        monthlyOutflow: 95000,
        months: 121.0,
      },
      incomeSources: [
        { source: "Salary - Goldman Sachs", amount: 250000, reliability: "Verified", tag: "salary" },
        { source: "Rental Income", amount: 35000, reliability: "Verified", tag: "passive" },
      ],
      expenseCategories: {
        fixedEssential: { amount: 35000, percentage: 37, items: ["EMIs", "Insurance", "Groceries"] },
        variableEssential: { amount: 15000, percentage: 16, items: ["Utilities", "Fuel"] },
        entertainment: { amount: 18000, percentage: 19, items: ["Dining", "Travel", "Events"] },
        shopping: { amount: 15000, percentage: 16, items: ["Luxury", "Electronics"] },
        lifestyle: { amount: 12000, percentage: 12, items: ["Club", "Golf", "Spa"] },
      },
      salaryRetention: {
        firstWeekBalance: 200000,
        lastWeekBalance: 120000,
        adjustedForInvestments: 75000,
        impulseScore: 15,
      },
    },

    assets: {
      investments: {
        mutualFunds: 3500000,
        stocks: 2500000,
        corporateBonds: 500000,
        governmentSecurities: 800000,
        nps: 1200000,
        epf: 1800000,
        ppf: 1500000,
        fd: 5000000,
        rd: 200000,
      },
      itrFiled: true,
      totalAssets: 17000000,
    },
    insurance: {
      policies: [
        { type: "Health", provider: "Max Bupa", premium: 75000, status: "Active" },
        { type: "Life", provider: "HDFC Life", premium: 120000, status: "Active" },
        { type: "Vehicle", provider: "TATA AIG", premium: 45000, status: "Active" },
        { type: "Term", provider: "ICICI Pru", premium: 35000, status: "Active" },
      ],
      paymentBehaviour: {
        avgDaysBeforeDue: 15,
        latePaymentsLast6Months: 0,
      },
    },
    liabilities: {
      available: true,
      activeLoans: [
        { type: "Mortgage", outstanding: 12000000, emi: 125000, bank: "SBI" },
        { type: "Business Loan", outstanding: 3500000, emi: 80000, bank: "HDFC" },
      ],
      loanRepaymentHistory: "Excellent",
      creditCardRepaymentHistory: "Excellent",
      creditEnquiries: 1,
      goodDebtVsBadDebt: {
        goodDebt: 15500000,
        badDebt: 0,
        index: 1.0,
      },
      defaultHistory: "None",
      bnplHistory: {
        active: 0,
        totalUsed: 0,
        repaymentStatus: "N/A",
      },
    },
    saturation: {
      emiToIncome: 82.0,
      rentToIncome: 0,
      utilityToIncome: 2.0,
      totalSaturation: 84.0,
      status: "High but Manageable",
    },

    behaviour: {
      spendingArchetype: {
        type: "Disciplined Saver",
        confidence: 92,
        traits: ["High savings rate", "Systematic investments", "Premium but controlled"],
      },
      financialStress: {
        atmWithdrawalTrend: "Stable",
        microUpiPayments: "Low",
        stressLevel: "Very Low",
        warningSignals: [],
      },
      billPayment: {
        avgDaysBeforeDue: 10,
        behaviour: "Ultra-Trustworthy",
        autoDebitEnabled: true,
        latePaymentsLast6Months: {
          utility: 0,
          recharges: 0,
          rent: 0,
          subscriptions: 0,
        },
        overallScore: 100,
      },
      subscriptions: {
        active: 12,
        latePaymentsLastYear: 0,
        downgradingPatterns: false,
        list: ["Netflix Premium", "Spotify Family", "Amazon Prime", "Apple One", "LinkedIn Premium", "Bloomberg", "WSJ", "NYT", "Club Mahindra", "Priority Pass", "Cult.fit", "Headspace"],
      },
      microCommitment: {
        consistencyScore: 95,
        dailySpendPatterns: ["Coffee - ₹300", "Driver - ₹500", "Lunch - ₹400"],
      },
      emotionalPurchasing: {
        lateNightSpending: 5,
        weekendSpending: 35,
        weekdaySpending: 60,
        pattern: "Routine-driven",
      },
      savingsConsistency: {
        sipIncreaseOnHike: true,
        activeSips: 8,
        totalSipValue: 150000,
        sipPaymentConsistency: 100,
        sipWithdrawalTrend: "None",
      },
      moneyPersonalityStability: {
        behaviourChanges: 0,
        stability: "Very Stable",
      },
      riskAppetite: {
        tradingAppInflows: 100000,
        cryptoActivity: "Minimal",
        lotteryGamingSpends: 0,
        segment: "Moderate",
      },
    },

    fraud: {
      historicalFraudSignals: 0,
      identityMatching: {
        nameMatchAcrossPlatforms: 100,
        emailPhoneConsistency: 100,
        geoLocationMatch: 100,
        overallScore: 100,
      },
      statementManipulation: {
        probability: 0,
        pixelStructureCheck: "Pass",
        fontVariationCheck: "Pass",
        duplicateTemplateCheck: "Pass",
        ocrConsistency: "Pass",
        salaryToUpiRatio: "Normal",
      },
      syntheticIdentity: {
        probability: 0,
        nameDobSimilarity: "No Match in Fraud DB",
        riskLevel: "Very Low",
      },
    },

    transactions: {
      spikeDetector: {
        upiVolumeChange: 2,
        balanceDropAlert: false,
        newMerchantsAdded: 1,
        emiFailures: 0,
        status: "Normal",
      },
      incomeAuthenticity: {
        inflowTimeConsistency: 100,
        salaryToUpiRatio: 1.4,
        status: "Verified",
      },
      utilityPayments: {
        rechargeConsistency: 100,
        electricityConsistency: 100,
        rentConsistency: 100,
        subscriptionConsistency: 100,
        overallScore: 100,
      },
    },

    summary: {
      financialHealthScore: 94,
      maxLoanAmount: 5000000,
      probabilityOfDefault: 1.8,
      recommendation: "Pre-Approved",
    },

    scoringHistory: [{ date: "2025-01-14", score: 812, method: "GBM v1.2.3" }],
  },
  {
    id: "4",
    name: "Neha Singh",
    phone: "+91-XXXX334567",
    email: "neha.singh@email.com",
    persona: "NTC",
    currentScore: 542,
    riskBucket: "High",
    lastUpdated: "2025-01-10",
    dob: "1998-11-30",

    identity: {
      faceMatch: 87.3,
      nameMatch: "Verified",
      address: "Pune, Maharashtra",
      pan: null,
      aadhaar: "XXXX3456",
      mobileVerified: true,
      digitalIdentity: {
        deviceAge: 8,
        simAge: 12,
        emailAge: 24,
        overallTrustScore: 48,
        platformConsistency: 55,
        aadhaarPanMatchStability: "PAN Not Available",
      },
      lifeStability: {
        jobStability: {
          avgEmploymentDuration: 0.8,
          salaryHikes: 0,
          score: 35,
        },
        residenceStability: {
          yearsAtCurrentAddress: 1,
          landlordVerified: false,
          rentPaymentPattern: "Irregular",
          score: 45,
        },
        householdStability: {
          status: "Weak",
          score: 40,
        },
        overallScore: 40,
      },
      socialCapital: {
        regularPeerTransactions: 45,
        professionalNetworkPayments: 30,
        overallScore: 38,
      },
    },

    income: {
      monthlyIncome: 18000,
      incomeStabilityScore: 48,
      accountBalances: [
        { bank: "SBI Savings", balance: 8000 },
        { bank: "Paytm Wallet", balance: 4000 },
      ],
      totalBalance: 12000,
      transactionValueExcludingP2P: 12000,
      incomeVolatility: {
        stdDeviation: 5400,
        avgIncome: 18000,
        volatilityIndex: 30,
      },
      survivability: {
        totalSavings: 25000,
        monthlyOutflow: 16000,
        months: 1.6,
      },
      incomeSources: [
        { source: "Salary - Retail", amount: 18000, reliability: "Medium", tag: "salary" },
      ],
      expenseCategories: {
        fixedEssential: { amount: 10000, percentage: 62, items: ["Rent", "Groceries", "Transport"] },
        variableEssential: { amount: 3000, percentage: 19, items: ["Utilities", "Phone"] },
        entertainment: { amount: 1500, percentage: 9, items: ["OTT"] },
        shopping: { amount: 1000, percentage: 6, items: ["Clothing"] },
        lifestyle: { amount: 500, percentage: 4, items: [] },
      },
      salaryRetention: {
        firstWeekBalance: 15000,
        lastWeekBalance: 3000,
        adjustedForInvestments: 0,
        impulseScore: 72,
      },
    },

    assets: {
      investments: {
        mutualFunds: 0,
        stocks: 0,
        corporateBonds: 0,
        governmentSecurities: 0,
        nps: 0,
        epf: 20000,
        ppf: 5000,
        fd: 0,
        rd: 0,
      },
      itrFiled: false,
      totalAssets: 25000,
    },
    insurance: {
      policies: [],
      paymentBehaviour: {
        avgDaysBeforeDue: 0,
        latePaymentsLast6Months: 0,
      },
    },
    liabilities: {
      available: false,
      activeLoans: [],
      loanRepaymentHistory: "Not Available",
      creditCardRepaymentHistory: "Not Available",
      creditEnquiries: 0,
      goodDebtVsBadDebt: {
        goodDebt: 0,
        badDebt: 0,
        index: 0,
      },
      defaultHistory: "Not Available",
      bnplHistory: {
        active: 1,
        totalUsed: 3,
        repaymentStatus: "1 Delayed",
      },
    },
    saturation: {
      emiToIncome: 0,
      rentToIncome: 44.4,
      utilityToIncome: 8.3,
      totalSaturation: 52.7,
      status: "Moderate",
    },

    behaviour: {
      spendingArchetype: {
        type: "Avoider",
        confidence: 68,
        traits: ["Last-minute payments", "No budgeting", "Reactive spending"],
      },
      financialStress: {
        atmWithdrawalTrend: "High",
        microUpiPayments: "High",
        stressLevel: "High",
        warningSignals: ["Frequent small withdrawals", "Rising micro-payments"],
      },
      billPayment: {
        avgDaysBeforeDue: -3,
        behaviour: "Low Discipline",
        autoDebitEnabled: false,
        latePaymentsLast6Months: {
          utility: 4,
          recharges: 3,
          rent: 2,
          subscriptions: 2,
        },
        overallScore: 45,
      },
      subscriptions: {
        active: 2,
        latePaymentsLastYear: 6,
        downgradingPatterns: true,
        list: ["Netflix Mobile", "Hotstar"],
      },
      microCommitment: {
        consistencyScore: 45,
        dailySpendPatterns: ["Tea - ₹30", "Bus - ₹40", "Snacks - ₹50"],
      },
      emotionalPurchasing: {
        lateNightSpending: 35,
        weekendSpending: 40,
        weekdaySpending: 25,
        pattern: "Impulse-driven",
      },
      savingsConsistency: {
        sipIncreaseOnHike: false,
        activeSips: 0,
        totalSipValue: 0,
        sipPaymentConsistency: 0,
        sipWithdrawalTrend: "N/A",
      },
      moneyPersonalityStability: {
        behaviourChanges: 6,
        stability: "Unstable",
      },
      riskAppetite: {
        tradingAppInflows: 0,
        cryptoActivity: "None",
        lotteryGamingSpends: 500,
        segment: "Conservative",
      },
    },

    fraud: {
      historicalFraudSignals: 1,
      identityMatching: {
        nameMatchAcrossPlatforms: 75,
        emailPhoneConsistency: 80,
        geoLocationMatch: 70,
        overallScore: 75,
      },
      statementManipulation: {
        probability: 8,
        pixelStructureCheck: "Pass",
        fontVariationCheck: "Minor Issues",
        duplicateTemplateCheck: "Pass",
        ocrConsistency: "Minor Issues",
        salaryToUpiRatio: "Normal",
      },
      syntheticIdentity: {
        probability: 12,
        nameDobSimilarity: "Low Similarity Found",
        riskLevel: "Medium",
      },
    },

    transactions: {
      spikeDetector: {
        upiVolumeChange: 25,
        balanceDropAlert: true,
        newMerchantsAdded: 12,
        emiFailures: 0,
        status: "Alert",
      },
      incomeAuthenticity: {
        inflowTimeConsistency: 75,
        salaryToUpiRatio: 0.6,
        status: "Needs Verification",
      },
      utilityPayments: {
        rechargeConsistency: 70,
        electricityConsistency: 65,
        rentConsistency: 75,
        subscriptionConsistency: 60,
        overallScore: 68,
      },
    },

    summary: {
      financialHealthScore: 38,
      maxLoanAmount: 50000,
      probabilityOfDefault: 18.5,
      recommendation: "High Risk - Manual Review",
    },

    scoringHistory: [{ date: "2025-01-10", score: 542, method: "GBM v1.2.3" }],
  },
  {
    id: "5",
    name: "Vikram Gupta",
    phone: "+91-XXXX445678",
    email: "vikram.gupta@email.com",
    persona: "Credit-Experienced",
    currentScore: 765,
    riskBucket: "Low",
    lastUpdated: "2025-01-13",
    dob: "1988-07-20",

    identity: {
      faceMatch: 97.6,
      nameMatch: "Verified",
      address: "Hyderabad, Telangana",
      pan: "XXXX7890V",
      aadhaar: "XXXX7890",
      mobileVerified: true,
      digitalIdentity: {
        deviceAge: 42,
        simAge: 72,
        emailAge: 120,
        overallTrustScore: 90,
        platformConsistency: 92,
        aadhaarPanMatchStability: "Stable",
      },
      lifeStability: {
        jobStability: {
          avgEmploymentDuration: 5.0,
          salaryHikes: 4,
          score: 90,
        },
        residenceStability: {
          yearsAtCurrentAddress: 4,
          landlordVerified: true,
          rentPaymentPattern: "On-time",
          score: 88,
        },
        householdStability: {
          status: "Strong",
          score: 85,
        },
        overallScore: 88,
      },
      socialCapital: {
        regularPeerTransactions: 80,
        professionalNetworkPayments: 88,
        overallScore: 84,
      },
    },

    income: {
      monthlyIncome: 120000,
      incomeStabilityScore: 94,
      accountBalances: [
        { bank: "Axis Savings", balance: 450000 },
        { bank: "HDFC Salary", balance: 250000 },
        { bank: "ICICI Savings", balance: 50000 },
      ],
      totalBalance: 750000,
      transactionValueExcludingP2P: 85000,
      incomeVolatility: {
        stdDeviation: 6000,
        avgIncome: 120000,
        volatilityIndex: 5,
      },
      survivability: {
        totalSavings: 3400000,
        monthlyOutflow: 55000,
        months: 61.8,
      },
      incomeSources: [
        { source: "Salary - Microsoft", amount: 120000, reliability: "Verified", tag: "salary" },
      ],
      expenseCategories: {
        fixedEssential: { amount: 22000, percentage: 40, items: ["EMIs", "Insurance", "Groceries"] },
        variableEssential: { amount: 10000, percentage: 18, items: ["Utilities", "Fuel"] },
        entertainment: { amount: 8000, percentage: 15, items: ["Dining", "OTT", "Movies"] },
        shopping: { amount: 8000, percentage: 15, items: ["Electronics", "Clothing"] },
        lifestyle: { amount: 7000, percentage: 12, items: ["Travel", "Fitness"] },
      },
      salaryRetention: {
        firstWeekBalance: 100000,
        lastWeekBalance: 55000,
        adjustedForInvestments: 30000,
        impulseScore: 22,
      },
    },

    assets: {
      investments: {
        mutualFunds: 800000,
        stocks: 600000,
        corporateBonds: 100000,
        governmentSecurities: 200000,
        nps: 400000,
        epf: 650000,
        ppf: 600000,
        fd: 1500000,
        rd: 100000,
      },
      itrFiled: true,
      totalAssets: 4950000,
    },
    insurance: {
      policies: [
        { type: "Health", provider: "Niva Bupa", premium: 35000, status: "Active" },
        { type: "Life", provider: "Max Life", premium: 55000, status: "Active" },
        { type: "Vehicle", provider: "Bajaj Allianz", premium: 18000, status: "Active" },
      ],
      paymentBehaviour: {
        avgDaysBeforeDue: 7,
        latePaymentsLast6Months: 0,
      },
    },
    liabilities: {
      available: true,
      activeLoans: [
        { type: "Home Loan", outstanding: 5500000, emi: 65000, bank: "Axis" },
        { type: "Personal Loan", outstanding: 150000, emi: 12000, bank: "HDFC" },
      ],
      loanRepaymentHistory: "Excellent",
      creditCardRepaymentHistory: "Excellent",
      creditEnquiries: 3,
      goodDebtVsBadDebt: {
        goodDebt: 5500000,
        badDebt: 150000,
        index: 0.97,
      },
      defaultHistory: "None",
      bnplHistory: {
        active: 0,
        totalUsed: 5,
        repaymentStatus: "All Cleared",
      },
    },
    saturation: {
      emiToIncome: 64.2,
      rentToIncome: 0,
      utilityToIncome: 3.3,
      totalSaturation: 67.5,
      status: "Moderate",
    },

    behaviour: {
      spendingArchetype: {
        type: "Family-centered",
        confidence: 82,
        traits: ["School fees priority", "Medical stability", "Household focused"],
      },
      financialStress: {
        atmWithdrawalTrend: "Stable",
        microUpiPayments: "Low",
        stressLevel: "Low",
        warningSignals: [],
      },
      billPayment: {
        avgDaysBeforeDue: 3,
        behaviour: "High Discipline",
        autoDebitEnabled: true,
        latePaymentsLast6Months: {
          utility: 0,
          recharges: 0,
          rent: 0,
          subscriptions: 1,
        },
        overallScore: 96,
      },
      subscriptions: {
        active: 6,
        latePaymentsLastYear: 1,
        downgradingPatterns: false,
        list: ["Netflix", "Amazon Prime", "Disney+", "Spotify Family", "Gym", "BYJU'S"],
      },
      microCommitment: {
        consistencyScore: 90,
        dailySpendPatterns: ["Coffee - ₹180", "Parking - ₹100", "Metro - ₹80"],
      },
      emotionalPurchasing: {
        lateNightSpending: 8,
        weekendSpending: 30,
        weekdaySpending: 62,
        pattern: "Routine-driven",
      },
      savingsConsistency: {
        sipIncreaseOnHike: true,
        activeSips: 5,
        totalSipValue: 40000,
        sipPaymentConsistency: 98,
        sipWithdrawalTrend: "None",
      },
      moneyPersonalityStability: {
        behaviourChanges: 1,
        stability: "Stable",
      },
      riskAppetite: {
        tradingAppInflows: 20000,
        cryptoActivity: "Minimal",
        lotteryGamingSpends: 0,
        segment: "Moderate",
      },
    },

    fraud: {
      historicalFraudSignals: 0,
      identityMatching: {
        nameMatchAcrossPlatforms: 98,
        emailPhoneConsistency: 100,
        geoLocationMatch: 95,
        overallScore: 98,
      },
      statementManipulation: {
        probability: 1,
        pixelStructureCheck: "Pass",
        fontVariationCheck: "Pass",
        duplicateTemplateCheck: "Pass",
        ocrConsistency: "Pass",
        salaryToUpiRatio: "Normal",
      },
      syntheticIdentity: {
        probability: 0,
        nameDobSimilarity: "No Match in Fraud DB",
        riskLevel: "Very Low",
      },
    },

    transactions: {
      spikeDetector: {
        upiVolumeChange: 3,
        balanceDropAlert: false,
        newMerchantsAdded: 2,
        emiFailures: 0,
        status: "Normal",
      },
      incomeAuthenticity: {
        inflowTimeConsistency: 100,
        salaryToUpiRatio: 1.3,
        status: "Verified",
      },
      utilityPayments: {
        rechargeConsistency: 100,
        electricityConsistency: 100,
        rentConsistency: 100,
        subscriptionConsistency: 98,
        overallScore: 99,
      },
    },

    summary: {
      financialHealthScore: 85,
      maxLoanAmount: 2000000,
      probabilityOfDefault: 2.8,
      recommendation: "Approved",
    },

    scoringHistory: [{ date: "2025-01-13", score: 765, method: "GBM v1.2.3" }],
  },
  {
    id: "6",
    name: "Arjun Mehta",
    phone: "+91-9876556789",
    email: "arjun.mehta@email.com",
    persona: "Credit Invisible",
    currentScore: 0,
    riskBucket: "Unscored",
    lastUpdated: "2025-01-16",
    reportDate: "16 January 2025",
    dob: "1999-04-12",
    age: 25,

    summary: {
      financialHealthScore: 72,
      maxLoanAmount: 300000,
      probabilityOfDefault: 6.5,
      recommendation: "Approved",
      riskGrade: "C",
      proximityToCibil: "700-740 equivalent",
    },

    identity: {
      faceMatch: 96.2,
      nameMatch: "Verified",
      address: "B-42, Sector 62, Noida, Uttar Pradesh - 201301",
      pan: "BXPPM4521M",
      aadhaar: "XXXX-XXXX-4521",
      mobileVerified: true,
      pinCode: "201301",
      pinCodeRisk: "Low Risk",
      
      digitalIdentity: {
        overallTrustScore: 78,
        deviceAge: 24,
        simAge: 36,
        emailAge: 72,
        platformConsistency: 85,
        aadhaarPanMatchStability: "Stable",
        lowAgeFlag: false,
      },
      
      lifeStability: {
        overallScore: 69,
        jobStability: {
          avgEmploymentDuration: 1.5,
          salaryHikes: 1,
          currentEmployer: "Infosys Ltd",
          designation: "Software Engineer",
          score: 62,
        },
        residenceStability: {
          yearsAtCurrentAddress: 2,
          landlordVerified: true,
          rentPaymentPattern: "On-time",
          score: 75,
        },
        householdStability: {
          status: "Moderate",
          score: 70,
        },
      },
      
      socialCapital: {
        level: "Medium",
        regularPeerTransactions: 72,
        professionalNetworkPayments: 68,
        overallScore: 70,
      },
    },

    income: {
      monthlyIncome: 45000,
      monthlyInflow: 48000,
      monthlyOutflow: 28000,
      incomeStabilityScore: 82,
      
      accountBalances: [
        { bank: "HDFC Savings", accountNo: "XXXX1234", balance: 85000 },
        { bank: "Paytm Payments Bank", accountNo: "XXXX5678", balance: 12000 },
      ],
      totalBalance: 97000,
      averageBalance: 97000,
      oneOffTransactionInflation: false,
      transactionValueExcludingP2P: 32000,
      
      incomeVolatility: {
        stdDeviation: 4500,
        avgIncome: 45000,
        volatilityIndex: 10,
      },
      
      survivability: {
        totalSavings: 180000,
        monthlyOutflow: 28000,
        months: 6.4,
        score: 64,
        emergencyFunds: 97000,
      },
      
      incomeSources: [
        { source: "Salary - Infosys Ltd", amount: 45000, reliability: "Verified", tag: "salary" },
      ],
      
      expenseCategories: {
        fixedEssential: { amount: 12000, percentage: 43, items: ["Rent - ₹8,000", "Groceries - ₹4,000"] },
        variableEssential: { amount: 5000, percentage: 18, items: ["Utilities - ₹2,000", "Transport - ₹3,000"] },
        entertainment: { amount: 4000, percentage: 14, items: ["OTT - ₹500", "Dining - ₹3,500"] },
        shopping: { amount: 4000, percentage: 14, items: ["Clothing - ₹2,000", "Gadgets - ₹2,000"] },
        lifestyle: { amount: 3000, percentage: 11, items: ["Gym - ₹1,500", "Events - ₹1,500"] },
      },
      
      salaryRetention: {
        firstWeekBalance: 42000,
        lastWeekBalance: 18000,
        adjustedForInvestments: 8000,
        daysInAccount: 18,
        impulseScore: 38,
        impatienceLevel: "Low",
      },
    },

    assets: {
      investments: {
        mutualFunds: 50000,
        stocks: 25000,
        corporateBonds: 0,
        governmentSecurities: 0,
        nps: 0,
        epf: 80000,
        ppf: 30000,
        fd: 0,
        rd: 15000,
      },
      itrFiled: true,
      itrYear: "FY 2023-24",
      totalAssets: 200000,
    },
    
    insurance: {
      policies: [
        { type: "Health", provider: "Star Health", sumAssured: 500000, premium: 12000, status: "Active" },
      ],
      paymentBehaviour: {
        avgDaysBeforeDue: 3,
        latePaymentsLast6Months: 0,
      },
    },
    
    liabilities: {
      available: false,
      activeLoans: [],
      loanRepaymentHistory: "Not Available",
      creditCardRepaymentHistory: "Not Available",
      creditEnquiries: 0,
      goodDebtVsBadDebt: {
        goodDebt: 0,
        badDebt: 0,
        index: 0,
        productivityOfDebt: "N/A",
        liabilityStrain: "None",
      },
      defaultHistory: "Not Available",
      bnplHistory: {
        active: 0,
        totalUsed: 0,
        repaymentStatus: "Never Used",
      },
    },
    
    saturation: {
      emiToIncome: 0,
      rentToIncome: 17.8,
      utilityToIncome: 4.4,
      totalSaturation: 22.2,
      status: "Low - Excellent Capacity",
    },

    behaviour: {
      spendingArchetype: {
        type: "Disciplined Saver",
        confidence: 75,
        traits: ["Regular savings", "Budget conscious", "Minimal lifestyle spend"],
      },
      
      financialStress: {
        atmWithdrawalTrend: "Stable",
        microUpiPayments: "Low",
        frequentMicroPayments: false,
        stressLevel: "Low",
        warningSignals: [],
      },
      
      billPayment: {
        avgDaysBeforeDue: 2,
        behaviour: "High Discipline",
        autoDebitEnabled: true,
        latePaymentsLast6Months: {
          utility: 0,
          recharges: 0,
          rent: 0,
          subscriptions: 1,
        },
        overallScore: 92,
      },
      
      subscriptions: {
        active: 4,
        latePaymentsLastYear: 1,
        downgradingPatterns: false,
        list: ["Netflix - ₹199/mo", "Spotify - ₹119/mo", "Cult.fit - ₹1,500/mo", "Zerodha - ₹0"],
      },
      
      microCommitment: {
        consistencyScore: 82,
        dailySpendPatterns: ["Coffee - ₹80", "Metro - ₹60", "Lunch - ₹120"],
      },
      
      emotionalPurchasing: {
        level: "Low",
        lateNightSpending: 12,
        weekendSpending: 35,
        weekdaySpending: 53,
        pattern: "Routine-driven",
      },
      
      savingsConsistency: {
        sipIncreaseOnHike: true,
        activeSips: 2,
        totalSipValue: 8000,
        sipPaymentConsistency: 100,
        sipWithdrawalTrend: "None",
        consistentPayments: true,
      },
      
      moneyPersonalityStability: {
        behaviourChanges: 1,
        stability: "Stable",
      },
      
      riskAppetite: {
        tradingAppInflows: 5000,
        cryptoActivity: "Minimal",
        lotteryGamingSpends: 0,
        segment: "Conservative",
      },
    },

    fraud: {
      historicalFraudSignals: 0,
      pinCodeRisk: "Low Risk",
      
      identityMatching: {
        nameMatchAcrossPlatforms: 95,
        emailPhoneConsistency: 98,
        geoLocationMatch: 92,
        socialMediaMatch: 94,
        overallScore: 95,
      },
      
      statementManipulation: {
        probability: 1,
        pixelStructureCheck: "Pass",
        fontVariationCheck: "Pass",
        duplicateTemplateCheck: "Pass",
        ocrConsistency: "Pass",
        salaryToUpiRatio: "Normal",
      },
      
      syntheticIdentity: {
        probability: 2,
        nameDobSimilarity: "No Match in Fraud DB",
        riskLevel: "Very Low",
      },
    },

    transactions: {
      spikeDetector: {
        upiVolumeChange: 5,
        balanceDropAlert: false,
        newMerchantsAdded: 3,
        emiFailures: 0,
        status: "Normal",
      },
      
      incomeAuthenticity: {
        inflowTimeConsistency: 98,
        salaryToUpiRatio: 1.4,
        status: "Verified",
      },
      
      utilityPayments: {
        rechargeConsistency: 100,
        electricityConsistency: 95,
        rentConsistency: 100,
        subscriptionConsistency: 92,
        overallScore: 97,
      },
    },

    scoringHistory: [{ date: "2025-01-16", score: 72, method: "Alt Data GBM v1.2.3" }],
  },
]

export const mockPortfolioStats = {
  totalUsersScored: 1247,
  averageScore: 704,
  riskDistribution: {
    low: { count: 820, percentage: 65.75 },
    medium: { count: 310, percentage: 24.86 },
    high: { count: 117, percentage: 9.39 },
  },
  personaDistribution: {
    Salaried: { count: 620, percentage: 49.68 },
    "Credit-Experienced": { count: 380, percentage: 30.47 },
    "Mass Affluent": { count: 150, percentage: 12.03 },
    Gig: { count: 75, percentage: 6.01 },
    NTC: { count: 22, percentage: 1.76 },
  },
  scoreDistribution: [
    { range: "300-400", count: 8 },
    { range: "400-500", count: 32 },
    { range: "500-600", count: 95 },
    { range: "600-700", count: 285 },
    { range: "700-800", count: 615 },
    { range: "800-900", count: 212 },
  ],
  recentScoringEvents: [
    {
      id: "e1",
      consumerId: "1",
      consumerName: "Rajesh Kumar",
      timestamp: "2025-01-15 14:30",
      score: 745,
      riskBucket: "Low",
      action: "Scored",
    },
    {
      id: "e2",
      consumerId: "2",
      consumerName: "Priya Sharma",
      timestamp: "2025-01-15 13:45",
      score: 658,
      riskBucket: "Medium",
      action: "Re-scored",
    },
    {
      id: "e3",
      consumerId: "5",
      consumerName: "Vikram Gupta",
      timestamp: "2025-01-14 11:20",
      score: 765,
      riskBucket: "Low",
      action: "Scored",
    },
    {
      id: "e4",
      consumerId: "3",
      consumerName: "Amit Patel",
      timestamp: "2025-01-14 09:15",
      score: 812,
      riskBucket: "Low",
      action: "Scored",
    },
    {
      id: "e5",
      consumerId: "4",
      consumerName: "Neha Singh",
      timestamp: "2025-01-10 16:00",
      score: 542,
      riskBucket: "High",
      action: "Alert: High Risk",
    },
  ],
  averageScoreTrend: [
    { date: "2024-12-16", avg: 698 },
    { date: "2024-12-23", avg: 700 },
    { date: "2024-12-30", avg: 701 },
    { date: "2025-01-06", avg: 702 },
    { date: "2025-01-13", avg: 704 },
  ],
  defaultProbabilityByPersona: [
    { persona: "NTC", defaultProb: 0.185 },
    { persona: "Gig", defaultProb: 0.128 },
    { persona: "Salaried", defaultProb: 0.042 },
    { persona: "Credit-Experienced", defaultProb: 0.035 },
    { persona: "Mass Affluent", defaultProb: 0.018 },
  ],
}

export const featureImportances = [
  { feature: "Income Stability Score", importance: 18.5 },
  { feature: "Average Balance", importance: 16.2 },
  { feature: "EMI Repayment Ratio", importance: 14.8 },
  { feature: "Face Match %", importance: 12.3 },
  { feature: "Budgeting Score", importance: 10.5 },
  { feature: "Recurring Payment Discipline", importance: 9.2 },
  { feature: "Utility Bill Consistency", importance: 7.8 },
  { feature: "SIP Consistency", importance: 6.5 },
  { feature: "Device Anomalies", importance: 2.1 },
  { feature: "Geo Anomalies", importance: 2.0 },
]

export const personaWeights = {
  NTC: {
    identity: 28,
    income: 22,
    assets: 12,
    behaviour: 18,
    transactions: 12,
    fraud: 8,
    family: 0,
  },
  Gig: {
    identity: 20,
    income: 25,
    assets: 15,
    behaviour: 15,
    transactions: 15,
    fraud: 8,
    family: 2,
  },
  Salaried: {
    identity: 15,
    income: 20,
    assets: 18,
    behaviour: 15,
    transactions: 15,
    fraud: 10,
    family: 7,
  },
  "Credit-Experienced": {
    identity: 12,
    income: 18,
    assets: 22,
    behaviour: 18,
    transactions: 15,
    fraud: 10,
    family: 5,
  },
  "Mass Affluent": {
    identity: 10,
    income: 15,
    assets: 30,
    behaviour: 20,
    transactions: 12,
    fraud: 8,
    family: 5,
  },
}
