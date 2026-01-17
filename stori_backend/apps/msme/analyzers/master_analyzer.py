"""
MSME Master Analyzer
====================

Orchestrates all MSME analysis modules and produces final credit score.

Section Weights (as per requirements):
- A) Director / Promoter Profile: 10%
- B) Business Identity & Registration: 10%
- C) Revenue & Business Performance: 20%
- D) Cash Flow & Banking: 25%
- E) Credit & Repayment: 22%
- F) Compliance & Taxation: 12%
- G) Fraud & Verification: 7%
- H) External Signals: 4%
- I) Vendor Payments: (Distributed across other sections)

Total: 100%
"""

from typing import Dict, Any
import numpy as np

from .director_analyzer import DirectorAnalyzer
from .business_identity_analyzer import BusinessIdentityAnalyzer
from .revenue_analyzer import RevenueAnalyzer
from .cashflow_analyzer import CashFlowAnalyzer
from .credit_repayment_analyzer import CreditRepaymentAnalyzer
from .compliance_analyzer import ComplianceAnalyzer
from .fraud_analyzer import FraudAnalyzer
from .external_signals_analyzer import ExternalSignalsAnalyzer
from .vendor_analyzer import VendorAnalyzer


class MSMEMasterAnalyzer:
    """Master analyzer that coordinates all MSME analysis modules"""
    
    def __init__(self):
        # Initialize all analyzers
        self.director_analyzer = DirectorAnalyzer()
        self.business_identity_analyzer = BusinessIdentityAnalyzer()
        self.revenue_analyzer = RevenueAnalyzer()
        self.cashflow_analyzer = CashFlowAnalyzer()
        self.credit_repayment_analyzer = CreditRepaymentAnalyzer()
        self.compliance_analyzer = ComplianceAnalyzer()
        self.fraud_analyzer = FraudAnalyzer()
        self.external_signals_analyzer = ExternalSignalsAnalyzer()
        self.vendor_analyzer = VendorAnalyzer()
        
        # Section weights (must sum to 1.0)
        self.section_weights = {
            'director': 0.10,           # 10%
            'business_identity': 0.10,  # 10%
            'revenue': 0.20,            # 20%
            'cashflow': 0.25,           # 25%
            'credit': 0.22,             # 22%
            'compliance': 0.07,         # 7%
            'fraud': 0.04,              # 4%
            'external': 0.02,           # 2%
            'vendor': 0.00              # Integrated into other sections
        }
    
    def analyze_complete_msme(self, msme_data: Dict) -> Dict[str, Any]:
        """
        Perform complete MSME analysis across all sections
        
        Args:
            msme_data: Complete MSME data including all sections
            
        Returns:
            Dict with comprehensive analysis results
        """
        results = {
            'section_results': {},
            'section_scores': {},
            'all_features': {},
            'final_score': 0,
            'risk_tier': 'high_risk',
            'default_probability': 1.0
        }
        
        try:
            # A) Director / Promoter Analysis
            director_results = self._analyze_director_section(
                msme_data.get('director_data', {}),
                msme_data.get('personal_bank_data', {})
            )
            results['section_results']['director'] = director_results
            results['section_scores']['director'] = director_results['overall_score']
            
            # B) Business Identity Analysis
            business_results = self._analyze_business_identity_section(
                msme_data.get('business_data', {}),
                msme_data.get('verification_data', {})
            )
            results['section_results']['business_identity'] = business_results
            results['section_scores']['business_identity'] = business_results['overall_score']
            
            # C) Revenue & Business Performance Analysis
            revenue_results = self._analyze_revenue_section(
                msme_data.get('revenue_data', {}),
                msme_data.get('financial_data', {}),
                msme_data.get('msme_category', 'micro')
            )
            results['section_results']['revenue'] = revenue_results
            results['section_scores']['revenue'] = revenue_results['overall_score']
            
            # D) Cash Flow & Banking Analysis
            cashflow_results = self._analyze_cashflow_section(
                msme_data.get('bank_data', {})
            )
            results['section_results']['cashflow'] = cashflow_results
            results['section_scores']['cashflow'] = cashflow_results['overall_score']
            
            # E) Credit & Repayment Analysis
            credit_results = self._analyze_credit_section(
                msme_data.get('bank_data', {}),
                msme_data.get('credit_report', {})
            )
            results['section_results']['credit'] = credit_results
            results['section_scores']['credit'] = credit_results['overall_score']
            
            # F) Compliance & Taxation Analysis
            compliance_results = self._analyze_compliance_section(
                msme_data.get('gst_data', {}),
                msme_data.get('itr_data', {}),
                msme_data.get('bank_data', {}),
                msme_data.get('platform_data', {})
            )
            results['section_results']['compliance'] = compliance_results
            results['section_scores']['compliance'] = compliance_results['overall_score']
            
            # G) Fraud & Verification Analysis
            fraud_results = self._analyze_fraud_section(
                msme_data.get('kyc_data', {}),
                msme_data.get('shop_data', {}),
                msme_data.get('bank_data', {})
            )
            results['section_results']['fraud'] = fraud_results
            results['section_scores']['fraud'] = fraud_results['overall_score']
            
            # H) External Signals Analysis
            external_results = self._analyze_external_section(
                msme_data.get('reviews_data', {})
            )
            results['section_results']['external'] = external_results
            results['section_scores']['external'] = external_results['overall_score']
            
            # I) Vendor Payments Analysis (informational)
            vendor_results = self._analyze_vendor_section(
                msme_data.get('gst2b_data', {}),
                msme_data.get('bank_data', {})
            )
            results['section_results']['vendor'] = vendor_results
            results['section_scores']['vendor'] = vendor_results['overall_score']
            
            # Calculate final weighted score
            weighted_score = self._calculate_weighted_score(results['section_scores'])
            
            # Convert to credit score (300-900)
            credit_score = self._convert_to_credit_score(weighted_score)
            
            # Determine risk tier
            risk_tier = self._determine_risk_tier(credit_score)
            
            # Estimate default probability
            default_prob = self._estimate_default_probability(credit_score)
            
            results['final_score'] = credit_score
            results['weighted_score'] = weighted_score
            results['risk_tier'] = risk_tier
            results['default_probability'] = default_prob
            
            # Aggregate all features for model input
            results['all_features'] = self._aggregate_features(results['section_results'])
            
            return results
            
        except Exception as e:
            results['error'] = str(e)
            return results
    
    def _analyze_director_section(self, director_data: Dict, bank_data: Dict) -> Dict[str, Any]:
        """Analyze director/promoter section"""
        personal_banking = self.director_analyzer.analyze_personal_banking(bank_data)
        behavioral = self.director_analyzer.analyze_behavioral_signals(bank_data)
        stability = self.director_analyzer.analyze_financial_stability(bank_data)
        
        overall_score = self.director_analyzer.calculate_overall_score(
            personal_banking['score'],
            behavioral['score'],
            stability['score']
        )
        
        return {
            'personal_banking': personal_banking,
            'behavioral_signals': behavioral,
            'financial_stability': stability,
            'overall_score': overall_score
        }
    
    def _analyze_business_identity_section(self, business_data: Dict, verification_data: Dict) -> Dict[str, Any]:
        """Analyze business identity section"""
        basics = self.business_identity_analyzer.analyze_business_basics(business_data)
        verification = self.business_identity_analyzer.analyze_verification(verification_data)
        locations = self.business_identity_analyzer.analyze_locations(business_data)
        
        overall_score = self.business_identity_analyzer.calculate_overall_score(
            basics['overall_score'],
            verification['overall_score'],
            locations['score']
        )
        
        return {
            'business_basics': basics,
            'verification': verification,
            'locations': locations,
            'overall_score': overall_score
        }
    
    def _analyze_revenue_section(self, revenue_data: Dict, financial_data: Dict, msme_category: str) -> Dict[str, Any]:
        """Analyze revenue & performance section"""
        revenue_metrics = self.revenue_analyzer.analyze_revenue_metrics(revenue_data, msme_category)
        profitability = self.revenue_analyzer.analyze_profitability(financial_data)
        transactions = self.revenue_analyzer.analyze_transaction_analytics(revenue_data)
        concentration = self.revenue_analyzer.analyze_concentration_risk(revenue_data)
        cost_efficiency = self.revenue_analyzer.analyze_cost_efficiency(financial_data)
        
        overall_score = self.revenue_analyzer.calculate_overall_score(
            revenue_metrics['overall_score'],
            profitability['score'],
            transactions['score'],
            concentration['score'],
            cost_efficiency['score']
        )
        
        return {
            'revenue_metrics': revenue_metrics,
            'profitability': profitability,
            'transaction_analytics': transactions,
            'concentration_risk': concentration,
            'cost_efficiency': cost_efficiency,
            'overall_score': overall_score
        }
    
    def _analyze_cashflow_section(self, bank_data: Dict) -> Dict[str, Any]:
        """Analyze cash flow & banking section"""
        balance_metrics = self.cashflow_analyzer.analyze_bank_balance_metrics(bank_data)
        inflow_outflow = self.cashflow_analyzer.analyze_inflow_outflow(bank_data, exclude_p2p=True)
        deposit_consistency = self.cashflow_analyzer.analyze_deposit_consistency(bank_data)
        
        overall_score = self.cashflow_analyzer.calculate_overall_score(
            balance_metrics['score'],
            inflow_outflow['score']
        )
        
        return {
            'balance_metrics': balance_metrics,
            'inflow_outflow': inflow_outflow,
            'deposit_consistency': deposit_consistency,  # Display only
            'overall_score': overall_score
        }
    
    def _analyze_credit_section(self, bank_data: Dict, credit_report: Dict) -> Dict[str, Any]:
        """Analyze credit & repayment section"""
        repayment = self.credit_repayment_analyzer.analyze_repayment_discipline(bank_data, credit_report)
        debt_position = self.credit_repayment_analyzer.analyze_debt_position(credit_report, bank_data)
        regular_payments = self.credit_repayment_analyzer.analyze_regular_payments(bank_data)
        
        overall_score = self.credit_repayment_analyzer.calculate_overall_score(
            repayment['score'],
            debt_position['score'],
            regular_payments['score']
        )
        
        return {
            'repayment_discipline': repayment,
            'debt_position': debt_position,
            'regular_payments': regular_payments,
            'overall_score': overall_score
        }
    
    def _analyze_compliance_section(self, gst_data: Dict, itr_data: Dict, 
                                   bank_data: Dict, platform_data: Dict) -> Dict[str, Any]:
        """Analyze compliance & taxation section"""
        filing = self.compliance_analyzer.analyze_gst_itr_discipline(gst_data, itr_data)
        mismatch = self.compliance_analyzer.analyze_mismatch_checks(gst_data, platform_data, itr_data)
        tax_payments = self.compliance_analyzer.analyze_tax_payments(bank_data)
        refunds = self.compliance_analyzer.analyze_refund_chargeback_rate(platform_data or bank_data, gst_data)
        
        overall_score = self.compliance_analyzer.calculate_overall_score(
            filing['score'],
            mismatch['score'],
            tax_payments['score'],
            refunds['score']
        )
        
        return {
            'gst_itr_discipline': filing,
            'mismatch_checks': mismatch,
            'tax_payments': tax_payments,
            'refund_chargeback': refunds,
            'overall_score': overall_score
        }
    
    def _analyze_fraud_section(self, kyc_data: Dict, shop_data: Dict, bank_data: Dict) -> Dict[str, Any]:
        """Analyze fraud & verification section"""
        kyc = self.fraud_analyzer.analyze_kyc_completion(kyc_data)
        shop = self.fraud_analyzer.analyze_shop_verification(shop_data)
        fraud_signals = self.fraud_analyzer.analyze_banking_fraud_signals(bank_data)
        
        overall_score = self.fraud_analyzer.calculate_overall_score(
            kyc['score'],
            shop['score'],
            fraud_signals['score']
        )
        
        return {
            'kyc_completion': kyc,
            'shop_verification': shop,
            'fraud_signals': fraud_signals,
            'overall_score': overall_score
        }
    
    def _analyze_external_section(self, reviews_data: Dict) -> Dict[str, Any]:
        """Analyze external signals section"""
        reviews = self.external_signals_analyzer.analyze_online_reviews(reviews_data)
        
        overall_score = self.external_signals_analyzer.calculate_overall_score(reviews['score'])
        
        return {
            'online_reviews': reviews,
            'overall_score': overall_score
        }
    
    def _analyze_vendor_section(self, gst2b_data: Dict, bank_data: Dict) -> Dict[str, Any]:
        """Analyze vendor payments section"""
        payment_behavior = self.vendor_analyzer.analyze_vendor_payment_behavior(gst2b_data, bank_data)
        vendor_strength = self.vendor_analyzer.analyze_vendor_strength(gst2b_data)
        transaction_analytics = self.vendor_analyzer.analyze_vendor_transaction_analytics(gst2b_data)
        
        overall_score = self.vendor_analyzer.calculate_overall_score(
            payment_behavior['score'],
            vendor_strength['score'],
            transaction_analytics['score']
        )
        
        return {
            'payment_behavior': payment_behavior,
            'vendor_strength': vendor_strength,
            'transaction_analytics': transaction_analytics,
            'overall_score': overall_score
        }
    
    def _calculate_weighted_score(self, section_scores: Dict[str, float]) -> float:
        """Calculate weighted final score from all sections"""
        weighted_sum = 0
        
        for section, weight in self.section_weights.items():
            score = section_scores.get(section, 0)
            weighted_sum += score * weight
        
        # Normalize to 0-1
        return min(1.0, max(0.0, weighted_sum))
    
    def _convert_to_credit_score(self, weighted_score: float) -> int:
        """Convert 0-1 score to 300-900 credit score"""
        # Linear mapping
        min_score = 300
        max_score = 900
        
        credit_score = min_score + (weighted_score * (max_score - min_score))
        
        return int(round(credit_score))
    
    def _determine_risk_tier(self, credit_score: int) -> str:
        """Determine risk tier based on credit score"""
        if credit_score >= 750:
            return 'prime'
        elif credit_score >= 650:
            return 'near_prime'
        elif credit_score >= 550:
            return 'standard'
        elif credit_score >= 450:
            return 'subprime'
        else:
            return 'high_risk'
    
    def _estimate_default_probability(self, credit_score: int) -> float:
        """Estimate default probability from credit score"""
        # Inverse relationship: higher score = lower probability
        # Using exponential decay
        
        # Map credit score to probability
        score_mapping = {
            900: 0.00,
            750: 0.02,
            650: 0.05,
            550: 0.12,
            450: 0.25,
            400: 0.40,
            350: 0.60,
            300: 1.00
        }
        
        # Find surrounding points and interpolate
        scores = sorted(score_mapping.keys(), reverse=True)
        
        for i in range(len(scores) - 1):
            s1, s2 = scores[i], scores[i+1]
            p1, p2 = score_mapping[s1], score_mapping[s2]
            
            if s2 <= credit_score <= s1:
                # Linear interpolation
                prob = p1 + (p2 - p1) * (s1 - credit_score) / (s1 - s2)
                return round(prob, 4)
        
        # Default
        return 1.0 if credit_score < 300 else 0.0
    
    def _aggregate_features(self, section_results: Dict) -> Dict:
        """Aggregate all features from section results into a flat dictionary"""
        features = {}
        
        for section, results in section_results.items():
            # Flatten nested results
            self._flatten_dict(results, features, prefix=f"{section}_")
        
        return features
    
    def _flatten_dict(self, d: Dict, result: Dict, prefix: str = ''):
        """Recursively flatten nested dictionary"""
        for key, value in d.items():
            new_key = f"{prefix}{key}"
            
            if isinstance(value, dict) and 'score' not in key.lower():
                self._flatten_dict(value, result, prefix=new_key + '_')
            elif isinstance(value, (int, float, str, bool)):
                result[new_key] = value
            elif isinstance(value, list) and len(value) > 0 and not isinstance(value[0], dict):
                result[new_key] = value

