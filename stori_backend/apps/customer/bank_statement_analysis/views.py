from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import pandas as pd

from .models import BankStatementUpload, BankStatementAnalysisResult
from .serializers import BankStatementUploadSerializer, BankStatementAnalysisResultSerializer
from .analyzer import (
    load_bank_excel, compute_core_features, compute_behaviour_features,
    compute_advanced_features, compute_impulse_behavioral_features,
    estimate_emi, compute_bounce_features, monthly_aggregation
)


class BankStatementAnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet for bank statement upload and analysis
    """
    permission_classes = [IsAuthenticated]
    serializer_class = BankStatementUploadSerializer
    
    def get_queryset(self):
        return BankStatementUpload.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Handle file upload"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """
        Analyze uploaded bank statement
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
            account_id = upload.account_number or 'default'
            
            # Load based on file type
            if upload.file_type in ['xlsx', 'xls']:
                bank_df = load_bank_excel(file_path, account_id)
            else:
                # For now, only Excel is supported
                return Response({
                    'success': False,
                    'message': 'Only Excel files (.xlsx, .xls) are currently supported'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Compute monthly aggregation
            monthly_df = monthly_aggregation(bank_df)
            
            # Extract all feature groups
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
            features = {
                **core_features,
                **behaviour_features,
                **emi_features,
                **bounce_features,
                **advanced_features,
                **impulse_features
            }
            
            # Create summary
            summary = {
                'total_transactions': len(bank_df),
                'total_credits': core_features.get('total_credits', 0),
                'total_debits': core_features.get('total_debits', 0),
                'average_balance': core_features.get('avg_balance', 0),
                'monthly_income': core_features.get('avg_monthly_credits', 0),
                'monthly_expense': core_features.get('avg_monthly_debits', 0),
                'statement_period': upload.statement_period or '',
                'bank_name': upload.bank_name or '',
            }
            
            # Convert transactions to list of dicts (limit to 1000 for performance)
            transactions = bank_df.head(1000).to_dict('records')
            
            # Save analysis result
            analysis_result, created = BankStatementAnalysisResult.objects.update_or_create(
                upload=upload,
                defaults={
                    'features': features,
                    'summary': summary,
                    'transactions': transactions
                }
            )
            
            # Mark as processed
            upload.processed = True
            upload.processed_at = timezone.now()
            upload.save()
            
            serializer = BankStatementAnalysisResultSerializer(analysis_result)
            
            return Response({
                'success': True,
                'message': 'Bank statement analyzed successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Analysis failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def result(self, request, pk=None):
        """
        Get analysis result for a bank statement upload
        """
        upload = self.get_object()
        
        try:
            analysis_result = upload.analysis_result
            serializer = BankStatementAnalysisResultSerializer(analysis_result)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except BankStatementAnalysisResult.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Analysis result not found. Please analyze the bank statement first.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def all_results(self, request):
        """
        Get all analysis results for the authenticated user
        """
        results = BankStatementAnalysisResult.objects.filter(
            upload__user=request.user
        ).select_related('upload')
        
        serializer = BankStatementAnalysisResultSerializer(results, many=True)
        
        return Response({
            'success': True,
            'count': results.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

