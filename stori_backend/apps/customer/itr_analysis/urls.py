from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ITRAnalysisViewSet
from .json_views import ITRJSONAnalysisView

router = DefaultRouter()
router.register(r'', ITRAnalysisViewSet, basename='itr-analysis')

urlpatterns = [
    # JSON-based analysis (for Account Aggregator)
    path('analyze-json/', ITRJSONAnalysisView.as_view(), name='itr-analyze-json'),
    
    # File-based analysis (original)
    path('', include(router.urls)),
]

