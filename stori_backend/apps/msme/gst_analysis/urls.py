"""
GST Analysis URLs
=================
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GSTUploadViewSet, GSTAnalysisResultViewSet, GSTFilingHistoryViewSet

# Create router
router = DefaultRouter()
router.register(r'uploads', GSTUploadViewSet, basename='gst-upload')
router.register(r'results', GSTAnalysisResultViewSet, basename='gst-result')
router.register(r'filing-history', GSTFilingHistoryViewSet, basename='gst-filing-history')

urlpatterns = [
    path('', include(router.urls)),
]

