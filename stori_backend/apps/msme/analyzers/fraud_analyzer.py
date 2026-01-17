"""
Fraud & Verification Analyzer
===============================

Analyzes:
- KYC Completion
- Shop Verification
- Banking Fraud Signals
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta


class FraudAnalyzer:
    """Analyzes fraud and verification signals"""
    
    def __init__(self):
        self.weights = {
            'kyc_completion': 0.40,
            'shop_verification': 0.30,
            'fraud_signals': 0.30
        }
    
    def analyze_kyc_completion(self, kyc_data: Dict) -> Dict[str, Any]:
        """
        Analyze KYC completion status
        
        Args:
            kyc_data: KYC data including:
                - status: str
                - documents_verified: List[str]
                - verification_date: str/datetime
                
        Returns:
            Dict with KYC metrics
        """
        try:
            kyc_status = kyc_data.get('status', '').lower()
            documents_verified = kyc_data.get('documents_verified', [])
            verification_date = kyc_data.get('verification_date')
            
            # Required documents
            required_docs = ['pan', 'aadhaar', 'address_proof', 'business_registration']
            verified_docs = [doc.lower() for doc in documents_verified] if documents_verified else []
            
            # Calculate completion
            doc_completion = sum(1 for doc in required_docs if any(req in doc for doc in verified_docs)) / len(required_docs)
            
            # Score KYC
            status_score = self._score_kyc_status(kyc_status)
            doc_score = doc_completion
            
            score = (status_score * 0.60 + doc_score * 0.40)
            
            return {
                'kyc_status': kyc_status,
                'documents_verified': documents_verified,
                'doc_completion_rate': float(doc_completion),
                'status_score': status_score,
                'doc_score': doc_score,
                'score': score
            }
        except Exception as e:
            return {
                'kyc_status': '',
                'documents_verified': [],
                'doc_completion_rate': 0,
                'score': 0,
                'error': str(e)
            }
    
    def analyze_shop_verification(self, shop_data: Dict) -> Dict[str, Any]:
        """
        Analyze shop verification status
        
        Args:
            shop_data: Shop verification data including:
                - verification_status: str
                - location_verified: bool
                - photos_verified: bool
                
        Returns:
            Dict with shop verification metrics
        """
        try:
            verification_status = shop_data.get('verification_status', '').lower()
            location_verified = shop_data.get('location_verified', False)
            photos_verified = shop_data.get('photos_verified', False)
            
            # Score verification
            status_score = self._score_verification_status(verification_status)
            location_score = 1.0 if location_verified else 0.0
            photos_score = 1.0 if photos_verified else 0.0
            
            score = (status_score * 0.50 + location_score * 0.30 + photos_score * 0.20)
            
            return {
                'verification_status': verification_status,
                'location_verified': location_verified,
                'photos_verified': photos_verified,
                'status_score': status_score,
                'location_score': location_score,
                'photos_score': photos_score,
                'score': score
            }
        except Exception as e:
            return {
                'verification_status': '',
                'location_verified': False,
                'photos_verified': False,
                'score': 0,
                'error': str(e)
            }
    
    def analyze_banking_fraud_signals(self, bank_data: Dict) -> Dict[str, Any]:
        """
        Analyze banking fraud signals
        
        Args:
            bank_data: Bank statement data
            
        Returns:
            Dict with fraud signal metrics
        """
        try:
            transactions = pd.DataFrame(bank_data.get('transactions', []))
            
            if transactions.empty:
                return {
                    'circular_transaction_risk': 0,
                    'suspicious_pattern_count': 0,
                    'fraud_risk_score': 0,
                    'score': 1.0  # No data = no fraud signals
                }
            
            transactions['date'] = pd.to_datetime(transactions['date'])
            transactions = transactions.sort_values('date')
            
            # Normalize transaction type
            if 'type' in transactions.columns:
                transactions['type'] = transactions['type'].str.upper()
            
            # Detect circular transactions
            circular_risk = self._detect_circular_transactions(transactions)
            
            # Detect suspicious patterns
            suspicious_patterns = self._detect_suspicious_patterns(transactions)
            
            # Calculate fraud risk score (lower is better, so we invert it)
            fraud_risk_score = min(1.0, circular_risk + (len(suspicious_patterns) * 0.1))
            score = max(0.0, 1.0 - fraud_risk_score)
            
            return {
                'circular_transaction_risk': float(circular_risk),
                'suspicious_pattern_count': len(suspicious_patterns),
                'suspicious_patterns': suspicious_patterns,
                'fraud_risk_score': float(fraud_risk_score),
                'score': score
            }
        except Exception as e:
            return {
                'circular_transaction_risk': 0,
                'suspicious_pattern_count': 0,
                'fraud_risk_score': 0,
                'score': 0.5,
                'error': str(e)
            }
    
    def calculate_overall_score(self, kyc_score: float, shop_score: float, fraud_score: float) -> float:
        """Calculate weighted overall fraud & verification score"""
        return (
            kyc_score * self.weights['kyc_completion'] +
            shop_score * self.weights['shop_verification'] +
            fraud_score * self.weights['fraud_signals']
        )
    
    # Helper Methods
    
    def _score_kyc_status(self, status: str) -> float:
        """Score KYC status"""
        status_scores = {
            'verified': 1.0,
            'approved': 1.0,
            'pending': 0.5,
            'rejected': 0.0,
            'incomplete': 0.3
        }
        return status_scores.get(status, 0.5)
    
    def _score_verification_status(self, status: str) -> float:
        """Score verification status"""
        status_scores = {
            'verified': 1.0,
            'approved': 1.0,
            'pending': 0.5,
            'rejected': 0.0,
            'incomplete': 0.3
        }
        return status_scores.get(status, 0.5)
    
    def _detect_circular_transactions(self, transactions: pd.DataFrame) -> float:
        """Detect circular transaction patterns"""
        try:
            if len(transactions) < 10:
                return 0.0
            
            # Check for rapid back-and-forth transactions
            if 'type' not in transactions.columns or 'amount' not in transactions.columns:
                return 0.0
            
            risk_score = 0.0
            
            # Check for same-day credit-debit pairs
            transactions['date_only'] = transactions['date'].dt.date
            same_day_txns = transactions.groupby('date_only')
            
            for date, day_txns in same_day_txns:
                credits = day_txns[day_txns['type'] == 'CR']['amount'].sum()
                debits = day_txns[day_txns['type'] == 'DR']['amount'].sum()
                
                # If credits and debits are very similar, might be circular
                if credits > 0 and debits > 0:
                    ratio = min(credits, debits) / max(credits, debits)
                    if ratio > 0.9:  # Very similar amounts
                        risk_score += 0.1
            
            return min(1.0, risk_score)
        except:
            return 0.0
    
    def _detect_suspicious_patterns(self, transactions: pd.DataFrame) -> List[str]:
        """Detect suspicious transaction patterns"""
        patterns = []
        
        try:
            if 'narration' not in transactions.columns and 'description' not in transactions.columns:
                return patterns
            
            narration_col = 'narration' if 'narration' in transactions.columns else 'description'
            
            # Check for suspicious keywords
            suspicious_keywords = ['cash', 'withdrawal', 'atm', 'unknown', 'unidentified']
            narration_text = transactions[narration_col].astype(str).str.lower()
            
            suspicious_count = narration_text.str.contains('|'.join(suspicious_keywords), na=False).sum()
            if suspicious_count > len(transactions) * 0.3:  # More than 30% suspicious
                patterns.append('high_suspicious_keyword_ratio')
            
            # Check for unusual amounts (round numbers, very large amounts)
            if 'amount' in transactions.columns:
                amounts = transactions['amount']
                round_numbers = (amounts % 1000 == 0).sum()
                if round_numbers > len(transactions) * 0.5:
                    patterns.append('high_round_number_ratio')
                
                if amounts.max() > amounts.median() * 10:
                    patterns.append('unusually_large_transactions')
            
        except:
            pass
        
        return patterns

