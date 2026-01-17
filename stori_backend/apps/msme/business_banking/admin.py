"""
Business Banking Admin
======================
"""

from django.contrib import admin
from .models import BusinessBankStatementUpload, BusinessBankAnalysisResult


@admin.register(BusinessBankStatementUpload)
class BusinessBankStatementUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'business_name', 'gstin', 'bank_name', 'uploaded_at', 'processed']
    list_filter = ['processed', 'account_type', 'uploaded_at']
    search_fields = ['business_name', 'gstin', 'file_name']
    readonly_fields = ['uploaded_at', 'processed_at']
    ordering = ['-uploaded_at']


@admin.register(BusinessBankAnalysisResult)
class BusinessBankAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'business_name', 'cashflow_health_score', 'business_risk_category', 'created_at']
    list_filter = ['business_risk_category', 'created_at']
    search_fields = ['upload__business_name', 'upload__gstin']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def business_name(self, obj):
        return obj.upload.business_name

