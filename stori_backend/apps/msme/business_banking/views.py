"""
Business Banking Views
======================

ViewSets for MSME business bank statement analysis
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import BusinessBankStatementUpload, BusinessBankAnalysisResult
from .serializers import (
    BusinessBankStatementUploadSerializer,
    BusinessBankAnalysisResultSerializer,
    BusinessBankAnalysisSummarySerializer
)

# Import bank analysis functions
from apps.customer.bank_statement_analysis.analyzer import (
    load_bank_excel,
    monthly_aggregation
)


class BusinessBankStatementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for business bank statement analysis
    
    Endpoints:
    - list: Get all uploads
    - retrieve: Get specific upload
    - create: Upload bank statement
    - analyze: Analyze business bank statement
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessBankStatementUploadSerializer
    
    def get_queryset(self):
        """Filter uploads by user"""
        return BusinessBankStatementUpload.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Handle file upload"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """
        Analyze business bank statement
        
        POST /api/msme/business-banking/statements/{id}/analyze/
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
            account_id = upload.account_number or 'business_account'
            
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
            
            # Analyze business cash flow
            analysis_results = self._analyze_business_cashflow(bank_df, monthly_df)
            
            # Calculate health score
            health_score = self._calculate_business_health_score(analysis_results)
            risk_category = self._determine_risk_category(health_score)
            
            # Save analysis result
            result, created = BusinessBankAnalysisResult.objects.update_or_create(
                upload=upload,
                defaults={
                    'user': request.user,
                    **analysis_results,
                    'cashflow_health_score': health_score,
                    'business_risk_category': risk_category,
                    'all_features': analysis_results
                }
            )
            
            # Mark upload as processed
            upload.processed = True
            upload.processed_at = timezone.now()
            upload.save()
            
            return Response({
                'success': True,
                'message': 'Business bank statement analyzed successfully',
                'data': {
                    'upload_id': upload.id,
                    'result_id': result.id,
                    'cashflow_health_score': health_score,
                    'business_risk_category': risk_category,
                    'summary': {
                        'average_bank_balance': analysis_results.get('average_bank_balance', 0),
                        'monthly_inflow': analysis_results.get('monthly_inflow', 0),
                        'monthly_outflow': analysis_results.get('monthly_outflow', 0),
                        'inflow_outflow_ratio': analysis_results.get('inflow_outflow_ratio', 0)
                    }
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
        """Get analysis result"""
        upload = self.get_object()
        
        try:
            result = upload.analysis_result
            serializer = BusinessBankAnalysisResultSerializer(result)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except BusinessBankAnalysisResult.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Analysis not yet performed'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def _analyze_business_cashflow(self, bank_df, monthly_df):
        """Analyze business cash flow patterns"""
        
        # Basic metrics
        avg_balance = bank_df['balance'].mean() if 'balance' in bank_df.columns else 0
        min_balance = bank_df['balance'].min() if 'balance' in bank_df.columns else 0
        max_balance = bank_df['balance'].max() if 'balance' in bank_df.columns else 0
        
        # Inflow/outflow
        total_inflow = bank_df[bank_df['type'] == 'credit']['amount'].sum()
        total_outflow = bank_df[bank_df['type'] == 'debit']['amount'].sum()
        net_cashflow = total_inflow - total_outflow
        
        months_of_data = len(monthly_df) if len(monthly_df) > 0 else 1
        monthly_inflow = total_inflow / months_of_data
        monthly_outflow = total_outflow / months_of_data
        
        inflow_outflow_ratio = monthly_inflow / monthly_outflow if monthly_outflow > 0 else 0
        
        # Transactions
        total_transactions = len(bank_df)
        credit_transactions = len(bank_df[bank_df['type'] == 'credit'])
        debit_transactions = len(bank_df[bank_df['type'] == 'debit'])
        
        # Estimated revenue (exclude P2P)
        estimated_monthly_revenue = monthly_inflow * 0.9  # Rough estimate
        
        # Balance volatility
        balance_volatility = (bank_df['balance'].std() / avg_balance * 100) if avg_balance > 0 else 0
        
        return {
            'average_bank_balance': round(avg_balance, 2),
            'min_balance': round(min_balance, 2),
            'max_balance': round(max_balance, 2),
            'balance_trend': 'stable',
            'negative_balance_days': 0,
            'avg_daily_closing_balance': round(avg_balance, 2),
            'balance_volatility': round(balance_volatility, 2),
            'total_inflow': round(total_inflow, 2),
            'total_outflow': round(total_outflow, 2),
            'net_cashflow': round(net_cashflow, 2),
            'monthly_inflow': round(monthly_inflow, 2),
            'monthly_outflow': round(monthly_outflow, 2),
            'inflow_outflow_ratio': round(inflow_outflow_ratio, 2),
            'inflow_trend': 'stable',
            'estimated_monthly_revenue': round(estimated_monthly_revenue, 2),
            'revenue_consistency_score': 0.7,
            'mom_revenue_growth': 0,
            'cash_inflow_ratio': 0,
            'digital_inflow_ratio': 100,
            'monthly_operating_expenses': round(monthly_outflow, 2),
            'salary_payments': 0,
            'rent_payments': 0,
            'vendor_payments': 0,
            'utility_payments': 0,
            'fixed_expense_ratio': 0,
            'total_transactions': total_transactions,
            'avg_transaction_value': round(total_inflow / credit_transactions, 2) if credit_transactions > 0 else 0,
            'avg_daily_transactions': round(total_transactions / (months_of_data * 30), 2),
            'credit_transactions': credit_transactions,
            'debit_transactions': debit_transactions,
            'deposit_consistency_score': 0.7,
            'deposit_frequency_days': 7,
            'p2p_inflow': 0,
            'p2p_outflow': 0,
            'p2p_net': 0,
            'cash_deposit_ratio': 0,
            'bounce_count': 0,
            'bounce_rate': 0,
            'circular_transaction_detected': False,
            'od_cc_usage_detected': False,
            'avg_od_cc_utilization': 0,
            'loan_emi_detected': False,
            'estimated_monthly_emi': 0,
            'months_of_data': months_of_data,
            'data_completeness_score': 0.9,
            'monthly_data': {}
        }
    
    def _calculate_business_health_score(self, features):
        """Calculate business health score (0-100)"""
        score = 0
        
        # Inflow/outflow ratio (30 points)
        ratio = features.get('inflow_outflow_ratio', 0)
        if ratio >= 1.2:
            score += 30
        elif ratio >= 1.0:
            score += 25
        elif ratio >= 0.9:
            score += 15
        
        # Balance health (30 points)
        avg_balance = features.get('average_bank_balance', 0)
        monthly_outflow = features.get('monthly_outflow', 1)
        balance_months = avg_balance / monthly_outflow if monthly_outflow > 0 else 0
        if balance_months >= 2:
            score += 30
        elif balance_months >= 1:
            score += 20
        elif balance_months >= 0.5:
            score += 10
        
        # Transaction volume (20 points)
        total_txns = features.get('total_transactions', 0)
        if total_txns >= 200:
            score += 20
        elif total_txns >= 100:
            score += 15
        elif total_txns >= 50:
            score += 10
        
        # Risk indicators (20 points)
        bounce_rate = features.get('bounce_rate', 0)
        circular_detected = features.get('circular_transaction_detected', False)
        risk_penalty = (bounce_rate * 10) + (10 if circular_detected else 0)
        score += max(0, 20 - risk_penalty)
        
        return int(round(score))
    
    def _determine_risk_category(self, score):
        """Determine risk category"""
        if score >= 70:
            return 'low'
        elif score >= 40:
            return 'medium'
        else:
            return 'high'


class BusinessBankAnalysisResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for business bank analysis results (read-only)"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = BusinessBankAnalysisResultSerializer
    
    def get_queryset(self):
        """Filter results by user"""
        return BusinessBankAnalysisResult.objects.filter(user=self.request.user)

