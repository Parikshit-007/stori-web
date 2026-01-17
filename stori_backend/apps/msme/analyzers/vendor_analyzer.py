"""
Vendor Payments Analyzer
=========================

Analyzes:
- Vendor Payment Behavior
- Vendor Strength
- Vendor Transaction Analytics
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta


class VendorAnalyzer:
    """Analyzes vendor payment behavior and relationships"""
    
    def __init__(self):
        self.weights = {
            'payment_behavior': 0.40,
            'vendor_strength': 0.35,
            'transaction_analytics': 0.25
        }
    
    def analyze_vendor_payment_behavior(self, gst2b_data: Dict, bank_data: Dict) -> Dict[str, Any]:
        """
        Analyze vendor payment behavior from GST 2B and bank data
        
        Args:
            gst2b_data: GST 2B data with vendor transactions
            bank_data: Bank statement data
            
        Returns:
            Dict with payment behavior metrics
        """
        try:
            vendor_transactions = gst2b_data.get('vendor_transactions', [])
            
            if not vendor_transactions:
                return {
                    'on_time_payment_ratio': 0,
                    'average_payment_delay_days': 0,
                    'payment_consistency': 0,
                    'score': 0
                }
            
            # Calculate payment metrics
            on_time_payments = 0
            total_payments = 0
            payment_delays = []
            
            for txn in vendor_transactions:
                if isinstance(txn, dict):
                    due_date = txn.get('due_date')
                    payment_date = txn.get('payment_date')
                    amount = txn.get('amount', 0)
                    
                    if due_date and payment_date:
                        try:
                            if isinstance(due_date, str):
                                due_date = datetime.strptime(due_date, '%Y-%m-%d')
                            if isinstance(payment_date, str):
                                payment_date = datetime.strptime(payment_date, '%Y-%m-%d')
                            
                            delay = (payment_date - due_date).days
                            payment_delays.append(delay)
                            
                            if delay <= 0:
                                on_time_payments += 1
                            total_payments += 1
                        except:
                            pass
            
            on_time_ratio = on_time_payments / total_payments if total_payments > 0 else 0
            avg_delay = np.mean(payment_delays) if payment_delays else 0
            
            # Calculate consistency (coefficient of variation of payment amounts)
            amounts = [txn.get('amount', 0) if isinstance(txn, dict) else 0 for txn in vendor_transactions]
            if amounts:
                consistency = 1 - (np.std(amounts) / np.mean(amounts)) if np.mean(amounts) > 0 else 0
            else:
                consistency = 0
            
            # Score payment behavior
            on_time_score = self._score_on_time_ratio(on_time_ratio)
            delay_score = self._score_payment_delay(avg_delay)
            consistency_score = max(0, min(1, consistency))
            
            score = (
                on_time_score * 0.50 +
                delay_score * 0.30 +
                consistency_score * 0.20
            )
            
            return {
                'on_time_payment_ratio': float(on_time_ratio),
                'average_payment_delay_days': float(avg_delay),
                'payment_consistency': float(consistency),
                'on_time_score': on_time_score,
                'delay_score': delay_score,
                'consistency_score': consistency_score,
                'score': score
            }
        except Exception as e:
            return {
                'on_time_payment_ratio': 0,
                'average_payment_delay_days': 0,
                'payment_consistency': 0,
                'score': 0,
                'error': str(e)
            }
    
    def analyze_vendor_strength(self, gst2b_data: Dict) -> Dict[str, Any]:
        """
        Analyze vendor strength and relationships
        
        Args:
            gst2b_data: GST 2B data with vendor information
            
        Returns:
            Dict with vendor strength metrics
        """
        try:
            vendors = gst2b_data.get('vendors', [])
            
            if not vendors:
                return {
                    'total_vendors': 0,
                    'long_term_vendors': 0,
                    'vendor_diversity_score': 0,
                    'score': 0
                }
            
            total_vendors = len(vendors)
            
            # Count long-term vendors (relationships > 6 months)
            long_term_vendors = 0
            for vendor in vendors:
                if isinstance(vendor, dict):
                    relationship_duration = vendor.get('relationship_duration_months', 0)
                    if relationship_duration >= 6:
                        long_term_vendors += 1
            
            # Calculate vendor diversity (HHI-like measure)
            vendor_amounts = [v.get('total_amount', 0) if isinstance(v, dict) else 0 for v in vendors]
            total_amount = sum(vendor_amounts)
            
            if total_amount > 0:
                vendor_shares = [amt / total_amount for amt in vendor_amounts]
                vendor_diversity = 1 - sum(share ** 2 for share in vendor_shares)  # Inverse HHI
            else:
                vendor_diversity = 0
            
            # Score vendor strength
            count_score = self._score_vendor_count(total_vendors)
            long_term_score = self._score_long_term_vendors(long_term_vendors, total_vendors)
            diversity_score = vendor_diversity
            
            score = (
                count_score * 0.30 +
                long_term_score * 0.40 +
                diversity_score * 0.30
            )
            
            return {
                'total_vendors': int(total_vendors),
                'long_term_vendors': int(long_term_vendors),
                'vendor_diversity_score': float(vendor_diversity),
                'count_score': count_score,
                'long_term_score': long_term_score,
                'diversity_score': diversity_score,
                'score': score
            }
        except Exception as e:
            return {
                'total_vendors': 0,
                'long_term_vendors': 0,
                'vendor_diversity_score': 0,
                'score': 0,
                'error': str(e)
            }
    
    def analyze_vendor_transaction_analytics(self, gst2b_data: Dict) -> Dict[str, Any]:
        """
        Analyze vendor transaction analytics
        
        Args:
            gst2b_data: GST 2B data with vendor transactions
            
        Returns:
            Dict with transaction analytics
        """
        try:
            vendor_transactions = gst2b_data.get('vendor_transactions', [])
            
            if not vendor_transactions:
                return {
                    'total_vendor_transactions': 0,
                    'avg_transaction_value': 0,
                    'transaction_frequency': 0,
                    'score': 0
                }
            
            total_transactions = len(vendor_transactions)
            amounts = [txn.get('amount', 0) if isinstance(txn, dict) else 0 for txn in vendor_transactions]
            avg_transaction_value = np.mean(amounts) if amounts else 0
            
            # Calculate transaction frequency (transactions per month)
            if vendor_transactions:
                dates = []
                for txn in vendor_transactions:
                    if isinstance(txn, dict):
                        date_str = txn.get('date') or txn.get('transaction_date')
                        if date_str:
                            try:
                                if isinstance(date_str, str):
                                    dates.append(datetime.strptime(date_str, '%Y-%m-%d'))
                                else:
                                    dates.append(date_str)
                            except:
                                pass
                
                if dates:
                    date_range = (max(dates) - min(dates)).days
                    months = max(1, date_range / 30)
                    transaction_frequency = total_transactions / months
                else:
                    transaction_frequency = 0
            else:
                transaction_frequency = 0
            
            # Score transaction analytics
            volume_score = self._score_transaction_volume(total_transactions)
            value_score = self._score_transaction_value(avg_transaction_value)
            frequency_score = self._score_transaction_frequency(transaction_frequency)
            
            score = (
                volume_score * 0.35 +
                value_score * 0.35 +
                frequency_score * 0.30
            )
            
            return {
                'total_vendor_transactions': int(total_transactions),
                'avg_transaction_value': float(avg_transaction_value),
                'transaction_frequency': float(transaction_frequency),
                'volume_score': volume_score,
                'value_score': value_score,
                'frequency_score': frequency_score,
                'score': score
            }
        except Exception as e:
            return {
                'total_vendor_transactions': 0,
                'avg_transaction_value': 0,
                'transaction_frequency': 0,
                'score': 0,
                'error': str(e)
            }
    
    def calculate_overall_score(self, payment_score: float, vendor_strength_score: float,
                               transaction_score: float) -> float:
        """Calculate weighted overall vendor score"""
        return (
            payment_score * self.weights['payment_behavior'] +
            vendor_strength_score * self.weights['vendor_strength'] +
            transaction_score * self.weights['transaction_analytics']
        )
    
    # Helper Methods
    
    def _score_on_time_ratio(self, ratio: float) -> float:
        """Score on-time payment ratio"""
        if ratio >= 0.95:
            return 1.0
        elif ratio >= 0.90:
            return 0.9
        elif ratio >= 0.80:
            return 0.7
        elif ratio >= 0.70:
            return 0.5
        elif ratio >= 0.50:
            return 0.3
        else:
            return 0.1
    
    def _score_payment_delay(self, avg_delay: float) -> float:
        """Score payment delay (negative delay = early payment, positive = late)"""
        if avg_delay <= -5:  # 5+ days early
            return 1.0
        elif avg_delay <= 0:  # On time or early
            return 0.9
        elif avg_delay <= 7:  # Within 7 days
            return 0.7
        elif avg_delay <= 15:  # Within 15 days
            return 0.5
        elif avg_delay <= 30:  # Within 30 days
            return 0.3
        else:
            return 0.1
    
    def _score_vendor_count(self, count: int) -> float:
        """Score vendor count"""
        if count >= 20:
            return 1.0
        elif count >= 10:
            return 0.8
        elif count >= 5:
            return 0.6
        elif count >= 3:
            return 0.4
        else:
            return 0.2
    
    def _score_long_term_vendors(self, long_term: int, total: int) -> float:
        """Score long-term vendor ratio"""
        if total == 0:
            return 0.0
        
        ratio = long_term / total
        if ratio >= 0.7:
            return 1.0
        elif ratio >= 0.5:
            return 0.8
        elif ratio >= 0.3:
            return 0.6
        elif ratio >= 0.1:
            return 0.4
        else:
            return 0.2
    
    def _score_transaction_volume(self, count: int) -> float:
        """Score transaction volume"""
        if count >= 100:
            return 1.0
        elif count >= 50:
            return 0.8
        elif count >= 20:
            return 0.6
        elif count >= 10:
            return 0.4
        else:
            return 0.2
    
    def _score_transaction_value(self, value: float) -> float:
        """Score average transaction value"""
        if value >= 50000:
            return 1.0
        elif value >= 20000:
            return 0.8
        elif value >= 10000:
            return 0.6
        elif value >= 5000:
            return 0.4
        else:
            return 0.2
    
    def _score_transaction_frequency(self, frequency: float) -> float:
        """Score transaction frequency (per month)"""
        if frequency >= 20:
            return 1.0
        elif frequency >= 10:
            return 0.8
        elif frequency >= 5:
            return 0.6
        elif frequency >= 2:
            return 0.4
        else:
            return 0.2

