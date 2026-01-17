"""
Unified Credit Scoring Endpoint - Testing
Calls all analysis APIs in parallel and combines with credit score
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import logging
import concurrent.futures
from typing import Dict, Any

from apps.authentication.authentication import APIKeyAuthentication
from .model_loader import ModelLoader
from .views import probability_to_score, score_to_risk_tier, get_feature_importance

# Import analysis functions directly
from apps.customer.bank_statement_analysis.json_views import extract_transactions_from_aa_format
from apps.customer.bank_statement_analysis.analyzer import (
    compute_core_features, compute_behaviour_features,
    compute_advanced_features, compute_impulse_behavioral_features,
    estimate_emi, compute_bounce_features, monthly_aggregation
)
from apps.customer.itr_analysis.analyzer import extract_itr_features_single_year
from apps.customer.credit_report_analysis.analyzer import extract_credit_features
from apps.customer.credit_report_analysis.json_views import parse_bureau_format
from apps.customer.asset_analysis.analyzer import AssetAnalyzer

logger = logging.getLogger(__name__)


class UnifiedCreditScoringView(APIView):
    """
    Unified endpoint that:
    1. Accepts all raw data from Account Aggregator
    2. Calls all analysis APIs in parallel
    3. Combines features from all sources
    4. Calculates credit score using GBM model
    5. Returns ALL analysis results + credit score
    
    POST /api/customer/credit-scoring/unified-score/
    
    Request Body:
    {
        "bank_statement": {...},  // Bank statement JSON
        "itr": {...},              // ITR JSON
        "credit_report": {...},    // Credit report JSON
        "assets": {...},           // Asset analysis JSON (SEBI format)
        "demographics": {          // Optional manual demographics
            "age": 32,
            "education_level": 3,
            "employment_type": 3,
            "employment_tenure_months": 24,
            "pan_verified": 1,
            "aadhaar_verified": 1,
            "phone_verified": 1
        }
    }
    """
    authentication_classes = [APIKeyAuthentication]
    
    def post(self, request):
        """
        Unified credit scoring from all data sources
        Returns all analysis results + credit score
        """
        try:
            data = request.data
            
            # Get API key from request headers
            api_key = request.META.get('HTTP_X_API_KEY', '')
            base_url = request.build_absolute_uri('/').rstrip('/')
            
            # Run all analyses in parallel
            analysis_results = self._run_all_analyses_parallel(data, base_url, api_key)
            
            # Combine features from all sources
            combined_features = self._combine_features(analysis_results, data.get('demographics', {}))
            
            # Calculate credit score
            score_result = self._calculate_credit_score(combined_features)
            
            # Prepare comprehensive response with ALL data
            response_data = {
                'success': True,
                'message': 'Unified analysis and credit scoring completed successfully',
                'data': {
                    # Credit Score Results
                    'credit_score': score_result['credit_score'],
                    'default_probability': score_result['default_probability'],
                    'risk_tier': score_result['risk_tier'],
                    'risk_description': score_result['risk_description'],
                    'recommendation': score_result['recommendation'],
                    'feature_importance': score_result.get('feature_importance', []),
                    
                    # All Analysis Results (Complete)
                    'bank_statement_analysis': analysis_results.get('bank_statement', {}),
                    'itr_analysis': analysis_results.get('itr', {}),
                    'credit_report_analysis': analysis_results.get('credit_report', {}),
                    'asset_analysis': analysis_results.get('assets', {}),
                    
                    # Combined Features (for model input)
                    'combined_features': combined_features,
                    
                    # Summary
                    'summary': {
                        'total_analyses': len([k for k, v in analysis_results.items() if v.get('success')]),
                        'analyses_completed': [k for k, v in analysis_results.items() if v.get('success')],
                        'analyses_failed': [k for k, v in analysis_results.items() if not v.get('success')],
                        'credit_score': score_result['credit_score'],
                        'risk_tier': score_result['risk_tier']
                    },
                    
                    'processed_at': timezone.now().isoformat()
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Unified credit scoring failed: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': f'Unified credit scoring failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _run_all_analyses_parallel(self, data: Dict, base_url: str, api_key: str) -> Dict[str, Any]:
        """
        Run all analysis functions in parallel (direct function calls)
        """
        results = {}
        
        # Run analyses in parallel using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            # Bank Statement Analysis
            if 'bank_statement' in data:
                futures['bank_statement'] = executor.submit(
                    self._analyze_bank_statement_direct,
                    data.get('bank_statement', {})
                )
            
            # ITR Analysis
            if 'itr' in data:
                futures['itr'] = executor.submit(
                    self._analyze_itr_direct,
                    data.get('itr', {})
                )
            
            # Credit Report Analysis
            if 'credit_report' in data:
                futures['credit_report'] = executor.submit(
                    self._analyze_credit_report_direct,
                    data.get('credit_report', {})
                )
            
            # Asset Analysis
            if 'assets' in data:
                futures['assets'] = executor.submit(
                    self._analyze_assets_direct,
                    data.get('assets', {})
                )
            
            # Collect results
            for key, future in futures.items():
                try:
                    results[key] = future.result(timeout=60)  # 60 second timeout per analysis
                except Exception as e:
                    logger.error(f"Analysis {key} failed: {e}", exc_info=True)
                    results[key] = {
                        'success': False,
                        'error': str(e),
                        'message': f'Analysis {key} failed: {str(e)}'
                    }
        
        return results
    
    def _analyze_bank_statement_direct(self, bank_data: Dict) -> Dict:
        """Direct bank statement analysis"""
        try:
            import pandas as pd
            
            # Extract transactions
            transactions, account_info = extract_transactions_from_aa_format(bank_data)
            
            if not transactions:
                # Try standard format
                transactions = bank_data.get('transactions', [])
                account_info = bank_data.get('account_info', {})
            
            if not transactions:
                return {
                    'success': False,
                    'message': 'No transactions found in bank statement data'
                }
            
            # Convert to DataFrame
            df = pd.DataFrame(transactions)
            
            # Add account_id
            if 'account_id' not in df.columns:
                df['account_id'] = account_info.get('account_number', 'default')
            
            # Compute features
            monthly_df = monthly_aggregation(df)
            core_features = compute_core_features(df, monthly_df)
            behaviour_features = compute_behaviour_features(df)
            emi_features = estimate_emi(df, core_features.get('monthly_income', 0))
            bounce_features = compute_bounce_features(df)
            advanced_features = compute_advanced_features(
                df,
                core_features.get('monthly_income', 0),
                core_features.get('monthly_expense', 0),
                emi_features.get('estimated_emi', 0)
            )
            impulse_features = compute_impulse_behavioral_features(
                df,
                core_features.get('monthly_income', 0),
                core_features.get('monthly_expense', 0)
            )
            
            # Combine all features
            all_features = {
                **core_features,
                **behaviour_features,
                **emi_features,
                **bounce_features,
                **advanced_features,
                **impulse_features
            }
            
            # Build summary
            summary = {
                'total_transactions': len(df),
                'total_credits': df[df['amount'] > 0]['amount'].sum() if 'amount' in df.columns else 0,
                'total_debits': abs(df[df['amount'] < 0]['amount'].sum()) if 'amount' in df.columns else 0,
                'average_balance': core_features.get('avg_balance', 0),
                'monthly_income': core_features.get('monthly_income', 0),
                'monthly_expense': core_features.get('monthly_expense', 0),
                'account_number': account_info.get('account_number', ''),
                'bank_name': account_info.get('bank_name', ''),
                'ifsc': account_info.get('ifsc', ''),
                'holder_name': account_info.get('holder_name', ''),
                'analysis_date': timezone.now().isoformat(),
                'months_of_data': monthly_df.shape[0] if monthly_df is not None and not monthly_df.empty else 0
            }
            
            return {
                'success': True,
                'message': 'Bank statement analyzed successfully',
                'data': {
                    'features': all_features,
                    'summary': summary
                }
            }
            
        except Exception as e:
            logger.error(f"Bank statement analysis error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'message': f'Bank statement analysis failed: {str(e)}'
            }
    
    def _analyze_itr_direct(self, itr_data: Dict) -> Dict:
        """Direct ITR analysis"""
        try:
            # Extract features
            features = extract_itr_features_single_year(itr_data)
            
            # Build summary
            summary = {
                'assessment_year': features.get('assessment_year', ''),
                'form_type': features.get('form_type', ''),
                'net_taxable_income': features.get('itr_net_taxable_income', 0),
                'gross_total_income': features.get('itr_gross_total_income', 0),
                'tax_paid': features.get('itr_tax_paid', 0),
                'salary_income': features.get('itr_salary_income', 0),
                'business_income': features.get('itr_business_income', 0),
                'income_type': 'Business' if features.get('itr_business_income', 0) > features.get('itr_salary_income', 0) else 'Salaried',
                'total_deductions': features.get('itr_total_deductions', 0),
                'analysis_date': timezone.now().isoformat()
            }
            
            return {
                'success': True,
                'message': 'ITR analyzed successfully',
                'data': {
                    'features': features,
                    'summary': summary
                }
            }
            
        except Exception as e:
            logger.error(f"ITR analysis error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'message': f'ITR analysis failed: {str(e)}'
            }
    
    def _analyze_credit_report_direct(self, credit_data: Dict) -> Dict:
        """Direct credit report analysis"""
        try:
            # Parse bureau format if needed
            if 'result' in credit_data or 'INProfileResponse' in credit_data:
                credit_data = parse_bureau_format(credit_data)
            
            # Extract features
            features = extract_credit_features(credit_data)
            
            # Build summary
            summary = {
                'bureau_score': features.get('bureau_score', 0),
                'total_accounts': features.get('total_accounts', 0),
                'active_accounts': features.get('active_accounts', 0),
                'utilization_ratio': features.get('utilization_ratio', 0),
                'total_outstanding': features.get('total_outstanding', 0),
                'analysis_date': timezone.now().isoformat()
            }
            
            return {
                'success': True,
                'message': 'Credit report analyzed successfully',
                'data': {
                    'features': features,
                    'summary': summary
                }
            }
            
        except Exception as e:
            logger.error(f"Credit report analysis error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'message': f'Credit report analysis failed: {str(e)}'
            }
    
    def _analyze_assets_direct(self, asset_data: Dict) -> Dict:
        """Direct asset analysis"""
        try:
            analyzer = AssetAnalyzer()
            analyzer.load_from_aa_json(asset_data)
            analysis = analyzer.calculate_analysis()
            
            # Build summary
            summary = {
                'total_assets': analysis['num_assets'],
                'total_value': analysis['total_asset_value'],
                'survivability_value': analysis['survivability_asset_value'],
                'highest_asset': analysis['highest_quantified_amount'],
                'liquidity_breakdown': {
                    'liquid': analysis['liquid_assets'],
                    'semi_liquid': analysis['semi_liquid_assets'],
                    'illiquid': analysis['illiquid_assets'],
                    'liquidity_ratio': analysis['liquidity_ratio']
                },
                'asset_type_breakdown': {
                    'stocks': analysis['stocks_value'],
                    'mutual_funds': analysis['mutual_funds_value'],
                    'fixed_deposits': analysis['fixed_deposits_value'],
                    'gold': analysis['gold_value'],
                    'real_estate': analysis['real_estate_value'],
                    'insurance': analysis['insurance_value'],
                    'provident_fund': analysis['provident_fund_value'],
                    'bonds': analysis['bonds_value'],
                    'nps': analysis['nps_value'],
                    'crypto': analysis['crypto_value']
                },
                'portfolio_returns_pct': analysis['portfolio_returns_pct']
            }
            
            return {
                'success': True,
                'message': 'Assets analyzed successfully',
                'data': {
                    'analysis': analysis,
                    'summary': summary,
                    'processed_at': timezone.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Asset analysis error: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'message': f'Asset analysis failed: {str(e)}'
            }
    
    def _combine_features(self, analysis_results: Dict, demographics: Dict) -> Dict:
        """
        Combine features from all analysis sources
        Maps to GBM model's expected feature names
        """
        combined = {}
        
        # Start with demographics
        combined.update({
            'age': demographics.get('age', 30),
            'education_level': demographics.get('education_level', 3),
            'employment_type': demographics.get('employment_type', 3),
            'employment_tenure_months': demographics.get('employment_tenure_months', 12),
            'name_dob_verified': demographics.get('name_dob_verified', 0),
            'pan_verified': demographics.get('pan_verified', 0),
            'aadhaar_verified': demographics.get('aadhaar_verified', 0),
            'phone_verified': demographics.get('phone_verified', 0),
            'phone_age_months': demographics.get('phone_age_months', 0),
            'email_verified': demographics.get('email_verified', 0),
            'email_age_months': demographics.get('email_age_months', 0),
            'dependents_count': demographics.get('dependents_count', 0),
            'job_changes_3y': demographics.get('job_changes_3y', 0),
            'monthly_income_stability': demographics.get('monthly_income_stability', 0.8),
            'income_cv': demographics.get('income_cv', 0.1),
            'employment_history_score': demographics.get('employment_history_score', 70),
            'vehicle_owned': demographics.get('vehicle_owned', 0),
        })
        
        # Bank Statement Features
        if analysis_results.get('bank_statement', {}).get('success'):
            bank_data = analysis_results['bank_statement'].get('data', {})
            bank_features = bank_data.get('features', {})
            bank_summary = bank_data.get('summary', {})
            
            combined.update({
                'monthly_income': bank_features.get('monthly_income', 0),
                'monthly_expense': bank_features.get('monthly_expense', 0),
                'avg_balance': bank_features.get('avg_balance', 0),
                'min_balance': bank_features.get('min_balance', 0),
                'balance_volatility': bank_features.get('balance_volatility', 0),
                'avg_monthly_credits': bank_summary.get('total_credits', 0) / max(bank_summary.get('months_of_data', 1), 1) if bank_summary.get('months_of_data', 0) > 0 else 0,
                'avg_monthly_debits': bank_summary.get('total_debits', 0) / max(bank_summary.get('months_of_data', 1), 1) if bank_summary.get('months_of_data', 0) > 0 else 0,
                'income_stability': bank_features.get('income_stability', 0),
                'bounce_rate': bank_features.get('bounce_rate', 0),
                'negative_balance_days_ratio': bank_features.get('bounce_rate', 0),  # Approximate
            })
        
        # ITR Features
        if analysis_results.get('itr', {}).get('success'):
            itr_data = analysis_results['itr'].get('data', {})
            itr_features = itr_data.get('features', {})
            
            combined.update({
                'itr_net_taxable_income': itr_features.get('itr_net_taxable_income', 0),
                'itr_gross_total_income': itr_features.get('itr_gross_total_income', 0),
                'itr_salary_income': itr_features.get('itr_salary_income', 0),
                'itr_business_income': itr_features.get('itr_business_income', 0),
                'tax_compliance_score': itr_features.get('tax_compliance_score', 0),
                'income_source_verification': 1 if itr_features.get('itr_net_taxable_income', 0) > 0 else 0,
            })
            
            # Use ITR income if available and higher than bank income
            itr_income = itr_features.get('itr_net_taxable_income', 0) / 12  # Monthly
            if itr_income > combined.get('monthly_income', 0):
                combined['monthly_income'] = itr_income
        
        # Credit Report Features
        if analysis_results.get('credit_report', {}).get('success'):
            credit_data = analysis_results['credit_report'].get('data', {})
            credit_features = credit_data.get('features', {})
            
            combined.update({
                'credit_score': credit_features.get('bureau_score', 0),
                'credit_accounts_total': credit_features.get('total_accounts', 0),
                'credit_accounts_active': credit_features.get('active_accounts', 0),
                'credit_utilization_ratio': credit_features.get('utilization_ratio', 0),
                'dpd_30_count': credit_features.get('dpd_30_count', 0),
                'dpd_60_count': credit_features.get('dpd_60_count', 0),
                'dpd_90_count': credit_features.get('dpd_90_count', 0),
                'credit_enquiries_3m': credit_features.get('enquiries_3m', 0),
                'credit_enquiries_6m': credit_features.get('enquiries_6m', 0),
            })
        
        # Asset Features
        if analysis_results.get('assets', {}).get('success'):
            asset_data = analysis_results['assets'].get('data', {})
            asset_analysis = asset_data.get('analysis', {})
            
            combined.update({
                'total_financial_assets': asset_analysis.get('total_asset_value', 0),
                'liquid_assets': asset_analysis.get('liquid_assets', 0),
                'property_owned': 1 if asset_analysis.get('real_estate_value', 0) > 0 else 0,
            })
        
        # Fill missing features with defaults (for model compatibility)
        default_features = {
            'monthly_income': 0,
            'monthly_expense': 0,
            'avg_balance': 0,
            'min_balance': 0,
            'balance_volatility': 0,
            'avg_monthly_credits': 0,
            'avg_monthly_debits': 0,
            'income_stability': 0,
            'bounce_rate': 0,
            'negative_balance_days_ratio': 0,
            'credit_score': 0,
            'credit_accounts_total': 0,
            'credit_accounts_active': 0,
            'credit_utilization_ratio': 0,
            'dpd_30_count': 0,
            'dpd_60_count': 0,
            'dpd_90_count': 0,
            'credit_enquiries_3m': 0,
            'credit_enquiries_6m': 0,
            'total_financial_assets': 0,
            'liquid_assets': 0,
            'property_owned': 0,
            'itr_net_taxable_income': 0,
            'itr_gross_total_income': 0,
            'itr_salary_income': 0,
            'itr_business_income': 0,
            'tax_compliance_score': 0,
            'income_source_verification': 0,
        }
        
        for key, default_value in default_features.items():
            if key not in combined:
                combined[key] = default_value
        
        return combined
    
    def _calculate_credit_score(self, features: Dict) -> Dict:
        """Calculate credit score using GBM model"""
        try:
            model_loader = ModelLoader.get_instance()
            if not model_loader.is_loaded():
                raise Exception('Credit scoring model not available')
            
            model = model_loader.model
            feature_names = model_loader.feature_names
            
            # Create DataFrame
            import pandas as pd
            df = pd.DataFrame([features])
            
            # Ensure all model features are present
            if feature_names:
                for feature in feature_names:
                    if feature not in df.columns:
                        df[feature] = 0
                
                # Reorder columns to match model training
                df = df[feature_names]
            
            # Predict
            # Handle LightGBM Booster (uses predict()) vs sklearn models (uses predict_proba())
            if hasattr(model, 'predict_proba'):
                # Sklearn-style model
                default_prob = float(model.predict_proba(df)[0][1])
            else:
                # LightGBM Booster - predict() returns probability directly for binary classification
                default_prob = float(model.predict(df)[0])
            
            credit_score = probability_to_score(default_prob)
            risk_info = score_to_risk_tier(credit_score)
            
            # Get feature importance
            feature_importance = get_feature_importance(model, feature_names or list(df.columns), top_n=10)
            
            return {
                'credit_score': credit_score,
                'default_probability': round(default_prob, 4),
                'risk_tier': risk_info['tier'],
                'risk_description': risk_info['description'],
                'recommendation': risk_info['recommendation'],
                'feature_importance': feature_importance
            }
            
        except Exception as e:
            logger.error(f"Credit score calculation error: {e}", exc_info=True)
            raise

