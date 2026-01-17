"""Feature configuration for MSME credit scoring"""

# Target column
TARGET_COLUMN = 'default_90dpd'

# Categorical features
CATEGORICAL_FEATURES = [
    'industry_sector',
    'business_type',
    'business_model',
    'gst_status',
    'bank_account_type',
    'primary_platform'
]

# Numerical features organized by category
REVENUE_FEATURES = [
    'avg_monthly_revenue',
    'revenue_growth_6m',
    'revenue_volatility',
    'avg_transaction_value',
    'daily_transaction_count'
]

BANKING_FEATURES = [
    'avg_bank_balance',
    'banking_relationship_months',
    'monthly_credits',
    'monthly_debits',
    'bounce_rate',
    'maintained_minimum_balance_ratio'
]

BUSINESS_FEATURES = [
    'business_age_months',
    'employee_count',
    'customer_count',
    'repeat_customer_ratio',
    'inventory_turnover_ratio'
]

CREDIT_FEATURES = [
    'existing_loans_count',
    'total_existing_loan_amount',
    'debt_service_coverage_ratio',
    'credit_utilization_ratio'
]

COMPLIANCE_FEATURES = [
    'gst_filing_regularity',
    'gst_filing_ontime_ratio',
    'itr_filed',
    'tax_payment_regularity',
    'outstanding_taxes_amount',
    'legal_proceedings_flag'
]

DIGITAL_FEATURES = [
    'digital_payment_adoption',
    'online_presence_score',
    'platform_integration_count',
    'api_integration_active'
]

FRAUD_FEATURES = [
    'fraud_flag',
    'circular_transaction_flag',
    'address_mismatch_flag',
    'fraud_transaction_signals'
]

OWNER_FEATURES = [
    'owner_age',
    'owner_cibil_score',
    'owner_pan_verified',
    'owner_aadhaar_verified',
    'owner_bank_verified'
]

# All numerical features combined
NUMERICAL_FEATURES = (
    REVENUE_FEATURES +
    BANKING_FEATURES +
    BUSINESS_FEATURES +
    CREDIT_FEATURES +
    COMPLIANCE_FEATURES +
    DIGITAL_FEATURES +
    OWNER_FEATURES
)

# All features
ALL_FEATURES = CATEGORICAL_FEATURES + NUMERICAL_FEATURES

# Feature groups for analysis and interpretation
FEATURE_GROUPS = {
    'Revenue & Performance': REVENUE_FEATURES,
    'Banking & Cash Flow': BANKING_FEATURES,
    'Business Fundamentals': BUSINESS_FEATURES,
    'Credit History': CREDIT_FEATURES,
    'Compliance & Tax': COMPLIANCE_FEATURES,
    'Digital Footprint': DIGITAL_FEATURES,
    'Fraud & Risk': FRAUD_FEATURES,
    'Owner Profile': OWNER_FEATURES
}

# Feature importance weights (for manual scoring if needed)
FEATURE_WEIGHTS = {
    'Revenue & Performance': 0.25,
    'Banking & Cash Flow': 0.20,
    'Business Fundamentals': 0.15,
    'Credit History': 0.15,
    'Compliance & Tax': 0.10,
    'Digital Footprint': 0.05,
    'Fraud & Risk': 0.05,
    'Owner Profile': 0.05
}

