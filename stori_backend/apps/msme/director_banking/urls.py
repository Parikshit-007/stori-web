"""
Director Banking URLs
=====================
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DirectorBankStatementViewSet, DirectorBankAnalysisResultViewSet
from .json_views import DirectorBankingJSONAnalysisView

# Create router
router = DefaultRouter()
router.register(r'statements', DirectorBankStatementViewSet, basename='director-bank-statement')
router.register(r'results', DirectorBankAnalysisResultViewSet, basename='director-bank-result')

urlpatterns = [
    path('', include(router.urls)),
    
    # JSON-based analysis (like consumer flow)
    path('analyze-json/', DirectorBankingJSONAnalysisView.as_view(), name='director-analyze-json'),
]

