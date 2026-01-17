"""Constants and business rules configuration"""

# Score range configuration
SCORE_RANGE = {
    'min_score': 300,
    'max_score': 900,
    'default_score': 500
}

# Risk tiers based on score
RISK_TIERS = {
    'Excellent': {'min': 800, 'max': 900, 'color': '#10b981'},
    'Very Good': {'min': 750, 'max': 799, 'color': '#34d399'},
    'Good': {'min': 700, 'max': 749, 'color': '#6ee7b7'},
    'Fair': {'min': 650, 'max': 699, 'color': '#fbbf24'},
    'Average': {'min': 600, 'max': 649, 'color': '#f59e0b'},
    'Below Average': {'min': 550, 'max': 599, 'color': '#f97316'},
    'Poor': {'min': 500, 'max': 549, 'color': '#ef4444'},
    'Very Poor': {'min': 300, 'max': 499, 'color': '#dc2626'}
}

# Default probability thresholds
DEFAULT_THRESHOLDS = {
    'very_low': 0.02,      # Score 750+
    'low': 0.05,           # Score 650-749
    'medium': 0.12,        # Score 550-649
    'high': 0.25,          # Score 450-549
    'very_high': 0.40,     # Score 350-449
    'critical': 1.00       # Score <350
}

# Business age categories
BUSINESS_AGE_CATEGORIES = {
    'New': {'min_months': 0, 'max_months': 12},
    'Early Stage': {'min_months': 13, 'max_months': 36},
    'Growing': {'min_months': 37, 'max_months': 60},
    'Established': {'min_months': 61, 'max_months': 120},
    'Mature': {'min_months': 121, 'max_months': float('inf')}
}

# Industry sectors
INDUSTRY_SECTORS = [
    'Retail & FMCG',
    'Food & Beverage',
    'Fashion & Apparel',
    'Electronics',
    'Healthcare & Pharmacy',
    'Automotive',
    'Home & Furniture',
    'Beauty & Personal Care',
    'Services',
    'Manufacturing',
    'Agriculture',
    'Technology',
    'Education',
    'Real Estate',
    'Other'
]

# Business types
BUSINESS_TYPES = [
    'Proprietorship',
    'Partnership',
    'Private Limited',
    'LLP',
    'Public Limited',
    'One Person Company'
]

# Business models
BUSINESS_MODELS = [
    'B2C',
    'B2B',
    'B2B2C',
    'Marketplace',
    'Direct-to-Consumer',
    'Franchise',
    'Hybrid'
]

# GST status categories
GST_STATUS = [
    'Regular',
    'Composition',
    'Not Registered',
    'Cancelled',
    'Suspended'
]

# Data split configuration
DATA_SPLIT_CONFIG = {
    'train_ratio': 0.70,
    'val_ratio': 0.15,
    'test_ratio': 0.15,
    'random_state': 42,
    'stratify': True
}

# Probability to score mapping anchor points
SCORE_MAPPING_ANCHORS = [
    (0.00, 900),
    (0.02, 750),
    (0.05, 650),
    (0.12, 550),
    (0.25, 450),
    (0.40, 400),
    (0.60, 350),
    (1.00, 300)
]

# Calibration configuration
CALIBRATION_CONFIG = {
    'method': 'isotonic',
    'min_samples': 100,
    'out_of_bounds': 'clip'
}

