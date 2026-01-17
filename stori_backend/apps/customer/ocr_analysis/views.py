from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import DocumentUpload, OCRResult, FaceMatchRequest, FaceMatchResult
from .serializers import (
    DocumentUploadSerializer, 
    OCRResultSerializer,
    FaceMatchRequestSerializer,
    FaceMatchResultSerializer
)


class DocumentUploadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for document upload
    """
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentUploadSerializer
    
    def get_queryset(self):
        return DocumentUpload.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Handle file upload"""
        serializer.save(user=self.request.user)


class FaceMatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for face matching operations
    """
    permission_classes = [IsAuthenticated]
    serializer_class = FaceMatchRequestSerializer
    
    def get_queryset(self):
        return FaceMatchRequest.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create face match request"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Perform face verification for uploaded documents
        """
        face_match_request = self.get_object()
        
        if face_match_request.processed:
            return Response({
                'success': False,
                'message': 'This request has already been processed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Lazy import face matcher
            try:
                from .face_match import FaceMatcher
            except ImportError as e:
                return Response({
                    'success': False,
                    'message': f'Face matching dependencies not installed: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Initialize face matcher
            matcher = FaceMatcher(
                model_name='Facenet512',
                detector_backend='retinaface'
            )
            
            # Get user photo path
            user_photo_path = face_match_request.user_photo.file.path
            
            # Prepare documents
            documents = {}
            if face_match_request.aadhaar_photo:
                documents['Aadhaar'] = face_match_request.aadhaar_photo.file.path
            if face_match_request.pan_photo:
                documents['PAN'] = face_match_request.pan_photo.file.path
            if face_match_request.voter_id_photo:
                documents['Voter_ID'] = face_match_request.voter_id_photo.file.path
            
            # Perform verification
            report = matcher.get_detailed_verification_report(
                user_image=user_photo_path,
                documents=documents
            )
            
            # Save result
            face_match_result, created = FaceMatchResult.objects.update_or_create(
                request=face_match_request,
                defaults={
                    'overall_verdict': report['overall_verdict'],
                    'verdict_description': report['verdict_description'],
                    'results': report
                }
            )
            
            # Mark as processed
            face_match_request.processed = True
            face_match_request.processed_at = timezone.now()
            face_match_request.save()
            
            serializer = FaceMatchResultSerializer(face_match_result)
            
            return Response({
                'success': True,
                'message': 'Face verification completed successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Face verification failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def result(self, request, pk=None):
        """
        Get face match result
        """
        face_match_request = self.get_object()
        
        try:
            result = face_match_request.result
            serializer = FaceMatchResultSerializer(result)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except FaceMatchResult.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Result not found. Please verify the request first.'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def quick_verify(self, request):
        """
        Quick face verification with uploaded files in request
        Accepts: user_photo, aadhaar_photo, pan_photo, voter_id_photo
        """
        user_photo = request.FILES.get('user_photo')
        aadhaar_photo = request.FILES.get('aadhaar_photo')
        pan_photo = request.FILES.get('pan_photo')
        voter_id_photo = request.FILES.get('voter_id_photo')
        
        if not user_photo:
            return Response({
                'success': False,
                'message': 'user_photo is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not any([aadhaar_photo, pan_photo, voter_id_photo]):
            return Response({
                'success': False,
                'message': 'At least one document photo is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Lazy import face matcher
            try:
                from .face_match import FaceMatcher
            except ImportError as e:
                return Response({
                    'success': False,
                    'message': f'Face matching dependencies not installed: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Save uploaded documents temporarily
            user_doc = DocumentUpload.objects.create(
                user=request.user,
                file=user_photo,
                document_type='user_photo'
            )
            
            documents = {}
            doc_objects = {}
            
            if aadhaar_photo:
                doc = DocumentUpload.objects.create(
                    user=request.user,
                    file=aadhaar_photo,
                    document_type='aadhaar'
                )
                documents['Aadhaar'] = doc.file.path
                doc_objects['aadhaar_photo'] = doc
            
            if pan_photo:
                doc = DocumentUpload.objects.create(
                    user=request.user,
                    file=pan_photo,
                    document_type='pan'
                )
                documents['PAN'] = doc.file.path
                doc_objects['pan_photo'] = doc
            
            if voter_id_photo:
                doc = DocumentUpload.objects.create(
                    user=request.user,
                    file=voter_id_photo,
                    document_type='voter_id'
                )
                documents['Voter_ID'] = doc.file.path
                doc_objects['voter_id_photo'] = doc
            
            # Initialize face matcher and verify
            matcher = FaceMatcher(
                model_name='Facenet512',
                detector_backend='retinaface'
            )
            
            report = matcher.get_detailed_verification_report(
                user_image=user_doc.file.path,
                documents=documents
            )
            
            # Create request and result
            face_match_request = FaceMatchRequest.objects.create(
                user=request.user,
                user_photo=user_doc,
                **doc_objects,
                processed=True,
                processed_at=timezone.now()
            )
            
            face_match_result = FaceMatchResult.objects.create(
                request=face_match_request,
                overall_verdict=report['overall_verdict'],
                verdict_description=report['verdict_description'],
                results=report
            )
            
            serializer = FaceMatchResultSerializer(face_match_result)
            
            return Response({
                'success': True,
                'message': 'Face verification completed successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Face verification failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

