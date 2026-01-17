"""
Consumer Credit Scoring - Constants and Configurations
======================================================

Author: ML Engineering Team
Version: 1.0.0
"""

# Credit score range
SCORE_RANGE = {
    'min': 0,
    'max': 100,
    'default': 50
}

# Risk tiers for consumers
CONSUMER_RISK_TIERS = {
    'excellent': {'min': 80, 'max': 100, 'label': 'Excellent'},
    'good': {'min': 65, 'max': 79, 'label': 'Good'},
    'fair': {'min': 50, 'max': 64, 'label': 'Fair'},
    'poor': {'min': 35, 'max': 49, 'label': 'Poor'},
    'very_poor': {'min': 0, 'max': 34, 'label': 'Very Poor'}
}

# Education levels
EDUCATION_LEVELS = [
    'no_formal_education',
    'primary_school',
    'high_school',
    'diploma',
    'undergraduate',
    'postgraduate',
    'phd'
]

# Employment types
EMPLOYMENT_TYPES = [
    'unemployed',
    'student',
    'self_employed',
    'salaried_private',
    'salaried_government',
    'business_owner',
    'freelancer',
    'retired'
]

# Income sources
INCOME_SOURCES = [
    'salary',
    'business',
    'freelance',
    'investments',
    'rental',
    'pension',
    'family_support',
    'other'
]

# Spending personalities (from image)
SPENDING_PERSONALITIES = [
    'conservative_spender',
    'planned_spender',
    'impulsive_spender',
    'luxury_seeker',
    'value_hunter',
    'balanced_spender'
]

# Risk appetite levels
RISK_APPETITE_LEVELS = [
    'very_low',
    'low',
    'moderate',
    'high',
    'very_high'
]

# Insurance types
INSURANCE_TYPES = [
    'life_insurance',
    'health_insurance',
    'vehicle_insurance',
    'property_insurance',
    'term_insurance'
]

# Default probability thresholds
DEFAULT_THRESHOLDS = {
    'very_low_risk': 0.02,    # 0-2% default probability
    'low_risk': 0.05,         # 2-5%
    'medium_risk': 0.10,      # 5-10%
    'high_risk': 0.20,        # 10-20%
    'very_high_risk': 1.0     # 20%+
}

# Income stability categories
INCOME_STABILITY_CATEGORIES = {
    'very_stable': {'cv': 0.1, 'label': 'Very Stable'},
    'stable': {'cv': 0.2, 'label': 'Stable'},
    'moderate': {'cv': 0.3, 'label': 'Moderate'},
    'unstable': {'cv': 0.5, 'label': 'Unstable'},
    'very_unstable': {'cv': 1.0, 'label': 'Very Unstable'}
}

# Bill payment categories
BILL_PAYMENT_CATEGORIES = {
    'excellent': {'on_time_ratio': 0.95, 'label': 'Excellent'},
    'good': {'on_time_ratio': 0.85, 'label': 'Good'},
    'fair': {'on_time_ratio': 0.70, 'label': 'Fair'},
    'poor': {'on_time_ratio': 0.50, 'label': 'Poor'},
    'very_poor': {'on_time_ratio': 0.0, 'label': 'Very Poor'}
}

# Pin code risk categories (metro vs tier-2 vs rural)
PIN_CODE_RISK = {
    'metro': {'risk_score': 0.9, 'cities': ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune']},
    'tier_1': {'risk_score': 0.8, 'cities': ['Ahmedabad', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur']},
    'tier_2': {'risk_score': 0.6, 'cities': ['Bhopal', 'Indore', 'Vadodara', 'Coimbatore']},
    'tier_3': {'risk_score': 0.4, 'cities': ['Tier 3 cities']},
    'rural': {'risk_score': 0.2, 'cities': ['Rural areas']}
}

# Age groups
AGE_GROUPS = {
    'gen_z': {'min': 18, 'max': 25, 'label': 'Gen Z'},
    'young_millennial': {'min': 26, 'max': 32, 'label': 'Young Millennial'},
    'millennial': {'min': 33, 'max': 40, 'label': 'Millennial'},
    'gen_x': {'min': 41, 'max': 55, 'label': 'Gen X'},
    'boomer': {'min': 56, 'max': 75, 'label': 'Boomer'},
    'silent_gen': {'min': 76, 'max': 100, 'label': 'Silent Generation'}
}

# Loan amount ranges (for future use)
LOAN_AMOUNT_RANGES = {
    'micro': {'min': 10000, 'max': 50000},
    'small': {'min': 50000, 'max': 200000},
    'medium': {'min': 200000, 'max': 500000},
    'large': {'min': 500000, 'max': 1000000}
}


