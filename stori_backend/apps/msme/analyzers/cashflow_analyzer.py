"""
Cash Flow & Banking Analyzer
=============================

Analyzes:
- Bank Balance Metrics
- Inflow/Outflow Analysis
- Deposit Consistency
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta


class CashFlowAnalyzer:
    """Analyzes cash flow and banking behavior"""
    
    def __init__(self):
        self.weights = {
            'balance_metrics': 0.50,
            'inflow_outflow': 0.50
        }
    
    def analyze_bank_balance_metrics(self, bank_data: Dict) -> Dict[str, Any]:
        """
        Analyze bank balance metrics
        
        Args:
            bank_data: Bank statement data with transactions
            
        Returns:
            Dict with balance metrics
        """
        try:
            transactions = pd.DataFrame(bank_data.get('transactions', []))
            
            if transactions.empty:
                return {
                    'avg_balance': 0,
                    'min_balance': 0,
                    'max_balance': 0,
                    'balance_stability': 0,
                    'score': 0
                }
            
            transactions['date'] = pd.to_datetime(transactions['date'])
            
            # Extract balances
            if 'balance' in transactions.columns:
                balances = transactions['balance'].dropna()
            else:
                # Calculate running balance if not present
                transactions = transactions.sort_values('date')
                if 'type' in transactions.columns:
                    transactions['type'] = transactions['type'].str.upper()
                    transactions['amount_signed'] = transactions.apply(
                        lambda x: x['amount'] if x['type'] == 'CR' else -x['amount'],
                        axis=1
                    )
                    transactions['balance'] = transactions['amount_signed'].cumsum()
                    balances = transactions['balance']
                else:
                    balances = pd.Series([0])
            
            if len(balances) == 0:
                return {
                    'avg_balance': 0,
                    'min_balance': 0,
                    'max_balance': 0,
                    'balance_stability': 0,
                    'score': 0
                }
            
            avg_balance = float(balances.mean())
            min_balance = float(balances.min())
            max_balance = float(balances.max())
            
            # Calculate balance stability (coefficient of variation)
            if avg_balance > 0:
                balance_cv = (balances.std() / avg_balance) * 100
            else:
                balance_cv = 100
            
            # Score balance metrics
            avg_balance_score = self._score_avg_balance(avg_balance)
            min_balance_score = self._score_min_balance(min_balance)
            stability_score = self._score_balance_stability(balance_cv)
            
            score = (
                avg_balance_score * 0.50 +
                min_balance_score * 0.30 +
                stability_score * 0.20
            )
            
            return {
                'avg_balance': avg_balance,
                'min_balance': min_balance,
                'max_balance': max_balance,
                'balance_stability': float(balance_cv),
                'avg_balance_score': avg_balance_score,
                'min_balance_score': min_balance_score,
                'stability_score': stability_score,
                'score': score
            }
        except Exception as e:
            return {
                'avg_balance': 0,
                'min_balance': 0,
                'max_balance': 0,
                'balance_stability': 0,
                'score': 0,
                'error': str(e)
            }
    
    def analyze_inflow_outflow(self, bank_data: Dict, exclude_p2p: bool = True) -> Dict[str, Any]:
        """
        Analyze inflow and outflow patterns
        
        Args:
            bank_data: Bank statement data
            exclude_p2p: Whether to exclude P2P transactions
            
        Returns:
            Dict with inflow/outflow metrics
        """
        try:
            transactions = pd.DataFrame(bank_data.get('transactions', []))
            
            if transactions.empty:
                return {
                    'total_inflow': 0,
                    'total_outflow': 0,
                    'net_cashflow': 0,
                    'inflow_outflow_ratio': 0,
                    'score': 0
                }
            
            transactions['date'] = pd.to_datetime(transactions['date'])
            
            # Normalize transaction type
            if 'type' in transactions.columns:
                transactions['type'] = transactions['type'].str.upper()
                transactions['type'] = transactions['type'].replace({
                    'CREDIT': 'CR', 'DEBIT': 'DR', 'CR': 'CR', 'DR': 'DR'
                })
            else:
                return {
                    'total_inflow': 0,
                    'total_outflow': 0,
                    'net_cashflow': 0,
                    'inflow_outflow_ratio': 0,
                    'score': 0
                }
            
            # Filter P2P if needed
            if exclude_p2p:
                p2p_keywords = ['upi', 'imps', 'neft', 'paytm', 'phonepe', 'gpay']
                narration_col = 'narration' if 'narration' in transactions.columns else 'description'
                if narration_col in transactions.columns:
                    is_p2p = transactions[narration_col].astype(str).str.lower().str.contains(
                        '|'.join(p2p_keywords), na=False
                    )
                    transactions = transactions[~is_p2p]
            
            # Calculate inflows and outflows
            credits = transactions[transactions['type'] == 'CR']
            debits = transactions[transactions['type'] == 'DR']
            
            total_inflow = float(credits['amount'].sum()) if not credits.empty else 0
            total_outflow = float(debits['amount'].sum()) if not debits.empty else 0
            net_cashflow = total_inflow - total_outflow
            
            # Calculate ratio
            if total_outflow > 0:
                inflow_outflow_ratio = total_inflow / total_outflow
            else:
                inflow_outflow_ratio = 10.0 if total_inflow > 0 else 0
            
            # Score inflow/outflow
            ratio_score = self._score_inflow_outflow_ratio(inflow_outflow_ratio)
            net_flow_score = self._score_net_cashflow(net_cashflow)
            
            score = (ratio_score * 0.60 + net_flow_score * 0.40)
            
            return {
                'total_inflow': total_inflow,
                'total_outflow': total_outflow,
                'net_cashflow': net_cashflow,
                'inflow_outflow_ratio': float(inflow_outflow_ratio),
                'ratio_score': ratio_score,
                'net_flow_score': net_flow_score,
                'score': score
            }
        except Exception as e:
            return {
                'total_inflow': 0,
                'total_outflow': 0,
                'net_cashflow': 0,
                'inflow_outflow_ratio': 0,
                'score': 0,
                'error': str(e)
            }
    
    def analyze_deposit_consistency(self, bank_data: Dict) -> Dict[str, Any]:
        """
        Analyze deposit consistency patterns
        
        Args:
            bank_data: Bank statement data
            
        Returns:
            Dict with deposit consistency metrics (display only)
        """
        try:
            transactions = pd.DataFrame(bank_data.get('transactions', []))
            
            if transactions.empty:
                return {
                    'deposit_frequency': 0,
                    'deposit_regularity': 0,
                    'avg_deposit_amount': 0
                }
            
            transactions['date'] = pd.to_datetime(transactions['date'])
            transactions['month'] = transactions['date'].dt.to_period('M')
            
            if 'type' in transactions.columns:
                transactions['type'] = transactions['type'].str.upper()
                credits = transactions[transactions['type'] == 'CR']
            else:
                credits = pd.DataFrame()
            
            if credits.empty:
                return {
                    'deposit_frequency': 0,
                    'deposit_regularity': 0,
                    'avg_deposit_amount': 0
                }
            
            # Calculate deposit frequency
            deposit_frequency = len(credits) / len(transactions['month'].unique()) if len(transactions['month'].unique()) > 0 else 0
            
            # Calculate regularity (coefficient of variation of monthly deposits)
            monthly_deposits = credits.groupby('month')['amount'].sum()
            if len(monthly_deposits) > 1:
                deposit_regularity = 1 - (monthly_deposits.std() / monthly_deposits.mean()) if monthly_deposits.mean() > 0 else 0
            else:
                deposit_regularity = 0
            
            avg_deposit_amount = float(credits['amount'].mean())
            
            return {
                'deposit_frequency': float(deposit_frequency),
                'deposit_regularity': float(deposit_regularity),
                'avg_deposit_amount': avg_deposit_amount
            }
        except Exception as e:
            return {
                'deposit_frequency': 0,
                'deposit_regularity': 0,
                'avg_deposit_amount': 0,
                'error': str(e)
            }
    
    def calculate_overall_score(self, balance_score: float, inflow_outflow_score: float) -> float:
        """Calculate weighted overall cash flow score"""
        return (
            balance_score * self.weights['balance_metrics'] +
            inflow_outflow_score * self.weights['inflow_outflow']
        )
    
    # Helper Methods
    
    def _score_avg_balance(self, balance: float) -> float:
        """Score average balance"""
        if balance >= 500000:
            return 1.0
        elif balance >= 200000:
            return 0.8
        elif balance >= 100000:
            return 0.6
        elif balance >= 50000:
            return 0.4
        elif balance >= 10000:
            return 0.2
        else:
            return 0.0
    
    def _score_min_balance(self, min_balance: float) -> float:
        """Score minimum balance (higher is better)"""
        if min_balance >= 100000:
            return 1.0
        elif min_balance >= 50000:
            return 0.8
        elif min_balance >= 10000:
            return 0.6
        elif min_balance >= 5000:
            return 0.4
        elif min_balance >= 0:
            return 0.2
        else:
            return 0.0  # Negative balance is bad
    
    def _score_balance_stability(self, cv: float) -> float:
        """Score balance stability (lower CV = better)"""
        if cv < 20:
            return 1.0
        elif cv < 40:
            return 0.8
        elif cv < 60:
            return 0.6
        elif cv < 80:
            return 0.4
        else:
            return 0.2
    
    def _score_inflow_outflow_ratio(self, ratio: float) -> float:
        """Score inflow/outflow ratio (higher is better)"""
        if ratio >= 1.5:
            return 1.0
        elif ratio >= 1.2:
            return 0.9
        elif ratio >= 1.0:
            return 0.7
        elif ratio >= 0.8:
            return 0.5
        elif ratio >= 0.6:
            return 0.3
        else:
            return 0.1
    
    def _score_net_cashflow(self, net_flow: float) -> float:
        """Score net cash flow (positive is better)"""
        if net_flow >= 100000:
            return 1.0
        elif net_flow >= 50000:
            return 0.8
        elif net_flow >= 10000:
            return 0.6
        elif net_flow >= 0:
            return 0.4
        elif net_flow >= -10000:
            return 0.2
        else:
            return 0.0

