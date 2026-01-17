# PowerShell script to test Nishil Parekh's credit score

$json = @"
{
  "features": {
    "name_dob_verified": 1,
    "pan_verified": 1,
    "aadhaar_verified": 1,
    "phone_verified": 1,
    "phone_age_months": 36,
    "email_verified": 1,
    "email_age_months": 48,
    "age": 23,
    "education_level": 3,
    "marital_status": "single",
    "dependents_count": 0,
    "employment_type": "salaried_private",
    "employment_tenure_months": 18,
    "job_changes_3y": 1,
    "monthly_income": 45000,
    "monthly_income_stability": 0.80,
    "income_cv": 0.15,
    "income_source_verification": 1,
    "employment_history_score": 70,
    "total_financial_assets": 180000,
    "liquid_assets": 85000,
    "property_owned": 0,
    "vehicle_owned": 0,
    "existing_loans_count": 0,
    "total_debt_outstanding": 0,
    "debt_to_income_ratio": 0,
    "emi_to_income_ratio": 0,
    "credit_history_months": 24,
    "credit_cards_count": 1,
    "credit_utilization_ratio": 0.30,
    "total_credit_limit": 100000,
    "loan_defaults_ever": 0,
    "max_dpd_12m": 0,
    "loan_inquiries_6m": 0,
    "loan_approvals_6m": 0,
    "primary_bank_vintage_months": 60,
    "avg_bank_balance_6m": 75000,
    "min_bank_balance_6m": 25000,
    "bank_balance_volatility": 0.20,
    "avg_monthly_credits": 48000,
    "avg_monthly_debits": 38000,
    "bounce_rate_12m": 0,
    "inflow_consistency_cv": 0.18,
    "avg_monthly_spending": 35000,
    "spending_to_income_ratio": 0.78,
    "essential_spending_ratio": 0.65,
    "luxury_spending_ratio": 0.10,
    "gambling_spending_flag": 0,
    "impulse_purchase_ratio": 0.15,
    "spending_discipline_index": 72,
    "savings_rate": 0.22,
    "utility_payment_ontime_ratio": 0.95,
    "bill_payment_ontime_ratio": 0.92,
    "bill_payment_discipline": 85,
    "rent_to_income_ratio": 0.25,
    "avg_transaction_amount": 1250,
    "upi_transactions_monthly": 65,
    "digital_payment_ratio": 0.88,
    "late_night_transaction_ratio": 0.08,
    "weekend_transaction_ratio": 0.28,
    "identity_matching": 95,
    "bank_statement_manipulation": 0.02,
    "synthetic_id_risk": 0.05,
    "transaction_pattern_anomaly": 0.10,
    "fraud_flag_count": 0,
    "survivability_months": 2.4,
    "emergency_fund_ratio": 0.5,
    "financial_stress_score": 35
  },
  "include_explanation": true
}
"@

Write-Host "`n===================================================================="
Write-Host "Testing Credit Score API for: NISHIL PAREKH"
Write-Host "PAN: FVMPP3211E | Aadhaar: 552678882545 | DOB: 29-04-2002"
Write-Host "===================================================================="

# Test API using Invoke-RestMethod
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8001/api/consumer/score" `
        -Method POST `
        -Body $json `
        -ContentType "application/json" `
        -Headers @{"Authorization" = "Bearer dev_token_12345"}
    
    Write-Host "`n[SUCCESS] Credit Score Generated!" -ForegroundColor Green
    Write-Host "`nCredit Score: $($response.score)/100" -ForegroundColor Cyan
    Write-Host "Risk Tier: $($response.risk_tier)" -ForegroundColor $(if($response.score -ge 70){'Green'}elseif($response.score -ge 50){'Yellow'}else{'Red'})
    Write-Host "Default Probability: $([math]::Round($response.default_probability * 100, 2))%" -ForegroundColor Yellow
    Write-Host "Model Version: $($response.model_version)"
    Write-Host "Timestamp: $($response.timestamp)"
    
    if ($response.feature_importance) {
        Write-Host "`nTop Features Influencing Score:" -ForegroundColor Magenta
        foreach ($feature in $response.feature_importance) {
            Write-Host "  - $($feature.feature): $([math]::Round($feature.importance, 2))"
        }
    }
    
    Write-Host "`nFull Response:"
    $response | ConvertTo-Json -Depth 10
    
} catch {
    Write-Host "`n[ERROR] API Request Failed!" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host "`nMake sure API is running on port 8001"
    Write-Host "Start API with: python api.py --port 8001"
}

Write-Host "`n===================================================================="

