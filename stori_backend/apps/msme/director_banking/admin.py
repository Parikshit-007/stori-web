"""
Director Banking Admin
======================
"""

from django.contrib import admin
from .models import DirectorBankStatementUpload, DirectorBankAnalysisResult


@admin.register(DirectorBankStatementUpload)
class DirectorBankStatementUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'director_name', 'director_pan', 'bank_name', 'uploaded_at', 'processed']
    list_filter = ['processed', 'account_type', 'uploaded_at']
    search_fields = ['director_name', 'director_pan', 'file_name']
    readonly_fields = ['uploaded_at', 'processed_at']
    ordering = ['-uploaded_at']


@admin.register(DirectorBankAnalysisResult)
class DirectorBankAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'director_name', 'director_pan', 'overall_score', 'risk_category', 'created_at']
    list_filter = ['risk_category', 'is_stable', 'created_at']
    search_fields = ['upload__director_name', 'upload__director_pan']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def director_name(self, obj):
        return obj.upload.director_name
    
    def director_pan(self, obj):
        return obj.upload.director_pan

