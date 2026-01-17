from django.contrib import admin
from .models import CreditScoreRequest, CreditScoreResult


@admin.register(CreditScoreRequest)
class CreditScoreRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(CreditScoreResult)
class CreditScoreResultAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_user', 'credit_score', 'default_probability', 'risk_tier', 'created_at']
    list_filter = ['risk_tier', 'created_at']
    search_fields = ['request__user__username']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_user(self, obj):
        return obj.request.user.username
    get_user.short_description = 'User'

