from django.contrib import admin
from .models import AssetAnalysis


@admin.register(AssetAnalysis)
class AssetAnalysisAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'total_asset_value']
    list_filter = ['created_at']
    search_fields = ['id']

