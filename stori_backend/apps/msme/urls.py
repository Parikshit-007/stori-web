"""
MSME API URL Configuration
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
    path('', include(router.urls)),
]

