"""
Business Banking URLs
=====================
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessBankStatementViewSet, BusinessBankAnalysisResultViewSet
from .json_views import BusinessBankingJSONAnalysisView

# Create router
router = DefaultRouter()
router.register(r'statements', BusinessBankStatementViewSet, basename='business-bank-statement')
router.register(r'results', BusinessBankAnalysisResultViewSet, basename='business-bank-result')

urlpatterns = [
    path('', include(router.urls)),
    
    # JSON-based analysis (like consumer flow)
    path('analyze-json/', BusinessBankingJSONAnalysisView.as_view(), name='business-analyze-json'),
]

