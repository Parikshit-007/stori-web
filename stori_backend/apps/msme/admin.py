"""
MSME Admin Configuration
========================

Django admin interface for MSME credit scoring
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    MSMEApplication, DirectorProfile, BusinessIdentity, RevenuePerformance,
    CashFlowBanking, CreditRepayment, ComplianceTaxation, FraudVerification,
    ExternalSignals, VendorPayments, MSMEDocumentUpload, MSMEAnalysisResult
)


@admin.register(MSMEApplication)
class MSMEApplicationAdmin(admin.ModelAdmin):
    """Admin interface for MSME Applications"""
    
    list_display = [
        'application_number', 'company_name', 'user', 'msme_category',
        'final_credit_score_display', 'risk_tier_badge', 'status_badge',
        'created_at'
    ]
    list_filter = ['status', 'msme_category', 'risk_tier', 'created_at']
    search_fields = ['application_number', 'company_name', 'user__username']
    readonly_fields = ['application_number', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'application_number', 'company_name', 'msme_category')
        }),
        ('Scoring Results', {
            'fields': ('final_credit_score', 'risk_tier', 'overdraft_limit')
        }),
        ('Status', {
            'fields': ('status', 'created_at', 'updated_at')
        }),
    )
    
    def final_credit_score_display(self, obj):
        if obj.final_credit_score:
            return f"{obj.final_credit_score}"
        return "-"
    final_credit_score_display.short_description = "Credit Score"
    
    def risk_tier_badge(self, obj):
        if not obj.risk_tier:
            return "-"
        
        colors = {
            'prime': 'green',
            'near_prime': 'lightgreen',
            'standard': 'orange',
            'subprime': 'darkorange',
            'high_risk': 'red'
        }
        color = colors.get(obj.risk_tier, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_risk_tier_display() if hasattr(obj, 'get_risk_tier_display') else obj.risk_tier
        )
    risk_tier_badge.short_description = "Risk Tier"
    
    def status_badge(self, obj):
        colors = {
            'pending': 'gray',
            'in_review': 'blue',
            'approved': 'green',
            'rejected': 'red',
            'more_info_required': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status
        )
    status_badge.short_description = "Status"


@admin.register(DirectorProfile)
class DirectorProfileAdmin(admin.ModelAdmin):
    """Admin interface for Director Profiles"""
    
    list_display = ['name', 'application', 'pan', 'age', 'monthly_income', 'is_stable']
    list_filter = ['is_stable', 'created_at']
    search_fields = ['name', 'pan', 'application__company_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BusinessIdentity)
class BusinessIdentityAdmin(admin.ModelAdmin):
    """Admin interface for Business Identity"""
    
    list_display = [
        'company_name', 'legal_entity_type', 'industry',
        'msme_category', 'business_vintage_years', 'verification_status'
    ]
    list_filter = ['legal_entity_type', 'msme_category', 'verification_status', 'industry']
    search_fields = ['company_name', 'gstin', 'pan']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(RevenuePerformance)
class RevenuePerformanceAdmin(admin.ModelAdmin):
    """Admin interface for Revenue Performance"""
    
    list_display = [
        'application', 'monthly_gtv', 'mom_growth', 'qoq_growth',
        'gross_profit_margin', 'net_profit_margin'
    ]
    list_filter = ['created_at']
    search_fields = ['application__company_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CashFlowBanking)
class CashFlowBankingAdmin(admin.ModelAdmin):
    """Admin interface for Cash Flow Banking"""
    
    list_display = [
        'application', 'average_bank_balance', 'balance_trend',
        'negative_balance_days', 'inflow_outflow_ratio'
    ]
    list_filter = ['balance_trend', 'created_at']
    search_fields = ['application__company_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CreditRepayment)
class CreditRepaymentAdmin(admin.ModelAdmin):
    """Admin interface for Credit Repayment"""
    
    list_display = [
        'application', 'on_time_repayment_ratio', 'bounced_cheques_count',
        'current_debt', 'total_debt_status'
    ]
    list_filter = ['total_debt_status', 'created_at']
    search_fields = ['application__company_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ComplianceTaxation)
class ComplianceTaxationAdmin(admin.ModelAdmin):
    """Admin interface for Compliance Taxation"""
    
    list_display = [
        'application', 'gst_filing_regularity', 'itr_filed',
        'gst_filing_on_time_ratio', 'tax_payment_regularity'
    ]
    list_filter = ['itr_filed', 'created_at']
    search_fields = ['application__company_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FraudVerification)
class FraudVerificationAdmin(admin.ModelAdmin):
    """Admin interface for Fraud Verification"""
    
    list_display = [
        'application', 'kyc_completion_score', 'shop_image_verified',
        'overall_fraud_risk_badge', 'circular_transaction_detected'
    ]
    list_filter = ['overall_fraud_risk', 'shop_image_verified', 'created_at']
    search_fields = ['application__company_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def overall_fraud_risk_badge(self, obj):
        colors = {
            'low': 'green',
            'medium': 'orange',
            'high': 'red'
        }
        color = colors.get(obj.overall_fraud_risk, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.overall_fraud_risk.upper()
        )
    overall_fraud_risk_badge.short_description = "Fraud Risk"


@admin.register(ExternalSignals)
class ExternalSignalsAdmin(admin.ModelAdmin):
    """Admin interface for External Signals"""
    
    list_display = [
        'application', 'online_reviews_count', 'online_reviews_avg_rating',
        'review_sentiment'
    ]
    list_filter = ['review_sentiment', 'created_at']
    search_fields = ['application__company_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(VendorPayments)
class VendorPaymentsAdmin(admin.ModelAdmin):
    """Admin interface for Vendor Payments"""
    
    list_display = [
        'application', 'total_vendors_count', 'verified_vendors_count',
        'vendor_verification_rate', 'long_term_vendors_count'
    ]
    list_filter = ['created_at']
    search_fields = ['application__company_name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(MSMEDocumentUpload)
class MSMEDocumentUploadAdmin(admin.ModelAdmin):
    """Admin interface for MSME Document Uploads"""
    
    list_display = [
        'application', 'document_type', 'file_name',
        'file_size_display', 'processed_badge', 'uploaded_at'
    ]
    list_filter = ['document_type', 'processed', 'uploaded_at']
    search_fields = ['application__company_name', 'file_name']
    readonly_fields = ['uploaded_at', 'processed_at']
    
    def file_size_display(self, obj):
        size_mb = obj.file_size / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    file_size_display.short_description = "File Size"
    
    def processed_badge(self, obj):
        if obj.processed:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 10px; border-radius: 3px;">✓ Processed</span>'
            )
        return format_html(
            '<span style="background-color: orange; color: white; padding: 3px 10px; border-radius: 3px;">Pending</span>'
        )
    processed_badge.short_description = "Status"


@admin.register(MSMEAnalysisResult)
class MSMEAnalysisResultAdmin(admin.ModelAdmin):
    """Admin interface for MSME Analysis Results"""
    
    list_display = [
        'application', 'final_credit_score', 'risk_tier_badge',
        'default_probability', 'created_at'
    ]
    list_filter = ['risk_tier', 'created_at']
    search_fields = ['application__company_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Application', {
            'fields': ('application',)
        }),
        ('Section Scores', {
            'fields': (
                'director_score', 'business_identity_score', 'revenue_score',
                'cashflow_score', 'credit_score', 'compliance_score',
                'fraud_score', 'external_score', 'vendor_score'
            )
        }),
        ('Final Results', {
            'fields': (
                'final_credit_score', 'default_probability', 'risk_tier',
                'overdraft_limit', 'recommended_interest_rate'
            )
        }),
        ('Explainability', {
            'fields': ('feature_importance', 'shap_values'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def risk_tier_badge(self, obj):
        if not obj.risk_tier:
            return "-"
        
        colors = {
            'prime': 'green',
            'near_prime': 'lightgreen',
            'standard': 'orange',
            'subprime': 'darkorange',
            'high_risk': 'red'
        }
        color = colors.get(obj.risk_tier, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.risk_tier.upper().replace('_', ' ')
        )
    risk_tier_badge.short_description = "Risk Tier"
