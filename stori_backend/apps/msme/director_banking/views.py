"""
Director Banking Views
======================

ViewSets for director personal bank statement analysis
Reuses consumer bank analysis logic
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import DirectorBankStatementUpload, DirectorBankAnalysisResult
from .serializers import (
    DirectorBankStatementUploadSerializer,
    DirectorBankAnalysisResultSerializer,
    DirectorBankAnalysisSummarySerializer
)

# Import consumer bank analysis functions
from apps.customer.bank_statement_analysis.analyzer import (
    load_bank_excel,
    monthly_aggregation,
    compute_core_features,
    compute_behaviour_features,
    estimate_emi,
    compute_bounce_features,
    compute_advanced_features,
    compute_impulse_behavioral_features
)


class DirectorBankStatementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for director personal bank statement analysis
    
    Endpoints:
    - list: Get all uploads
    - retrieve: Get specific upload
    - create: Upload bank statement
    - update/patch: Update upload
    - delete: Delete upload
    - analyze: Analyze bank statement using consumer flow
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = DirectorBankStatementUploadSerializer
    
    def get_queryset(self):
        """Filter uploads by user"""
        return DirectorBankStatementUpload.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Handle file upload"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """
        Analyze director's personal bank statement
        
        POST /api/msme/director-banking/{id}/analyze/
        
        Uses the same logic as consumer bank statement analysis
        """
        upload = self.get_object()
        
        if upload.processed:
            return Response({
                'success': False,
                'message': 'This bank statement has already been analyzed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Load bank statement
            file_path = upload.file.path
            account_id = upload.account_number or 'director_account'
            
            # Load based on file type
            if upload.file_type in ['xlsx', 'xls']:
                bank_df = load_bank_excel(file_path, account_id)
            else:
                return Response({
                    'success': False,
                    'message': 'Only Excel files (.xlsx, .xls) are currently supported'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Compute monthly aggregation
            monthly_df = monthly_aggregation(bank_df)
            
            # Extract all feature groups (same as consumer analysis)
            core_features = compute_core_features(bank_df, monthly_df)
            behaviour_features = compute_behaviour_features(bank_df)
            emi_features = estimate_emi(bank_df, core_features.get('monthly_income', 0))
            bounce_features = compute_bounce_features(bank_df)
            advanced_features = compute_advanced_features(
                bank_df,
                core_features.get('monthly_income', 0),
                core_features.get('monthly_expense', 0),
                emi_features.get('estimated_emi', 0)
            )
            impulse_features = compute_impulse_behavioral_features(
                bank_df,
                core_features.get('monthly_income', 0),
                core_features.get('monthly_expense', 0)
            )
            
            # Merge all features
            all_features = {
                **core_features,
                **behaviour_features,
                **emi_features,
                **bounce_features,
                **advanced_features,
                **impulse_features
            }
            
            # Additional MSME-specific analysis
            msme_features = self._extract_msme_specific_features(bank_df, all_features)
            
            # Calculate overall score
            overall_score = self._calculate_director_score(all_features)
            risk_category = self._determine_risk_category(overall_score)
            
            # Save analysis result
            result, created = DirectorBankAnalysisResult.objects.update_or_create(
                upload=upload,
                defaults={
                    'user': request.user,
                    
                    # Core features
                    'monthly_income': all_features.get('monthly_income', 0),
                    'monthly_expense': all_features.get('monthly_expense', 0),
                    'income_stability': all_features.get('income_stability', 0),
                    'spending_to_income': all_features.get('spending_to_income', 0),
                    'avg_balance': all_features.get('avg_balance', 0),
                    'min_balance': all_features.get('min_balance', 0),
                    'balance_volatility': all_features.get('balance_volatility', 0),
                    'survivability_months': all_features.get('survivability_months', 0),
                    
                    # Behavioral features
                    'late_night_txn_ratio': all_features.get('late_night_txn_ratio', 0),
                    'weekend_txn_ratio': all_features.get('weekend_txn_ratio', 0),
                    
                    # EMI features
                    'estimated_emi': all_features.get('estimated_emi', 0),
                    'emi_to_income': all_features.get('emi_to_income', 0),
                    
                    # Data quality
                    'data_confidence': all_features.get('data_confidence', 0),
                    'num_bank_accounts': all_features.get('num_bank_accounts', 1),
                    'txn_count': all_features.get('txn_count', 0),
                    'months_of_data': all_features.get('months_of_data', 0),
                    
                    # Risk indicators
                    'bounce_rate': all_features.get('bounce_rate', 0),
                    'max_inflow': all_features.get('max_inflow', 0),
                    'max_outflow': all_features.get('max_outflow', 0),
                    
                    # Advanced features
                    'upi_p2p_ratio': all_features.get('upi_p2p_ratio', 0),
                    'utility_to_income': all_features.get('utility_to_income', 0),
                    'utility_payment_consistency': all_features.get('utility_payment_consistency', 0),
                    'insurance_payment_detected': all_features.get('insurance_payment_detected', False),
                    'rent_to_income': all_features.get('rent_to_income', 0),
                    'inflow_time_consistency': all_features.get('inflow_time_consistency', 0),
                    'manipulation_risk_score': all_features.get('manipulation_risk_score', 0),
                    'expense_rigidity': all_features.get('expense_rigidity', 0),
                    
                    # Impulse features
                    'salary_retention_ratio': all_features.get('salary_retention_ratio', 0),
                    'week1_vs_week4_spending_ratio': all_features.get('week1_vs_week4_spending_ratio', 0),
                    'impulse_spending_score': all_features.get('impulse_spending_score', 0),
                    'upi_volume_spike_score': all_features.get('upi_volume_spike_score', 0),
                    'avg_balance_drop_rate': all_features.get('avg_balance_drop_rate', 0),
                    
                    # MSME-specific
                    'assets_derived': msme_features.get('assets_derived', {}),
                    'liabilities_derived': msme_features.get('liabilities_derived', {}),
                    'regular_p2p_transactions': msme_features.get('regular_p2p_transactions', False),
                    'income_volatility': msme_features.get('income_volatility', 0),
                    'subscriptions': msme_features.get('subscriptions', []),
                    'micro_commitments': msme_features.get('micro_commitments', []),
                    'savings_consistency_score': msme_features.get('savings_consistency_score', 0),
                    'is_stable': msme_features.get('is_stable', True),
                    'income_change_percentage': msme_features.get('income_change_percentage', 0),
                    
                    # Summary
                    'overall_score': overall_score,
                    'risk_category': risk_category,
                    'all_features': all_features
                }
            )
            
            # Mark upload as processed
            upload.processed = True
            upload.processed_at = timezone.now()
            upload.save()
            
            return Response({
                'success': True,
                'message': 'Director bank statement analyzed successfully',
                'data': {
                    'upload_id': upload.id,
                    'result_id': result.id,
                    'overall_score': overall_score,
                    'risk_category': risk_category,
                    'monthly_income': all_features.get('monthly_income', 0),
                    'monthly_expense': all_features.get('monthly_expense', 0),
                    'avg_balance': all_features.get('avg_balance', 0),
                    'estimated_emi': all_features.get('estimated_emi', 0),
                    'is_stable': msme_features.get('is_stable', True),
                    'features': all_features
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            upload.processing_error = str(e)
            upload.save()
            
            return Response({
                'success': False,
                'message': f'Analysis failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def result(self, request, pk=None):
        """
        Get analysis result for an upload
        
        GET /api/msme/director-banking/{id}/result/
        """
        upload = self.get_object()
        
        try:
            result = upload.analysis_result
            serializer = DirectorBankAnalysisResultSerializer(result)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except DirectorBankAnalysisResult.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Analysis not yet performed for this upload'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get summary for a specific director
        
        GET /api/msme/director-banking/summary/?pan=XXXXXXXXXX
        """
        director_pan = request.query_params.get('pan')
        
        if not director_pan:
            return Response({
                'success': False,
                'message': 'PAN parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get latest result for this director
        try:
            result = DirectorBankAnalysisResult.objects.filter(
                user=request.user,
                upload__director_pan=director_pan.upper()
            ).latest('created_at')
            
            summary_data = {
                'director_name': result.upload.director_name,
                'director_pan': result.upload.director_pan,
                'overall_score': result.overall_score,
                'risk_category': result.risk_category,
                'monthly_income': result.monthly_income,
                'monthly_expense': result.monthly_expense,
                'avg_balance': result.avg_balance,
                'income_stability': result.income_stability,
                'is_stable': result.is_stable,
                'estimated_emi': result.estimated_emi
            }
            
            serializer = DirectorBankAnalysisSummarySerializer(summary_data)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except DirectorBankAnalysisResult.DoesNotExist:
            return Response({
                'success': False,
                'message': f'No analysis found for PAN: {director_pan}'
            }, status=status.HTTP_404_NOT_FOUND)
    
    # ========== Helper Methods ==========
    
    def _extract_msme_specific_features(self, bank_df, all_features):
        """Extract MSME-specific features from bank statement"""
        
        # Assets derived (mutual funds, FDs, etc.)
        assets_derived = {
            'mutual_funds': 0,
            'fixed_deposits': 0,
            'stocks': 0
        }
        
        # Liabilities derived (loans, credit cards)
        liabilities_derived = {
            'personal_loans': all_features.get('estimated_emi', 0) * 12 * 3,  # Rough estimate
            'credit_cards': 0
        }
        
        # Regular P2P transactions
        regular_p2p = all_features.get('upi_p2p_ratio', 0) > 0.3
        
        # Income volatility
        income_volatility = all_features.get('balance_volatility', 0)
        
        # Subscriptions (Netflix, Amazon Prime, etc.)
        subscriptions = []
        
        # Micro commitments
        micro_commitments = []
        
        # Savings consistency
        savings_consistency = max(0, 1 - all_features.get('spending_to_income', 0))
        
        # Stability check
        monthly_income = all_features.get('monthly_income', 0)
        income_change = income_volatility
        is_stable = income_change < 30
        
        return {
            'assets_derived': assets_derived,
            'liabilities_derived': liabilities_derived,
            'regular_p2p_transactions': regular_p2p,
            'income_volatility': income_volatility,
            'subscriptions': subscriptions,
            'micro_commitments': micro_commitments,
            'savings_consistency_score': savings_consistency,
            'is_stable': is_stable,
            'income_change_percentage': income_change
        }
    
    def _calculate_director_score(self, features):
        """
        Calculate overall director financial health score (0-100)
        
        Weighted scoring:
        - Income stability: 25%
        - Balance health: 25%
        - EMI burden: 20%
        - Spending behavior: 15%
        - Risk indicators: 15%
        """
        score = 0
        
        # Income stability (25 points)
        income_stability = features.get('income_stability', 0)
        score += income_stability * 25
        
        # Balance health (25 points)
        avg_balance = features.get('avg_balance', 0)
        monthly_income = features.get('monthly_income', 1)
        balance_ratio = min(1, avg_balance / (monthly_income * 2)) if monthly_income > 0 else 0
        score += balance_ratio * 25
        
        # EMI burden (20 points)
        emi_to_income = features.get('emi_to_income', 0)
        emi_score = max(0, 1 - (emi_to_income / 50))  # 50% EMI = 0 score
        score += emi_score * 20
        
        # Spending behavior (15 points)
        spending_ratio = features.get('spending_to_income', 0)
        spending_score = max(0, 1 - (spending_ratio / 100))
        score += spending_score * 15
        
        # Risk indicators (15 points)
        bounce_rate = features.get('bounce_rate', 0)
        manipulation_risk = features.get('manipulation_risk_score', 0)
        risk_score = max(0, 1 - ((bounce_rate + manipulation_risk) / 2))
        score += risk_score * 15
        
        return int(round(score))
    
    def _determine_risk_category(self, score):
        """Determine risk category based on score"""
        if score >= 70:
            return 'low'
        elif score >= 40:
            return 'medium'
        else:
            return 'high'


class DirectorBankAnalysisResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for director bank analysis results (read-only)
    
    Endpoints:
    - list: Get all results
    - retrieve: Get specific result
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = DirectorBankAnalysisResultSerializer
    
    def get_queryset(self):
        """Filter results by user"""
        return DirectorBankAnalysisResult.objects.filter(user=self.request.user)

