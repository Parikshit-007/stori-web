"""
MSME Serializers
================

DRF Serializers for all MSME models
"""

from rest_framework import serializers
from .models import (
    MSMEApplication, DirectorProfile, BusinessIdentity, RevenuePerformance,
    CashFlowBanking, CreditRepayment, ComplianceTaxation, FraudVerification,
    ExternalSignals, VendorPayments, MSMEDocumentUpload, MSMEAnalysisResult
)


# ==================== MSME APPLICATION ====================

class MSMEApplicationSerializer(serializers.ModelSerializer):
    """Serializer for MSME Application"""
    
    user_name = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = MSMEApplication
        fields = [
            'id', 'user', 'user_name', 'application_number', 'company_name',
            'msme_category', 'final_credit_score', 'risk_tier', 'overdraft_limit',
            'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user_name', 'created_at', 'updated_at']


class MSMEApplicationDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with all related data"""
    
    directors = serializers.SerializerMethodField()
    business_identity = serializers.SerializerMethodField()
    revenue_performance = serializers.SerializerMethodField()
    cashflow_banking = serializers.SerializerMethodField()
    credit_repayment = serializers.SerializerMethodField()
    compliance_taxation = serializers.SerializerMethodField()
    fraud_verification = serializers.SerializerMethodField()
    external_signals = serializers.SerializerMethodField()
    vendor_payments = serializers.SerializerMethodField()
    analysis_result = serializers.SerializerMethodField()
    
    class Meta:
        model = MSMEApplication
        fields = '__all__'
    
    def get_directors(self, obj):
        return DirectorProfileSerializer(obj.directors.all(), many=True).data
    
    def get_business_identity(self, obj):
        try:
            return BusinessIdentitySerializer(obj.business_identity).data
        except:
            return None
    
    def get_revenue_performance(self, obj):
        try:
            return RevenuePerformanceSerializer(obj.revenue_performance).data
        except:
            return None
    
    def get_cashflow_banking(self, obj):
        try:
            return CashFlowBankingSerializer(obj.cashflow_banking).data
        except:
            return None
    
    def get_credit_repayment(self, obj):
        try:
            return CreditRepaymentSerializer(obj.credit_repayment).data
        except:
            return None
    
    def get_compliance_taxation(self, obj):
        try:
            return ComplianceTaxationSerializer(obj.compliance_taxation).data
        except:
            return None
    
    def get_fraud_verification(self, obj):
        try:
            return FraudVerificationSerializer(obj.fraud_verification).data
        except:
            return None
    
    def get_external_signals(self, obj):
        try:
            return ExternalSignalsSerializer(obj.external_signals).data
        except:
            return None
    
    def get_vendor_payments(self, obj):
        try:
            return VendorPaymentsSerializer(obj.vendor_payments).data
        except:
            return None
    
    def get_analysis_result(self, obj):
        try:
            return MSMEAnalysisResultSerializer(obj.analysis_result).data
        except:
            return None


# ==================== DIRECTOR PROFILE ====================

class DirectorProfileSerializer(serializers.ModelSerializer):
    """Serializer for Director Profile"""
    
    class Meta:
        model = DirectorProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== BUSINESS IDENTITY ====================

class BusinessIdentitySerializer(serializers.ModelSerializer):
    """Serializer for Business Identity"""
    
    class Meta:
        model = BusinessIdentity
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== REVENUE PERFORMANCE ====================

class RevenuePerformanceSerializer(serializers.ModelSerializer):
    """Serializer for Revenue Performance"""
    
    class Meta:
        model = RevenuePerformance
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== CASH FLOW & BANKING ====================

class CashFlowBankingSerializer(serializers.ModelSerializer):
    """Serializer for Cash Flow Banking"""
    
    class Meta:
        model = CashFlowBanking
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== CREDIT & REPAYMENT ====================

class CreditRepaymentSerializer(serializers.ModelSerializer):
    """Serializer for Credit Repayment"""
    
    class Meta:
        model = CreditRepayment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== COMPLIANCE & TAXATION ====================

class ComplianceTaxationSerializer(serializers.ModelSerializer):
    """Serializer for Compliance Taxation"""
    
    class Meta:
        model = ComplianceTaxation
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== FRAUD & VERIFICATION ====================

class FraudVerificationSerializer(serializers.ModelSerializer):
    """Serializer for Fraud Verification"""
    
    class Meta:
        model = FraudVerification
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== EXTERNAL SIGNALS ====================

class ExternalSignalsSerializer(serializers.ModelSerializer):
    """Serializer for External Signals"""
    
    class Meta:
        model = ExternalSignals
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== VENDOR PAYMENTS ====================

class VendorPaymentsSerializer(serializers.ModelSerializer):
    """Serializer for Vendor Payments"""
    
    class Meta:
        model = VendorPayments
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== DOCUMENT UPLOAD ====================

class MSMEDocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for MSME Document Upload"""
    
    class Meta:
        model = MSMEDocumentUpload
        fields = '__all__'
        read_only_fields = ['id', 'uploaded_at', 'processed', 'processed_at']
    
    def validate_file(self, value):
        """Validate file size and extension"""
        # Max 50MB for MSME documents
        if value.size > 50 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 50MB")
        
        allowed_extensions = ['.pdf', '.xlsx', '.xls', '.csv', '.jpg', '.jpeg', '.png']
        if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        return value


