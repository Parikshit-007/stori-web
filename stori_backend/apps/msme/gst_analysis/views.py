"""
GST Analysis Views
==================

DRF ViewSets for GST analysis
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Sum, Avg
from datetime import datetime, timedelta

from .models import GSTUpload, GSTAnalysisResult, GSTFilingHistory
from .serializers import (
    GSTUploadSerializer, GSTAnalysisResultSerializer,
    GSTFilingHistorySerializer, GSTAnalysisInputSerializer,
    GSTSummarySerializer
)
from .analyzer import GSTAnalyzer


class GSTUploadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for GST file uploads
    
    Endpoints:
    - list: Get all GST uploads
    - retrieve: Get specific upload
    - create: Upload new GST return
    - update/patch: Update upload
    - delete: Delete upload
    - analyze: Analyze uploaded GST return
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = GSTUploadSerializer
    
    def get_queryset(self):
        """Filter uploads by user"""
        return GSTUpload.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Handle file upload"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """
        Analyze uploaded GST return
        
        POST /api/msme/gst/uploads/{id}/analyze/
        
        Body (optional):
        {
            "itr_data": {...},  // Optional ITR data for cross-check
            "platform_sales_data": {...},  // Optional platform sales
            "filing_history": [...]  // Optional historical filings
        }
        """
        upload = self.get_object()
        
        if upload.processed:
            return Response({
                'success': False,
                'message': 'This GST return has already been analyzed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Load GST data from uploaded file
            import json
            
            file_path = upload.file.path
            
            if upload.file_type == 'json':
                with open(file_path, 'r') as f:
                    gst_data = json.load(f)
            else:
                return Response({
                    'success': False,
                    'message': 'Only JSON files are currently supported'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Prepare input data
            input_data = {
                'gstin': upload.gstin,
                'return_type': upload.return_type,
                'return_period': upload.return_period,
                'financial_year': upload.financial_year,
                'gst_data': gst_data,
                'itr_data': request.data.get('itr_data'),
                'platform_sales_data': request.data.get('platform_sales_data'),
                'filing_history': request.data.get('filing_history', [])
            }
            
            # Perform analysis
            analyzer = GSTAnalyzer()
            analysis_results = analyzer.analyze_gst_complete(input_data)
            
            if 'error' in analysis_results:
                upload.processing_error = analysis_results['error']
                upload.save()
                
                return Response({
                    'success': False,
                    'message': f'Analysis failed: {analysis_results["error"]}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Save analysis results
            result, created = GSTAnalysisResult.objects.update_or_create(
                upload=upload,
                defaults={
                    'user': request.user,
                    
                    # Filing discipline
                    'gst_filing_regularity': analysis_results['filing_discipline']['gst_filing_regularity'],
                    'total_expected_filings': analysis_results['filing_discipline']['total_expected_filings'],
                    'actual_filings': analysis_results['filing_discipline']['actual_filings'],
                    'late_filings': analysis_results['filing_discipline']['late_filings'],
                    'missed_filings': analysis_results['filing_discipline']['missed_filings'],
                    
                    # Revenue analysis
                    'monthly_revenue': analysis_results['revenue_analysis']['monthly_revenue'],
                    'total_revenue_fy': analysis_results['revenue_analysis']['total_revenue_fy'],
                    'avg_monthly_revenue': analysis_results['revenue_analysis']['avg_monthly_revenue'],
                    'mom_revenue_growth': analysis_results['revenue_analysis']['mom_revenue_growth'],
                    'qoq_revenue_growth': analysis_results['revenue_analysis']['qoq_revenue_growth'],
                    'revenue_volatility': analysis_results['revenue_analysis']['revenue_volatility'],
                    
                    # Tax compliance
                    'total_gst_liability': analysis_results['tax_compliance']['total_gst_liability'],
                    'total_gst_paid': analysis_results['tax_compliance']['total_gst_paid'],
                    'outstanding_gst': analysis_results['tax_compliance']['outstanding_gst'],
                    'tax_payment_regularity': analysis_results['tax_compliance']['tax_payment_regularity'],
                    
                    # Mismatch checks
                    'gst_r1_revenue': analysis_results['mismatch_checks']['gst_r1_revenue'],
                    'itr_revenue': analysis_results['mismatch_checks']['itr_revenue'],
                    'gst_r1_itr_mismatch': analysis_results['mismatch_checks']['gst_r1_itr_mismatch'],
                    'mismatch_flag': analysis_results['mismatch_checks']['mismatch_flag'],
                    'platform_sales': analysis_results['mismatch_checks'].get('platform_sales', 0),
                    'gst_platform_sales_mismatch': analysis_results['mismatch_checks'].get('gst_platform_sales_mismatch', 0),
                    
                    # ITC analysis
                    'total_itc_claimed': analysis_results['itc_analysis']['total_itc_claimed'],
                    'total_itc_utilized': analysis_results['itc_analysis']['total_itc_utilized'],
                    'itc_balance': analysis_results['itc_analysis']['itc_balance'],
                    'itc_to_revenue_ratio': analysis_results['itc_analysis']['itc_to_revenue_ratio'],
                    
                    # Vendor analysis
                    'total_vendors': analysis_results['vendor_analysis']['total_vendors'],
                    'verified_vendors': analysis_results['vendor_analysis']['verified_vendors'],
                    'vendor_verification_rate': analysis_results['vendor_analysis']['vendor_verification_rate'],
                    'top_vendor_concentration': analysis_results['vendor_analysis']['top_vendor_concentration'],
                    'top_3_vendor_concentration': analysis_results['vendor_analysis']['top_3_vendor_concentration'],
                    'long_term_vendors_count': analysis_results['vendor_analysis']['long_term_vendors_count'],
                    'long_term_vendor_percentage': analysis_results['vendor_analysis']['long_term_vendor_percentage'],
                    
                    # Industry analysis
                    'industry': analysis_results['industry_analysis']['industry'],
                    'effective_gst_rate': analysis_results['industry_analysis']['effective_gst_rate'],
                    
                    # Risk assessment
                    'risk_flags': analysis_results['risk_assessment']['risk_flags'],
                    'risk_level': analysis_results['risk_assessment']['risk_level'],
                    
                    # Compliance score
                    'compliance_score': analysis_results['compliance_score'],
                    
                    # Additional data
                    'hsn_sac_codes': analysis_results['hsn_sac_analysis']['hsn_sac_codes'],
                    'primary_business_activity': analysis_results['hsn_sac_analysis']['primary_business_activity'],
                    'gst_locations': analysis_results['geographic_analysis']['gst_locations'],
                    'multi_state_operations': analysis_results['geographic_analysis']['multi_state_operations'],
                    
                    # Raw data
                    'raw_gst_data': gst_data
                }
            )
            
            # Mark upload as processed
            upload.processed = True
            upload.processed_at = timezone.now()
            upload.save()
            
            return Response({
                'success': True,
                'message': 'GST analysis completed successfully',
                'data': {
                    'upload_id': upload.id,
                    'result_id': result.id,
                    'compliance_score': analysis_results['compliance_score'],
                    'risk_level': analysis_results['risk_assessment']['risk_level'],
                    'total_revenue_fy': analysis_results['revenue_analysis']['total_revenue_fy'],
                    'summary': analysis_results
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
        
        GET /api/msme/gst/uploads/{id}/result/
        """
        upload = self.get_object()
        
        try:
            result = upload.analysis_result
            serializer = GSTAnalysisResultSerializer(result)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except GSTAnalysisResult.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Analysis not yet performed for this upload'
            }, status=status.HTTP_404_NOT_FOUND)


class GSTAnalysisResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for GST analysis results (read-only)
    
    Endpoints:
    - list: Get all analysis results
    - retrieve: Get specific result
    - summary: Get summary for a GSTIN
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = GSTAnalysisResultSerializer
    
    def get_queryset(self):
        """Filter results by user"""
        return GSTAnalysisResult.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get summary for a specific GSTIN
        
        GET /api/msme/gst/results/summary/?gstin=XXXXXXXXXXXXXXX
        """
        gstin = request.query_params.get('gstin')
        
        if not gstin:
            return Response({
                'success': False,
                'message': 'GSTIN parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get latest result for this GSTIN
        try:
            result = GSTAnalysisResult.objects.filter(
                user=request.user,
                upload__gstin=gstin
            ).latest('created_at')
            
            summary_data = {
                'gstin': gstin,
                'total_revenue_fy': result.total_revenue_fy,
                'avg_monthly_revenue': result.avg_monthly_revenue,
                'compliance_score': result.compliance_score,
                'risk_level': result.risk_level,
                'gst_filing_regularity': result.gst_filing_regularity,
                'outstanding_gst': result.outstanding_gst,
                'total_vendors': result.total_vendors,
                'verified_vendors': result.verified_vendors
            }
            
            serializer = GSTSummarySerializer(summary_data)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except GSTAnalysisResult.DoesNotExist:
            return Response({
                'success': False,
                'message': f'No analysis found for GSTIN: {gstin}'
            }, status=status.HTTP_404_NOT_FOUND)


class GSTFilingHistoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for GST filing history
    
    Used to track filing regularity over time
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = GSTFilingHistorySerializer
    
    def get_queryset(self):
        """Filter by GSTIN if provided"""
        queryset = GSTFilingHistory.objects.all()
        
        gstin = self.request.query_params.get('gstin')
        if gstin:
            queryset = queryset.filter(gstin=gstin)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def regularity(self, request):
        """
        Get filing regularity for a GSTIN
        
        GET /api/msme/gst/filing-history/regularity/?gstin=XXXXXXXXXXXXXXX
        """
        gstin = request.query_params.get('gstin')
        
        if not gstin:
            return Response({
                'success': False,
                'message': 'GSTIN parameter is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get filing history for last 12 months
        history = GSTFilingHistory.objects.filter(gstin=gstin).order_by('-return_period')[:12]
        
        if not history:
            return Response({
                'success': False,
                'message': f'No filing history found for GSTIN: {gstin}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Calculate metrics
        total_filings = len(history)
        on_time = sum(1 for h in history if h.status == 'filed_on_time')
        late = sum(1 for h in history if h.status == 'filed_late')
        not_filed = sum(1 for h in history if h.status == 'not_filed')
        
        regularity = (on_time / total_filings * 100) if total_filings > 0 else 0
        
        return Response({
            'success': True,
            'data': {
                'gstin': gstin,
                'total_filings': total_filings,
                'on_time_filings': on_time,
                'late_filings': late,
                'not_filed': not_filed,
                'regularity_percentage': round(regularity, 2)
            }
        }, status=status.HTTP_200_OK)

