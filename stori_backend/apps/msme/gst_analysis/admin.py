"""
GST Analysis Admin
==================
"""

from django.contrib import admin
from .models import GSTUpload, GSTAnalysisResult, GSTFilingHistory


@admin.register(GSTUpload)
class GSTUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'gstin', 'return_type', 'return_period', 'uploaded_at', 'processed']
    list_filter = ['return_type', 'processed', 'uploaded_at']
    search_fields = ['gstin', 'file_name']
    readonly_fields = ['uploaded_at', 'processed_at']
    ordering = ['-uploaded_at']


@admin.register(GSTAnalysisResult)
class GSTAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'gstin', 'return_period', 'compliance_score', 'risk_level', 'created_at']
    list_filter = ['risk_level', 'created_at']
    search_fields = ['upload__gstin']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def gstin(self, obj):
        return obj.upload.gstin
    
    def return_period(self, obj):
        return obj.upload.return_period


@admin.register(GSTFilingHistory)
class GSTFilingHistoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'gstin', 'return_type', 'return_period', 'status', 'days_delay']
    list_filter = ['status', 'return_type']
    search_fields = ['gstin']
    ordering = ['-return_period']

