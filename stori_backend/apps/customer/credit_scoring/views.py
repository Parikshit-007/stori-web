"""
Credit Scoring Views - Django REST Framework
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import pandas as pd
import numpy as np
import logging

from .model_loader import ModelLoader
from .serializers import CreditScoreInputSerializer, CreditScoreOutputSerializer
from .models import CreditScoreRequest, CreditScoreResult

logger = logging.getLogger(__name__)


def map_input_features_to_model_features(input_data: dict, model_feature_names: list) -> dict:
    """
    Map input feature names to model's expected feature names
    
    Handles feature name mismatches between API input and model training
    Also derives missing features where possible
    """
    mapped_data = {}
    
    # Comprehensive feature name mapping: input_name -> model_name
    # Based on complete list of 71 model features
    feature_mapping = {
        # Identity & Demographics
        'phone_verified': 'phone_number_verified',
        'phone_age_months': 'phone_number_tenure_months',
        'email_age_months': 'email_tenure_months',
        'job_changes_3y': 'employment_changes_last_5yr',
        
        # Income features
        'income_source_verification': 'income_source_verified',
        
        # Banking features
        'avg_balance': 'avg_account_balance',
        'monthly_expense': 'total_monthly_outflow',
        'avg_monthly_debits': 'total_monthly_outflow',  # Alternative mapping
        'survivability_months': 'survivability_months',
        'spending_to_income': 'monthly_outflow_burden',  # Similar concept
        'expense_rigidity': 'expense_rigidity',
        'inflow_time_consistency': 'inflow_time_consistency',
        'salary_retention_ratio': 'income_retention_ratio',
        
        # UPI/P2P features
        'upi_p2p_ratio': 'p2p_upi_transaction_count',  # Approximate
        'avg_monthly_credits': 'monthly_upi_amount',  # Approximate
        
        # EMI features
        'estimated_emi': 'total_emi',
        'emi_to_income': 'emi_to_income_ratio',
        
        # Asset features
        'stocks_value': 'investments',  # Approximate - sum of investments
        'mutual_funds_value': 'investments',  # Will be summed
        'insurance_payment_detected': 'has_insurance',
        'insurance_value': 'insurance_coverage',
        
        # Spending/Behavioral features
        'impulse_spending_score': 'impulse_purchase_ratio',
        'spending_to_income': 'spending_personality_score',  # Alternative
        'late_night_txn_ratio': 'late_night_transaction_ratio',
        'utility_payment_consistency': 'utility_payment_consistency',
        'utility_to_income': 'utility_to_income_ratio',
        'rent_to_income': 'rent_to_income_ratio',
        
        # Risk/Fraud features
        'manipulation_risk_score': 'bank_statement_manipulation',
        'bounce_rate': 'statement_tampering_detected',  # High bounce = tampering
    }
    
    # First, try direct matches and mappings
    for input_key, input_value in input_data.items():
        # Try mapping first
        model_key = feature_mapping.get(input_key)
        if model_key and model_key in model_feature_names:
            mapped_data[model_key] = input_value
        # If no mapping, try direct match
        elif input_key in model_feature_names:
            mapped_data[input_key] = input_value
    
    # Derive missing features where possible
    derived_features = {}
    
    # education_score: derive from education_level if missing
    if 'education_score' in model_feature_names and 'education_score' not in mapped_data:
        if 'education_level' in mapped_data:
            edu_level = mapped_data.get('education_level', 0)
            derived_features['education_score'] = min(edu_level * 20, 100)
    
    # identity_matching: derive from verification flags
    if 'identity_matching' in model_feature_names and 'identity_matching' not in mapped_data:
        pan_verified = input_data.get('pan_verified', 0)
        aadhaar_verified = input_data.get('aadhaar_verified', 0)
        name_dob_verified = mapped_data.get('name_dob_verified', 0)
        derived_features['identity_matching'] = (pan_verified + aadhaar_verified + name_dob_verified) / 3.0
    
    # income_trend: derive from income stability
    if 'income_trend' in model_feature_names and 'income_trend' not in mapped_data:
        income_stability = mapped_data.get('monthly_income_stability', 0.8)
        derived_features['income_trend'] = (income_stability - 0.5) * 2  # Scale to -1 to 1
    
    # income_source_type: derive from ITR data
    if 'income_source_type' in model_feature_names and 'income_source_type' not in mapped_data:
        itr_salary = input_data.get('itr_salary_income', 0)
        itr_business = input_data.get('itr_business_income', 0)
        if itr_salary > itr_business:
            derived_features['income_source_type'] = 1  # Salaried
        elif itr_business > 0:
            derived_features['income_source_type'] = 2  # Business
        else:
            derived_features['income_source_type'] = 0  # Unknown
    
    # income_source_verification: derive from ITR/income data
    if 'income_source_verification' in model_feature_names and 'income_source_verification' not in mapped_data:
        itr_income = input_data.get('itr_net_taxable_income', 0)
        derived_features['income_source_verification'] = 1 if itr_income > 0 else mapped_data.get('income_source_verified', 0)
    
    # p2p_upi_transaction_count: derive from upi_p2p_ratio
    if 'p2p_upi_transaction_count' in model_feature_names and 'p2p_upi_transaction_count' not in mapped_data:
        upi_ratio = input_data.get('upi_p2p_ratio', 0)
        txn_count = input_data.get('txn_count', 0)
        if txn_count > 0:
            derived_features['p2p_upi_transaction_count'] = int(upi_ratio * txn_count)
        else:
            derived_features['p2p_upi_transaction_count'] = 0
    
    # regular_p2p_upi_transactions: derive from upi_p2p_ratio
    if 'regular_p2p_upi_transactions' in model_feature_names and 'regular_p2p_upi_transactions' not in mapped_data:
        upi_ratio = input_data.get('upi_p2p_ratio', 0)
        derived_features['regular_p2p_upi_transactions'] = 1 if upi_ratio > 0.1 else 0
    
    # p2p_upi_regularity_score: derive from upi_p2p_ratio
    if 'p2p_upi_regularity_score' in model_feature_names and 'p2p_upi_regularity_score' not in mapped_data:
        upi_ratio = input_data.get('upi_p2p_ratio', 0)
        derived_features['p2p_upi_regularity_score'] = min(upi_ratio * 100, 100)
    
    # account_balance_trend: derive from balance volatility
    if 'account_balance_trend' in model_feature_names and 'account_balance_trend' not in mapped_data:
        balance_vol = mapped_data.get('account_balance_volatility', input_data.get('balance_volatility', 0))
        avg_bal = mapped_data.get('avg_account_balance', input_data.get('avg_balance', 0))
        if balance_vol > 1.0 and avg_bal < 0:
            derived_features['account_balance_trend'] = -1
        elif balance_vol < 0.5:
            derived_features['account_balance_trend'] = 1
        else:
            derived_features['account_balance_trend'] = 0
    
    # total_monthly_outflow: derive from monthly_expense
    if 'total_monthly_outflow' in model_feature_names and 'total_monthly_outflow' not in mapped_data:
        monthly_expense = input_data.get('monthly_expense', 0)
        avg_debits = input_data.get('avg_monthly_debits', 0)
        derived_features['total_monthly_outflow'] = monthly_expense if monthly_expense > 0 else avg_debits
    
    # monthly_outflow_burden: derive from spending_to_income
    if 'monthly_outflow_burden' in model_feature_names and 'monthly_outflow_burden' not in mapped_data:
        spending_ratio = input_data.get('spending_to_income', 0)
        monthly_income = mapped_data.get('monthly_income', 0)
        monthly_expense = input_data.get('monthly_expense', 0)
        if monthly_income > 0:
            derived_features['monthly_outflow_burden'] = monthly_expense / monthly_income if monthly_expense > 0 else spending_ratio
        else:
            derived_features['monthly_outflow_burden'] = spending_ratio
    
    # survivability_months: use from input if available
    if 'survivability_months' in model_feature_names and 'survivability_months' not in mapped_data:
        derived_features['survivability_months'] = input_data.get('survivability_months', 0)
    
    # income_retention_ratio: derive from salary_retention_ratio
    if 'income_retention_ratio' in model_feature_names and 'income_retention_ratio' not in mapped_data:
        salary_retention = input_data.get('salary_retention_ratio', 1.0)
        derived_features['income_retention_ratio'] = salary_retention
    
    # expense_rigidity: use from input if available
    if 'expense_rigidity' in model_feature_names and 'expense_rigidity' not in mapped_data:
        derived_features['expense_rigidity'] = input_data.get('expense_rigidity', 0)
    
    # inflow_consistency_cv: derive from income_stability
    if 'inflow_consistency_cv' in model_feature_names and 'inflow_consistency_cv' not in mapped_data:
        income_stability = mapped_data.get('monthly_income_stability', 0.8)
        # CV is inverse of stability (higher stability = lower CV)
        derived_features['inflow_consistency_cv'] = 1.0 - income_stability
    
    # inflow_time_consistency: use from input if available
    if 'inflow_time_consistency' in model_feature_names and 'inflow_time_consistency' not in mapped_data:
        derived_features['inflow_time_consistency'] = input_data.get('inflow_time_consistency', 0)
    
    # monthly_upi_amount: derive from avg_monthly_credits or UPI transactions
    if 'monthly_upi_amount' in model_feature_names and 'monthly_upi_amount' not in mapped_data:
        avg_credits = input_data.get('avg_monthly_credits', 0)
        upi_ratio = input_data.get('upi_p2p_ratio', 0)
        derived_features['monthly_upi_amount'] = avg_credits * upi_ratio if upi_ratio > 0 else avg_credits * 0.3  # Estimate
    
    # total_emi: use from input if available
    if 'total_emi' in model_feature_names and 'total_emi' not in mapped_data:
        derived_features['total_emi'] = input_data.get('estimated_emi', 0)
    
    # emi_to_monthly_upi_amount: derive from EMI and UPI amount
    if 'emi_to_monthly_upi_amount' in model_feature_names and 'emi_to_monthly_upi_amount' not in mapped_data:
        emi = input_data.get('estimated_emi', 0)
        upi_amount = derived_features.get('monthly_upi_amount', 0)
        if upi_amount > 0:
            derived_features['emi_to_monthly_upi_amount'] = emi / upi_amount
        else:
            derived_features['emi_to_monthly_upi_amount'] = 0
    
    # investments: sum of stocks, mutual funds, etc.
    if 'investments' in model_feature_names and 'investments' not in mapped_data:
        stocks = input_data.get('stocks_value', 0)
        mf = input_data.get('mutual_funds_value', 0)
        bonds = input_data.get('bonds_value', 0)
        derived_features['investments'] = stocks + mf + bonds
    
    # has_insurance: derive from insurance_payment_detected
    if 'has_insurance' in model_feature_names and 'has_insurance' not in mapped_data:
        insurance_detected = input_data.get('insurance_payment_detected', 0)
        insurance_value = input_data.get('insurance_value', 0)
        derived_features['has_insurance'] = 1 if (insurance_detected > 0 or insurance_value > 0) else 0
    
    # insurance_count: estimate
    if 'insurance_count' in model_feature_names and 'insurance_count' not in mapped_data:
        has_insurance = derived_features.get('has_insurance', 0)
        derived_features['insurance_count'] = 1 if has_insurance > 0 else 0
    
    # insurance_coverage: use from input if available
    if 'insurance_coverage' in model_feature_names and 'insurance_coverage' not in mapped_data:
        derived_features['insurance_coverage'] = input_data.get('insurance_value', 0)
    
    # emi_to_income_ratio: use from input if available
    if 'emi_to_income_ratio' in model_feature_names and 'emi_to_income_ratio' not in mapped_data:
        derived_features['emi_to_income_ratio'] = input_data.get('emi_to_income', 0)
    
    # monthly_rent: estimate from rent_to_income
    if 'monthly_rent' in model_feature_names and 'monthly_rent' not in mapped_data:
        rent_ratio = input_data.get('rent_to_income', 0)
        monthly_income = mapped_data.get('monthly_income', 0)
        derived_features['monthly_rent'] = monthly_income * rent_ratio if monthly_income > 0 else 0
    
    # rent_to_income_ratio: use from input if available
    if 'rent_to_income_ratio' in model_feature_names and 'rent_to_income_ratio' not in mapped_data:
        derived_features['rent_to_income_ratio'] = input_data.get('rent_to_income', 0)
    
    # monthly_utility: estimate from utility_to_income
    if 'monthly_utility' in model_feature_names and 'monthly_utility' not in mapped_data:
        utility_ratio = input_data.get('utility_to_income', 0)
        monthly_income = mapped_data.get('monthly_income', 0)
        derived_features['monthly_utility'] = monthly_income * utility_ratio if monthly_income > 0 else 0
    
    # utility_to_income_ratio: use from input if available
    if 'utility_to_income_ratio' in model_feature_names and 'utility_to_income_ratio' not in mapped_data:
        derived_features['utility_to_income_ratio'] = input_data.get('utility_to_income', 0)
    
    # insurance_payment_ontime_ratio: derive from insurance_payment_consistency
    if 'insurance_payment_ontime_ratio' in model_feature_names and 'insurance_payment_ontime_ratio' not in mapped_data:
        consistency = input_data.get('utility_payment_consistency', 0)  # Approximate
        derived_features['insurance_payment_ontime_ratio'] = consistency
    
    # insurance_payment_discipline: derive from insurance_payment_consistency
    if 'insurance_payment_discipline' in model_feature_names and 'insurance_payment_discipline' not in mapped_data:
        consistency = input_data.get('utility_payment_consistency', 0)
        derived_features['insurance_payment_discipline'] = consistency * 100  # Scale to 0-100
    
    # spending_personality: derive from spending patterns
    if 'spending_personality' in model_feature_names and 'spending_personality' not in mapped_data:
        impulse_score = input_data.get('impulse_spending_score', 0)
        if impulse_score > 0.7:
            derived_features['spending_personality'] = 3  # High spender
        elif impulse_score > 0.3:
            derived_features['spending_personality'] = 2  # Moderate
        else:
            derived_features['spending_personality'] = 1  # Conservative
    
    # spending_personality_score: derive from impulse_spending_score
    if 'spending_personality_score' in model_feature_names and 'spending_personality_score' not in mapped_data:
        impulse_score = input_data.get('impulse_spending_score', 0)
        derived_features['spending_personality_score'] = impulse_score * 100  # Scale to 0-100
    
    # impulse_purchase_ratio: use from input if available
    if 'impulse_purchase_ratio' in model_feature_names and 'impulse_purchase_ratio' not in mapped_data:
        derived_features['impulse_purchase_ratio'] = input_data.get('impulse_spending_score', 0)
    
    # budget_adherence: derive from spending_to_income
    if 'budget_adherence' in model_feature_names and 'budget_adherence' not in mapped_data:
        spending_ratio = input_data.get('spending_to_income', 1.0)
        # Lower spending ratio = better budget adherence
        derived_features['budget_adherence'] = max(0, 1.0 - spending_ratio) if spending_ratio <= 1.0 else 0
    
    # spending_discipline_index: derive from multiple factors
    if 'spending_discipline_index' in model_feature_names and 'spending_discipline_index' not in mapped_data:
        impulse_score = input_data.get('impulse_spending_score', 0)
        spending_ratio = input_data.get('spending_to_income', 1.0)
        # Lower impulse and lower spending ratio = higher discipline
        discipline = (1.0 - impulse_score) * (1.0 - min(spending_ratio, 1.0)) * 100
        derived_features['spending_discipline_index'] = max(0, min(100, discipline))
    
    # bill_payment_ontime_ratio: derive from utility_payment_consistency
    if 'bill_payment_ontime_ratio' in model_feature_names and 'bill_payment_ontime_ratio' not in mapped_data:
        consistency = input_data.get('utility_payment_consistency', 0)
        derived_features['bill_payment_ontime_ratio'] = consistency
    
    # bill_payment_delays_count: estimate
    if 'bill_payment_delays_count' in model_feature_names and 'bill_payment_delays_count' not in mapped_data:
        consistency = input_data.get('utility_payment_consistency', 0)
        # Lower consistency = more delays
        derived_features['bill_payment_delays_count'] = int((1.0 - consistency) * 10) if consistency < 1.0 else 0
    
    # bill_payment_discipline: derive from utility_payment_consistency
    if 'bill_payment_discipline' in model_feature_names and 'bill_payment_discipline' not in mapped_data:
        consistency = input_data.get('utility_payment_consistency', 0)
        derived_features['bill_payment_discipline'] = consistency * 100  # Scale to 0-100
    
    # late_night_transaction_ratio: use from input if available
    if 'late_night_transaction_ratio' in model_feature_names and 'late_night_transaction_ratio' not in mapped_data:
        derived_features['late_night_transaction_ratio'] = input_data.get('late_night_txn_ratio', 0)
    
    # late_night_payment_behaviour: derive from late_night_txn_ratio
    if 'late_night_payment_behaviour' in model_feature_names and 'late_night_payment_behaviour' not in mapped_data:
        late_night_ratio = input_data.get('late_night_txn_ratio', 0)
        if late_night_ratio > 0.5:
            derived_features['late_night_payment_behaviour'] = 3  # High
        elif late_night_ratio > 0.2:
            derived_features['late_night_payment_behaviour'] = 2  # Moderate
        else:
            derived_features['late_night_payment_behaviour'] = 1  # Low
    
    # utility_payment_ontime_ratio: use from input if available
    if 'utility_payment_ontime_ratio' in model_feature_names and 'utility_payment_ontime_ratio' not in mapped_data:
        derived_features['utility_payment_ontime_ratio'] = input_data.get('utility_payment_consistency', 0)
    
    # utility_payment_consistency: use from input if available
    if 'utility_payment_consistency' in model_feature_names and 'utility_payment_consistency' not in mapped_data:
        derived_features['utility_payment_consistency'] = input_data.get('utility_payment_consistency', 0)
    
    # risk_appetite: derive from spending patterns
    if 'risk_appetite' in model_feature_names and 'risk_appetite' not in mapped_data:
        impulse_score = input_data.get('impulse_spending_score', 0)
        if impulse_score > 0.7:
            derived_features['risk_appetite'] = 3  # High
        elif impulse_score > 0.3:
            derived_features['risk_appetite'] = 2  # Moderate
        else:
            derived_features['risk_appetite'] = 1  # Low
    
    # risk_appetite_score: derive from impulse_spending_score
    if 'risk_appetite_score' in model_feature_names and 'risk_appetite_score' not in mapped_data:
        impulse_score = input_data.get('impulse_spending_score', 0)
        derived_features['risk_appetite_score'] = impulse_score * 100  # Scale to 0-100
    
    # location_type: default (can't derive from available data)
    if 'location_type' in model_feature_names and 'location_type' not in mapped_data:
        derived_features['location_type'] = 2  # Default to urban (2)
    
    # pin_code_risk_score: default (can't derive from available data)
    if 'pin_code_risk_score' in model_feature_names and 'pin_code_risk_score' not in mapped_data:
        derived_features['pin_code_risk_score'] = 50  # Default medium risk
    
    # statement_tampering_detected: derive from manipulation_risk_score
    if 'statement_tampering_detected' in model_feature_names and 'statement_tampering_detected' not in mapped_data:
        manipulation_score = input_data.get('manipulation_risk_score', 0)
        derived_features['statement_tampering_detected'] = 1 if manipulation_score > 0.5 else 0
    
    # transaction_pattern_anomaly: derive from manipulation_risk_score
    if 'transaction_pattern_anomaly' in model_feature_names and 'transaction_pattern_anomaly' not in mapped_data:
        manipulation_score = input_data.get('manipulation_risk_score', 0)
        derived_features['transaction_pattern_anomaly'] = 1 if manipulation_score > 0.3 else 0
    
    # bank_statement_manipulation: use from input if available
    if 'bank_statement_manipulation' in model_feature_names and 'bank_statement_manipulation' not in mapped_data:
        derived_features['bank_statement_manipulation'] = input_data.get('manipulation_risk_score', 0)
    
    # digital_footprint_age_days: estimate from phone_age_months
    if 'digital_footprint_age_days' in model_feature_names and 'digital_footprint_age_days' not in mapped_data:
        phone_age = input_data.get('phone_age_months', 0)
        email_age = input_data.get('email_age_months', 0)
        avg_age = (phone_age + email_age) / 2.0 if (phone_age > 0 or email_age > 0) else 12
        derived_features['digital_footprint_age_days'] = avg_age * 30  # Convert months to days
    
    # cross_platform_consistency: default (can't derive from available data)
    if 'cross_platform_consistency' in model_feature_names and 'cross_platform_consistency' not in mapped_data:
        derived_features['cross_platform_consistency'] = 0.8  # Default moderate consistency
    
    # device_fingerprint_changes: default (can't derive from available data)
    if 'device_fingerprint_changes' in model_feature_names and 'device_fingerprint_changes' not in mapped_data:
        derived_features['device_fingerprint_changes'] = 0  # Default no changes
    
    # synthetic_id_risk: derive from verification flags
    if 'synthetic_id_risk' in model_feature_names and 'synthetic_id_risk' not in mapped_data:
        pan_verified = input_data.get('pan_verified', 0)
        aadhaar_verified = input_data.get('aadhaar_verified', 0)
        name_dob_verified = mapped_data.get('name_dob_verified', 0)
        # Lower verification = higher synthetic ID risk
        verification_score = (pan_verified + aadhaar_verified + name_dob_verified) / 3.0
        derived_features['synthetic_id_risk'] = 1.0 - verification_score
    
    # Add derived features
    for key, value in derived_features.items():
        if key in model_feature_names:
            mapped_data[key] = value
    
    logger.info(f"Feature mapping: {len(mapped_data)} features mapped ({len(derived_features)} derived) from {len(input_data)} input features")
    
    return mapped_data


def probability_to_score(prob: float, min_score: int = 0, max_score: int = 100) -> int:
    """Convert default probability to credit score"""
    # Lower probability = higher score
    score = min_score + (max_score - min_score) * (1 - prob)
    return int(np.clip(score, min_score, max_score))


def score_to_risk_tier(score: int) -> dict:
    """Map credit score to risk tier"""
    if score >= 80:
        return {
            'tier': 'Excellent',
            'description': 'Prime borrower - Very low risk',
            'recommendation': 'Approve with best rates'
        }
    elif score >= 65:
        return {
            'tier': 'Good',
            'description': 'Near-prime borrower - Low risk',
            'recommendation': 'Approve with standard rates'
        }
    elif score >= 50:
        return {
            'tier': 'Fair',
            'description': 'Subprime borrower - Medium risk',
            'recommendation': 'Manual review recommended'
        }
    elif score >= 35:
        return {
            'tier': 'Poor',
            'description': 'Deep subprime - High risk',
            'recommendation': 'Additional verification required'
        }
    else:
        return {
            'tier': 'Very Poor',
            'description': 'Very high risk',
            'recommendation': 'Decline or require collateral'
        }


def get_feature_importance(model, feature_names: list, top_n: int = 10) -> list:
    """Get top N important features"""
    try:
        # Handle LightGBM Booster
        if hasattr(model, 'feature_importance'):
            # LightGBM Booster uses feature_importance() method
            importances = model.feature_importance(importance_type='gain')
            indices = np.argsort(importances)[::-1][:top_n]
            
            return [
                {
                    "feature": feature_names[idx] if idx < len(feature_names) else f"feature_{idx}",
                    "importance": float(importances[idx]),
                    "rank": rank + 1
                }
                for rank, idx in enumerate(indices)
            ]
        # Handle sklearn-style models
        elif hasattr(model, 'feature_importances_'):
            importances = model.feature_importances_
            indices = np.argsort(importances)[::-1][:top_n]
            
            return [
                {
                    "feature": feature_names[idx] if idx < len(feature_names) else f"feature_{idx}",
                    "importance": float(importances[idx]),
                    "rank": rank + 1
                }
                for rank, idx in enumerate(indices)
            ]
    except Exception as e:
        logger.error(f"Error getting feature importance: {e}")
    
    return []


class CreditScoreView(APIView):
    """
    Main credit scoring endpoint
    POST: Calculate credit score and default probability
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Calculate credit score from consumer data
        
        Request Body: Consumer financial features (JSON)
        Response: Credit score, default probability, risk tier
        """
        try:
            # Validate input
            serializer = CreditScoreInputSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'message': 'Invalid input data',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get model
            model_loader = ModelLoader.get_instance()
            if not model_loader.is_loaded():
                return Response({
                    'success': False,
                    'message': 'Credit scoring model not available'
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            model = model_loader.model
            feature_names = model_loader.feature_names
            
            # Log model info for verification
            logger.info(f"Model type: {type(model).__name__}")
            logger.info(f"Model loaded: {model is not None}")
            logger.info(f"Feature count: {len(feature_names) if feature_names else 0}")
            if hasattr(model, 'num_trees'):
                logger.info(f"Model trees: {model.num_trees()}")
            
            # Log ALL feature names the model expects (for debugging)
            if feature_names:
                logger.info(f"Model expects these features (first 20): {feature_names[:20]}")
                logger.info(f"Model expects ALL {len(feature_names)} features: {feature_names}")
            
            # Prepare features
            input_data = serializer.validated_data.copy()
            
            # Normalize credit_utilization_ratio if it's > 1 (treat as percentage)
            if 'credit_utilization_ratio' in input_data and input_data['credit_utilization_ratio'] > 1:
                input_data['credit_utilization_ratio'] = input_data['credit_utilization_ratio'] / 100.0
            
            # Map input features to model's expected feature names
            if feature_names:
                mapped_data = map_input_features_to_model_features(input_data, feature_names)
                logger.info(f"Mapped {len(mapped_data)} features from input to model features")
            else:
                mapped_data = input_data
            
            # Create DataFrame with all features (fill missing with defaults)
            df = pd.DataFrame([mapped_data])
            
            # Log input features received
            logger.info(f"Input features received: {len(input_data)} features")
            logger.info(f"Sample input features: {list(input_data.keys())[:10]}...")
            
            # Ensure all model features are present
            missing_features = []
            if feature_names:
                for feature in feature_names:
                    if feature not in df.columns:
                        df[feature] = 0
                        missing_features.append(feature)
                
                # Log missing features
                if missing_features:
                    logger.warning(f"Missing {len(missing_features)} model features (filled with 0): {missing_features[:10]}...")
                else:
                    logger.info("All model features present in input")
                
                # Log which input features are NOT in model (extra features)
                extra_features = [f for f in input_data.keys() if f not in feature_names]
                if extra_features:
                    logger.warning(f"Extra features in input (not used by model): {extra_features[:10]}...")
                
                # Reorder columns to match model training
                df = df[feature_names]
                
                # Log actual values being sent to model for key features
                key_features = ['monthly_income', 'credit_score', 'credit_utilization_ratio', 
                              'avg_balance', 'bounce_rate', 'total_financial_assets',
                              'age', 'education_level', 'employment_type']
                logger.info("Key feature values sent to model:")
                for feat in key_features:
                    if feat in df.columns:
                        logger.info(f"  {feat}: {df[feat].iloc[0]}")
            
            # Predict
            # Handle LightGBM Booster (uses predict()) vs sklearn models (uses predict_proba())
            if hasattr(model, 'predict_proba'):
                # Sklearn-style model
                prob_array = model.predict_proba(df)
                default_prob = float(prob_array[0][1])
                logger.info(f"Model prediction (sklearn): prob_array shape={prob_array.shape}, default_prob={default_prob}")
            else:
                # LightGBM Booster - predict() returns probability directly for binary classification
                raw_prediction = model.predict(df)
                default_prob = float(raw_prediction[0])
                logger.info(f"Model prediction (LightGBM): raw_prediction={raw_prediction}, default_prob={default_prob}")
            
            # Log input features summary for debugging
            logger.info(f"Input features summary: income={input_data.get('monthly_income', 0):.2f}, "
                       f"credit_score={input_data.get('credit_score', 0)}, "
                       f"utilization={input_data.get('credit_utilization_ratio', 0):.3f}, "
                       f"avg_balance={input_data.get('avg_balance', 0):.2f}")
            
            credit_score = probability_to_score(default_prob)
            risk_info = score_to_risk_tier(credit_score)
            
            logger.info(f"Scoring result: default_prob={default_prob:.4f}, credit_score={credit_score}, risk_tier={risk_info['tier']}")
            
            # Get feature importance
            feature_importance = get_feature_importance(model, feature_names or list(df.columns), top_n=10)
            
            # Save request and result to database
            try:
                score_request = CreditScoreRequest.objects.create(
                    user=request.user,
                    request_data=input_data
                )
                
                CreditScoreResult.objects.create(
                    request=score_request,
                    credit_score=credit_score,
                    default_probability=default_prob,
                    risk_tier=risk_info['tier'],
                    feature_importance={'top_features': feature_importance}
                )
            except Exception as e:
                logger.error(f"Error saving results to database: {e}")
            
            # Prepare response
            response_data = {
                'success': True,
                'credit_score': credit_score,
                'default_probability': round(default_prob, 4),
                'risk_tier': risk_info['tier'],
                'risk_description': risk_info['description'],
                'recommendation': risk_info['recommendation'],
                'feature_importance': feature_importance,
                'model_info': {
                    'model_type': 'LightGBM',
                    'version': '1.0.0',
                    'score_range': '0-100',
                    'metrics': model_loader.metrics if model_loader.metrics else {}
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in credit scoring: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': f'Credit scoring failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreditScoreHistoryView(APIView):
    """Get credit score history for the authenticated user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get all credit score results for the user"""
        try:
            results = CreditScoreResult.objects.filter(
                request__user=request.user
            ).select_related('request').order_by('-created_at')[:20]
            
            history = []
            for result in results:
                history.append({
                    'credit_score': result.credit_score,
                    'default_probability': result.default_probability,
                    'risk_tier': result.risk_tier,
                    'created_at': result.created_at.isoformat(),
                    'request_data': result.request.request_data
                })
            
            return Response({
                'success': True,
                'count': len(history),
                'history': history
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Failed to get history: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ModelHealthView(APIView):
    """Check if model is loaded and ready"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get model health status"""
        model_loader = ModelLoader.get_instance()
        
        is_loaded = model_loader.is_loaded()
        
        return Response({
            'success': True,
            'model_loaded': is_loaded,
            'model_type': 'LightGBM' if is_loaded else None,
            'metrics': model_loader.metrics if is_loaded else None,
            'feature_count': len(model_loader.feature_names) if is_loaded and model_loader.feature_names else 0
        }, status=status.HTTP_200_OK)

