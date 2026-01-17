from django.contrib import admin
from .models import DocumentUpload, OCRResult, FaceMatchRequest, FaceMatchResult


@admin.register(DocumentUpload)
class DocumentUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'document_type', 'uploaded_at', 'processed']
    list_filter = ['document_type', 'processed', 'uploaded_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['uploaded_at', 'processed_at']
    date_hierarchy = 'uploaded_at'


@admin.register(OCRResult)
class OCRResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user', 'get_document_type', 'confidence_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['document__user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_user(self, obj):
        return obj.document.user.username
    get_user.short_description = 'User'
    
    def get_document_type(self, obj):
        return obj.document.get_document_type_display()
    get_document_type.short_description = 'Document Type'


@admin.register(FaceMatchRequest)
class FaceMatchRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'processed']
    list_filter = ['processed', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'processed_at']
    date_hierarchy = 'created_at'


@admin.register(FaceMatchResult)
class FaceMatchResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user', 'overall_verdict', 'created_at']
    list_filter = ['overall_verdict', 'created_at']
    search_fields = ['request__user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_user(self, obj):
        return obj.request.user.username
    get_user.short_description = 'User'


