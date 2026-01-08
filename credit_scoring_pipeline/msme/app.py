"""
MSME Credit Scoring Pipeline - FastAPI Application
===================================================

REST API endpoints for MSME credit scoring:
1. /api/score - Score an MSME business
2. /api/explain - Get detailed explanation
3. /api/features/{business_id} - Get business features
4. /api/health - Health check
5. /api/segments - List business segments

Author: ML Engineering Team
Version: 1.0.0
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict
import uvicorn

from score import (
    MSMECreditScorer, BUSINESS_SEGMENT_WEIGHTS, DEFAULT_MSME_CATEGORY_WEIGHTS,
    compute_msme_segment_subscore, msme_prob_to_score
)


# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL_PATH = os.environ.get('MODEL_PATH', 'msme_model_artifacts/msme_credit_scoring_model.joblib')
PREPROCESSOR_PATH = os.environ.get('PREPROCESSOR_PATH', 'msme_model_artifacts/msme_preprocessor.joblib')
CONFIG_PATH = os.environ.get('CONFIG_PATH', 'feature_config.json')

API_VERSION = "1.0.0"
API_TITLE = "MSME Credit Scoring API"
API_DESCRIPTION = """
MSME Credit Scoring API for predicting 90-DPD default probability.

## Business Segments
- **micro_new**: Micro Enterprise - New (<2 years)
- **micro_established**: Micro Enterprise - Established (2+ years)
- **small_trading**: Small Enterprise - Trading
- **small_manufacturing**: Small Enterprise - Manufacturing
- **small_services**: Small Enterprise - Services
- **medium_enterprise**: Medium Enterprise

