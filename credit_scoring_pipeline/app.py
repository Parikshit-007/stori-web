"""
Credit Scoring Pipeline - FastAPI Application
==============================================

This module provides REST API endpoints for:
1. /api/score - Score a user and return credit score
2. /api/explain - Get detailed SHAP explanation
3. /api/features/{id} - Get features for a user (stub)
4. /api/health - Health check endpoint
5. /api/model/info - Model metadata

Security: Bearer token authentication (stub implementation)

Author: ML Engineering Team
Version: 1.0.0
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import scoring components
from score import (
    CreditScorer, PERSONA_WEIGHTS, DEFAULT_CATEGORY_WEIGHTS,
    compute_persona_subscore, prob_to_score
)

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths to model artifacts
MODEL_PATH = os.environ.get('MODEL_PATH', 'model_artifacts/credit_scoring_model.joblib')
PREPROCESSOR_PATH = os.environ.get('PREPROCESSOR_PATH', 'model_artifacts/preprocessor.joblib')
CONFIG_PATH = os.environ.get('CONFIG_PATH', 'feature_config.json')

# API configuration
API_VERSION = "1.0.0"
API_TITLE = "Credit Scoring API"
API_DESCRIPTION = """
Credit Scoring API for predicting 90-DPD default probability and generating credit scores.

## Features
- GBM-based credit scoring with LightGBM
- Persona-specific weight adjustments
- SHAP-based explainability
- Score range: 300-900

