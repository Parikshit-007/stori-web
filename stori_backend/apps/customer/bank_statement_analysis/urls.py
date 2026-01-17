from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BankStatementAnalysisViewSet
from .json_views import BankStatementJSONAnalysisView

router = DefaultRouter()
router.register(r'', BankStatementAnalysisViewSet, basename='bank-statement-analysis')

urlpatterns = [
    # JSON-based analysis (for Account Aggregator)
    path('analyze-json/', BankStatementJSONAnalysisView.as_view(), name='bank-statement-analyze-json'),
    
    # File-based analysis (original)
    path('', include(router.urls)),
]

