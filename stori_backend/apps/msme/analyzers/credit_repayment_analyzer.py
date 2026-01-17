"""
Credit & Repayment Behavior Analyzer
=====================================

Analyzes:
- Repayment Discipline
- Debt Position
- Regular Payments (Rent, Supplier, Utility)
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any


class CreditRepaymentAnalyzer:
    """Analyzes credit and repayment behavior"""
    
    def __init__(self):
        self.weights = {
            'repayment_discipline': 0.50,
            'debt_position': 0.30,
            'regular_payments': 0.20
        }
    
    def analyze_repayment_discipline(self, bank_data: Dict, credit_report: Dict = None) -> Dict[str, Any]:
        """
        Analyze on-time repayment ratio and payment history
        
        Args:
            bank_data: Bank statement data
            credit_report: Credit report from bureau (optional)
            
        Returns:
            Dict with repayment discipline metrics
        """
        try:
            transactions = pd.DataFrame(bank_data.get('transactions', []))
            
            if transactions.empty:
                return self._empty_repayment_discipline()
            
            transactions['date'] = pd.to_datetime(transactions['date'])
            transactions['month'] = transactions['date'].dt.to_period('M')
            
            # Identify loan EMI payments
            emi_keywords = ['emi', 'loan', 'repayment', 'instalment', 'installment']
            emi_transactions = transactions[
                transactions['narration'].str.lower().str.contains('|'.join(emi_keywords), na=False)
            ]
            
            # Calculate on-time ratio
            if credit_report and 'payment_history' in credit_report:
                payment_history = credit_report['payment_history']
                on_time_count = sum(1 for p in payment_history if p.get('status') == 'on_time')
                total_payments = len(payment_history)
                on_time_ratio = on_time_count / total_payments if total_payments > 0 else 1.0
                
                # Last 6 months history
                last_6_months = payment_history[-6:] if len(payment_history) >= 6 else payment_history
            else:
                # Estimate from bank statement
                monthly_emis = emi_transactions.groupby('month').size()
                
                # Assume on-time if consistent monthly payments
                expected_payments = len(transactions['month'].unique())
                actual_payments = len(monthly_emis)
                on_time_ratio = min(1.0, actual_payments / expected_payments) if expected_payments > 0 else 0.5
                
                last_6_months = []
                for month in monthly_emis.index[-6:]:
                    last_6_months.append({
                        'month': str(month),
                        'status': 'on_time',
                        'amount': float(emi_transactions[emi_transactions['month'] == month]['amount'].sum())
                    })
            
            # Bounced cheques/failed payments
            bounced_keywords = ['bounce', 'return', 'failed', 'insufficient', 'dishonour']
            bounced_transactions = transactions[
                transactions['narration'].str.lower().str.contains('|'.join(bounced_keywords), na=False)
            ]
            bounced_count = len(bounced_transactions)
            
            # Score repayment discipline
            score = self._score_repayment_discipline(on_time_ratio, bounced_count)
            
            return {
                'on_time_repayment_ratio': float(on_time_ratio),
                'last_6_months_payment_history': last_6_months,
                'bounced_cheques_count': int(bounced_count),
                'score': score
            }
        except Exception as e:
            return {**self._empty_repayment_discipline(), 'error': str(e)}
    
    def analyze_debt_position(self, credit_report: Dict, bank_data: Dict = None) -> Dict[str, Any]:
        """
        Analyze current debt position and utilization
        
        Args:
            credit_report: Credit report from bureau
            bank_data: Bank statement (optional)
            
        Returns:
            Dict with debt position metrics
        """
        try:
            if credit_report:
                current_debt = credit_report.get('total_outstanding', 0)
                total_limit = credit_report.get('total_limit', 0)
                
                # Calculate utilization
                if total_limit > 0:
                    utilization = (current_debt / total_limit)
                else:
                    utilization = 0 if current_debt == 0 else 1.0
                
                historical_utilization = credit_report.get('historical_utilization', utilization)
            else:
                # Estimate from bank statement EMI
                if bank_data:
                    transactions = pd.DataFrame(bank_data.get('transactions', []))
                    emi_keywords = ['emi', 'loan']
                    emi_transactions = transactions[
                        transactions['narration'].str.lower().str.contains('|'.join(emi_keywords), na=False)
                    ]
                    monthly_emi = emi_transactions['amount'].sum() / len(transactions['date'].dt.to_period('M').unique()) if not emi_transactions.empty else 0
                    
                    # Rough estimate: EMI = 3% of principal per month
                    estimated_debt = monthly_emi / 0.03 if monthly_emi > 0 else 0
                    current_debt = estimated_debt
                    utilization = 0.5  # Unknown
                    historical_utilization = 0.5
                else:
                    current_debt = 0
                    utilization = 0
                    historical_utilization = 0
            
            # Determine debt status
            if current_debt == 0:
                debt_status = 'low'
            elif current_debt < 500000:
                debt_status = 'low'
            elif current_debt < 2000000:
                debt_status = 'moderate'
            else:
                debt_status = 'high'
            
            # Score debt position
            score = self._score_debt_position(utilization, debt_status)
            
            return {
                'current_debt': float(current_debt),
                'total_debt_status': debt_status,
                'historical_loan_utilization': float(historical_utilization),
                'score': score
            }
        except Exception as e:
            return {
                'current_debt': 0,
                'total_debt_status': 'low',
                'historical_loan_utilization': 0,
                'score': 0.5,
                'error': str(e)
            }
    
    def analyze_regular_payments(self, bank_data: Dict) -> Dict[str, Any]:
        """
        Analyze regularity of rent, supplier, and utility payments
        
        Args:
            bank_data: Bank statement data
            
        Returns:
            Dict with regular payment metrics
        """
        try:
            transactions = pd.DataFrame(bank_data.get('transactions', []))
            
            if transactions.empty:
                return {
                    'rent_payment_regularity': 0,
                    'supplier_payment_regularity': 0,
                    'utility_payment_on_time_ratio': 0,
                    'score': 0
                }
            
            transactions['date'] = pd.to_datetime(transactions['date'])
            transactions['month'] = transactions['date'].dt.to_period('M')
            
            total_months = len(transactions['month'].unique())
            
            # Rent payments
            rent_keywords = ['rent', 'lease']
            rent_payments = transactions[
                transactions['narration'].str.lower().str.contains('|'.join(rent_keywords), na=False)
            ]
            rent_months = len(rent_payments['month'].unique())
            rent_regularity = rent_months / total_months if total_months > 0 else 0
            
            # Supplier payments (vendors)
            supplier_keywords = ['supplier', 'vendor', 'purchase', 'invoice']
            supplier_payments = transactions[
                transactions['narration'].str.lower().str.contains('|'.join(supplier_keywords), na=False)
            ]
            supplier_months = len(supplier_payments['month'].unique())
            supplier_regularity = supplier_months / total_months if total_months > 0 else 0
            
            # Utility payments
            utility_keywords = ['electricity', 'water', 'gas', 'internet', 'broadband', 'mobile']
            utility_payments = transactions[
                transactions['narration'].str.lower().str.contains('|'.join(utility_keywords), na=False)
            ]
            utility_months = len(utility_payments['month'].unique())
            utility_on_time_ratio = utility_months / total_months if total_months > 0 else 0
            
            # Score regular payments
            score = self._score_regular_payments(rent_regularity, supplier_regularity, utility_on_time_ratio)
            
            return {
                'rent_payment_regularity': float(rent_regularity),
                'supplier_payment_regularity': float(supplier_regularity),
                'utility_payment_on_time_ratio': float(utility_on_time_ratio),
                'score': score
            }
        except Exception as e:
            return {
                'rent_payment_regularity': 0,
                'supplier_payment_regularity': 0,
                'utility_payment_on_time_ratio': 0,
                'score': 0,
                'error': str(e)
            }
    
    def calculate_overall_score(self, repayment_score: float, debt_score: float, 
                               regular_payment_score: float) -> float:
        """Calculate weighted overall credit & repayment score"""
        return (
            repayment_score * self.weights['repayment_discipline'] +
            debt_score * self.weights['debt_position'] +
            regular_payment_score * self.weights['regular_payments']
        )
    
    # Helper Methods
    
    def _score_repayment_discipline(self, on_time_ratio: float, bounced_count: int) -> float:
        """Score repayment discipline"""
        # On-time ratio score
        if on_time_ratio >= 0.95:
            ratio_score = 1.0
        elif on_time_ratio >= 0.90:
            ratio_score = 0.85
        elif on_time_ratio >= 0.80:
            ratio_score = 0.65
        elif on_time_ratio >= 0.70:
            ratio_score = 0.40
        elif on_time_ratio >= 0.50:
            ratio_score = 0.15
        else:
            ratio_score = 0.0
        
        # Bounced cheques penalty
        if bounced_count == 0:
            bounce_score = 1.0
        elif bounced_count == 1:
            bounce_score = 0.7
        elif bounced_count == 2:
            bounce_score = 0.4
        elif bounced_count <= 5:
            bounce_score = 0.1
        else:
            bounce_score = 0.0
        
        # Combined score
        return (ratio_score * 0.70 + bounce_score * 0.30)
    
    def _score_debt_position(self, utilization: float, debt_status: str) -> float:
        """Score debt position"""
        # Utilization score (lower is better)
        if utilization < 0.30:
            util_score = 1.0
        elif utilization < 0.50:
            util_score = 0.8
        elif utilization < 0.70:
            util_score = 0.5
        elif utilization < 0.90:
            util_score = 0.3
        else:
            util_score = 0.1
        
        # Debt status score
        status_scores = {
            'low': 1.0,
            'moderate': 0.6,
            'high': 0.2
        }
        status_score = status_scores.get(debt_status, 0.5)
        
        return (util_score * 0.60 + status_score * 0.40)
    
    def _score_regular_payments(self, rent_reg: float, supplier_reg: float, utility_reg: float) -> float:
        """Score regular payments consistency"""
        # All should ideally be > 0.9
        rent_score = min(1.0, rent_reg / 0.9) if rent_reg > 0 else 0.5
        supplier_score = min(1.0, supplier_reg / 0.9) if supplier_reg > 0 else 0.5
        utility_score = min(1.0, utility_reg / 0.9) if utility_reg > 0 else 0.5
        
        # Weighted average
        return (rent_score * 0.30 + supplier_score * 0.40 + utility_score * 0.30)
    
    def _empty_repayment_discipline(self) -> Dict:
        """Return empty repayment discipline metrics"""
        return {
            'on_time_repayment_ratio': 0,
            'last_6_months_payment_history': [],
            'bounced_cheques_count': 0,
            'score': 0
        }

