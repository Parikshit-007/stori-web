"""
Consumer Credit Scoring API - FastAPI Application
==================================================

This module provides REST API endpoints for consumer credit scoring:
1. /api/consumer/score - Score a consumer and return credit score
2. /api/consumer/explain - Get detailed feature explanation
3. /api/consumer/health - Health check endpoint
4. /api/consumer/model/info - Model metadata

Security: Bearer token authentication (stub implementation)

Author: ML Engineering Team
Version: 1.0.0
"""

import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import config
from config.constants import SCORE_RANGE, CONSUMER_RISK_TIERS
from config.feature_weights import CONSUMER_FEATURE_WEIGHTS, FEATURE_CATEGORIES

# ============================================================================
# CONFIGURATION
# ============================================================================

# Paths to model artifacts
MODEL_DIR = os.path.join(os.path.dirname(__file__), 'consumer_model_artifacts')
MODEL_PATH = os.path.join(MODEL_DIR, 'consumer_credit_model.joblib')
METRICS_PATH = os.path.join(MODEL_DIR, 'training_metrics.json')

# API configuration
API_VERSION = "1.0.0"
API_TITLE = "Consumer Credit Scoring API"
API_DESCRIPTION = """
Consumer Credit Scoring API for predicting default probability and generating credit scores.

## Features
- LightGBM-based credit scoring
- Feature importance and SHAP explainability
- Score range: 0-100
- Comprehensive consumer profiling

## Risk Tiers
- **Excellent**: 80-100 (Prime borrowers)
- **Good**: 70-79 (Near-prime)
- **Fair**: 60-69 (Subprime)
- **Poor**: 50-59 (Deep subprime)
- **Very Poor**: 0-49 (High risk)
"""