# ==================== ANALYSIS RESULT ====================

class MSMEAnalysisResultSerializer(serializers.ModelSerializer):
    """Serializer for MSME Analysis Result"""
    
    application_details = MSMEApplicationSerializer(source='application', read_only=True)
    
    class Meta:
        model = MSMEAnalysisResult
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


# ==================== COMPREHENSIVE INPUT SERIALIZER ====================

class MSMEAnalysisInputSerializer(serializers.Serializer):
    """
    Comprehensive input serializer for complete MSME analysis
    
    Accepts all data needed for analysis across all sections
    """
    
    # Application Details
    application_id = serializers.IntegerField(required=False)
    company_name = serializers.CharField(max_length=200)
    msme_category = serializers.ChoiceField(choices=['micro', 'small', 'medium'])
    
    # A) Director Data
    director_data = serializers.JSONField(required=False)
    personal_bank_data = serializers.JSONField(required=False)
    
    # B) Business Identity Data
    business_data = serializers.JSONField(required=False)
    verification_data = serializers.JSONField(required=False)
    
    # C) Revenue Data
    revenue_data = serializers.JSONField(required=False)
    financial_data = serializers.JSONField(required=False)
    
    # D) Bank Data (Business)
    bank_data = serializers.JSONField(required=False)
    
    # E) Credit Report
    credit_report = serializers.JSONField(required=False)
    
    # F) GST & ITR Data
    gst_data = serializers.JSONField(required=False)
    gst2b_data = serializers.JSONField(required=False)
    itr_data = serializers.JSONField(required=False)
    platform_data = serializers.JSONField(required=False)
    
    # G) Fraud & Verification
    kyc_data = serializers.JSONField(required=False)
    shop_data = serializers.JSONField(required=False)
    
    # H) External Signals
    reviews_data = serializers.JSONField(required=False)
    
    def validate(self, data):
        """Validate that at least basic required data is present"""
        required_fields = ['company_name', 'msme_category']
        
        for field in required_fields:
            if field not in data:
                raise serializers.ValidationError(f"{field} is required")
        
        return data


# ==================== QUICK ANALYSIS SERIALIZERS ====================

class DirectorAnalysisInputSerializer(serializers.Serializer):
    """Input for director-only analysis"""
    director_data = serializers.JSONField()
    personal_bank_data = serializers.JSONField()


class RevenueAnalysisInputSerializer(serializers.Serializer):
    """Input for revenue-only analysis"""
    revenue_data = serializers.JSONField()
    financial_data = serializers.JSONField()
    msme_category = serializers.ChoiceField(choices=['micro', 'small', 'medium'], default='micro')


class CashFlowAnalysisInputSerializer(serializers.Serializer):
    """Input for cashflow-only analysis"""
    bank_data = serializers.JSONField()


class ComplianceAnalysisInputSerializer(serializers.Serializer):
    """Input for compliance-only analysis"""
    gst_data = serializers.JSONField()
    itr_data = serializers.JSONField(required=False)
    bank_data = serializers.JSONField(required=False)
    platform_data = serializers.JSONField(required=False)