## Personas
- **new_to_credit**: Users with limited or no credit history
- **gig_worker**: Users with irregular income from gig/freelance work
- **salaried_professional**: Users with stable salaried employment
- **credit_experienced**: Users with established credit history
- **mass_affluent**: High net worth users with significant assets
"""

# Bearer token for authentication (stub - replace with proper auth in production)
VALID_TOKENS = {
    "dev_token_12345": {"user": "dev_user", "role": "developer"},
    "prod_token_67890": {"user": "prod_service", "role": "service"},
    "test_token_abcde": {"user": "test_user", "role": "tester"}
}


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class FeatureInput(BaseModel):
    """Input model for user features"""
    # Identity & Demographics
    name_dob_verified: Optional[int] = Field(None, ge=0, le=1)
    phone_verified: Optional[int] = Field(None, ge=0, le=1)
    phone_age_months: Optional[float] = Field(None, ge=0)
    email_verified: Optional[int] = Field(None, ge=0, le=1)
    email_age_months: Optional[float] = Field(None, ge=0)
    location_stability_score: Optional[float] = Field(None, ge=0, le=1)
    location_tier: Optional[str] = None
    education_level: Optional[int] = Field(None, ge=0, le=5)
    employment_tenure_months: Optional[float] = Field(None, ge=0)
    employment_type: Optional[str] = None
    
    # Income & Cashflow
    monthly_income: Optional[float] = Field(None, ge=0)
    income_growth_rate: Optional[float] = None
    avg_account_balance: Optional[float] = Field(None, ge=0)
    min_account_balance: Optional[float] = Field(None, ge=0)
    income_stability_score: Optional[float] = Field(None, ge=0, le=1)
    income_variance_coefficient: Optional[float] = Field(None, ge=0)
    itr_filed: Optional[int] = Field(None, ge=0, le=1)
    itr_income_declared: Optional[float] = Field(None, ge=0)
    employability_score: Optional[float] = Field(None, ge=0, le=1)
    ppf_balance: Optional[float] = Field(None, ge=0)
    gov_schemes_enrolled: Optional[int] = Field(None, ge=0)
    bank_statement_months_available: Optional[int] = Field(None, ge=0)
    
    # Assets & Liabilities
    current_loan_count: Optional[int] = Field(None, ge=0)
    current_loan_amount: Optional[float] = Field(None, ge=0)
    credit_card_count: Optional[int] = Field(None, ge=0)
    credit_card_utilization: Optional[float] = Field(None, ge=0, le=1)
    credit_card_limit: Optional[float] = Field(None, ge=0)
    lic_policy_count: Optional[int] = Field(None, ge=0)
    lic_premium_annual: Optional[float] = Field(None, ge=0)
    fd_total_amount: Optional[float] = Field(None, ge=0)
    total_assets_value: Optional[float] = Field(None, ge=0)
    insurance_premium_paid_ratio: Optional[float] = Field(None, ge=0, le=1)
    insurance_renewal_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    debt_to_income_ratio: Optional[float] = Field(None, ge=0)
    
    # Spending & Behavioral
    monthly_spending: Optional[float] = Field(None, ge=0)
    spending_to_income_ratio: Optional[float] = Field(None, ge=0)
    essential_spending_ratio: Optional[float] = Field(None, ge=0, le=1)
    discretionary_spending_ratio: Optional[float] = Field(None, ge=0, le=1)
    purchase_frequency: Optional[int] = Field(None, ge=0)
    avg_purchase_value: Optional[float] = Field(None, ge=0)
    subscription_cancellation_count: Optional[int] = Field(None, ge=0)
    subscription_downgrade_count: Optional[int] = Field(None, ge=0)
    impatience_score: Optional[float] = Field(None, ge=0, le=1)
    impulse_buying_score: Optional[float] = Field(None, ge=0, le=1)
    budgeting_score: Optional[float] = Field(None, ge=0, le=1)
    financial_literacy_score: Optional[float] = Field(None, ge=0, le=1)
    recurring_payment_habit_score: Optional[float] = Field(None, ge=0, le=1)
    loan_application_count_6m: Optional[int] = Field(None, ge=0)
    application_rejection_rate: Optional[float] = Field(None, ge=0, le=1)
    social_media_score: Optional[float] = Field(None, ge=0, le=1)
    email_response_time_score: Optional[float] = Field(None, ge=0, le=1)
    
    # Transactions & Repayments
    upi_transaction_count_monthly: Optional[int] = Field(None, ge=0)
    upi_transaction_amount_monthly: Optional[float] = Field(None, ge=0)
    p2m_transaction_ratio: Optional[float] = Field(None, ge=0, le=1)
    utility_payment_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    rent_payment_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    phone_bill_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    internet_bill_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    repayment_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    max_dpd_ever: Optional[int] = Field(None, ge=0)
    avg_dpd: Optional[float] = Field(None, ge=0)
    ecommerce_transaction_count: Optional[int] = Field(None, ge=0)
    ecommerce_return_rate: Optional[float] = Field(None, ge=0, le=1)
    paid_subscription_count: Optional[int] = Field(None, ge=0)
    sip_active_count: Optional[int] = Field(None, ge=0)
    sip_monthly_amount: Optional[float] = Field(None, ge=0)
    investment_portfolio_value: Optional[float] = Field(None, ge=0)
    savings_rate: Optional[float] = Field(None, ge=0, le=1)
    
    # Fraud & Identity
    face_recognition_match_score: Optional[float] = Field(None, ge=0, le=1)
    name_match_score: Optional[float] = Field(None, ge=0, le=1)
    location_mismatch_flag: Optional[int] = Field(None, ge=0, le=1)
    device_anomaly_score: Optional[float] = Field(None, ge=0, le=1)
    fraud_history_flag: Optional[int] = Field(None, ge=0, le=1)
    fraud_attempt_count: Optional[int] = Field(None, ge=0)
    income_source_verified: Optional[int] = Field(None, ge=0, le=1)
    
    # Family & Network
    spouse_credit_score: Optional[float] = Field(None, ge=300, le=900)
    spouse_credit_available: Optional[int] = Field(None, ge=0, le=1)
    family_credit_score_avg: Optional[float] = Field(None, ge=300, le=900)
    family_credit_available: Optional[int] = Field(None, ge=0, le=1)
    family_financial_responsibility_score: Optional[float] = Field(None, ge=0, le=1)
    dependents_count: Optional[int] = Field(None, ge=0)
    
    class Config:
        schema_extra = {
            "example": {
                "name_dob_verified": 1,
                "phone_verified": 1,
                "phone_age_months": 48,
                "email_verified": 1,
                "monthly_income": 75000,
                "avg_account_balance": 150000,
                "income_stability_score": 0.85,
                "credit_card_utilization": 0.35,
                "repayment_ontime_ratio": 0.92,
                "budgeting_score": 0.7
            }
        }


class ScoreRequest(BaseModel):
    """Request model for scoring endpoint"""
    features: FeatureInput
    persona: Optional[str] = Field(
        "salaried_professional",
        description="User persona for weight adjustments"
    )
    alpha: Optional[float] = Field(
        0.7,
        ge=0, le=1,
        description="Weight for GBM prediction (vs persona subscore)"
    )
    include_explanation: Optional[bool] = Field(
        True,
        description="Whether to include SHAP explanation"
    )


class ScoreResponse(BaseModel):
    """Response model for scoring endpoint"""
    score: int = Field(..., ge=300, le=900, description="Credit score")
    prob_default_90dpd: float = Field(..., ge=0, le=1, description="90-day default probability")
    risk_category: str = Field(..., description="Risk level category")
    model_version: str = Field(..., description="Model version identifier")
    persona: str = Field(..., description="Persona used for scoring")
    component_scores: Dict[str, float] = Field(..., description="Component score breakdown")
    category_contributions: Dict[str, float] = Field(..., description="Category-level contributions")
    explanation: Optional[Dict] = Field(None, description="SHAP explanation if requested")
    timestamp: str = Field(..., description="Scoring timestamp")


class ExplainRequest(BaseModel):
    """Request model for explanation endpoint"""
    features: FeatureInput
    persona: Optional[str] = "salaried_professional"
    top_n: Optional[int] = Field(5, ge=1, le=20, description="Number of top features")


class ExplainResponse(BaseModel):
    """Response model for explanation endpoint"""
    score: int
    top_positive_features: List[Dict]
    top_negative_features: List[Dict]
    category_contributions: Dict[str, float]
    persona_details: Dict
    timestamp: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_version: str
    timestamp: str


class ModelInfoResponse(BaseModel):
    """Model information response"""
    model_version: str
    api_version: str
    available_personas: List[str]
    category_weights: Dict[str, float]
    score_range: Dict[str, int]
    alpha_default: float


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: str
    timestamp: str


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Global scorer instance
scorer: Optional[CreditScorer] = None


# ============================================================================
# AUTHENTICATION
# ============================================================================

async def verify_token(authorization: str = Header(None)) -> Dict:
    """
    Verify bearer token authentication.
    
    In production, replace with proper JWT validation or OAuth2.
    """
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization format. Use 'Bearer <token>'"
        )
    
    token = parts[1]
    
    if token not in VALID_TOKENS:
        raise HTTPException(
            status_code=403,
            detail="Invalid or expired token"
        )
    
    return VALID_TOKENS[token]


# ============================================================================
# STARTUP / SHUTDOWN
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Load model and preprocessor on startup"""
    global scorer
    
    print("=" * 60)
    print("CREDIT SCORING API STARTUP")
    print("=" * 60)
    
    # Try to load model
    model_path = MODEL_PATH if os.path.exists(MODEL_PATH) else None
    preprocessor_path = PREPROCESSOR_PATH if os.path.exists(PREPROCESSOR_PATH) else None
    config_path = CONFIG_PATH if os.path.exists(CONFIG_PATH) else None
    
    scorer = CreditScorer(
        model_path=model_path,
        preprocessor_path=preprocessor_path,
        config_path=config_path,
        alpha=0.7
    )
    
    if model_path:
        print(f"Model loaded from: {model_path}")
        print(f"Model version: {scorer.model_version}")
    else:
        print("WARNING: Model not found. Running in persona-only mode.")
    
    if preprocessor_path:
        print(f"Preprocessor loaded from: {preprocessor_path}")
    
    print("API ready to serve requests.")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down Credit Scoring API...")


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Health check endpoint.
    
    Returns API health status and model availability.
    """
    return HealthResponse(
        status="healthy",
        model_loaded=scorer is not None and scorer.model is not None,
        model_version=scorer.model_version if scorer else "unknown",
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/api/model/info", response_model=ModelInfoResponse, tags=["System"])
async def get_model_info(auth: Dict = Depends(verify_token)):
    """
    Get model and API information.
    
    Requires authentication.
    """
    return ModelInfoResponse(
        model_version=scorer.model_version if scorer else "unknown",
        api_version=API_VERSION,
        available_personas=list(PERSONA_WEIGHTS.keys()),
        category_weights=DEFAULT_CATEGORY_WEIGHTS,
        score_range={"min": 300, "max": 900},
        alpha_default=0.7
    )


@app.post("/api/score", response_model=ScoreResponse, tags=["Scoring"])
async def score_user(
    request: ScoreRequest,
    auth: Dict = Depends(verify_token)
):
    """
    Score a user based on provided features and persona.
    
    ## Request Body
    - **features**: User feature values (see FeatureInput model)
    - **persona**: User persona for weight adjustments
    - **alpha**: Weight for GBM prediction (0.7 default)
    - **include_explanation**: Whether to include SHAP explanation
    
    ## Response
    - **score**: Credit score (300-900)
    - **prob_default_90dpd**: 90-day default probability
    - **risk_category**: Risk level (Very Low to Very High)
    - **component_scores**: Breakdown of GBM and persona scores
    - **category_contributions**: Per-category contributions
    - **explanation**: SHAP feature attributions (if requested)
    """
    if scorer is None:
        raise HTTPException(
            status_code=503,
            detail="Scorer not initialized"
        )
    
    # Validate persona
    if request.persona not in PERSONA_WEIGHTS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid persona. Must be one of: {list(PERSONA_WEIGHTS.keys())}"
        )
    
    # Convert features to dict (excluding None values)
    features_dict = {k: v for k, v in request.features.dict().items() if v is not None}
    
    if not features_dict:
        raise HTTPException(
            status_code=400,
            detail="At least one feature must be provided"
        )
    
    try:
        # Score user
        result = scorer.score_user(
            features=features_dict,
            persona=request.persona,
            alpha=request.alpha,
            include_explanation=request.include_explanation
        )
        
        return ScoreResponse(
            score=result['score'],
            prob_default_90dpd=result['prob_default_90dpd'],
            risk_category=result['risk_category'],
            model_version=result['model_version'],
            persona=result['persona'],
            component_scores=result['component_scores'],
            category_contributions=result['category_contributions'],
            explanation=result.get('explanation'),
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scoring error: {str(e)}"
        )


@app.post("/api/explain", response_model=ExplainResponse, tags=["Explainability"])
async def explain_score(
    request: ExplainRequest,
    auth: Dict = Depends(verify_token)
):
    """
    Get detailed explanation for a credit score.
    
    Returns SHAP-based feature attributions and category-level contributions.
    """
    if scorer is None:
        raise HTTPException(
            status_code=503,
            detail="Scorer not initialized"
        )
    
    features_dict = {k: v for k, v in request.features.dict().items() if v is not None}
    
    try:
        # Get full score with explanation
        result = scorer.score_user(
            features=features_dict,
            persona=request.persona,
            include_explanation=True
        )
        
        explanation = result.get('explanation', {})
        
        return ExplainResponse(
            score=result['score'],
            top_positive_features=explanation.get('top_positive_features', [])[:request.top_n],
            top_negative_features=explanation.get('top_negative_features', [])[:request.top_n],
            category_contributions=result['category_contributions'],
            persona_details={
                'name': result['persona'],
                'category_weights': PERSONA_WEIGHTS.get(request.persona, {}).get('category_weights', {})
            },
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Explanation error: {str(e)}"
        )


@app.get("/api/features/{user_id}", tags=["Features"])
async def get_user_features(
    user_id: str,
    auth: Dict = Depends(verify_token)
):
    """
    Get features for a user by ID.
    
    NOTE: This is a stub endpoint. In production, implement database lookup.
    """
    # Stub implementation - return sample features
    # In production, fetch from database/feature store
    
    sample_features = {
        "user_id": user_id,
        "features": {
            "name_dob_verified": 1,
            "phone_verified": 1,
            "phone_age_months": 48,
            "email_verified": 1,
            "monthly_income": 75000,
            "avg_account_balance": 150000,
            "income_stability_score": 0.85,
            "credit_card_utilization": 0.35,
            "repayment_ontime_ratio": 0.92,
            "budgeting_score": 0.7
        },
        "persona": "salaried_professional",
        "last_updated": datetime.utcnow().isoformat(),
        "note": "This is stub data. Implement database lookup in production."
    }
    
    return sample_features


@app.get("/api/personas", tags=["Configuration"])
async def list_personas(auth: Dict = Depends(verify_token)):
    """
    List all available personas and their configurations.
    """
    personas = {}
    for key, config in PERSONA_WEIGHTS.items():
        personas[key] = {
            "name": config['name'],
            "description": config['description'],
            "category_weights": config['category_weights']
        }
    
    return {
        "personas": personas,
        "default": "salaried_professional"
    }


@app.get("/api/categories", tags=["Configuration"])
async def list_categories(auth: Dict = Depends(verify_token)):
    """
    List all scoring categories and their default weights.
    """
    return {
        "categories": DEFAULT_CATEGORY_WEIGHTS,
        "total_weight": sum(DEFAULT_CATEGORY_WEIGHTS.values())
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
    
    parser = argparse.ArgumentParser(description='Credit Scoring API Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    args = parser.parse_args()
    
    print(f"Starting Credit Scoring API on {args.host}:{args.port}")
    
    uvicorn.run(
        "app:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )


