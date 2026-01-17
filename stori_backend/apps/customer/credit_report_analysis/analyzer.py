"""
Credit Report Analysis Module
Comprehensive credit report analysis with liability detection
"""

import json
from typing import Dict, Any, Optional
import pandas as pd


def load_credit_report(file_path: str) -> Dict[str, Any]:
    """
    Load credit report from file
    
    Args:
        file_path: Path to credit report file
        
    Returns:
        Dictionary containing credit report data
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data


def extract_credit_features(credit_data: Dict[str, Any]) -> Dict[str, float]:
    """
    Extract features from credit report data
    
    Args:
        credit_data: Credit report data dictionary
        
    Returns:
        Dictionary of extracted features
    """
    features = {}
    
    # Validate input type
    if not isinstance(credit_data, dict):
        raise TypeError(f"Expected dictionary, got {type(credit_data).__name__}")
    
    # Basic credit score
    features['credit_score'] = credit_data.get('score', 0)
    
    # Account information
    accounts = credit_data.get('accounts', [])
    
    # Ensure accounts is a list
    if not isinstance(accounts, list):
        accounts = []
    
    features['total_accounts'] = len(accounts)
    
    # Count accounts by status - handle both dict and non-dict items
    active_count = 0
    closed_count = 0
    for acc in accounts:
        if isinstance(acc, dict):
            if acc.get('status') == 'active':
                active_count += 1
            elif acc.get('status') == 'closed':
                closed_count += 1
    
    features['active_accounts'] = active_count
    features['closed_accounts'] = closed_count
    
    # Outstanding amounts
    total_outstanding = 0
    total_credit_limit = 0
    for acc in accounts:
        if isinstance(acc, dict):
            total_outstanding += acc.get('outstanding', 0)
            total_credit_limit += acc.get('credit_limit', 0)
    
    features['total_outstanding'] = total_outstanding
    features['total_credit_limit'] = total_credit_limit
    
    # Credit utilization
    if features['total_credit_limit'] > 0:
        features['credit_utilization'] = (features['total_outstanding'] / features['total_credit_limit']) * 100
    else:
        features['credit_utilization'] = 0
    
    # Delinquency
    delinquent_count = 0
    max_dpd_value = 0
    for acc in accounts:
        if isinstance(acc, dict):
            dpd = acc.get('dpd', 0)
            if dpd > 0:
                delinquent_count += 1
            if dpd > max_dpd_value:
                max_dpd_value = dpd
    
    features['delinquent_accounts'] = delinquent_count
    features['max_dpd'] = max_dpd_value
    
    # Enquiries
    enquiries = credit_data.get('enquiries', [])
    if not isinstance(enquiries, list):
        enquiries = []
    
    features['total_enquiries'] = len(enquiries)
    
    recent_enquiries = 0
    for enq in enquiries:
        if isinstance(enq, dict) and enq.get('months_ago', 99) <= 6:
            recent_enquiries += 1
    
    features['recent_enquiries_6m'] = recent_enquiries
    
    # Account types - fixed to use 'account_type' field
    credit_card_count = 0
    loan_count = 0
    for acc in accounts:
        if isinstance(acc, dict):
            acc_type = acc.get('account_type', acc.get('type', ''))
            if acc_type == 'credit_card':
                credit_card_count += 1
            elif acc_type in ['loan', 'personal_loan', 'home_loan']:
                loan_count += 1
    
    features['credit_cards'] = credit_card_count
    features['loans'] = loan_count
    
    return features


def extract_liabilities_from_credit_report(
    credit_data: Dict[str, Any],
    bank_statement_df: Optional[pd.DataFrame] = None,
    monthly_income: float = 0.0
) -> Dict[str, Any]:
    """
    Extract comprehensive liabilities from credit report and bank statements.
    
    Args:
        credit_data: Credit report data dictionary
        bank_statement_df: Optional bank statement DataFrame for cross-validation
        monthly_income: Monthly income for ratio calculations
        
    Returns:
        Complete liability analysis
    """
    from .liability_detector import LiabilityDetector
    
    detector = LiabilityDetector()
    return detector.detect_liabilities(
        credit_report_data=credit_data,
        bank_statement_df=bank_statement_df,
        monthly_income=monthly_income
    )

