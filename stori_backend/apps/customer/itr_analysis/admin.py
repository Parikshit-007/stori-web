from django.contrib import admin
from .models import ITRUpload, ITRAnalysisResult


@admin.register(ITRUpload)
class ITRUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'assessment_year', 'file_type', 'uploaded_at', 'processed']
    list_filter = ['processed', 'file_type', 'uploaded_at']
    search_fields = ['user__username', 'user__email', 'assessment_year']
    readonly_fields = ['uploaded_at', 'processed_at']
    date_hierarchy = 'uploaded_at'


@admin.register(ITRAnalysisResult)
class ITRAnalysisResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user', 'get_assessment_year', 'created_at']
    list_filter = ['created_at']
    search_fields = ['upload__user__username', 'upload__assessment_year']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_user(self, obj):
        return obj.upload.user.username
    get_user.short_description = 'User'
    
    def get_assessment_year(self, obj):
        return obj.upload.assessment_year
    get_assessment_year.short_description = 'Assessment Year'