# Bearer token for authentication (stub - replace with proper auth in production)
VALID_TOKENS = {
    "dev_token_12345": {"user": "dev_user", "role": "developer"},
    "prod_token_67890": {"user": "prod_service", "role": "service"},
    "test_token_abcde": {"user": "test_user", "role": "tester"}
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def probability_to_score(prob: float, min_score: int = 0, max_score: int = 100) -> int:
    """Convert default probability to credit score"""
    # Lower probability = higher score
    score = min_score + (max_score - min_score) * (1 - prob)
    return int(np.clip(score, min_score, max_score))


def score_to_risk_tier(score: int) -> str:
    """Map credit score to risk tier"""
    if score >= 80:
        return "Excellent"
    elif score >= 70:
        return "Good"
    elif score >= 60:
        return "Fair"
    elif score >= 50:
        return "Poor"
    else:
        return "Very Poor"


def get_feature_importance(model, feature_names: List[str], top_n: int = 20) -> List[Dict]:
    """Get top N important features from model"""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1][:top_n]
        
        return [
            {
                "feature": feature_names[idx],
                "importance": float(importances[idx]),
                "rank": rank + 1
            }
            for rank, idx in enumerate(indices)
        ]
    return []


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class FeatureInput(BaseModel):
    """Input model for consumer features"""
    # Identity & Demographics
    name_dob_verified: Optional[int] = Field(None, ge=0, le=1)
    pan_verified: Optional[int] = Field(None, ge=0, le=1)
    aadhaar_verified: Optional[int] = Field(None, ge=0, le=1)
    phone_verified: Optional[int] = Field(None, ge=0, le=1)
    phone_age_months: Optional[float] = Field(None, ge=0)
    email_verified: Optional[int] = Field(None, ge=0, le=1)
    email_age_months: Optional[float] = Field(None, ge=0)
    age: Optional[int] = Field(None, ge=18, le=100)
    education_level: Optional[int] = Field(None, ge=0, le=5)
    marital_status: Optional[str] = None
    dependents_count: Optional[int] = Field(None, ge=0)
    
    # Employment & Income
    employment_type: Optional[str] = None
    employment_tenure_months: Optional[float] = Field(None, ge=0)
    job_changes_3y: Optional[int] = Field(None, ge=0)
    monthly_income: Optional[float] = Field(None, ge=0)
    monthly_income_stability: Optional[float] = Field(None, ge=0, le=1)
    income_cv: Optional[float] = Field(None, ge=0)
    income_source_verification: Optional[int] = Field(None, ge=0, le=1)
    employment_history_score: Optional[float] = Field(None, ge=0, le=100)
    
    # Assets & Liabilities
    total_financial_assets: Optional[float] = Field(None, ge=0)
    liquid_assets: Optional[float] = Field(None, ge=0)
    property_owned: Optional[int] = Field(None, ge=0, le=1)
    vehicle_owned: Optional[int] = Field(None, ge=0, le=1)
    existing_loans_count: Optional[int] = Field(None, ge=0)
    total_debt_outstanding: Optional[float] = Field(None, ge=0)
    debt_to_income_ratio: Optional[float] = Field(None, ge=0)
    emi_to_income_ratio: Optional[float] = Field(None, ge=0)
    
    # Credit & Repayment
    credit_history_months: Optional[int] = Field(None, ge=0)
    credit_cards_count: Optional[int] = Field(None, ge=0)
    credit_utilization_ratio: Optional[float] = Field(None, ge=0, le=1)
    total_credit_limit: Optional[float] = Field(None, ge=0)
    loan_defaults_ever: Optional[int] = Field(None, ge=0)
    max_dpd_12m: Optional[int] = Field(None, ge=0)
    loan_inquiries_6m: Optional[int] = Field(None, ge=0)
    loan_approvals_6m: Optional[int] = Field(None, ge=0)
    
    # Banking & Cashflow
    primary_bank_vintage_months: Optional[int] = Field(None, ge=0)
    avg_bank_balance_6m: Optional[float] = Field(None, ge=0)
    min_bank_balance_6m: Optional[float] = Field(None, ge=0)
    bank_balance_volatility: Optional[float] = Field(None, ge=0)
    avg_monthly_credits: Optional[float] = Field(None, ge=0)
    avg_monthly_debits: Optional[float] = Field(None, ge=0)
    bounce_rate_12m: Optional[float] = Field(None, ge=0, le=1)
    inflow_consistency_cv: Optional[float] = Field(None, ge=0)
    
    # Spending & Behavior
    avg_monthly_spending: Optional[float] = Field(None, ge=0)
    spending_to_income_ratio: Optional[float] = Field(None, ge=0)
    essential_spending_ratio: Optional[float] = Field(None, ge=0, le=1)
    luxury_spending_ratio: Optional[float] = Field(None, ge=0, le=1)
    gambling_spending_flag: Optional[int] = Field(None, ge=0, le=1)
    impulse_purchase_ratio: Optional[float] = Field(None, ge=0, le=1)
    spending_discipline_index: Optional[float] = Field(None, ge=0, le=100)
    savings_rate: Optional[float] = Field(None, ge=0, le=1)
    
    # Bills & Utilities
    utility_payment_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    bill_payment_ontime_ratio: Optional[float] = Field(None, ge=0, le=1)
    bill_payment_discipline: Optional[float] = Field(None, ge=0, le=100)
    rent_to_income_ratio: Optional[float] = Field(None, ge=0)
    
    # Transaction Patterns
    avg_transaction_amount: Optional[float] = Field(None, ge=0)
    upi_transactions_monthly: Optional[int] = Field(None, ge=0)
    digital_payment_ratio: Optional[float] = Field(None, ge=0, le=1)
    late_night_transaction_ratio: Optional[float] = Field(None, ge=0, le=1)
    weekend_transaction_ratio: Optional[float] = Field(None, ge=0, le=1)
    
    # Fraud & Risk Signals
    identity_matching: Optional[float] = Field(None, ge=0, le=100)
    bank_statement_manipulation: Optional[float] = Field(None, ge=0, le=1)
    synthetic_id_risk: Optional[float] = Field(None, ge=0, le=1)
    transaction_pattern_anomaly: Optional[float] = Field(None, ge=0, le=1)
    fraud_flag_count: Optional[int] = Field(None, ge=0)
    
    # Financial Health
    survivability_months: Optional[float] = Field(None, ge=0)
    emergency_fund_ratio: Optional[float] = Field(None, ge=0)
    financial_stress_score: Optional[float] = Field(None, ge=0, le=100)
    
    class Config:
        schema_extra = {
            "example": {
                "name_dob_verified": 1,
                "pan_verified": 1,
                "aadhaar_verified": 1,
                "phone_verified": 1,
                "age": 32,
                "monthly_income": 65000,
                "employment_tenure_months": 36,
                "monthly_income_stability": 0.85,
                "total_financial_assets": 250000,
                "debt_to_income_ratio": 0.3,
                "credit_utilization_ratio": 0.4,
                "bill_payment_ontime_ratio": 0.95,
                "spending_discipline_index": 75
            }
        }


