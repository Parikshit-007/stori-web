from django.db import models


# Placeholder models - can be extended later if needed
class AssetAnalysis(models.Model):
    """Model to store asset analysis results if needed"""
    created_at = models.DateTimeField(auto_now_add=True)
    total_asset_value = models.FloatField(default=0.0)
    
    class Meta:
        db_table = 'asset_analysis'

