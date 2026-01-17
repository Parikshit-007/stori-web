from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentUploadViewSet, FaceMatchViewSet
from .kyc_ocr_views import KYCDocumentOCRView

router = DefaultRouter()
router.register(r'documents', DocumentUploadViewSet, basename='document-upload')
router.register(r'face-match', FaceMatchViewSet, basename='face-match')

urlpatterns = [
    path('', include(router.urls)),
    # KYC Document OCR endpoint
    path('document-ocr/', KYCDocumentOCRView.as_view(), name='kyc-document-ocr'),
]


