from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CreditReportAnalysisViewSet
from .json_views import CreditReportJSONAnalysisView

router = DefaultRouter()
router.register(r'', CreditReportAnalysisViewSet, basename='credit-report-analysis')

urlpatterns = [
    # JSON-based analysis (for Account Aggregator)
    path('analyze-json/', CreditReportJSONAnalysisView.as_view(), name='credit-report-analyze-json'),
    
    # File-based analysis (original)
    path('', include(router.urls)),
]

