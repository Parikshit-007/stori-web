from django.contrib import admin
from .models import CreditReportUpload, CreditReportAnalysisResult


@admin.register(CreditReportUpload)
class CreditReportUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'bureau_name', 'report_date', 'file_type', 'uploaded_at', 'processed']
    list_filter = ['processed', 'file_type', 'bureau_name', 'uploaded_at']
    search_fields = ['user__username', 'user__email', 'bureau_name']
    readonly_fields = ['uploaded_at', 'processed_at']
    date_hierarchy = 'uploaded_at'


@admin.register(CreditReportAnalysisResult)
class CreditReportAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user', 'get_bureau_name', 'get_credit_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['upload__user__username', 'upload__bureau_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_user(self, obj):
        return obj.upload.user.username
    get_user.short_description = 'User'
    
    def get_bureau_name(self, obj):
        return obj.upload.bureau_name
    get_bureau_name.short_description = 'Bureau'
    
    def get_credit_score(self, obj):
        return obj.summary.get('credit_score', 'N/A')
    get_credit_score.short_description = 'Credit Score'


