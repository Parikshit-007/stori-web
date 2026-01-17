"""
Compliance & Taxation Analyzer
================================

Analyzes:
- GST/ITR Filing Discipline
- Mismatch Checks
- Tax Payments
- Refund/Chargeback Rate
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta


class ComplianceAnalyzer:
    """Analyzes compliance and taxation behavior"""
    
    def __init__(self):
        self.weights = {
            'filing_discipline': 0.40,
            'mismatch_checks': 0.30,
            'tax_payments': 0.20,
            'refund_chargeback': 0.10
        }
    
    def analyze_gst_itr_discipline(self, gst_data: Dict, itr_data: Dict) -> Dict[str, Any]:
        """
        Analyze GST and ITR filing discipline
        
        Args:
            gst_data: GST data including:
                - filing_status: str
                - last_filed_date: str/datetime
                - filing_frequency: str
            itr_data: ITR data including:
                - filing_status: str
                - last_filed_date: str/datetime
                
        Returns:
            Dict with filing discipline metrics
        """
        try:
            # GST filing
            gst_filing_status = gst_data.get('filing_status', '').lower()
            gst_last_filed = gst_data.get('last_filed_date')
            gst_filing_frequency = gst_data.get('filing_frequency', 'monthly').lower()
            
            gst_score = self._score_gst_filing(gst_filing_status, gst_last_filed, gst_filing_frequency)
            
            # ITR filing
            itr_filing_status = itr_data.get('filing_status', '').lower()
            itr_last_filed = itr_data.get('last_filed_date')
            
            itr_score = self._score_itr_filing(itr_filing_status, itr_last_filed)
            
            # Overall filing score
            score = (gst_score * 0.60 + itr_score * 0.40)
            
            return {
                'gst_filing_status': gst_filing_status,
                'gst_score': gst_score,
                'itr_filing_status': itr_filing_status,
                'itr_score': itr_score,
                'score': score
            }
        except Exception as e:
            return {
                'gst_filing_status': '',
                'gst_score': 0,
                'itr_filing_status': '',
                'itr_score': 0,
                'score': 0,
                'error': str(e)
            }
    
    def analyze_mismatch_checks(self, gst_data: Dict, platform_data: Dict, itr_data: Dict) -> Dict[str, Any]:
        """
        Analyze mismatches between GST, platform, and ITR data
        
        Args:
            gst_data: GST data
            platform_data: Platform transaction data
            itr_data: ITR data
            
        Returns:
            Dict with mismatch check results
        """
        try:
            gst_revenue = gst_data.get('total_revenue', 0)
            platform_revenue = platform_data.get('total_revenue', 0) if platform_data else 0
            itr_revenue = itr_data.get('total_revenue', 0)
            
            mismatches = []
            mismatch_score = 1.0
            
            # GST vs Platform mismatch
            if gst_revenue > 0 and platform_revenue > 0:
                gst_platform_diff = abs(gst_revenue - platform_revenue) / max(gst_revenue, platform_revenue) * 100
                if gst_platform_diff > 20:
                    mismatches.append('gst_platform_revenue_mismatch')
                    mismatch_score *= 0.7
                elif gst_platform_diff > 10:
                    mismatches.append('gst_platform_revenue_minor_mismatch')
                    mismatch_score *= 0.9
            
            # GST vs ITR mismatch
            if gst_revenue > 0 and itr_revenue > 0:
                gst_itr_diff = abs(gst_revenue - itr_revenue) / max(gst_revenue, itr_revenue) * 100
                if gst_itr_diff > 20:
                    mismatches.append('gst_itr_revenue_mismatch')
                    mismatch_score *= 0.6
                elif gst_itr_diff > 10:
                    mismatches.append('gst_itr_revenue_minor_mismatch')
                    mismatch_score *= 0.85
            
            # Platform vs ITR mismatch
            if platform_revenue > 0 and itr_revenue > 0:
                platform_itr_diff = abs(platform_revenue - itr_revenue) / max(platform_revenue, itr_revenue) * 100
                if platform_itr_diff > 20:
                    mismatches.append('platform_itr_revenue_mismatch')
                    mismatch_score *= 0.7
                elif platform_itr_diff > 10:
                    mismatches.append('platform_itr_revenue_minor_mismatch')
                    mismatch_score *= 0.9
            
            return {
                'gst_revenue': float(gst_revenue),
                'platform_revenue': float(platform_revenue),
                'itr_revenue': float(itr_revenue),
                'mismatches': mismatches,
                'mismatch_count': len(mismatches),
                'score': mismatch_score
            }
        except Exception as e:
            return {
                'gst_revenue': 0,
                'platform_revenue': 0,
                'itr_revenue': 0,
                'mismatches': [],
                'mismatch_count': 0,
                'score': 0.5,
                'error': str(e)
            }
    
    def analyze_tax_payments(self, bank_data: Dict) -> Dict[str, Any]:
        """
        Analyze tax payment patterns from bank statements
        
        Args:
            bank_data: Bank statement data
            
        Returns:
            Dict with tax payment metrics
        """
        try:
            transactions = pd.DataFrame(bank_data.get('transactions', []))
            
            if transactions.empty:
                return {
                    'tax_payment_count': 0,
                    'total_tax_paid': 0,
                    'tax_payment_regularity': 0,
                    'score': 0
                }
            
            transactions['date'] = pd.to_datetime(transactions['date'])
            
            # Identify tax payments
            tax_keywords = ['gst', 'tax', 'tds', 'tcs', 'income tax', 'advance tax']
            narration_col = 'narration' if 'narration' in transactions.columns else 'description'
            
            if narration_col in transactions.columns:
                tax_transactions = transactions[
                    transactions[narration_col].astype(str).str.lower().str.contains(
                        '|'.join(tax_keywords), na=False
                    )
                ]
            else:
                tax_transactions = pd.DataFrame()
            
            tax_payment_count = len(tax_transactions)
            total_tax_paid = float(tax_transactions['amount'].sum()) if not tax_transactions.empty else 0
            
            # Calculate regularity (monthly frequency)
            if not tax_transactions.empty:
                tax_transactions['month'] = tax_transactions['date'].dt.to_period('M')
                total_months = len(transactions['date'].dt.to_period('M').unique())
                tax_months = len(tax_transactions['month'].unique())
                tax_payment_regularity = tax_months / total_months if total_months > 0 else 0
            else:
                tax_payment_regularity = 0
            
            # Score tax payments
            count_score = self._score_tax_payment_count(tax_payment_count)
            regularity_score = self._score_tax_payment_regularity(tax_payment_regularity)
            
            score = (count_score * 0.40 + regularity_score * 0.60)
            
            return {
                'tax_payment_count': int(tax_payment_count),
                'total_tax_paid': total_tax_paid,
                'tax_payment_regularity': float(tax_payment_regularity),
                'count_score': count_score,
                'regularity_score': regularity_score,
                'score': score
            }
        except Exception as e:
            return {
                'tax_payment_count': 0,
                'total_tax_paid': 0,
                'tax_payment_regularity': 0,
                'score': 0,
                'error': str(e)
            }
    
    def analyze_refund_chargeback_rate(self, platform_data: Dict, gst_data: Dict) -> Dict[str, Any]:
        """
        Analyze refund and chargeback rates
        
        Args:
            platform_data: Platform transaction data
            gst_data: GST data
            
        Returns:
            Dict with refund/chargeback metrics
        """
        try:
            total_transactions = platform_data.get('total_transactions', 0) if platform_data else 0
            refund_count = platform_data.get('refund_count', 0) if platform_data else 0
            chargeback_count = platform_data.get('chargeback_count', 0) if platform_data else 0
            
            if total_transactions > 0:
                refund_rate = (refund_count / total_transactions) * 100
                chargeback_rate = (chargeback_count / total_transactions) * 100
            else:
                refund_rate = 0
                chargeback_rate = 0
            
            # Score refund/chargeback rates (lower is better)
            refund_score = self._score_refund_rate(refund_rate)
            chargeback_score = self._score_chargeback_rate(chargeback_rate)
            
            score = (refund_score * 0.60 + chargeback_score * 0.40)
            
            return {
                'refund_count': int(refund_count),
                'chargeback_count': int(chargeback_count),
                'refund_rate': float(refund_rate),
                'chargeback_rate': float(chargeback_rate),
                'refund_score': refund_score,
                'chargeback_score': chargeback_score,
                'score': score
            }
        except Exception as e:
            return {
                'refund_count': 0,
                'chargeback_count': 0,
                'refund_rate': 0,
                'chargeback_rate': 0,
                'score': 0.5,
                'error': str(e)
            }
    
    def calculate_overall_score(self, filing_score: float, mismatch_score: float,
                               tax_payment_score: float, refund_score: float) -> float:
        """Calculate weighted overall compliance score"""
        return (
            filing_score * self.weights['filing_discipline'] +
            mismatch_score * self.weights['mismatch_checks'] +
            tax_payment_score * self.weights['tax_payments'] +
            refund_score * self.weights['refund_chargeback']
        )
    
    # Helper Methods
    
    def _score_gst_filing(self, status: str, last_filed, frequency: str) -> float:
        """Score GST filing discipline"""
        if status == 'filed' or status == 'active':
            # Check if recent (within last 2 months for monthly, last 3 months for quarterly)
            if last_filed:
                try:
                    if isinstance(last_filed, str):
                        last_filed_date = datetime.strptime(last_filed, '%Y-%m-%d')
                    else:
                        last_filed_date = last_filed
                    
                    days_since = (datetime.now() - last_filed_date).days
                    
                    if frequency == 'monthly':
                        if days_since <= 60:
                            return 1.0
                        elif days_since <= 90:
                            return 0.7
                        else:
                            return 0.4
                    else:  # quarterly
                        if days_since <= 120:
                            return 1.0
                        elif days_since <= 180:
                            return 0.7
                        else:
                            return 0.4
                except:
                    return 0.7
            return 0.7
        elif status == 'not_filed' or status == 'pending':
            return 0.2
        else:
            return 0.5
    
    def _score_itr_filing(self, status: str, last_filed) -> float:
        """Score ITR filing discipline"""
        if status == 'filed' or status == 'submitted':
            # Check if recent (within last year)
            if last_filed:
                try:
                    if isinstance(last_filed, str):
                        last_filed_date = datetime.strptime(last_filed, '%Y-%m-%d')
                    else:
                        last_filed_date = last_filed
                    
                    days_since = (datetime.now() - last_filed_date).days
                    
                    if days_since <= 365:
                        return 1.0
                    elif days_since <= 730:
                        return 0.6
                    else:
                        return 0.3
                except:
                    return 0.7
            return 0.7
        elif status == 'not_filed' or status == 'pending':
            return 0.1
        else:
            return 0.5
    
    def _score_tax_payment_count(self, count: int) -> float:
        """Score tax payment count"""
        if count >= 12:
            return 1.0
        elif count >= 6:
            return 0.7
        elif count >= 3:
            return 0.5
        elif count >= 1:
            return 0.3
        else:
            return 0.0
    
    def _score_tax_payment_regularity(self, regularity: float) -> float:
        """Score tax payment regularity"""
        if regularity >= 0.9:
            return 1.0
        elif regularity >= 0.7:
            return 0.8
        elif regularity >= 0.5:
            return 0.6
        elif regularity >= 0.3:
            return 0.4
        else:
            return 0.2
    
    def _score_refund_rate(self, rate: float) -> float:
        """Score refund rate (lower is better)"""
        if rate < 2:
            return 1.0
        elif rate < 5:
            return 0.8
        elif rate < 10:
            return 0.6
        elif rate < 15:
            return 0.4
        else:
            return 0.2
    
    def _score_chargeback_rate(self, rate: float) -> float:
        """Score chargeback rate (lower is better)"""
        if rate < 1:
            return 1.0
        elif rate < 2:
            return 0.7
        elif rate < 5:
            return 0.4
        else:
            return 0.1