class ScoreRequest(BaseModel):
    """Request model for scoring endpoint"""
    features: FeatureInput
    include_explanation: Optional[bool] = Field(
        True,
        description="Whether to include feature importance explanation"
    )


class ScoreResponse(BaseModel):
    """Response model for scoring endpoint"""
    score: int = Field(..., ge=0, le=100, description="Credit score (0-100)")
    default_probability: float = Field(..., ge=0, le=1, description="Default probability")
    risk_tier: str = Field(..., description="Risk tier category")
    model_version: str = Field(..., description="Model version identifier")
    category_scores: Optional[Dict[str, float]] = Field(None, description="Category-level scores")
    feature_importance: Optional[List[Dict]] = Field(None, description="Top important features")
    timestamp: str = Field(..., description="Scoring timestamp")


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
    score_range: Dict[str, int]
    risk_tiers: Dict[str, str]
    feature_categories: List[str]
    total_features: int


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

# Global model and metadata
model = None
feature_names = None
training_metrics = None
model_version = "unknown"


# ============================================================================
# AUTHENTICATION
# ============================================================================

async def verify_token(authorization: str = Header(None)) -> Dict:
    """Verify bearer token authentication"""
    if authorization is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
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
    """Load model on startup"""
    global model, feature_names, training_metrics, model_version
    
    print("=" * 70)
    print("CONSUMER CREDIT SCORING API STARTUP")
    print("=" * 70)
    
    # Load model
    if os.path.exists(MODEL_PATH):
        try:
            model_data = joblib.load(MODEL_PATH)
            model = model_data['model']
            feature_names = model_data.get('feature_names', model_data.get('feature_cols', []))
            model_version = model_data.get('version', 'v1.0.0')
            
            print(f"Model loaded successfully from: {MODEL_PATH}")
            print(f"Model version: {model_version}")
            print(f"Features: {len(feature_names)}")
            
            # Load metrics
            if os.path.exists(METRICS_PATH):
                with open(METRICS_PATH, 'r') as f:
                    training_metrics = json.load(f)
                print(f"Training metrics loaded")
                print(f"  - Test AUC: {training_metrics.get('test_auc', 'N/A')}")
            
            print("API ready to serve requests.")
            
        except Exception as e:
            print(f"ERROR loading model: {e}")
            model = None
    else:
        print(f"WARNING: Model not found at {MODEL_PATH}")
        print("API running without model.")
    
    print("=" * 70)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("Shutting down Consumer Credit Scoring API...")


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/api/consumer/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model is not None else "degraded",
        model_loaded=model is not None,
        model_version=model_version,
        timestamp=datetime.utcnow().isoformat()
    )


