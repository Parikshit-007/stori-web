from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
import json

from .models import CreditReportUpload, CreditReportAnalysisResult
from .serializers import CreditReportUploadSerializer, CreditReportAnalysisResultSerializer
from .analyzer import extract_credit_features, load_credit_report, extract_liabilities_from_credit_report
import pandas as pd


class CreditReportAnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet for credit report upload and analysis
    """
    permission_classes = [IsAuthenticated]
    serializer_class = CreditReportUploadSerializer
    
    def get_queryset(self):
        return CreditReportUpload.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Handle file upload"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """
        Analyze uploaded credit report
        """
        upload = self.get_object()
        
        if upload.processed:
            return Response({
                'success': False,
                'message': 'This credit report has already been analyzed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Load credit report
            file_path = upload.file.path
            
            if upload.file_type == 'json':
                with open(file_path, 'r') as f:
                    credit_data = json.load(f)
            else:
                credit_data = load_credit_report(file_path)
            
            # Extract features
            features = extract_credit_features(credit_data)
            
            # Extract liabilities (from credit report only for now)
            # Can be enhanced to include bank statement if provided
            liabilities = extract_liabilities_from_credit_report(credit_data)
            
            # Create summary
            summary = {
                'credit_score': features.get('credit_score', 0),
                'total_accounts': features.get('total_accounts', 0),
                'active_accounts': features.get('active_accounts', 0),
                'total_outstanding': features.get('total_outstanding', 0),
                'delinquent_accounts': features.get('delinquent_accounts', 0),
                'bureau_name': upload.bureau_name or '',
                # Add liability summary
                'total_liabilities': liabilities.get('total_liabilities', 0),
                'total_monthly_emi': liabilities.get('total_monthly_emi', 0),
                'active_loans_count': len(liabilities.get('active_loans', [])),
                'credit_cards_count': len(liabilities.get('credit_cards', [])),
            }
            
            # Extract accounts and enquiries
            accounts = credit_data.get('accounts', [])
            enquiries = credit_data.get('enquiries', [])
            
            # Save analysis result (include liabilities in features)
            features_with_liabilities = {
                **features,
                'liabilities': liabilities
            }
            
            analysis_result, created = CreditReportAnalysisResult.objects.update_or_create(
                upload=upload,
                defaults={
                    'features': features_with_liabilities,
                    'summary': summary,
                    'accounts': accounts,
                    'enquiries': enquiries
                }
            )
            
            # Mark as processed
            upload.processed = True
            upload.processed_at = timezone.now()
            upload.save()
            
            serializer = CreditReportAnalysisResultSerializer(analysis_result)
            
            return Response({
                'success': True,
                'message': 'Credit report analyzed successfully',
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
        Get analysis result for a credit report upload
        """
        upload = self.get_object()
        
        try:
            analysis_result = upload.analysis_result
            serializer = CreditReportAnalysisResultSerializer(analysis_result)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except CreditReportAnalysisResult.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Analysis result not found. Please analyze the credit report first.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def all_results(self, request):
        """
        Get all analysis results for the authenticated user
        """
        results = CreditReportAnalysisResult.objects.filter(
            upload__user=request.user
        ).select_related('upload')
        
        serializer = CreditReportAnalysisResultSerializer(results, many=True)
        
        return Response({
            'success': True,
            'count': results.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def analyze_with_bank_statement(self, request):
        """
        Analyze credit report with bank statement for comprehensive liability detection.
        
        Request Body:
        {
            "credit_report": {...},  // Credit report JSON
            "bank_statement": [...],  // Bank statement transactions array
            "monthly_income": 50000   // Optional: Monthly income
        }
        """
        try:
            credit_report_data = request.data.get('credit_report')
            bank_statement_data = request.data.get('bank_statement', [])
            monthly_income = float(request.data.get('monthly_income', 0))
            
            if not credit_report_data:
                return Response({
                    'success': False,
                    'message': 'Credit report data is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Convert bank statement to DataFrame if provided
            bank_statement_df = None
            if bank_statement_data:
                try:
                    bank_statement_df = pd.DataFrame(bank_statement_data)
                    # Normalize columns
                    if 'date' in bank_statement_df.columns:
                        bank_statement_df['date'] = pd.to_datetime(bank_statement_df['date'])
                    if 'txn_date' not in bank_statement_df.columns and 'date' in bank_statement_df.columns:
                        bank_statement_df['txn_date'] = bank_statement_df['date']
                    if 'description' not in bank_statement_df.columns and 'narration' in bank_statement_df.columns:
                        bank_statement_df['description'] = bank_statement_df['narration']
                except Exception as e:
                    return Response({
                        'success': False,
                        'message': f'Invalid bank statement format: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract credit features
            features = extract_credit_features(credit_report_data)
            
            # Extract comprehensive liabilities (from both sources)
            liabilities = extract_liabilities_from_credit_report(
                credit_report_data,
                bank_statement_df=bank_statement_df,
                monthly_income=monthly_income
            )
            
            # Combine results
            result = {
                'credit_features': features,
                'liabilities': liabilities,
                'summary': {
                    'credit_score': features.get('credit_score', 0),
                    'total_liabilities': liabilities.get('total_liabilities', 0),
                    'total_monthly_emi': liabilities.get('total_monthly_emi', 0),
                    'active_loans': len(liabilities.get('active_loans', [])),
                    'credit_cards': len(liabilities.get('credit_cards', [])),
                    'liability_sources': liabilities.get('liability_sources', {}),
                    'debt_ratios': liabilities.get('debt_ratios', {}),
                    'risk_level': liabilities.get('risk_indicators', {}).get('overall_risk_level', 'low')
                }
            }
            
            return Response({
                'success': True,
                'message': 'Comprehensive liability analysis completed',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Analysis failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


