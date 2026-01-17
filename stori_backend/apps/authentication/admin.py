from django.contrib import admin
from .models import APIKey, ClientSession


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'key', 'is_active', 'created_at', 'last_used_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'user__username', 'key']
    readonly_fields = ['key', 'created_at', 'last_used_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('API Key Information', {
            'fields': ('user', 'name', 'key')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_used_at')
        }),
    )


@admin.register(ClientSession)
class ClientSessionAdmin(admin.ModelAdmin):
    list_display = ['client_id', 'user', 'is_active', 'created_at', 'expires_at', 'last_accessed_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['client_id', 'user__username']
    readonly_fields = ['created_at', 'last_accessed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Session Information', {
            'fields': ('user', 'client_id')
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_accessed_at')
        }),
    )


