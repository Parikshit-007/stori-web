"""
Synthetic Identity Fraud Detection Module

Detects synthetic identities created by combining real and fake information.
Includes criminal history verification, pattern analysis, and risk scoring.

Author: Stori Credit Scoring System
Date: 2026-01-15
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta
import re
import warnings


class SyntheticIdentityDetector:
    """
    Detect synthetic identity fraud using multiple verification layers.
    
    Synthetic Identity Fraud: Creating fake identities using combination of:
    - Real SSN/Aadhaar (often from children or deceased)
    - Fake name, address, phone
    - Manipulated documents
    
    Detection Methods:
    1. Criminal History Verification
    2. Identity Consistency Checks
    3. Digital Footprint Analysis
    4. Document Anomaly Detection
    5. Behavioral Pattern Analysis
    """
    
    def __init__(self):
        """Initialize detector with thresholds and patterns."""
        self.risk_thresholds = {
            'low': 0.3,
            'medium': 0.5,
            'high': 0.7,
            'critical': 0.85
        }
        
        # Criminal record red flags
        self.criminal_patterns = [
            'FRAUD', 'FORGERY', 'IDENTITY THEFT', 'CHEATING',
            'FINANCIAL FRAUD', 'CYBER CRIME', 'EMBEZZLEMENT',
            'MONEY LAUNDERING', 'COUNTERFEITING', 'SCAM',
            'IPC 420', 'IPC 467', 'IPC 468', 'IPC 471',  # Indian Penal Code sections
            'SECTION 420', 'ECONOMIC OFFENCE', 'BANK FRAUD'
        ]
    
    def detect_synthetic_identity(
        self,
        applicant_data: Dict,
        bank_data: Optional[pd.DataFrame] = None,
        criminal_records: Optional[List[Dict]] = None,
        cibil_data: Optional[Dict] = None
    ) -> Dict[str, Union[float, str, bool, Dict]]:
        """
        Comprehensive synthetic identity detection.
        
        Args:
            applicant_data: Personal details (name, age, address, phone, etc.)
            bank_data: Bank statement transactions
            criminal_records: Criminal record check results
            cibil_data: Credit bureau data
            
        Returns:
            Dict with synthetic identity risk score and detailed flags
        """
        results = {
            'synthetic_identity_risk_score': 0.0,
            'risk_level': 'low',
            'is_suspicious': False,
            'red_flags': [],
            'checks': {}
        }
        
        risk_score = 0.0
        
        # Check 1: Criminal History Verification
        criminal_risk, criminal_details = self._check_criminal_history(
            applicant_data, criminal_records
        )
        risk_score += criminal_risk
        results['checks']['criminal_history'] = criminal_details
        
        # Check 2: Identity Consistency
        identity_risk, identity_details = self._check_identity_consistency(
            applicant_data
        )
        risk_score += identity_risk
        results['checks']['identity_consistency'] = identity_details
        
        # Check 3: Age and Document Anomalies
        age_risk, age_details = self._check_age_anomalies(
            applicant_data, cibil_data
        )
        risk_score += age_risk
        results['checks']['age_anomalies'] = age_details
        
        # Check 4: Digital Footprint
        digital_risk, digital_details = self._check_digital_footprint(
            applicant_data
        )
        risk_score += digital_risk
        results['checks']['digital_footprint'] = digital_details
        
        # Check 5: Bank Statement Patterns
        if bank_data is not None:
            bank_risk, bank_details = self._check_bank_patterns(
                bank_data, applicant_data
            )
            risk_score += bank_risk
            results['checks']['bank_patterns'] = bank_details
        
        # Check 6: Credit Bureau Anomalies
        if cibil_data is not None:
            bureau_risk, bureau_details = self._check_bureau_anomalies(
                cibil_data, applicant_data
            )
            risk_score += bureau_risk
            results['checks']['bureau_anomalies'] = bureau_details
        
        # Cap risk score at 1.0
        results['synthetic_identity_risk_score'] = min(risk_score, 1.0)
        
        # Determine risk level
        if results['synthetic_identity_risk_score'] >= self.risk_thresholds['critical']:
            results['risk_level'] = 'critical'
            results['is_suspicious'] = True
        elif results['synthetic_identity_risk_score'] >= self.risk_thresholds['high']:
            results['risk_level'] = 'high'
            results['is_suspicious'] = True
        elif results['synthetic_identity_risk_score'] >= self.risk_thresholds['medium']:
            results['risk_level'] = 'medium'
            results['is_suspicious'] = True
        else:
            results['risk_level'] = 'low'
        
        # Compile red flags
        for check_name, check_data in results['checks'].items():
            if isinstance(check_data, dict) and check_data.get('flags'):
                results['red_flags'].extend(check_data['flags'])
        
        return results
    
    def _check_criminal_history(
        self,
        applicant_data: Dict,
        criminal_records: Optional[List[Dict]]
    ) -> Tuple[float, Dict]:
        """
        Check criminal history for fraud-related offenses.
        
        Red Flags:
        - Financial fraud convictions
        - Identity theft cases
        - Forgery/counterfeiting
        - Pending cases in financial crimes
        
        Returns:
            (risk_score, details_dict)
        """
        details = {
            'has_criminal_record': False,
            'financial_crimes': 0,
            'identity_crimes': 0,
            'pending_cases': 0,
            'flags': [],
            'severity': 'none'
        }
        
        risk = 0.0
        
        if not criminal_records or len(criminal_records) == 0:
            # No records provided - neutral (could be clean or not checked)
            details['status'] = 'not_verified'
            return 0.0, details
        
        details['has_criminal_record'] = True
        
        for record in criminal_records:
            offense = str(record.get('offense', '')).upper()
            status = str(record.get('status', '')).upper()
            
            # Check for financial/identity fraud patterns
            is_financial_crime = any(pattern in offense for pattern in self.criminal_patterns)
            
            if is_financial_crime:
                details['financial_crimes'] += 1
                
                # Severity based on status
                if 'CONVICTED' in status or 'GUILTY' in status:
                    risk += 0.4  # High risk - convicted fraudster
                    details['flags'].append(f"Convicted: {offense}")
                    details['severity'] = 'critical'
                elif 'PENDING' in status or 'UNDER TRIAL' in status:
                    risk += 0.2  # Medium risk - pending case
                    details['flags'].append(f"Pending case: {offense}")
                    details['severity'] = max(details['severity'], 'high') if details['severity'] != 'critical' else 'critical'
                    details['pending_cases'] += 1
                elif 'ACQUITTED' in status:
                    risk += 0.05  # Low risk - acquitted but history exists
                    details['flags'].append(f"Acquitted: {offense}")
            
            # Check specifically for identity crimes
            if any(pattern in offense for pattern in ['IDENTITY', 'FORGERY', 'COUNTERFE']):
                details['identity_crimes'] += 1
                risk += 0.1  # Additional risk for identity-specific crimes
        
        # Name mismatch with criminal records
        applicant_name = applicant_data.get('name', '').upper()
        for record in criminal_records:
            record_name = str(record.get('name', '')).upper()
            if applicant_name and record_name:
                # Check if names are significantly different (not just spelling)
                if applicant_name != record_name and not self._names_similar(applicant_name, record_name):
                    risk += 0.15
                    details['flags'].append("Name mismatch with criminal record")
        
        return min(risk, 0.6), details  # Cap at 0.6 for this check
    
    def _check_identity_consistency(self, applicant_data: Dict) -> Tuple[float, Dict]:
        """
        Check consistency across identity documents.
        
        Red Flags:
        - Name variations across documents
        - Address inconsistencies
        - Phone/email pattern mismatches
        - Missing key documents
        
        Returns:
            (risk_score, details_dict)
        """
        details = {
            'name_consistent': True,
            'address_consistent': True,
            'contact_consistent': True,
            'documents_complete': True,
            'flags': []
        }
        
        risk = 0.0
        
        # Check name consistency
        name_variations = [
            applicant_data.get('name', ''),
            applicant_data.get('pan_name', ''),
            applicant_data.get('aadhaar_name', ''),
            applicant_data.get('bank_account_name', '')
        ]
        name_variations = [n.upper().strip() for n in name_variations if n]
        
        if len(set(name_variations)) > 1:
            # Multiple different names
            unique_names = len(set(name_variations))
            if unique_names > 2:
                risk += 0.2
                details['name_consistent'] = False
                details['flags'].append(f"Multiple name variations detected ({unique_names})")
        
        # Check address consistency
        addresses = [
            applicant_data.get('current_address', ''),
            applicant_data.get('permanent_address', ''),
            applicant_data.get('aadhaar_address', '')
        ]
        addresses = [a.upper().strip() for a in addresses if a]
        
        if len(addresses) >= 2:
            # Check if addresses are completely different (not just format)
            if not self._addresses_similar(addresses):
                risk += 0.15
                details['address_consistent'] = False
                details['flags'].append("Significant address inconsistencies")
        
        # Check phone/email patterns
        phone = str(applicant_data.get('phone', ''))
        email = str(applicant_data.get('email', ''))
        
        # Suspicious phone patterns
        if phone:
            if len(set(phone)) <= 2:  # Too repetitive (e.g., 9999999999)
                risk += 0.1
                details['contact_consistent'] = False
                details['flags'].append("Suspicious phone number pattern")
        
        # Suspicious email patterns
        if email:
            if any(pattern in email.lower() for pattern in ['temp', 'fake', 'test', '123', 'xyz']):
                risk += 0.1
                details['contact_consistent'] = False
                details['flags'].append("Suspicious email pattern")
        
        # Check document completeness
        required_docs = ['pan', 'aadhaar', 'address_proof']
        missing_docs = [doc for doc in required_docs if not applicant_data.get(f'{doc}_verified', False)]
        
        if missing_docs:
            risk += 0.05 * len(missing_docs)
            details['documents_complete'] = False
            details['flags'].append(f"Missing documents: {', '.join(missing_docs)}")
        
        return min(risk, 0.4), details
    
    def _check_age_anomalies(
        self,
        applicant_data: Dict,
        cibil_data: Optional[Dict]
    ) -> Tuple[float, Dict]:
        """
        Check age-related anomalies common in synthetic identities.
        
        Red Flags:
        - Very young applicant with established credit history
        - Recent credit file creation for older applicant
        - DOB inconsistencies
        
        Returns:
            (risk_score, details_dict)
        """
        details = {
            'age': None,
            'credit_file_age': None,
            'suspicious_age_pattern': False,
            'flags': []
        }
        
        risk = 0.0
        
        # Get applicant age
        dob = applicant_data.get('date_of_birth')
        if dob:
            try:
                if isinstance(dob, str):
                    dob = pd.to_datetime(dob)
                age = (datetime.now() - dob).days // 365
                details['age'] = age
                
                # Check if age is suspiciously young for credit activity
                if age < 21 and cibil_data:
                    credit_accounts = cibil_data.get('total_accounts', 0)
                    if credit_accounts > 3:
                        risk += 0.15
                        details['suspicious_age_pattern'] = True
                        details['flags'].append(f"Young applicant ({age}) with {credit_accounts} credit accounts")
                
                # Check if age is unrealistic
                if age < 18 or age > 100:
                    risk += 0.3
                    details['flags'].append(f"Unrealistic age: {age}")
                
            except Exception as e:
                details['flags'].append("Invalid date of birth")
                risk += 0.1
        
        # Check credit file age vs applicant age
        if cibil_data:
            credit_file_date = cibil_data.get('file_creation_date')
            if credit_file_date and dob:
                try:
                    if isinstance(credit_file_date, str):
                        credit_file_date = pd.to_datetime(credit_file_date)
                    
                    file_age_days = (datetime.now() - credit_file_date).days
                    details['credit_file_age'] = file_age_days // 365
                    
                    # Recently created credit file for middle-aged person
                    if details['age'] and details['age'] > 30 and file_age_days < 365:
                        risk += 0.2
                        details['suspicious_age_pattern'] = True
                        details['flags'].append(f"Recent credit file ({file_age_days} days) for age {details['age']}")
                    
                    # Credit file created when person was a minor
                    age_at_file_creation = details['age'] - (file_age_days // 365)
                    if age_at_file_creation < 18:
                        risk += 0.25
                        details['flags'].append(f"Credit file created when applicant was {age_at_file_creation} years old")
                
                except Exception:
                    pass
        
        return min(risk, 0.4), details
    
    def _check_digital_footprint(self, applicant_data: Dict) -> Tuple[float, Dict]:
        """
        Check digital footprint and online presence.
        
        Red Flags:
        - No social media presence for claimed age
        - Newly created email accounts
        - VOIP/virtual phone numbers
        - No online history
        
        Returns:
            (risk_score, details_dict)
        """
        details = {
            'email_age_days': None,
            'phone_type': 'unknown',
            'social_media_presence': False,
            'flags': []
        }
        
        risk = 0.0
        
        # Check email domain
        email = str(applicant_data.get('email', '')).lower()
        if email:
            domain = email.split('@')[-1] if '@' in email else ''
            
            # Temporary email services
            temp_domains = ['temp-mail', 'guerrillamail', '10minutemail', 'throwaway', 'maildrop']
            if any(temp in domain for temp in temp_domains):
                risk += 0.2
                details['flags'].append("Temporary email service detected")
            
            # Check if email creation date is recent (if available)
            email_created = applicant_data.get('email_creation_date')
            if email_created:
                try:
                    if isinstance(email_created, str):
                        email_created = pd.to_datetime(email_created)
                    days_old = (datetime.now() - email_created).days
                    details['email_age_days'] = days_old
                    
                    if days_old < 30:  # Email less than 30 days old
                        risk += 0.15
                        details['flags'].append(f"Very new email account ({days_old} days)")
                except Exception:
                    pass
        
        # Check phone type (if available)
        phone_type = applicant_data.get('phone_type', '').lower()
        details['phone_type'] = phone_type
        
        if 'voip' in phone_type or 'virtual' in phone_type:
            risk += 0.1
            details['flags'].append("VOIP/virtual phone number")
        
        # Check social media presence
        has_social_media = applicant_data.get('linkedin_verified', False) or \
                          applicant_data.get('facebook_verified', False)
        details['social_media_presence'] = has_social_media
        
        age = applicant_data.get('age')
        if age and age > 25 and not has_social_media:
            # Older person with no social media presence (unusual but not definitive)
            risk += 0.05
            details['flags'].append("No verified social media presence")
        
        return min(risk, 0.3), details
    
    def _check_bank_patterns(
        self,
        bank_data: pd.DataFrame,
        applicant_data: Dict
    ) -> Tuple[float, Dict]:
        """
        Check bank statement patterns for synthetic identity indicators.
        
        Red Flags:
        - Very recent account opening
        - Minimal organic transactions
        - Suspicious transaction patterns
        - Name mismatches
        
        Returns:
            (risk_score, details_dict)
        """
        details = {
            'account_age_months': None,
            'organic_transaction_ratio': 0.0,
            'flags': []
        }
        
        risk = 0.0
        
        if bank_data.empty:
            return 0.0, details
        
        # Check account age
        if 'txn_date' in bank_data.columns:
            bank_data['txn_date'] = pd.to_datetime(bank_data['txn_date'])
            first_txn = bank_data['txn_date'].min()
            account_age_days = (datetime.now() - first_txn).days
            details['account_age_months'] = account_age_days // 30
            
            # Very new account
            if account_age_days < 90:  # Less than 3 months
                risk += 0.15
                details['flags'].append(f"Very new bank account ({account_age_days} days)")
        
        # Check transaction variety (organic vs structured)
        if 'description' in bank_data.columns:
            # Count unique merchants/descriptions
            unique_descriptions = bank_data['description'].nunique()
            total_txns = len(bank_data)
            
            variety_ratio = unique_descriptions / total_txns if total_txns > 0 else 0
            details['organic_transaction_ratio'] = float(variety_ratio)
            
            # Low variety indicates non-organic patterns
            if variety_ratio < 0.3 and total_txns > 20:
                risk += 0.1
                details['flags'].append("Low transaction variety - possible structured activity")
        
        # Check for name in bank account vs application
        bank_account_name = str(applicant_data.get('bank_account_name', '')).upper()
        applicant_name = str(applicant_data.get('name', '')).upper()
        
        if bank_account_name and applicant_name:
            if not self._names_similar(bank_account_name, applicant_name):
                risk += 0.2
                details['flags'].append("Bank account name mismatch with application")
        
        return min(risk, 0.3), details
    
    def _check_bureau_anomalies(
        self,
        cibil_data: Dict,
        applicant_data: Dict
    ) -> Tuple[float, Dict]:
        """
        Check credit bureau data for synthetic identity patterns.
        
        Red Flags:
        - Thin file with recent activity
        - Only authorized user accounts (piggybacking)
        - Rapid account additions
        - No inquiries before accounts
        
        Returns:
            (risk_score, details_dict)
        """
        details = {
            'thin_file': False,
            'authorized_user_accounts': 0,
            'rapid_credit_building': False,
            'flags': []
        }
        
        risk = 0.0
        
        # Check for thin file
        total_accounts = cibil_data.get('total_accounts', 0)
        file_age_years = cibil_data.get('file_age_years', 0)
        
        details['thin_file'] = total_accounts < 3 and file_age_years < 2
        
        if details['thin_file']:
            risk += 0.1
            details['flags'].append("Thin credit file")
        
        # Check for authorized user accounts (credit piggybacking)
        au_accounts = cibil_data.get('authorized_user_accounts', 0)
        details['authorized_user_accounts'] = au_accounts
        
        if au_accounts > 0 and au_accounts == total_accounts:
            # All accounts are authorized user (synthetic identity tactic)
            risk += 0.3
            details['flags'].append("All accounts are authorized user accounts")
        
        # Check for rapid credit building
        if file_age_years < 1 and total_accounts > 5:
            risk += 0.2
            details['rapid_credit_building'] = True
            details['flags'].append(f"Rapid credit building: {total_accounts} accounts in {file_age_years} years")
        
        # Check for inquiries vs accounts ratio
        inquiries = cibil_data.get('inquiries_last_12m', 0)
        new_accounts = cibil_data.get('new_accounts_last_12m', 0)
        
        if new_accounts > inquiries and new_accounts > 0:
            # Accounts opened without inquiries (unusual)
            risk += 0.15
            details['flags'].append("Accounts opened without corresponding inquiries")
        
        # Check for address variations in bureau
        bureau_addresses = cibil_data.get('address_count', 0)
        if bureau_addresses > 5:
            risk += 0.1
            details['flags'].append(f"Multiple addresses in credit file ({bureau_addresses})")
        
        return min(risk, 0.4), details
    
    # Helper methods
    
    def _names_similar(self, name1: str, name2: str) -> bool:
        """Check if two names are similar (allowing for minor variations)."""
        if not name1 or not name2:
            return False
        
        # Remove common prefixes/suffixes
        for title in ['MR', 'MRS', 'MS', 'DR', 'PROF']:
            name1 = name1.replace(title, '').strip()
            name2 = name2.replace(title, '').strip()
        
        # Simple similarity check
        name1_parts = set(name1.split())
        name2_parts = set(name2.split())
        
        # Check if at least 50% of name parts match
        common_parts = name1_parts.intersection(name2_parts)
        return len(common_parts) >= len(name1_parts) * 0.5
    
    def _addresses_similar(self, addresses: List[str]) -> bool:
        """Check if addresses are similar (allowing for format variations)."""
        if len(addresses) < 2:
            return True
        
        # Extract key components (city, pincode)
        def extract_pincode(addr):
            match = re.search(r'\b\d{6}\b', addr)
            return match.group() if match else None
        
        pincodes = [extract_pincode(addr) for addr in addresses]
        pincodes = [p for p in pincodes if p]
        
        # If pincodes are available, check if they match
        if len(pincodes) >= 2:
            return len(set(pincodes)) == 1
        
        # Otherwise, check for common words
        all_words = [set(addr.split()) for addr in addresses]
        common_words = set.intersection(*all_words) if all_words else set()
        
        # At least 30% common words
        return len(common_words) >= len(all_words[0]) * 0.3


def detect_synthetic_identity_simple(applicant_data: Dict) -> Dict:
    """
    Simple wrapper function for basic synthetic identity detection.
    
    Args:
        applicant_data: Applicant information dictionary
        
    Returns:
        Detection results with risk score
    """
    detector = SyntheticIdentityDetector()
    return detector.detect_synthetic_identity(applicant_data)

