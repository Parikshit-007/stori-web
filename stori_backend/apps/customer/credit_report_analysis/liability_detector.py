"""
Comprehensive Liability Detection System
========================================

Combines credit report and bank statement analysis to detect all liabilities:
- Loans (Personal, Home, Auto, etc.)
- Credit Cards
- EMIs
- Outstanding amounts
- Debt-to-Income ratios

Author: Stori Credit Scoring
Date: 2026-01-15
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import re


class LiabilityDetector:
    """
    Detect liabilities from both credit report and bank statements.
    
    Combines multiple data sources for comprehensive liability assessment.
    """
    
    def __init__(self):
        """Initialize detector with patterns and thresholds."""
        # EMI/Loan patterns in bank statements
        self.emi_patterns = [
            r'\bemi\b',
            r'\bloan\b',
            r'\binstallment\b',
            r'\bhome\s*loan',
            r'\bpersonal\s*loan',
            r'\bcar\s*loan',
            r'\bauto\s*loan',
            r'\beducation\s*loan',
            r'\bhl\b',
            r'\bpl\b',
            r'\bel\b',
            r'\bicici\s*loan',
            r'\bhdfc\s*loan',
            r'\bsbi\s*loan',
            r'\baxis\s*loan',
            r'\bbajaj\s*finserv',
            r'\btata\s*capital',
            r'\bfullerton',
            r'\bmuthoot',
            r'\bmanappuram'
        ]
        
        # Credit card payment patterns
        self.cc_patterns = [
            r'\bcredit\s*card',
            r'\bcc\s*payment',
            r'\bcc\s*bill',
            r'\bhdfc\s*cc',
            r'\bicici\s*cc',
            r'\bsbi\s*cc',
            r'\baxis\s*cc',
            r'\bamex',
            r'\bvisa',
            r'\bmastercard',
            r'\bcred\s*app',
            r'\bpaytm\s*cc'
        ]
        
        # Loan provider names
        self.loan_providers = [
            'hdfc', 'icici', 'sbi', 'axis', 'kotak', 'yes bank',
            'bajaj finserv', 'tata capital', 'fullerton', 'muthoot',
            'manappuram', 'home credit', 'money tap', 'early salary',
            'paysense', 'cashe', 'lazypay', 'simpl', 'zestmoney'
        ]
    
    def detect_liabilities(
        self,
        credit_report_data: Optional[Dict] = None,
        bank_statement_df: Optional[pd.DataFrame] = None,
        monthly_income: float = 0.0
    ) -> Dict[str, Any]:
        """
        Comprehensive liability detection from both sources.
        
        Args:
            credit_report_data: Credit report JSON data
            bank_statement_df: Bank statement DataFrame
            monthly_income: Monthly income for ratio calculations
            
        Returns:
            Complete liability analysis with breakdown
        """
        result = {
            'total_liabilities': 0.0,
            'total_monthly_emi': 0.0,
            'active_loans': [],
            'credit_cards': [],
            'liability_sources': {
                'from_credit_report': False,
                'from_bank_statement': False
            },
            'debt_ratios': {},
            'risk_indicators': {}
        }
        
        # Extract from credit report
        credit_liabilities = self._extract_from_credit_report(credit_report_data) if credit_report_data else {}
        
        # Extract from bank statement
        bank_liabilities = self._extract_from_bank_statement(bank_statement_df) if bank_statement_df is not None and not bank_statement_df.empty else {}
        
        # Combine both sources
        combined_liabilities = self._combine_liability_sources(credit_liabilities, bank_liabilities)
        
        # Calculate totals
        result['total_liabilities'] = combined_liabilities.get('total_outstanding', 0.0)
        result['total_monthly_emi'] = combined_liabilities.get('total_monthly_emi', 0.0)
        result['active_loans'] = combined_liabilities.get('loans', [])
        result['credit_cards'] = combined_liabilities.get('credit_cards', [])
        
        # Track sources
        result['liability_sources']['from_credit_report'] = credit_liabilities.get('has_data', False)
        result['liability_sources']['from_bank_statement'] = bank_liabilities.get('has_data', False)
        
        # Calculate debt ratios
        if monthly_income > 0:
            result['debt_ratios'] = {
                'emi_to_income_ratio': (result['total_monthly_emi'] / monthly_income) * 100,
                'debt_to_income_ratio': (result['total_liabilities'] / (monthly_income * 12)) * 100,
                'total_obligation_ratio': (result['total_monthly_emi'] / monthly_income) * 100
            }
        else:
            result['debt_ratios'] = {
                'emi_to_income_ratio': 0.0,
                'debt_to_income_ratio': 0.0,
                'total_obligation_ratio': 0.0
            }
        
        # Risk indicators
        result['risk_indicators'] = self._assess_liability_risk(
            result['total_liabilities'],
            result['total_monthly_emi'],
            monthly_income,
            combined_liabilities
        )
        
        return result
    
    def _extract_from_credit_report(self, credit_data: Dict) -> Dict[str, Any]:
        """
        Extract liabilities from credit report.
        
        Expected format:
        {
            "accounts": [
                {
                    "account_type": "loan" | "credit_card",
                    "status": "active" | "closed",
                    "outstanding": 500000,
                    "emi": 15000,
                    "bank": "HDFC",
                    "loan_type": "home_loan" | "personal_loan" | etc.
                }
            ]
        }
        """
        result = {
            'has_data': False,
            'loans': [],
            'credit_cards': [],
            'total_outstanding': 0.0,
            'total_monthly_emi': 0.0
        }
        
        if not credit_data or not isinstance(credit_data, dict):
            return result
        
        accounts = credit_data.get('accounts', [])
        if not isinstance(accounts, list):
            return result
        
        result['has_data'] = True
        
        for account in accounts:
            if not isinstance(account, dict):
                continue
            
            # Only process active accounts
            if account.get('status', '').lower() != 'active':
                continue
            
            account_type = account.get('account_type', account.get('type', '')).lower()
            outstanding = float(account.get('outstanding', 0))
            emi = float(account.get('emi', account.get('monthly_payment', 0)))
            bank = account.get('bank', account.get('lender', 'Unknown'))
            loan_type = account.get('loan_type', account.get('account_type', 'loan'))
            
            liability_item = {
                'source': 'credit_report',
                'type': account_type,
                'bank': bank,
                'outstanding': outstanding,
                'monthly_emi': emi,
                'loan_type': loan_type if account_type == 'loan' else None,
                'credit_limit': float(account.get('credit_limit', 0)) if account_type == 'credit_card' else 0,
                'utilization': float(account.get('utilization', 0)) if account_type == 'credit_card' else 0,
                'dpd': int(account.get('dpd', 0)),
                'account_number': account.get('account_number', '')
            }
            
            if account_type in ['loan', 'personal_loan', 'home_loan', 'auto_loan', 'education_loan']:
                result['loans'].append(liability_item)
                result['total_outstanding'] += outstanding
                result['total_monthly_emi'] += emi
            elif account_type == 'credit_card':
                result['credit_cards'].append(liability_item)
                result['total_outstanding'] += outstanding
                # Credit card minimum payment (typically 5% of outstanding)
                if emi == 0 and outstanding > 0:
                    emi = outstanding * 0.05  # 5% minimum payment
                result['total_monthly_emi'] += emi
        
        return result
    
    def _extract_from_bank_statement(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Extract liabilities from bank statement patterns.
        
        Detects:
        - Recurring EMI payments
        - Credit card payments
        - Loan-related transactions
        """
        result = {
            'has_data': False,
            'loans': [],
            'credit_cards': [],
            'total_outstanding': 0.0,
            'total_monthly_emi': 0.0,
            'detected_emi_patterns': []
        }
        
        if df.empty or 'description' not in df.columns:
            return result
        
        result['has_data'] = True
        
        # Normalize description column
        df = df.copy()
        df['description'] = df['description'].astype(str).str.lower()
        
        # Normalize type column
        if 'type' in df.columns:
            df['type'] = df['type'].str.upper()
        else:
            df['type'] = 'DR'  # Default to debit
        
        # Filter debit transactions only
        debits = df[df['type'] == 'DR'].copy()
        
        if debits.empty:
            return result
        
        # Detect EMI patterns
        emi_pattern = '|'.join(self.emi_patterns)
        emi_mask = debits['description'].str.contains(emi_pattern, case=False, regex=True, na=False)
        emi_transactions = debits[emi_mask].copy()
        
        if not emi_transactions.empty:
            # Group by amount to find recurring EMIs
            emi_amounts = emi_transactions.groupby('amount').agg({
                'amount': 'count',
                'description': lambda x: x.iloc[0] if len(x) > 0 else ''
            }).reset_index()
            emi_amounts.columns = ['amount', 'frequency', 'description']
            
            # Filter for recurring payments (at least 2 occurrences)
            recurring_emis = emi_amounts[emi_amounts['frequency'] >= 2]
            
            for _, emi_row in recurring_emis.iterrows():
                emi_amount = float(emi_row['amount'])
                frequency = int(emi_row['frequency'])
                desc = str(emi_row['description'])
                
                # Estimate loan type from description
                loan_type = self._infer_loan_type(desc)
                bank = self._extract_bank_name(desc)
                
                # Estimate outstanding (rough: EMI * 36 months average tenure)
                estimated_outstanding = emi_amount * 36
                
                liability_item = {
                    'source': 'bank_statement',
                    'type': 'loan',
                    'bank': bank,
                    'outstanding': estimated_outstanding,
                    'monthly_emi': emi_amount,
                    'loan_type': loan_type,
                    'frequency': frequency,
                    'description': desc[:100]  # First 100 chars
                }
                
                result['loans'].append(liability_item)
                result['total_outstanding'] += estimated_outstanding
                result['total_monthly_emi'] += emi_amount
                result['detected_emi_patterns'].append({
                    'amount': emi_amount,
                    'frequency': frequency,
                    'description': desc[:50]
                })
        
        # Detect credit card payments
        cc_pattern = '|'.join(self.cc_patterns)
        cc_mask = debits['description'].str.contains(cc_pattern, case=False, regex=True, na=False)
        cc_transactions = debits[cc_mask].copy()
        
        if not cc_transactions.empty:
            # Group by amount to find recurring CC payments
            cc_amounts = cc_transactions.groupby('amount').agg({
                'amount': 'count',
                'description': lambda x: x.iloc[0] if len(x) > 0 else ''
            }).reset_index()
            cc_amounts.columns = ['amount', 'frequency', 'description']
            
            # Filter for recurring payments
            recurring_cc = cc_amounts[cc_amounts['frequency'] >= 2]
            
            for _, cc_row in recurring_cc.iterrows():
                cc_amount = float(cc_row['amount'])
                frequency = int(cc_row['frequency'])
                desc = str(cc_row['description'])
                bank = self._extract_bank_name(desc)
                
                # Estimate outstanding (rough: 3x monthly payment)
                estimated_outstanding = cc_amount * 3
                
                liability_item = {
                    'source': 'bank_statement',
                    'type': 'credit_card',
                    'bank': bank,
                    'outstanding': estimated_outstanding,
                    'monthly_emi': cc_amount,
                    'credit_limit': estimated_outstanding * 2,  # Rough estimate
                    'utilization': 50.0,  # Default estimate
                    'frequency': frequency,
                    'description': desc[:100]
                }
                
                result['credit_cards'].append(liability_item)
                result['total_outstanding'] += estimated_outstanding
                result['total_monthly_emi'] += cc_amount
        
        return result
    
    def _combine_liability_sources(
        self,
        credit_liabilities: Dict,
        bank_liabilities: Dict
    ) -> Dict[str, Any]:
        """
        Combine liabilities from both sources, avoiding duplicates.
        
        Priority: Credit report > Bank statement (more accurate)
        """
        combined = {
            'loans': [],
            'credit_cards': [],
            'total_outstanding': 0.0,
            'total_monthly_emi': 0.0
        }
        
        # Add credit report loans (more accurate)
        credit_loans = credit_liabilities.get('loans', [])
        combined['loans'].extend(credit_loans)
        
        # Add bank statement loans (avoid duplicates by bank + amount)
        bank_loans = bank_liabilities.get('loans', [])
        credit_banks = {loan.get('bank', '').lower() for loan in credit_loans}
        
        for bank_loan in bank_loans:
            bank_name = bank_loan.get('bank', '').lower()
            # Only add if not already in credit report
            if bank_name not in credit_banks:
                combined['loans'].append(bank_loan)
        
        # Add credit report credit cards
        credit_cards = credit_liabilities.get('credit_cards', [])
        combined['credit_cards'].extend(credit_cards)
        
        # Add bank statement credit cards (avoid duplicates)
        bank_cards = bank_liabilities.get('credit_cards', [])
        credit_card_banks = {card.get('bank', '').lower() for card in credit_cards}
        
        for bank_card in bank_cards:
            bank_name = bank_card.get('bank', '').lower()
            if bank_name not in credit_card_banks:
                combined['credit_cards'].append(bank_card)
        
        # Calculate totals
        combined['total_outstanding'] = (
            sum(loan.get('outstanding', 0) for loan in combined['loans']) +
            sum(card.get('outstanding', 0) for card in combined['credit_cards'])
        )
        
        combined['total_monthly_emi'] = (
            sum(loan.get('monthly_emi', 0) for loan in combined['loans']) +
            sum(card.get('monthly_emi', card.get('monthly_emi', 0)) for card in combined['credit_cards'])
        )
        
        return combined
    
    def _infer_loan_type(self, description: str) -> str:
        """Infer loan type from transaction description."""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['home', 'hl', 'housing']):
            return 'home_loan'
        elif any(word in desc_lower for word in ['personal', 'pl']):
            return 'personal_loan'
        elif any(word in desc_lower for word in ['car', 'auto', 'vehicle']):
            return 'auto_loan'
        elif any(word in desc_lower for word in ['education', 'el', 'student']):
            return 'education_loan'
        elif any(word in desc_lower for word in ['gold', 'jewel']):
            return 'gold_loan'
        else:
            return 'loan'
    
    def _extract_bank_name(self, description: str) -> str:
        """Extract bank name from transaction description."""
        desc_lower = description.lower()
        
        for provider in self.loan_providers:
            if provider in desc_lower:
                return provider.title()
        
        # Try to extract from common patterns
        patterns = [
            r'([a-z]+)\s*(?:bank|finserv|capital)',
            r'(?:to|from)\s*([a-z]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, desc_lower)
            if match:
                return match.group(1).title()
        
        return 'Unknown'
    
    def _assess_liability_risk(
        self,
        total_liabilities: float,
        total_monthly_emi: float,
        monthly_income: float,
        combined_liabilities: Dict
    ) -> Dict[str, Any]:
        """
        Assess risk based on liability levels.
        
        Returns risk indicators and flags.
        """
        risk = {
            'overall_risk_level': 'low',
            'risk_score': 0.0,
            'flags': [],
            'warnings': []
        }
        
        risk_score = 0.0
        
        # EMI to Income ratio
        if monthly_income > 0:
            emi_ratio = (total_monthly_emi / monthly_income) * 100
            
            if emi_ratio > 50:
                risk_score += 0.4
                risk['flags'].append(f'High EMI burden: {emi_ratio:.1f}% of income')
                risk['overall_risk_level'] = 'high'
            elif emi_ratio > 40:
                risk_score += 0.3
                risk['flags'].append(f'Moderate EMI burden: {emi_ratio:.1f}% of income')
                risk['overall_risk_level'] = 'medium'
            elif emi_ratio > 30:
                risk_score += 0.2
                risk['warnings'].append(f'EMI burden: {emi_ratio:.1f}% of income')
        
        # Number of active loans
        loan_count = len(combined_liabilities.get('loans', []))
        if loan_count > 5:
            risk_score += 0.2
            risk['flags'].append(f'Multiple loans: {loan_count} active loans')
        elif loan_count > 3:
            risk_score += 0.1
            risk['warnings'].append(f'Multiple loans: {loan_count} active loans')
        
        # Credit card utilization
        credit_cards = combined_liabilities.get('credit_cards', [])
        high_utilization_cards = [card for card in credit_cards if card.get('utilization', 0) > 80]
        
        if len(high_utilization_cards) > 0:
            risk_score += 0.2
            risk['flags'].append(f'{len(high_utilization_cards)} credit cards with >80% utilization')
        
        # Total debt level
        if monthly_income > 0:
            annual_income = monthly_income * 12
            debt_to_income = (total_liabilities / annual_income) * 100
            
            if debt_to_income > 300:
                risk_score += 0.3
                risk['flags'].append(f'Very high debt: {debt_to_income:.1f}% of annual income')
                risk['overall_risk_level'] = 'high'
            elif debt_to_income > 200:
                risk_score += 0.2
                risk['flags'].append(f'High debt: {debt_to_income:.1f}% of annual income')
        
        risk['risk_score'] = min(risk_score, 1.0)
        
        if risk['overall_risk_level'] == 'low' and risk_score > 0.3:
            risk['overall_risk_level'] = 'medium'
        elif risk_score > 0.5:
            risk['overall_risk_level'] = 'high'
        
        return risk


def detect_liabilities_simple(
    credit_report_data: Optional[Dict] = None,
    bank_statement_df: Optional[pd.DataFrame] = None,
    monthly_income: float = 0.0
) -> Dict[str, Any]:
    """
    Simple wrapper function for liability detection.
    
    Args:
        credit_report_data: Credit report JSON
        bank_statement_df: Bank statement DataFrame
        monthly_income: Monthly income
        
    Returns:
        Liability analysis results
    """
    detector = LiabilityDetector()
    return detector.detect_liabilities(credit_report_data, bank_statement_df, monthly_income)

