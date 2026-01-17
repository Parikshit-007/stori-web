from django.urls import path
from .views import CreditScoreView, CreditScoreHistoryView, ModelHealthView
from .unified_views import UnifiedCreditScoringView

urlpatterns = [
    # Main credit scoring endpoint
    path('score/', CreditScoreView.as_view(), name='credit-score'),
    
    # Get user's credit score history
    path('history/', CreditScoreHistoryView.as_view(), name='credit-score-history'),
    
    # Model health check
    path('health/', ModelHealthView.as_view(), name='model-health'),
    
    # Unified scoring endpoint (calls all analyses + credit score)
    path('unified-score/', UnifiedCreditScoringView.as_view(), name='unified_score'),
]

