"""
MSME API URL Configuration
=========================

Complete URL configuration for MSME module including:
- Main application management
- GST analysis
- Director personal banking
- Business banking
- Section-wise analysis
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MSMEApplicationViewSet,
    MSMEDocumentUploadViewSet,
    SectionAnalysisViewSet
)

router = DefaultRouter()
router.register(r'applications', MSMEApplicationViewSet, basename='msme-application')
router.register(r'documents', MSMEDocumentUploadViewSet, basename='msme-document')
router.register(r'section-analysis', SectionAnalysisViewSet, basename='msme-section-analysis')

urlpatterns = [
    # Main MSME application endpoints
    path('', include(router.urls)),
    
    # GST analysis module
    path('gst/', include('apps.msme.gst_analysis.urls')),
    
    # Director personal banking module
    path('director-banking/', include('apps.msme.director_banking.urls')),
    
    # Business banking module
    path('business-banking/', include('apps.msme.business_banking.urls')),
]

