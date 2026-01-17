"""
URLs for Asset Analysis API
"""
from django.urls import path
from .json_views import AssetAnalysisJSONView

app_name = 'asset_analysis'

urlpatterns = [
    path('analyze-json/', AssetAnalysisJSONView.as_view(), name='analyze_json'),
]

