"""
MSME Synthetic Identity & Criminal History Detection

Detects synthetic business identities and verifies promoter/director backgrounds.
Includes criminal history checks, business authenticity verification, and fraud detection.

Author: Stori MSME Credit Scoring
Date: 2026-01-15
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta
import re


class MSMESyntheticIdentityAnalyzer:
    """
    Detect synthetic business identities and verify director backgrounds.
    
    MSME-Specific Fraud Patterns:
    1. Shell companies with fake directors
    2. Directors with criminal fraud history
    3. GST/PAN mismatches
    4. Fake business operations
    5. Director identity inconsistencies
    """
    
    def __init__(self):
        """Initialize analyzer with fraud patterns and thresholds."""
        self.criminal_patterns = [
            'FRAUD', 'FORGERY', 'IDENTITY THEFT', 'CHEATING',
            'FINANCIAL FRAUD', 'CYBER CRIME', 'EMBEZZLEMENT',
            'MONEY LAUNDERING', 'COUNTERFEITING', 'SCAM',
            'IPC 420', 'IPC 467', 'IPC 468', 'IPC 471',
            'SECTION 420', 'ECONOMIC OFFENCE', 'BANK FRAUD',
            'GST FRAUD', 'TAX EVASION', 'BENAMI', 'SHELL COMPANY',
            'HAWALA', 'PONZI SCHEME', 'PYRAMID SCHEME'
        ]
        
        self.risk_thresholds = {
            'low': 0.3,
            'medium': 0.5,
            'high': 0.7,
            'critical': 0.85
        }
    
    def analyze_msme_synthetic_risk(
        self,
        business_data: Dict,
        directors_data: List[Dict],
        gstin_data: Optional[Dict] = None,
        criminal_records: Optional[List[Dict]] = None,
        mca_data: Optional[Dict] = None
    ) -> Dict:
        """
        Comprehensive MSME synthetic identity and fraud detection.
        
        Args:
            business_data: Business details (name, GST, PAN, address, etc.)
            directors_data: List of directors/promoters with their details
            gstin_data: GST verification data
            criminal_records: Criminal background check results
            mca_data: MCA/ROC registration data
            
        Returns:
            Dict with risk scores and detailed findings
        """
        results = {
            'synthetic_business_risk_score': 0.0,
            'director_criminal_risk_score': 0.0,
            'overall_fraud_risk_score': 0.0,
            'risk_level': 'low',
            'is_high_risk': False,
            'red_flags': [],
            'checks': {}
        }
        
        total_risk = 0.0
        
        # Check 1: Director Criminal History (CRITICAL)
        criminal_risk, criminal_details = self._check_director_criminal_history(
            directors_data, criminal_records
        )
        total_risk += criminal_risk
        results['director_criminal_risk_score'] = criminal_risk
        results['checks']['director_criminal_history'] = criminal_details
        
        # Check 2: Business Identity Verification
        business_risk, business_details = self._check_business_identity(
            business_data, gstin_data, mca_data
        )
        total_risk += business_risk
        results['checks']['business_identity'] = business_details
        
        # Check 3: Director Identity Consistency
        director_risk, director_details = self._check_director_consistency(
            directors_data, business_data
        )
        total_risk += director_risk
        results['checks']['director_consistency'] = director_details
        
        # Check 4: Business Age vs Operations
        operation_risk, operation_details = self._check_business_operations(
            business_data, gstin_data
        )
        total_risk += operation_risk
        results['checks']['business_operations'] = operation_details
        
        # Check 5: Shell Company Indicators
        shell_risk, shell_details = self._check_shell_company_indicators(
            business_data, directors_data, mca_data
        )
        total_risk += shell_risk
        results['checks']['shell_company_indicators'] = shell_details
        
        # Calculate overall scores
        results['synthetic_business_risk_score'] = min(total_risk - criminal_risk, 1.0)
        results['overall_fraud_risk_score'] = min(total_risk, 1.0)
        
        # Determine risk level
        if results['overall_fraud_risk_score'] >= self.risk_thresholds['critical']:
            results['risk_level'] = 'critical'
            results['is_high_risk'] = True
        elif results['overall_fraud_risk_score'] >= self.risk_thresholds['high']:
            results['risk_level'] = 'high'
            results['is_high_risk'] = True
        elif results['overall_fraud_risk_score'] >= self.risk_thresholds['medium']:
            results['risk_level'] = 'medium'
            results['is_high_risk'] = True
        else:
            results['risk_level'] = 'low'
        
        # Compile red flags
        for check_name, check_data in results['checks'].items():
            if isinstance(check_data, dict) and check_data.get('flags'):
                results['red_flags'].extend(check_data['flags'])
        
        return results
    
    def _check_director_criminal_history(
        self,
        directors_data: List[Dict],
        criminal_records: Optional[List[Dict]]
    ) -> Tuple[float, Dict]:
        """
        Check criminal history of all directors/promoters.
        
        CRITICAL CHECK - Financial fraud history is deal-breaker.
        
        Returns:
            (risk_score, details_dict)
        """
        details = {
            'directors_checked': len(directors_data),
            'directors_with_records': 0,
            'financial_fraud_cases': 0,
            'pending_cases': 0,
            'convicted_directors': 0,
            'director_details': [],
            'flags': []
        }
        
        risk = 0.0
        
        if not criminal_records:
            details['status'] = 'not_verified'
            details['flags'].append("Criminal history not verified")
            return 0.1, details  # Small risk for not checking
        
        # Check each director
        for director in directors_data:
            director_name = director.get('name', '').upper()
            director_pan = director.get('pan', '')
            director_aadhaar = director.get('aadhaar', '')
            
            director_info = {
                'name': director_name,
                'pan': director_pan,
                'has_criminal_record': False,
                'financial_crimes': 0,
                'severity': 'clean'
            }
            
            # Match criminal records to this director
            director_records = [
                rec for rec in criminal_records
                if self._match_person(rec, director_name, director_pan, director_aadhaar)
            ]
            
            if director_records:
                details['directors_with_records'] += 1
                director_info['has_criminal_record'] = True
                
                for record in director_records:
                    offense = str(record.get('offense', '')).upper()
                    status = str(record.get('status', '')).upper()
                    
                    # Check if it's a financial/fraud crime
                    is_financial_crime = any(pattern in offense for pattern in self.criminal_patterns)
                    
                    if is_financial_crime:
                        details['financial_fraud_cases'] += 1
                        director_info['financial_crimes'] += 1
                        
                        if 'CONVICTED' in status or 'GUILTY' in status:
                            risk += 0.5  # CRITICAL - Convicted fraudster as director
                            details['convicted_directors'] += 1
                            director_info['severity'] = 'critical'
                            details['flags'].append(
                                f"Director {director_name[:20]} convicted: {offense[:50]}"
                            )
                        
                        elif 'PENDING' in status or 'UNDER TRIAL' in status:
                            risk += 0.3  # HIGH - Pending fraud case
                            details['pending_cases'] += 1
                            director_info['severity'] = 'high'
                            details['flags'].append(
                                f"Director {director_name[:20]} pending case: {offense[:50]}"
                            )
                        
                        elif 'ACQUITTED' in status:
                            risk += 0.1  # LOW - Acquitted but history exists
                            director_info['severity'] = 'low'
                    
                    else:
                        # Non-financial crimes (lower risk but still relevant)
                        if 'CONVICTED' in status:
                            risk += 0.1
                            director_info['severity'] = max(director_info['severity'], 'medium') \
                                if director_info['severity'] != 'critical' else 'critical'
            
            details['director_details'].append(director_info)
        
        # Additional risk for multiple directors with records
        if details['directors_with_records'] > 1:
            risk += 0.2
            details['flags'].append(f"Multiple directors ({details['directors_with_records']}) with criminal records")
        
        return min(risk, 0.8), details
    
    def _check_business_identity(
        self,
        business_data: Dict,
        gstin_data: Optional[Dict],
        mca_data: Optional[Dict]
    ) -> Tuple[float, Dict]:
        """
        Verify business identity authenticity.
        
        Checks:
        - GST registration validity
        - PAN-GST linkage
        - MCA registration
        - Address verification
        
        Returns:
            (risk_score, details_dict)
        """
        details = {
            'gst_verified': False,
            'pan_verified': False,
            'mca_verified': False,
            'address_verified': False,
            'flags': []
        }
        
        risk = 0.0
        
        # Check GST verification
        business_gstin = business_data.get('gstin', '')
        
        if gstin_data:
            gst_status = gstin_data.get('status', '').upper()
            
            if gst_status == 'ACTIVE':
                details['gst_verified'] = True
            elif gst_status == 'CANCELLED' or gst_status == 'SUSPENDED':
                risk += 0.3
                details['flags'].append(f"GST status: {gst_status}")
            else:
                risk += 0.2
                details['flags'].append("GST status unclear")
            
            # Check PAN-GST linkage
            gst_pan = gstin_data.get('pan', '')
            business_pan = business_data.get('pan', '')
            
            if gst_pan and business_pan:
                if gst_pan.upper() == business_pan.upper():
                    details['pan_verified'] = True
                else:
                    risk += 0.25
                    details['flags'].append("PAN-GST mismatch")
            
            # Check business name match
            gst_name = gstin_data.get('legal_name', '').upper()
            business_name = business_data.get('name', '').upper()
            
            if gst_name and business_name:
                if not self._names_similar(gst_name, business_name):
                    risk += 0.15
                    details['flags'].append("Business name mismatch with GST")
        else:
            if business_gstin:
                risk += 0.15
                details['flags'].append("GST not verified")
        
        # Check MCA registration
        if mca_data:
            mca_status = mca_data.get('status', '').upper()
            
            if mca_status == 'ACTIVE':
                details['mca_verified'] = True
            else:
                risk += 0.2
                details['flags'].append(f"MCA status: {mca_status}")
        
        # Check if no verifications done
        if not any([details['gst_verified'], details['pan_verified'], details['mca_verified']]):
            risk += 0.2
            details['flags'].append("No business identity verification completed")
        
        return min(risk, 0.4), details
    
    def _check_director_consistency(
        self,
        directors_data: List[Dict],
        business_data: Dict
    ) -> Tuple[float, Dict]:
        """
        Check director identity consistency.
        
        Red Flags:
        - Missing director details
        - Name/document inconsistencies
        - Too many directors for small business
        - Director address same as business (shell company indicator)
        
        Returns:
            (risk_score, details_dict)
        """
        details = {
            'total_directors': len(directors_data),
            'verified_directors': 0,
            'incomplete_profiles': 0,
            'flags': []
        }
        
        risk = 0.0
        
        if not directors_data:
            risk += 0.3
            details['flags'].append("No director information provided")
            return risk, details
        
        for director in directors_data:
            # Check completeness
            required_fields = ['name', 'pan', 'aadhaar', 'address']
            missing_fields = [f for f in required_fields if not director.get(f)]
            
            if missing_fields:
                details['incomplete_profiles'] += 1
                risk += 0.05
            else:
                details['verified_directors'] += 1
            
            # Check if director address is same as business address
            director_addr = str(director.get('address', '')).upper()
            business_addr = str(business_data.get('registered_address', '')).upper()
            
            if director_addr and business_addr:
                if director_addr == business_addr:
                    risk += 0.1
                    details['flags'].append(f"Director address same as business address")
        
        # Too many directors for MSME
        if len(directors_data) > 5:
            risk += 0.1
            details['flags'].append(f"Unusually many directors ({len(directors_data)}) for MSME")
        
        # Incomplete profiles
        if details['incomplete_profiles'] > 0:
            details['flags'].append(f"{details['incomplete_profiles']} directors with incomplete information")
        
        return min(risk, 0.3), details
    
    def _check_business_operations(
        self,
        business_data: Dict,
        gstin_data: Optional[Dict]
    ) -> Tuple[float, Dict]:
        """
        Check if business operations are authentic.
        
        Red Flags:
        - Very new business with high turnover claims
        - No GST filings
        - Irregular filing patterns
        - Claimed revenue not matching GST returns
        
        Returns:
            (risk_score, details_dict)
        """
        details = {
            'business_age_months': None,
            'gst_filings_count': 0,
            'filing_regular': True,
            'revenue_mismatch': False,
            'flags': []
        }
        
        risk = 0.0
        
        # Check business age
        incorporation_date = business_data.get('incorporation_date')
        if incorporation_date:
            try:
                if isinstance(incorporation_date, str):
                    incorporation_date = pd.to_datetime(incorporation_date)
                
                age_days = (datetime.now() - incorporation_date).days
                details['business_age_months'] = age_days // 30
                
                # Very new business
                if age_days < 180:  # Less than 6 months
                    claimed_revenue = business_data.get('annual_turnover', 0)
                    
                    if claimed_revenue > 5000000:  # >50L revenue in <6 months
                        risk += 0.2
                        details['flags'].append(f"New business ({age_days} days) with high revenue claims")
            except:
                pass
        
        # Check GST filings
        if gstin_data:
            filings = gstin_data.get('filings', [])
            details['gst_filings_count'] = len(filings)
            
            if details['business_age_months'] and details['business_age_months'] > 6:
                expected_filings = details['business_age_months']  # Monthly filings
                
                if len(filings) < expected_filings * 0.5:  # Less than 50% expected filings
                    risk += 0.15
                    details['filing_regular'] = False
                    details['flags'].append("Irregular GST filing pattern")
            
            # Check revenue consistency
            if filings:
                gst_revenue = sum(filing.get('turnover', 0) for filing in filings[-12:])  # Last 12 months
                claimed_revenue = business_data.get('annual_turnover', 0)
                
                if claimed_revenue > 0 and gst_revenue > 0:
                    ratio = abs(claimed_revenue - gst_revenue) / claimed_revenue
                    
                    if ratio > 0.5:  # >50% mismatch
                        risk += 0.25
                        details['revenue_mismatch'] = True
                        details['flags'].append(f"Revenue mismatch: Claimed ₹{claimed_revenue/100000}L vs GST ₹{gst_revenue/100000}L")
        
        return min(risk, 0.4), details
    
    def _check_shell_company_indicators(
        self,
        business_data: Dict,
        directors_data: List[Dict],
        mca_data: Optional[Dict]
    ) -> Tuple[float, Dict]:
        """
        Check for shell company indicators.
        
        Red Flags:
        - Multiple businesses at same address
        - Circular ownership
        - No employees
        - Virtual office address
        - Director in many companies
        
        Returns:
            (risk_score, details_dict)
        """
        details = {
            'shell_company_indicators': 0,
            'flags': []
        }
        
        risk = 0.0
        
        # Check employee count
        employee_count = business_data.get('employee_count', 0)
        annual_turnover = business_data.get('annual_turnover', 0)
        
        if employee_count == 0 and annual_turnover > 1000000:  # No employees but 10L+ revenue
            risk += 0.15
            details['shell_company_indicators'] += 1
            details['flags'].append("No employees despite significant revenue")
        
        # Check if director is in too many companies
        if mca_data:
            for director in directors_data:
                director_din = director.get('din', '')
                if director_din:
                    director_companies = mca_data.get(f'companies_{director_din}', [])
                    
                    if len(director_companies) > 10:
                        risk += 0.2
                        details['shell_company_indicators'] += 1
                        details['flags'].append(f"Director in {len(director_companies)} companies")
        
        # Check business address type
        business_address = str(business_data.get('registered_address', '')).lower()
        virtual_office_indicators = ['coworking', 'virtual office', 'business center', 'shared space']
        
        if any(indicator in business_address for indicator in virtual_office_indicators):
            risk += 0.1
            details['shell_company_indicators'] += 1
            details['flags'].append("Virtual/shared office address")
        
        return min(risk, 0.3), details
    
    # Helper methods
    
    def _match_person(
        self,
        record: Dict,
        name: str,
        pan: str,
        aadhaar: str
    ) -> bool:
        """Match criminal record to person using name, PAN, or Aadhaar."""
        record_name = str(record.get('name', '')).upper()
        record_pan = str(record.get('pan', '')).upper()
        record_aadhaar = str(record.get('aadhaar', ''))
        
        # Match by PAN (most reliable)
        if pan and record_pan and pan.upper() == record_pan:
            return True
        
        # Match by Aadhaar
        if aadhaar and record_aadhaar and aadhaar == record_aadhaar:
            return True
        
        # Match by name (less reliable)
        if name and record_name:
            return self._names_similar(name, record_name)
        
        return False
    
    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if two names are similar."""
        if not name1 or not name2:
            return False
        
        name1_parts = set(name1.split())
        name2_parts = set(name2.split())
        
        common_parts = name1_parts.intersection(name2_parts)
        return len(common_parts) >= len(name1_parts) * 0.5

