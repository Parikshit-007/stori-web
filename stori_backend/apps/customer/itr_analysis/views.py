from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.conf import settings
import os

from .models import ITRUpload, ITRAnalysisResult
from .serializers import ITRUploadSerializer, ITRAnalysisResultSerializer
from .analyzer import extract_itr_features_single_year, load_itr_json


class ITRAnalysisViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ITR upload and analysis
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ITRUploadSerializer
    
    def get_queryset(self):
        return ITRUpload.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Handle file upload and initiate analysis"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """
        Analyze uploaded ITR file
        """
        upload = self.get_object()
        
        if upload.processed:
            return Response({
                'success': False,
                'message': 'This ITR has already been analyzed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Load ITR data
            file_path = upload.file.path
            
            if upload.file_type == 'json':
                itr_data = load_itr_json(file_path)
            else:
                return Response({
                    'success': False,
                    'message': 'PDF analysis coming soon'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract features
            features = extract_itr_features_single_year(itr_data)
            
            # Create summary
            summary = {
                'assessment_year': itr_data.get('assessment_year', ''),
                'net_taxable_income': features.get('itr_net_taxable_income', 0),
                'gross_total_income': features.get('itr_gross_total_income', 0),
                'tax_paid': features.get('itr_tax_paid', 0),
                'form_type': itr_data.get('form_type', ''),
                'filing_status': itr_data.get('filing_status', ''),
            }
            
            # Save analysis result
            analysis_result, created = ITRAnalysisResult.objects.update_or_create(
                upload=upload,
                defaults={
                    'features': features,
                    'summary': summary
                }
            )
            
            # Mark as processed
            upload.processed = True
            upload.processed_at = timezone.now()
            upload.save()
            
            serializer = ITRAnalysisResultSerializer(analysis_result)
            
            return Response({
                'success': True,
                'message': 'ITR analyzed successfully',
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
        Get analysis result for an ITR upload
        """
        upload = self.get_object()
        
        try:
            analysis_result = upload.analysis_result
            serializer = ITRAnalysisResultSerializer(analysis_result)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except ITRAnalysisResult.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Analysis result not found. Please analyze the ITR first.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def all_results(self, request):
        """
        Get all analysis results for the authenticated user
        """
        results = ITRAnalysisResult.objects.filter(
            upload__user=request.user
        ).select_related('upload')
        
        serializer = ITRAnalysisResultSerializer(results, many=True)
        
        return Response({
            'success': True,
            'count': results.count(),
            'data': serializer.data
        }, status=status.HTTP_200_OK)