## Key Parameters (with weights)
- Weekly GTV: 7
- On-time repayment ratio: 4
- Weekly Inflow-outflow ratio: 4
- Bounced cheques: 3
- Cash buffer days: 3
- GST filing regularity: 1.5
"""

VALID_TOKENS = {
    "msme_dev_token_12345": {"user": "dev_user", "role": "developer"},
    "msme_prod_token_67890": {"user": "prod_service", "role": "service"},
    "msme_test_token_abcde": {"user": "test_user", "role": "tester"}
}


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class MSMEFeatureInput(BaseModel):
    """Input model for MSME features"""
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "business_age_years": 3.5,
            "weekly_gtv": 2500000,
            "overdraft_repayment_ontime_ratio": 0.92,
            "gst_filing_regularity": 0.95
        }
    })
    
    # Business Identity
    legal_entity_type: Optional[str] = None
    business_age_years: Optional[float] = Field(None, ge=0)
    business_address_verified: Optional[int] = Field(None, ge=0, le=1)
    geolocation_verified: Optional[int] = Field(None, ge=0, le=1)
    industry_code: Optional[str] = None
    industry_risk_score: Optional[float] = Field(None, ge=0, le=1)
    num_business_locations: Optional[int] = Field(None, ge=1)
    employees_count: Optional[int] = Field(None, ge=0)
    gstin_verified: Optional[int] = Field(None, ge=0, le=1)
    pan_verified: Optional[int] = Field(None, ge=0, le=1)
    msme_registered: Optional[int] = Field(None, ge=0, le=1)
    msme_category: Optional[str] = None
    business_structure: Optional[str] = None
    licenses_certificates_score: Optional[float] = Field(None, ge=0, le=1)
    
    # Revenue & Performance
    weekly_gtv: Optional[float] = Field(None, ge=0)
    monthly_gtv: Optional[float] = Field(None, ge=0)
    transaction_count_daily: Optional[int] = Field(None, ge=0)
    avg_transaction_value: Optional[float] = Field(None, ge=0)
    revenue_concentration_score: Optional[float] = Field(None, ge=0, le=1)
    peak_day_dependency: Optional[float] = Field(None, ge=0, le=1)
    revenue_growth_rate_mom: Optional[float] = None
    revenue_growth_rate_qoq: Optional[float] = None
    profit_margin: Optional[float] = None
    profit_margin_trend: Optional[float] = None
    inventory_turnover_ratio: Optional[float] = Field(None, ge=0)
    total_assets_value: Optional[float] = Field(None, ge=0)
    operational_leverage_ratio: Optional[float] = Field(None, ge=0)
    
    # Cash Flow & Banking
    avg_bank_balance: Optional[float] = Field(None, ge=0)
    bank_balance_trend: Optional[float] = None
    weekly_inflow_outflow_ratio: Optional[float] = Field(None, ge=0)
    overdraft_days_count: Optional[int] = Field(None, ge=0)
    overdraft_amount_avg: Optional[float] = Field(None, ge=0)
    cash_buffer_days: Optional[float] = Field(None, ge=0)
    avg_daily_closing_balance: Optional[float] = Field(None, ge=0)
    cash_balance_std_dev: Optional[float] = Field(None, ge=0)
    negative_balance_days: Optional[int] = Field(None, ge=0)
    daily_min_balance_pattern: Optional[float] = Field(None, ge=0)
    consistent_deposits_score: Optional[float] = Field(None, ge=0, le=1)
    cashflow_regularity_score: Optional[float] = Field(None, ge=0, le=1)
    receivables_aging_days: Optional[float] = Field(None, ge=0)
    payables_aging_days: Optional[float] = Field(None, ge=0)
    
    # Credit & Repayment
    bounced_cheques_count: Optional[int] = Field(None, ge=0)
    bounced_cheques_rate: Optional[float] = Field(None, ge=0, le=1)
    historical_loan_utilization: Optional[float] = Field(None, ge=0, le=1)
    overdraft_repayment_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    previous_defaults_count: Optional[int] = Field(None, ge=0)
    previous_writeoffs_count: Optional[int] = Field(None, ge=0)
    current_loans_outstanding: Optional[int] = Field(None, ge=0)
    total_debt_amount: Optional[float] = Field(None, ge=0)
    utility_payment_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    utility_payment_days_before_due: Optional[float] = None
    mobile_recharge_regularity: Optional[float] = Field(None, ge=0, le=1)
    mobile_recharge_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    rent_payment_regularity: Optional[float] = Field(None, ge=0, le=1)
    rent_payment_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    supplier_payment_regularity: Optional[float] = Field(None, ge=0, le=1)
    supplier_payment_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    
    # Compliance & Taxation
    gst_filing_regularity: Optional[float] = Field(None, ge=0, le=1)
    gst_filing_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    gst_vs_platform_sales_mismatch: Optional[float] = Field(None, ge=0, le=1)
    outstanding_taxes_amount: Optional[float] = Field(None, ge=0)
    outstanding_dues_flag: Optional[int] = Field(None, ge=0, le=1)
    itr_filed: Optional[int] = Field(None, ge=0, le=1)
    itr_income_declared: Optional[float] = Field(None, ge=0)
    gst_r1_vs_itr_mismatch: Optional[float] = Field(None, ge=0, le=1)
    tax_payment_regularity: Optional[float] = Field(None, ge=0, le=1)
    tax_payment_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    refund_chargeback_rate: Optional[float] = Field(None, ge=0, le=1)
    
    # Fraud & Verification
    kyc_completion_score: Optional[float] = Field(None, ge=0, le=1)
    kyc_attempts_count: Optional[int] = Field(None, ge=1)
    device_consistency_score: Optional[float] = Field(None, ge=0, le=1)
    ip_stability_score: Optional[float] = Field(None, ge=0, le=1)
    pan_address_bank_mismatch: Optional[int] = Field(None, ge=0, le=1)
    image_ocr_verified: Optional[int] = Field(None, ge=0, le=1)
    shop_image_verified: Optional[int] = Field(None, ge=0, le=1)
    reporting_error_rate: Optional[float] = Field(None, ge=0, le=1)
    incoming_funds_verified: Optional[float] = Field(None, ge=0, le=1)
    insurance_coverage_score: Optional[float] = Field(None, ge=0, le=1)
    insurance_premium_paid_ratio: Optional[float] = Field(None, ge=0, le=1)
    
    # External Signals
    local_economic_health_score: Optional[float] = Field(None, ge=0, le=1)
    customer_concentration_risk: Optional[float] = Field(None, ge=0, le=1)
    legal_proceedings_flag: Optional[int] = Field(None, ge=0, le=1)
    legal_disputes_count: Optional[int] = Field(None, ge=0)
    social_media_presence_score: Optional[float] = Field(None, ge=0, le=1)
    social_media_sentiment_score: Optional[float] = Field(None, ge=0, le=1)
    online_reviews_score: Optional[float] = Field(None, ge=0, le=5)


class MSMEScoreRequest(BaseModel):
    """Request model for scoring"""
    features: MSMEFeatureInput
    business_segment: Optional[str] = Field("micro_established", description="Business segment")
    alpha: Optional[float] = Field(0.7, ge=0, le=1, description="GBM weight")
    include_explanation: Optional[bool] = Field(True, description="Include SHAP explanation")


class MSMEScoreResponse(BaseModel):
    """Response model for scoring"""
    score: int = Field(..., ge=300, le=900)
    prob_default_90dpd: float = Field(..., ge=0, le=1)
    risk_category: str
    recommended_decision: str
    model_version: str
    business_segment: str
    component_scores: Dict[str, float]
    category_contributions: Dict[str, float]
    explanation: Optional[Dict] = None
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_version: str
    timestamp: str


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

scorer: Optional[MSMECreditScorer] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    global scorer
    
    print("=" * 60)
    print("MSME CREDIT SCORING API STARTUP")
    print("=" * 60)
    
    model_path = MODEL_PATH if os.path.exists(MODEL_PATH) else None
    preprocessor_path = PREPROCESSOR_PATH if os.path.exists(PREPROCESSOR_PATH) else None
    config_path = CONFIG_PATH if os.path.exists(CONFIG_PATH) else None
    
    scorer = MSMECreditScorer(
        model_path=model_path,
        preprocessor_path=preprocessor_path,
        config_path=config_path,
        alpha=0.7
    )
    
    if model_path:
        print(f"Model loaded: {model_path}")
        print(f"Model version: {scorer.model_version}")
    else:
        print("WARNING: Model not found. Running in segment-only mode.")
    
    print("API ready!")
    
    yield
    
    print("Shutting down MSME API...")


app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ============================================================================
# AUTHENTICATION
# ============================================================================

async def verify_token(authorization: str = Header(None)) -> Dict:
    """Verify bearer token"""
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization required")
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = parts[1]
    if token not in VALID_TOKENS:
        raise HTTPException(status_code=403, detail="Invalid token")
    
    return VALID_TOKENS[token]


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=scorer is not None and scorer.model is not None,
        model_version=scorer.model_version if scorer else "unknown",
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/api/segments", tags=["Configuration"])
async def list_segments(auth: Dict = Depends(verify_token)):
    """List available business segments"""
    segments = {}
    for key, config in BUSINESS_SEGMENT_WEIGHTS.items():
        segments[key] = {
            "name": config['name'],
            "description": config['description'],
            "category_weights": config['category_weights']
        }
    
    return {
        "segments": segments,
        "default": "micro_established"
    }


@app.get("/api/categories", tags=["Configuration"])
async def list_categories(auth: Dict = Depends(verify_token)):
    """List scoring categories"""
    return {
        "categories": DEFAULT_MSME_CATEGORY_WEIGHTS,
        "description": {
            "A_business_identity": "Business Identity & Registration (10%)",
            "B_revenue_performance": "Revenue & Business Performance (20%)",
            "C_cashflow_banking": "Cash Flow & Banking (25%)",
            "D_credit_repayment": "Credit & Repayment Behavior (22%)",
            "E_compliance_taxation": "Compliance & Taxation (12%)",
            "F_fraud_verification": "Fraud & Verification (7%)",
            "G_external_signals": "External Signals (4%)"
        }
    }


@app.post("/api/score", response_model=MSMEScoreResponse, tags=["Scoring"])
async def score_business(
    request: MSMEScoreRequest,
    auth: Dict = Depends(verify_token)
):
    """
    Score an MSME business.
    
    ## Key Parameters (with weights from specification)
    - **weekly_gtv**: Weekly Gross Transaction Value (weight: 7)
    - **overdraft_repayment_ontime_ratio**: On-time repayment ratio (weight: 4)
    - **weekly_inflow_outflow_ratio**: Cash flow ratio (weight: 4)
    - **bounced_cheques_count**: Bounced cheques (weight: 3)
    - **cash_buffer_days**: Cash buffer days (weight: 3)
    - **gst_filing_regularity**: GST compliance (weight: 1.5)
    
    ## Business Segments
    - micro_new, micro_established, small_trading, small_manufacturing, small_services, medium_enterprise
    """
    if scorer is None:
        raise HTTPException(status_code=503, detail="Scorer not initialized")
    
    if request.business_segment not in BUSINESS_SEGMENT_WEIGHTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid segment. Must be one of: {list(BUSINESS_SEGMENT_WEIGHTS.keys())}"
        )
    
    features_dict = {k: v for k, v in request.features.model_dump().items() if v is not None}
    
    if not features_dict:
        raise HTTPException(status_code=400, detail="At least one feature required")
    
    try:
        result = scorer.score_business(
            features=features_dict,
            segment=request.business_segment,
            alpha=request.alpha,
            include_explanation=request.include_explanation
        )
        
        return MSMEScoreResponse(
            score=result['score'],
            prob_default_90dpd=result['prob_default_90dpd'],
            risk_category=result['risk_category'],
            recommended_decision=result['recommended_decision'],
            model_version=result['model_version'],
            business_segment=result['business_segment'],
            component_scores=result['component_scores'],
            category_contributions=result['category_contributions'],
            explanation=result.get('explanation'),
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring error: {str(e)}")


@app.post("/api/explain", tags=["Explainability"])
async def explain_score(
    request: MSMEScoreRequest,
    auth: Dict = Depends(verify_token)
):
    """Get detailed explanation for MSME score"""
    if scorer is None:
        raise HTTPException(status_code=503, detail="Scorer not initialized")
    
    features_dict = {k: v for k, v in request.features.model_dump().items() if v is not None}
    
    try:
        result = scorer.score_business(
            features=features_dict,
            segment=request.business_segment,
            include_explanation=True
        )
        
        explanation = result.get('explanation', {})
        
        return {
            "score": result['score'],
            "risk_category": result['risk_category'],
            "recommended_decision": result['recommended_decision'],
            "top_positive_features": explanation.get('top_positive_features', []),
            "top_negative_features": explanation.get('top_negative_features', []),
            "category_contributions": result['category_contributions'],
            "segment_details": {
                "name": result['business_segment'],
                "weights": BUSINESS_SEGMENT_WEIGHTS.get(request.business_segment, {}).get('category_weights', {})
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explanation error: {str(e)}")


@app.get("/api/features/{business_id}", tags=["Features"])
async def get_business_features(
    business_id: str,
    auth: Dict = Depends(verify_token)
):
    """Get features for a business (stub endpoint)"""
    # Stub - implement database lookup in production
    return {
        "business_id": business_id,
        "features": {
            "business_age_years": 3.5,
            "weekly_gtv": 2500000,
            "overdraft_repayment_ontime_ratio": 0.92,
            "gst_filing_regularity": 0.95,
            "bounced_cheques_count": 1
        },
        "business_segment": "small_trading",
        "last_updated": datetime.utcnow().isoformat(),
        "note": "Stub data - implement database in production"
    }


@app.get("/api/model/info", tags=["System"])
async def get_model_info(auth: Dict = Depends(verify_token)):
    """Get model information"""
    return {
        "model_version": scorer.model_version if scorer else "unknown",
        "api_version": API_VERSION,
        "available_segments": list(BUSINESS_SEGMENT_WEIGHTS.keys()),
        "category_weights": DEFAULT_MSME_CATEGORY_WEIGHTS,
        "score_range": {"min": 300, "max": 900},
        "alpha_default": 0.7,
        "risk_buckets": [
            {"range": "750-900", "risk": "Very Low", "decision": "Fast Track Approval"},
            {"range": "650-749", "risk": "Low", "decision": "Approve"},
            {"range": "550-649", "risk": "Medium", "decision": "Conditional Approval"},
            {"range": "450-549", "risk": "High", "decision": "Manual Review"},
            {"range": "300-449", "risk": "Very High", "decision": "Decline"}
        ]
    }


# ============================================================================
# OVERDRAFT ENDPOINTS
# ============================================================================

class OverdraftRequest(BaseModel):
    """Request model for overdraft calculation"""
    credit_score: int = Field(..., ge=300, le=900, description="Credit score")
    monthly_gtv: float = Field(..., ge=0, description="Monthly Gross Transaction Value")
    business_age_years: float = Field(2.0, ge=0, description="Years since formation")
    industry: str = Field("trading", description="Industry category")
    msme_category: str = Field("micro", description="MSME category")
    existing_debt: float = Field(0, ge=0, description="Existing debt amount")
    avg_bank_balance: float = Field(0, ge=0, description="Average bank balance")
    total_assets: float = Field(0, ge=0, description="Total asset value")
    inventory_value: float = Field(0, ge=0, description="Inventory value")
    receivables_value: float = Field(0, ge=0, description="Receivables value")
    cash_flow_health_score: float = Field(0.7, ge=0, le=1, description="Cash flow health (0-1)")
    payment_discipline_score: float = Field(0.8, ge=0, le=1, description="Payment discipline (0-1)")
    monthly_cash_inflow: Optional[float] = Field(None, ge=0)
    monthly_cash_outflow: Optional[float] = Field(None, ge=0)
    existing_emi: float = Field(0, ge=0, description="Existing EMI obligations")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "credit_score": 720,
            "monthly_gtv": 2500000,
            "business_age_years": 3.5,
            "industry": "trading",
            "msme_category": "small",
            "existing_debt": 500000,
            "cash_flow_health_score": 0.8,
            "payment_discipline_score": 0.85
        }
    })


class OverdraftResponse(BaseModel):
    """Response model for overdraft recommendation"""
    eligibility: str
    risk_tier: str
    credit_score: int
    
    recommended_limit: float
    min_limit: float
    max_limit: float
    
    calculation_methods: Dict[str, float]
    
    interest_rate: float
    processing_fee_pct: float
    processing_fee_amount: float
    
    tenure_months: int
    renewal_frequency_months: int
    emi_amount: Optional[float]
    
    collateral_required: bool
    collateral_value_required: float
    personal_guarantee_required: bool
    
    dscr: float
    debt_to_turnover: float
    emi_coverage_ratio: float
    
    conditions: List[str]
    recommendations: List[str]
    
    timestamp: str


class QuickOverdraftEstimate(BaseModel):
    """Quick overdraft estimate request"""
    credit_score: int = Field(..., ge=300, le=900)
    monthly_gtv: float = Field(..., ge=0)
    msme_category: str = Field("micro")


@app.post("/api/overdraft/calculate", response_model=OverdraftResponse, tags=["Overdraft"])
async def calculate_overdraft(
    request: OverdraftRequest,
    auth: Dict = Depends(verify_token)
):
    """
    Calculate overdraft limit recommendation based on credit score and business profile.
    
    ## Calculation Methods Used
    - **Turnover Method**: 20-40% of annual turnover based on risk tier
    - **Cash Flow Method**: Based on DSCR and monthly surplus
    - **MPBF Method**: Maximum Permissible Bank Finance (Tandon Committee)
    
    ## Risk Tiers & Limits
    | Score | Tier | Max Turnover % | Base Rate |
    |-------|------|----------------|-----------|
    | 750+ | Prime | 40% | 10.5% |
    | 650-749 | Near Prime | 30% | 13.0% |
    | 550-649 | Standard | 25% | 16.0% |
    | 450-549 | Subprime | 15% | 20.0% |
    | <450 | High Risk | 0% | N/A |
    
    ## MSME Category Limits (RBI Guidelines)
    - Micro: Up to ₹25 Lakh
    - Small: Up to ₹1 Crore
    - Medium: Up to ₹5 Crore
    """
    from overdraft_engine import OverdraftRecommendationEngine
    
    engine = OverdraftRecommendationEngine()
    
    recommendation = engine.calculate_recommendation(
        credit_score=request.credit_score,
        business_age_years=request.business_age_years,
        industry=request.industry,
        msme_category=request.msme_category,
        monthly_gtv=request.monthly_gtv,
        avg_bank_balance=request.avg_bank_balance,
        monthly_cash_inflow=request.monthly_cash_inflow,
        monthly_cash_outflow=request.monthly_cash_outflow,
        total_assets=request.total_assets,
        inventory_value=request.inventory_value,
        receivables_value=request.receivables_value,
        existing_debt=request.existing_debt,
        existing_emi=request.existing_emi,
        cash_flow_health_score=request.cash_flow_health_score,
        payment_discipline_score=request.payment_discipline_score
    )
    
    return OverdraftResponse(
        eligibility=recommendation.eligibility,
        risk_tier=recommendation.risk_tier,
        credit_score=recommendation.credit_score,
        
        recommended_limit=recommendation.recommended_limit,
        min_limit=recommendation.min_limit,
        max_limit=recommendation.max_limit,
        
        calculation_methods={
            'turnover_method': recommendation.turnover_based_limit,
            'cash_flow_method': recommendation.cash_flow_based_limit,
            'mpbf_method': recommendation.mpbf_based_limit
        },
        
        interest_rate=recommendation.interest_rate,
        processing_fee_pct=recommendation.processing_fee_pct,
        processing_fee_amount=recommendation.processing_fee_amount,
        
        tenure_months=recommendation.tenure_months,
        renewal_frequency_months=recommendation.renewal_frequency_months,
        emi_amount=recommendation.emi_amount,
        
        collateral_required=recommendation.collateral_required,
        collateral_value_required=recommendation.collateral_value_required,
        personal_guarantee_required=recommendation.personal_guarantee_required,
        
        dscr=recommendation.dscr,
        debt_to_turnover=recommendation.debt_to_turnover,
        emi_coverage_ratio=recommendation.emi_coverage_ratio,
        
        conditions=recommendation.conditions,
        recommendations=recommendation.recommendations,
        
        timestamp=datetime.utcnow().isoformat()
    )


@app.post("/api/overdraft/quick-estimate", tags=["Overdraft"])
async def quick_overdraft_estimate(
    request: QuickOverdraftEstimate,
    auth: Dict = Depends(verify_token)
):
    """
    Get quick overdraft estimate with minimal inputs.
    
    Only requires credit score, monthly GTV, and MSME category.
    Returns estimated limit range and indicative rate.
    """
    from overdraft_engine import OverdraftRecommendationEngine
    
    engine = OverdraftRecommendationEngine()
    estimate = engine.get_quick_estimate(
        credit_score=request.credit_score,
        monthly_gtv=request.monthly_gtv,
        msme_category=request.msme_category
    )
    
    estimate['timestamp'] = datetime.utcnow().isoformat()
    return estimate


@app.post("/api/score-with-overdraft", tags=["Scoring", "Overdraft"])
async def score_with_overdraft_limit(
    request: MSMEScoreRequest,
    auth: Dict = Depends(verify_token)
):
    """
    Combined endpoint: Score MSME and get overdraft recommendation.
    
    Returns both credit score assessment and overdraft limit in single call.
    """
    if scorer is None:
        raise HTTPException(status_code=503, detail="Scorer not initialized")
    
    features_dict = {k: v for k, v in request.features.model_dump().items() if v is not None}
    
    if not features_dict:
        raise HTTPException(status_code=400, detail="At least one feature required")
    
    try:
        # Score business
        score_result = scorer.score_business(
            features=features_dict,
            segment=request.business_segment,
            alpha=request.alpha,
            include_explanation=request.include_explanation
        )
        
        # Calculate overdraft
        from overdraft_engine import OverdraftRecommendationEngine
        engine = OverdraftRecommendationEngine()
        
        monthly_gtv = features_dict.get('monthly_gtv', features_dict.get('weekly_gtv', 0) * 4)
        
        od_result = engine.calculate_recommendation(
            credit_score=score_result['score'],
            business_age_years=features_dict.get('business_age_years', 2),
            industry=features_dict.get('industry_code', 'trading'),
            msme_category=features_dict.get('msme_category', 'micro'),
            monthly_gtv=monthly_gtv,
            avg_bank_balance=features_dict.get('avg_bank_balance', 0),
            existing_debt=features_dict.get('total_debt_amount', 0),
            cash_flow_health_score=features_dict.get('cashflow_regularity_score', 0.7),
            payment_discipline_score=features_dict.get('overdraft_repayment_ontime_ratio', 0.8),
            total_assets=features_dict.get('total_assets_value', 0)
        )
        
        return {
            'credit_assessment': {
                'score': score_result['score'],
                'prob_default_90dpd': score_result['prob_default_90dpd'],
                'risk_category': score_result['risk_category'],
                'recommended_decision': score_result['recommended_decision'],
                'business_segment': score_result['business_segment'],
                'component_scores': score_result['component_scores'],
                'category_contributions': score_result['category_contributions']
            },
            'overdraft_recommendation': {
                'eligibility': od_result.eligibility,
                'risk_tier': od_result.risk_tier,
                'recommended_limit': od_result.recommended_limit,
                'interest_rate': od_result.interest_rate,
                'tenure_months': od_result.tenure_months,
                'emi_amount': od_result.emi_amount,
                'collateral_required': od_result.collateral_required,
                'collateral_value': od_result.collateral_value_required,
                'processing_fee': od_result.processing_fee_amount,
                'dscr': od_result.dscr,
                'calculation_methods': {
                    'turnover': od_result.turnover_based_limit,
                    'cash_flow': od_result.cash_flow_based_limit,
                    'mpbf': od_result.mpbf_based_limit
                },
                'conditions': od_result.conditions,
                'recommendations': od_result.recommendations
            },
            'timestamp': datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/api/overdraft/tiers", tags=["Overdraft"])
async def get_overdraft_tiers(auth: Dict = Depends(verify_token)):
    """Get overdraft eligibility tiers and rates"""
    return {
        'tiers': {
            'prime': {
                'score_range': '750-900',
                'max_turnover_pct': '40%',
                'base_rate': '10.5%',
                'collateral': 'Not Required',
                'tenure': '36 months'
            },
            'near_prime': {
                'score_range': '650-749',
                'max_turnover_pct': '30%',
                'base_rate': '13.0%',
                'collateral': 'Not Required',
                'tenure': '24 months'
            },
            'standard': {
                'score_range': '550-649',
                'max_turnover_pct': '25%',
                'base_rate': '16.0%',
                'collateral': 'Required',
                'tenure': '18 months'
            },
            'subprime': {
                'score_range': '450-549',
                'max_turnover_pct': '15%',
                'base_rate': '20.0%',
                'collateral': 'Required',
                'tenure': '12 months'
            },
            'high_risk': {
                'score_range': '300-449',
                'max_turnover_pct': '0%',
                'base_rate': 'N/A',
                'collateral': 'N/A',
                'tenure': 'Not Eligible'
            }
        },
        'msme_limits': {
            'micro': {'max': '₹25 Lakh', 'min': '₹50,000'},
            'small': {'max': '₹1 Crore', 'min': '₹1 Lakh'},
            'medium': {'max': '₹5 Crore', 'min': '₹5 Lakh'}
        },
        'calculation_methods': [
            'Turnover Method (RBI recommended)',
            'Cash Flow Coverage Method (DSCR-based)',
            'MPBF Method (Tandon Committee)'
        ],
        'key_factors': [
            'Credit Score',
            'Business Vintage',
            'Industry Risk',
            'Cash Flow Health',
            'Payment Discipline',
            'Existing Debt Obligations'
        ]
    }


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "detail": exc.detail,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='MSME Credit Scoring API')
    parser.add_argument('--host', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=8001)
    parser.add_argument('--reload', action='store_true')
    
    args = parser.parse_args()
    
    print(f"Starting MSME Credit Scoring API on {args.host}:{args.port}")
    
    uvicorn.run("app:app", host=args.host, port=args.port, reload=args.reload)