@app.get("/api/consumer/model/info", response_model=ModelInfoResponse, tags=["System"])
async def get_model_info(auth: Dict = Depends(verify_token)):
    """Get model and API information"""
    return ModelInfoResponse(
        model_version=model_version,
        api_version=API_VERSION,
        score_range={"min": 0, "max": 100},
        risk_tiers={
            "Excellent": "80-100",
            "Good": "70-79",
            "Fair": "60-69",
            "Poor": "50-59",
            "Very Poor": "0-49"
        },
        feature_categories=list(FEATURE_CATEGORIES.keys()),
        total_features=len(feature_names) if feature_names else 0
    )


@app.post("/api/consumer/score", response_model=ScoreResponse, tags=["Scoring"])
async def score_consumer(
    request: ScoreRequest,
    auth: Dict = Depends(verify_token)
):
    """
    Score a consumer based on provided features.
    
    ## Request Body
    - **features**: Consumer feature values (see FeatureInput model)
    - **include_explanation**: Whether to include feature importance
    
    ## Response
    - **score**: Credit score (0-100)
    - **default_probability**: Default probability (0-1)
    - **risk_tier**: Risk tier classification
    - **feature_importance**: Top important features (if requested)
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    # Convert features to dict (excluding None values)
    features_dict = {k: v for k, v in request.features.dict().items() if v is not None}
    
    if not features_dict:
        raise HTTPException(
            status_code=400,
            detail="At least one feature must be provided"
        )
    
    try:
        # Create DataFrame with all expected features
        feature_df = pd.DataFrame([features_dict])
        
        # Add missing features with default values (0)
        for feat in feature_names:
            if feat not in feature_df.columns:
                feature_df[feat] = 0
        
        # Ensure correct column order
        feature_df = feature_df[feature_names]
        
        # Predict probability
        prob = model.predict_proba(feature_df)[0][1]  # Probability of default (class 1)
        
        # Convert to score
        score = probability_to_score(prob)
        
        # Get risk tier
        risk_tier = score_to_risk_tier(score)
        
        # Prepare response
        response_data = {
            "score": score,
            "default_probability": float(prob),
            "risk_tier": risk_tier,
            "model_version": model_version,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Add feature importance if requested
        if request.include_explanation:
            top_features = get_feature_importance(model, feature_names, top_n=10)
            # Filter to only features that were provided
            provided_features = [f for f in top_features if f['feature'] in features_dict]
            response_data["feature_importance"] = provided_features[:5]
        
        return ScoreResponse(**response_data)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scoring error: {str(e)}"
        )


@app.post("/api/consumer/batch-score", tags=["Scoring"])
async def batch_score_consumers(
    requests: List[ScoreRequest],
    auth: Dict = Depends(verify_token)
):
    """
    Score multiple consumers in batch.
    
    Returns a list of score responses.
    """
    if model is None:
        raise HTTPException(
            status_code=503,
            detail="Model not loaded"
        )
    
    results = []
    
    for idx, request in enumerate(requests):
        try:
            # Score individual consumer
            result = await score_consumer(request, auth)
            results.append({
                "index": idx,
                "success": True,
                "result": result
            })
        except Exception as e:
            results.append({
                "index": idx,
                "success": False,
                "error": str(e)
            })
    
    return {
        "total": len(requests),
        "successful": sum(1 for r in results if r['success']),
        "failed": sum(1 for r in results if not r['success']),
        "results": results
    }


@app.get("/api/consumer/metrics", tags=["System"])
async def get_training_metrics(auth: Dict = Depends(verify_token)):
    """Get model training metrics"""
    if training_metrics is None:
        raise HTTPException(
            status_code=404,
            detail="Training metrics not available"
        )
    
    return {
        "model_version": model_version,
        "metrics": training_metrics,
        "timestamp": datetime.utcnow().isoformat()
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
    
    parser = argparse.ArgumentParser(description='Consumer Credit Scoring API Server')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8001, help='Port to bind to')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload')
    
    args = parser.parse_args()
    
    print(f"\nStarting Consumer Credit Scoring API on {args.host}:{args.port}\n")
    
    uvicorn.run(
        "api:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )

