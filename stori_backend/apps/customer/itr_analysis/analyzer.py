"""
Production-Grade ITR (Income Tax Return) Analysis Pipeline
===========================================================
ITR-based income verification and tax compliance for credit underwriting

Design Philosophy:
- Income verification and reconciliation with bank statements
- Tax compliance scoring
- Multi-year income trend analysis
- Stable feature names for ML model compatibility
- Robust edge-case handling
- Compatible with ITR JSON/Excel formats

Author: Senior Fintech Backend Engineer
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
import warnings
import json
from datetime import datetime

warnings.filterwarnings('ignore', category=pd.errors.PerformanceWarning)

# =========================================================
# CONSTANTS & CONFIGURATION
# =========================================================

# Stable ITR feature names (DO NOT CHANGE - ML models depend on these)
ITR_FEATURE_NAMES = [
    # Income Features (5)
    "itr_net_taxable_income",
    "itr_gross_total_income",
    "itr_income_growth_yoy",
    "itr_income_stability",
    "itr_income_to_bank_income_ratio",
    
    # Tax Compliance (4)
    "itr_filed_current_year",
    "itr_filed_last_3_years",
    "tax_compliance_score",
    "itr_tax_outstanding",
    
    # Income Type (3)
    "itr_salary_income",
    "itr_business_income",
    "income_type_salaried",
    
    # Deductions (2)
    "itr_total_deductions",
    "itr_deductions_to_income_ratio",
    
    # Filing Behavior (2)
    "itr_filing_delay_days",
    "itr_revision_filed",
    
    # Additional (3)
    "itr_tax_paid",
    "itr_house_property_income",
    "itr_capital_gains"
]

# ITR Form Types
ITR_FORMS = {
    'ITR-1': 'Sahaj (Salaried)',
    'ITR-2': 'Multiple Properties/Capital Gains',
    'ITR-3': 'Business Income',
    'ITR-4': 'Sugam (Presumptive Taxation)'
}


# =========================================================
# 1. LOAD ITR DATA (JSON/Excel)
# =========================================================

def load_itr_json(itr_path: str) -> Dict:
    """
    Load ITR data from JSON file (Income Tax Department format).
    
    Handles actual ITR JSON structure from Income Tax Portal:
    - ITR-1 (Sahaj): Salary, pension, interest
    - ITR-4 (Sugam): Presumptive taxation (44AD/44ADA/44AE)
    
    Args:
        itr_path: Path to ITR JSON file
        
    Returns:
        Dict with standardized ITR data structure
    """
    file_path = Path(itr_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"ITR file not found: {itr_path}")
    
    if file_path.suffix.lower() == '.json':
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_itr = json.load(f)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    # Parse Income Tax Department JSON structure
    itr_root = raw_itr.get('ITR', {})
    
    # Determine ITR form type
    itr_form = None
    form_data = None
    
    if 'ITR1' in itr_root:
        itr_form = 'ITR-1'
        form_data = itr_root['ITR1']
    elif 'ITR4' in itr_root:
        itr_form = 'ITR-4'
        form_data = itr_root['ITR4']
    else:
        raise ValueError("Unsupported ITR form (only ITR-1 and ITR-4 supported)")
    
    # Extract form details
    if itr_form == 'ITR-1':
        form_info = form_data.get('Form_ITR1', {})
        income_section = form_data.get('ITR1_IncomeDeductions', {})
        tax_section = form_data.get('ITR1_TaxComputation', {})
        tax_paid_section = form_data.get('TaxPaid', {})
    else:  # ITR-4
        form_info = form_data.get('Form_ITR4', {})
        income_section = form_data.get('IncomeDeductions', {})
        tax_section = form_data.get('TaxComputation', {})
        tax_paid_section = form_data.get('TaxPaid', {})
        
        # If TaxComputation is not found at top level, it might be nested differently
        if not tax_section:
            tax_section = {}
    
    # Extract assessment year
    assessment_year = form_info.get('AssessmentYear', 'Unknown')
    
    # Extract filing status
    filing_status = form_data.get('FilingStatus', {})
    due_date = filing_status.get('ItrFilingDueDate', None)
    filing_date = form_data.get('CreationInfo', {}).get('JSONCreationDate', None)
    
    # Extract income data
    income_data = {}
    
    # Salary income - use get with default 0.0, don't use 'or' as 0 is falsy
    salary_gross = income_section.get('GrossSalary', 0.0)
    salary_alt = income_section.get('Salary', 0.0)
    income_data['salary_income'] = float(salary_gross) if salary_gross else float(salary_alt) if salary_alt else 0.0
    income_data['net_salary'] = float(income_section.get('NetSalary', 0.0)) if income_section.get('NetSalary') else income_data['salary_income']
    income_data['income_from_salary'] = float(income_section.get('IncomeFromSal', 0.0)) if income_section.get('IncomeFromSal') else 0.0
    
    # Business income (for ITR-4)
    if itr_form == 'ITR-4':
        business_section = form_data.get('ScheduleBP', {})
        presumptive_inc_44ada = business_section.get('PersumptiveInc44ADA', {})
        presumptive_inc_44ae = business_section.get('PersumptiveInc44AE', {})
        
        # Try multiple sources, use first non-zero value
        business_inc_44ada = float(presumptive_inc_44ada.get('TotPersumptiveInc44ADA', 0.0)) if presumptive_inc_44ada.get('TotPersumptiveInc44ADA') else 0.0
        business_inc_44ae = float(presumptive_inc_44ae.get('TotPersumInc44AE', 0.0)) if presumptive_inc_44ae.get('TotPersumInc44AE') else 0.0
        business_inc_prof = float(income_section.get('IncomeFromBusinessProf', 0.0)) if income_section.get('IncomeFromBusinessProf') else 0.0
        
        income_data['business_income'] = business_inc_44ada or business_inc_44ae or business_inc_prof or 0.0
    else:
        income_data['business_income'] = 0.0
    
    # House property
    income_data['house_property_income'] = float(income_section.get('TotalIncomeOfHP', 0.0)) if income_section.get('TotalIncomeOfHP') else 0.0
    
    # Capital gains
    if 'LTCG112A' in form_data:
        ltcg = form_data['LTCG112A']
        income_data['capital_gains'] = float(ltcg.get('LongCap112A', 0.0)) if ltcg.get('LongCap112A') else 0.0
    else:
        income_data['capital_gains'] = 0.0
    
    # Other income
    others_inc = income_section.get('OthersInc', {})
    other_income_list = others_inc.get('OthersIncDtlsOthSrc', [])
    other_income_total = sum(float(item.get('OthSrcOthAmount', 0.0)) for item in other_income_list if item.get('OthSrcOthAmount'))
    income_data['other_income'] = float(income_section.get('IncomeOthSrc', 0.0)) if income_section.get('IncomeOthSrc') else other_income_total
    
    # Total income
    income_data['gross_total_income'] = float(income_section.get('GrossTotIncome', 0.0)) if income_section.get('GrossTotIncome') else 0.0
    income_data['net_taxable_income'] = float(income_section.get('TotalIncome', 0.0)) if income_section.get('TotalIncome') else 0.0
    
    # Extract deductions
    deductions_data = {}
    deductions_section = income_section.get('DeductUndChapVIA', {})
    deductions_data['section_80c'] = float(deductions_section.get('Section80C', 0.0)) if deductions_section.get('Section80C') else 0.0
    deductions_data['section_80d'] = float(deductions_section.get('Section80D', 0.0)) if deductions_section.get('Section80D') else 0.0
    deductions_data['section_24b'] = 0.0  # Home loan interest (not in standard structure)
    deductions_data['total_deductions'] = float(deductions_section.get('TotalChapVIADeductions', 0.0)) if deductions_section.get('TotalChapVIADeductions') else 0.0
    
    # Also check UsrDeductUndChapVIA (user deductions)
    user_deductions = income_section.get('UsrDeductUndChapVIA', {})
    if user_deductions and user_deductions.get('TotalChapVIADeductions'):
        user_total = float(user_deductions.get('TotalChapVIADeductions', 0.0))
        if user_total > 0:
            deductions_data['total_deductions'] = user_total
    
    # Extract tax data
    tax_data = {}
    taxes_paid = tax_paid_section.get('TaxesPaid', {}) if tax_paid_section else {}
    tax_data['tax_paid'] = float(taxes_paid.get('TotalTaxesPaid', 0.0)) if taxes_paid.get('TotalTaxesPaid') else 0.0
    tax_data['tds_deducted'] = float(taxes_paid.get('TDS', 0.0)) if taxes_paid.get('TDS') else 0.0
    
    # Extract TDS from TDSonOthThanSals section if available
    if 'TDSonOthThanSals' in form_data:
        tds_section = form_data.get('TDSonOthThanSals', {})
        tds_total = float(tds_section.get('TotalTDSonOthThanSals', 0.0)) if tds_section.get('TotalTDSonOthThanSals') else 0.0
        if tds_total > 0:
            tax_data['tds_deducted'] = tds_total
    
    tax_data['tax_refund'] = float(form_data.get('Refund', {}).get('RefundDue', 0.0)) if form_data.get('Refund', {}).get('RefundDue') else 0.0
    
    # Tax outstanding
    tax_data['tax_outstanding'] = float(tax_paid_section.get('BalTaxPayable', 0.0)) if tax_paid_section and tax_paid_section.get('BalTaxPayable') else 0.0
    
    # Tax computation
    tax_liability = float(tax_section.get('NetTaxLiability', 0.0)) if tax_section and tax_section.get('NetTaxLiability') else 0.0
    if tax_liability == 0 and tax_section:
        tax_liability = float(tax_section.get('TotalTaxPayable', 0.0)) if tax_section.get('TotalTaxPayable') else 0.0
    
    # Filing status
    filing_status_data = {
        'filed': True,  # If JSON exists, it's filed
        'revised': filing_status.get('SeventhProvisio139', 'N') == 'Y',
        'assessment_pending': False  # Not available in standard structure
    }
    
    # Build standardized structure
    standardized_itr = {
        'assessment_year': assessment_year,
        'itr_form': itr_form,
        'filing_date': filing_date,
        'due_date': due_date,
        'income': income_data,
        'deductions': deductions_data,
        'tax': tax_data,
        'filing_status': filing_status_data
    }
    
    return standardized_itr


def load_itr_excel(itr_path: str) -> Dict:
    """
    Load ITR data from Excel file.
    
    Expected Excel structure:
    - Sheet 1: Income Details
    - Sheet 2: Deductions
    - Sheet 3: Tax Details
    
    Args:
        itr_path: Path to ITR Excel file
        
    Returns:
        Dict with ITR data
    """
    file_path = Path(itr_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"ITR file not found: {itr_path}")
    
    try:
        # Read Excel sheets
        income_df = pd.read_excel(itr_path, sheet_name='Income', header=0)
        deductions_df = pd.read_excel(itr_path, sheet_name='Deductions', header=0)
        tax_df = pd.read_excel(itr_path, sheet_name='Tax', header=0)
        
        # Convert to dict structure
        itr_data = {
            'income': income_df.to_dict('records')[0] if len(income_df) > 0 else {},
            'deductions': deductions_df.to_dict('records')[0] if len(deductions_df) > 0 else {},
            'tax': tax_df.to_dict('records')[0] if len(tax_df) > 0 else {},
        }
        
        return itr_data
        
    except Exception as e:
        raise ValueError(f"Failed to read ITR Excel: {str(e)}")


def load_itr_data(itr_path: str, format: str = 'auto') -> Dict:
    """
    Load ITR data from JSON or Excel (auto-detect format).
    
    Args:
        itr_path: Path to ITR file
        format: 'json', 'excel', or 'auto'
        
    Returns:
        Dict with ITR data
    """
    file_path = Path(itr_path)
    
    if format == 'auto':
        if file_path.suffix.lower() == '.json':
            return load_itr_json(itr_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            return load_itr_excel(itr_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")
    elif format == 'json':
        return load_itr_json(itr_path)
    elif format == 'excel':
        return load_itr_excel(itr_path)
    else:
        raise ValueError(f"Invalid format: {format}")


# =========================================================
# 2. LOAD MULTI-YEAR ITR DATA
# =========================================================

def load_multiple_itr_years(itr_files: List[Dict[str, str]]) -> List[Dict]:
    """
    Load ITR data for multiple years.
    
    Args:
        itr_files: List of dicts with 'path', 'assessment_year', 'format'
                   [{"path": "itr_2024.json", "assessment_year": "2024-25", "format": "json"}, ...]
    
    Returns:
        List of ITR data dicts, sorted by assessment year (newest first)
    """
    itr_data_list = []
    
    for itr_file in itr_files:
        try:
            format_type = itr_file.get('format', 'auto')
            itr_data = load_itr_data(itr_file['path'], format=format_type)
            # Use actual assessment year from ITR data, fallback to provided year
            actual_year = itr_data.get('assessment_year', itr_file.get('assessment_year', 'Unknown'))
            itr_data['assessment_year'] = actual_year
            itr_data_list.append(itr_data)
        except Exception as e:
            warnings.warn(f"Failed to load ITR {itr_file.get('path', 'unknown')}: {str(e)}")
            continue
    
    # Sort by assessment year (newest first)
    # Assessment year format: "2025" or "2024-25" - extract first year number
    def sort_key(x):
        year_str = str(x.get('assessment_year', '0'))
        # Extract first year number
        try:
            # Handle formats like "2025", "2024-25", "2024"
            year_part = year_str.split('-')[0].strip()
            return int(year_part)
        except:
            return 0
    
    itr_data_list.sort(key=sort_key, reverse=True)
    
    return itr_data_list


# =========================================================
# 3. EXTRACT ITR FEATURES (SINGLE YEAR)
# =========================================================

def extract_itr_features_single_year(itr_data: Dict) -> Dict[str, float]:
    """
    Extract features from single year ITR data.
    
    Args:
        itr_data: ITR data dict
        
    Returns:
        Dict with ITR features
    """
    features = {}
    
    # Extract income data
    income = itr_data.get('income', {})
    deductions = itr_data.get('deductions', {})
    tax = itr_data.get('tax', {})
    filing_status = itr_data.get('filing_status', {})
    
    # ==========================================
    # INCOME FEATURES
    # ==========================================
    
    features['itr_net_taxable_income'] = _safe_float(
        income.get('net_taxable_income', income.get('total_income', 0.0))
    )
    
    features['itr_gross_total_income'] = _safe_float(
        income.get('gross_total_income', income.get('gross_income', 0.0))
    )
    
    features['itr_salary_income'] = _safe_float(
        income.get('salary_income', income.get('salary', 0.0))
    )
    
    features['itr_business_income'] = _safe_float(
        income.get('business_income', income.get('business', 0.0))
    )
    
    features['itr_house_property_income'] = _safe_float(
        income.get('house_property_income', income.get('house_property', 0.0))
    )
    
    features['itr_capital_gains'] = _safe_float(
        income.get('capital_gains', income.get('capital_gain', 0.0))
    )
    
    # Income type classification
    total_income = features['itr_net_taxable_income']
    if total_income > 0:
        salary_ratio = features['itr_salary_income'] / total_income
        features['income_type_salaried'] = 1.0 if salary_ratio > 0.8 else 0.0
    else:
        features['income_type_salaried'] = 0.0
    
    # ==========================================
    # DEDUCTIONS
    # ==========================================
    
    features['itr_total_deductions'] = _safe_float(
        deductions.get('total_deductions', 0.0)
    )
    
    if total_income > 0:
        features['itr_deductions_to_income_ratio'] = _safe_float(
            features['itr_total_deductions'] / total_income
        )
    else:
        features['itr_deductions_to_income_ratio'] = 0.0
    
    # ==========================================
    # TAX COMPLIANCE
    # ==========================================
    
    features['itr_filed_current_year'] = 1.0 if filing_status.get('filed', False) else 0.0
    
    features['itr_tax_paid'] = _safe_float(tax.get('tax_paid', 0.0))
    
    features['itr_tax_outstanding'] = _safe_float(tax.get('tax_outstanding', 0.0))
    
    features['itr_revision_filed'] = 1.0 if filing_status.get('revised', False) else 0.0
    
    # Filing delay calculation
    filing_date = filing_status.get('filing_date', itr_data.get('filing_date', None))
    due_date = itr_data.get('due_date', None)
    
    if filing_date and due_date:
        try:
            filing_dt = pd.to_datetime(filing_date)
            due_dt = pd.to_datetime(due_date)
            delay_days = (filing_dt - due_dt).days
            features['itr_filing_delay_days'] = _safe_float(max(0, delay_days))
        except:
            features['itr_filing_delay_days'] = 0.0
    else:
        features['itr_filing_delay_days'] = 0.0
    
    # Tax compliance score
    compliance_score = 1.0
    
    if not filing_status.get('filed', False):
        compliance_score -= 0.5
    
    if features['itr_tax_outstanding'] > 0:
        # Penalty based on outstanding amount relative to income
        if total_income > 0:
            outstanding_ratio = features['itr_tax_outstanding'] / total_income
            compliance_score -= min(0.3, outstanding_ratio * 2)
        else:
            compliance_score -= 0.3
    
    if features['itr_filing_delay_days'] > 30:
        compliance_score -= 0.2
    elif features['itr_filing_delay_days'] > 0:
        compliance_score -= 0.1
    
    if filing_status.get('assessment_pending', False):
        compliance_score -= 0.2
    
    # Bonus for paying taxes (indicates earning capacity)
    if features['itr_tax_paid'] > 0:
        compliance_score += 0.1
    
    features['tax_compliance_score'] = _safe_float(max(0.0, min(1.0, compliance_score)))
    
    # Multi-year filing (will be updated if multiple years provided)
    features['itr_filed_last_3_years'] = 0.0
    
    # Income growth and stability (will be updated if multiple years provided)
    features['itr_income_growth_yoy'] = 0.0
    features['itr_income_stability'] = 0.0
    
    # Income reconciliation (will be updated when bank statement data provided)
    features['itr_income_to_bank_income_ratio'] = 0.0
    
    # ==========================================
    # INCOME SOURCE RELIABILITY
    # ==========================================
    # Calculate reliability score based on:
    # 1. TDS presence (indicates formal income)
    # 2. Multiple income sources (diversification)
    # 3. Consistency of income declaration
    
    reliability_score = 0.5  # Base score
    
    # TDS indicates formal, verified income
    tds_amount = _safe_float(tax.get('tds_deducted', 0.0))
    if tds_amount > 0:
        reliability_score += 0.3
        # Higher TDS relative to income = more reliable
        if total_income > 0:
            tds_ratio = tds_amount / total_income
            if tds_ratio > 0.1:  # TDS > 10% of income
                reliability_score += 0.1
    
    # Multiple income sources indicate diversification
    income_sources_count = 0
    if features['itr_salary_income'] > 0:
        income_sources_count += 1
    if features['itr_business_income'] > 0:
        income_sources_count += 1
    if features['itr_house_property_income'] > 0:
        income_sources_count += 1
    if features['itr_capital_gains'] > 0:
        income_sources_count += 1
    other_income = _safe_float(income.get('other_income', 0.0))
    if other_income > 0:
        income_sources_count += 1
    
    if income_sources_count >= 2:
        reliability_score += 0.1
    
    # Salary income is generally more reliable than business
    if features['itr_salary_income'] > 0 and features['income_type_salaried'] == 1.0:
        reliability_score += 0.1
    
    # Cap at 1.0
    features['income_source_reliability'] = min(1.0, reliability_score)
    
    # Additional income details for summary
    features['itr_other_income'] = other_income
    features['itr_tds_deducted'] = tds_amount
    features['itr_tax_refund'] = _safe_float(tax.get('tax_refund', 0.0))
    
    return features


# =========================================================
# 4. EXTRACT ITR FEATURES (MULTI-YEAR)
# =========================================================

def extract_itr_features_multi_year(itr_data_list: List[Dict]) -> Dict[str, float]:
    """
    Extract features from multiple years of ITR data.
    Includes income growth, stability, and filing consistency.
    
    Args:
        itr_data_list: List of ITR data dicts (sorted newest first)
        
    Returns:
        Dict with ITR features (including multi-year metrics)
    """
    if len(itr_data_list) == 0:
        return _get_default_itr_features()
    
    # Get current year features
    current_year_features = extract_itr_features_single_year(itr_data_list[0])
    
    # ==========================================
    # MULTI-YEAR ANALYSIS
    # ==========================================
    
    # Check filing consistency (last 3 years)
    if len(itr_data_list) >= 3:
        filed_count = sum(
            1 for itr in itr_data_list[:3]
            if itr.get('filing_status', {}).get('filed', False)
        )
        current_year_features['itr_filed_last_3_years'] = 1.0 if filed_count >= 3 else 0.0
    elif len(itr_data_list) >= 1:
        # If only 1-2 years, check if all available years are filed
        filed_count = sum(
            1 for itr in itr_data_list
            if itr.get('filing_status', {}).get('filed', False)
        )
        current_year_features['itr_filed_last_3_years'] = 1.0 if filed_count == len(itr_data_list) else 0.0
    
    # Income growth (Year-over-Year)
    if len(itr_data_list) >= 2:
        current_income = current_year_features['itr_net_taxable_income']
        prev_year_features = extract_itr_features_single_year(itr_data_list[1])
        prev_income = prev_year_features['itr_net_taxable_income']
        
        if prev_income > 0:
            growth = (current_income - prev_income) / prev_income
            current_year_features['itr_income_growth_yoy'] = _safe_float(growth)
        else:
            current_year_features['itr_income_growth_yoy'] = 0.0
    else:
        current_year_features['itr_income_growth_yoy'] = 0.0
    
    # Income stability (Coefficient of Variation across years)
    if len(itr_data_list) >= 2:
        incomes = []
        for itr in itr_data_list:
            income = itr.get('income', {})
            net_income = income.get('net_taxable_income', income.get('total_income', 0.0))
            if net_income > 0:
                incomes.append(net_income)
        
        if len(incomes) >= 2:
            mean_income = np.mean(incomes)
            std_income = np.std(incomes)
            
            if mean_income > 0:
                cv = std_income / mean_income
                # Convert to stability score (lower CV = higher stability)
                stability = 1.0 - min(cv, 1.0)
                current_year_features['itr_income_stability'] = _safe_float(stability)
            else:
                current_year_features['itr_income_stability'] = 0.0
        else:
            current_year_features['itr_income_stability'] = 0.0
    else:
        current_year_features['itr_income_stability'] = 0.0
    
    return current_year_features


# =========================================================
# 5. RECONCILE ITR WITH BANK STATEMENT
# =========================================================

def reconcile_itr_with_bank_statement(
    itr_features: Dict[str, float],
    bank_statement_annual_income: float
) -> Dict[str, float]:
    """
    Reconcile ITR income with bank statement income.
    
    Args:
        itr_features: ITR features dict
        bank_statement_annual_income: Annual income from bank statement analysis
        
    Returns:
        Updated ITR features with reconciliation ratio
    """
    itr_income = itr_features.get('itr_net_taxable_income', 0.0)
    
    if bank_statement_annual_income > 0 and itr_income > 0:
        ratio = itr_income / bank_statement_annual_income
        itr_features['itr_income_to_bank_income_ratio'] = _safe_float(ratio)
    else:
        itr_features['itr_income_to_bank_income_ratio'] = 0.0
    
    return itr_features


# =========================================================
# 6. MAIN ITR FEATURE EXTRACTION FUNCTION
# =========================================================

def build_itr_feature_vector(
    itr_files: List[Dict[str, str]],
    bank_statement_annual_income: Optional[float] = None
) -> pd.DataFrame:
    """
    Build complete ITR feature vector for ML model.
    
    Args:
        itr_files: List of ITR file dicts
                  [{"path": "itr_2024.json", "assessment_year": "2024-25", "format": "json"}, ...]
        bank_statement_annual_income: Optional annual income from bank statement
                                      for reconciliation
        
    Returns:
        Single-row DataFrame with all ITR features in stable order
    """
    try:
        # Load ITR data for multiple years
        itr_data_list = load_multiple_itr_years(itr_files)
        
        if len(itr_data_list) == 0:
            warnings.warn("No valid ITR data loaded")
            return pd.DataFrame([_get_default_itr_features()])
        
        # Extract features
        if len(itr_data_list) == 1:
            features = extract_itr_features_single_year(itr_data_list[0])
        else:
            features = extract_itr_features_multi_year(itr_data_list)
        
        # Reconcile with bank statement if provided
        if bank_statement_annual_income is not None:
            features = reconcile_itr_with_bank_statement(features, bank_statement_annual_income)
        
    except Exception as e:
        warnings.warn(f"ITR feature extraction failed: {str(e)}")
        features = _get_default_itr_features()
    
    # Ensure all expected features exist
    for fname in ITR_FEATURE_NAMES:
        if fname not in features:
            features[fname] = 0.0
    
    # Convert to DataFrame with stable column order
    feature_df = pd.DataFrame([features])
    feature_df = feature_df[ITR_FEATURE_NAMES]  # Enforce order
    
    return feature_df


# =========================================================
# 7. HELPER FUNCTIONS
# =========================================================

def _safe_float(value: Union[float, int, np.number], default: float = 0.0) -> float:
    """
    Convert value to safe float, handling NaN, Inf, None.
    """
    try:
        f = float(value)
        if np.isnan(f) or np.isinf(f):
            return default
        return f
    except (TypeError, ValueError):
        return default


def _get_default_itr_features() -> Dict[str, float]:
    """Return safe default ITR feature vector."""
    return {fname: 0.0 for fname in ITR_FEATURE_NAMES}


# =========================================================
# 8. CLI INTERFACE
# =========================================================

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ITR Analysis for Credit Underwriting',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python itr_analysis.py itr_2024.json
  python itr_analysis.py itr_2024.json --bank-income 600000
  python itr_analysis.py itr_2024.json itr_2023.json itr_2022.json --multi-year
        """
    )
    
    parser.add_argument('itr_files', nargs='+', help='ITR file(s) (JSON/Excel)')
    parser.add_argument('--bank-income', type=float, help='Bank statement annual income for reconciliation')
    parser.add_argument('--export', help='Export features to CSV file')
    parser.add_argument('--years', nargs='*', help='Assessment years (e.g., 2024-25 2023-24)')
    
    args = parser.parse_args()
    
    # Prepare ITR files list
    itr_files = []
    for i, file_path in enumerate(args.itr_files):
        itr_file = {
            'path': file_path,
            'format': 'auto'
        }
        if args.years and i < len(args.years):
            itr_file['assessment_year'] = args.years[i]
        itr_files.append(itr_file)
    
    print("=" * 80)
    print("ITR ANALYSIS FOR CREDIT UNDERWRITING")
    print("=" * 80)
    
    for itf in itr_files:
        print(f"  {itf.get('assessment_year', 'Unknown')}: {itf['path']}")
    
    try:
        # Build feature vector
        print("\nExtracting ITR features...")
        features_df = build_itr_feature_vector(itr_files, args.bank_income)
        
        # Display features
        print("\n" + "=" * 80)
        print("EXTRACTED ITR FEATURES (FOR ML MODEL)")
        print("=" * 80)
        print(features_df.T.to_string())
        
        # Display key metrics
        print("\n" + "=" * 80)
        print("KEY ITR METRICS")
        print("=" * 80)
        
        print(f"\nINCOME:")
        print(f"  Net Taxable Income:    Rs {features_df['itr_net_taxable_income'].iloc[0]:,.2f}")
        print(f"  Gross Total Income:    Rs {features_df['itr_gross_total_income'].iloc[0]:,.2f}")
        print(f"  Salary Income:         Rs {features_df['itr_salary_income'].iloc[0]:,.2f}")
        print(f"  Business Income:      Rs {features_df['itr_business_income'].iloc[0]:,.2f}")
        
        print(f"\nTAX COMPLIANCE:")
        print(f"  Filed Current Year:    {'Yes' if features_df['itr_filed_current_year'].iloc[0] > 0 else 'No'}")
        print(f"  Filed Last 3 Years:    {'Yes' if features_df['itr_filed_last_3_years'].iloc[0] > 0 else 'No'}")
        print(f"  Tax Compliance Score:  {features_df['tax_compliance_score'].iloc[0]:.2%}")
        print(f"  Tax Outstanding:       Rs {features_df['itr_tax_outstanding'].iloc[0]:,.2f}")
        print(f"  Tax Paid:              Rs {features_df['itr_tax_paid'].iloc[0]:,.2f}")
        
        if features_df['itr_income_growth_yoy'].iloc[0] != 0:
            print(f"\nINCOME TRENDS:")
            print(f"  YoY Growth:            {features_df['itr_income_growth_yoy'].iloc[0]:.2%}")
            print(f"  Income Stability:      {features_df['itr_income_stability'].iloc[0]:.2%}")
        
        if features_df['itr_income_to_bank_income_ratio'].iloc[0] > 0:
            ratio = features_df['itr_income_to_bank_income_ratio'].iloc[0]
            print(f"\nRECONCILIATION:")
            print(f"  ITR/Bank Income Ratio: {ratio:.2f}")
            if 0.8 <= ratio <= 1.2:
                print(f"  Assessment:            Good match")
            elif ratio < 0.6:
                print(f"  Assessment:            WARNING: Under-reporting in ITR")
            else:
                print(f"  Assessment:            WARNING: Possible discrepancy")
        
        print("\n" + "=" * 80)
        
        # Export if requested
        if args.export:
            features_df.to_csv(args.export, index=False)
            print(f"\nFeatures exported to: {args.export}")
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

