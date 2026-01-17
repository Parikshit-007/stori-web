"""
Business Banking Serializers
=============================
"""

from rest_framework import serializers
from .models import BusinessBankStatementUpload, BusinessBankAnalysisResult


class BusinessBankStatementUploadSerializer(serializers.ModelSerializer):
    """Serializer for business bank statement uploads"""
    
    class Meta:
        model = BusinessBankStatementUpload
        fields = [
            'id', 'business_name', 'gstin', 'bank_name', 'account_number',
            'account_type', 'file', 'file_type', 'file_name', 'file_size',
            'statement_start_date', 'statement_end_date',
            'uploaded_at', 'processed', 'processed_at', 'processing_error'
        ]
        read_only_fields = ['id', 'uploaded_at', 'processed', 'processed_at', 'processing_error']


class BusinessBankAnalysisResultSerializer(serializers.ModelSerializer):
    """Serializer for business bank analysis results"""
    
    business_name = serializers.CharField(source='upload.business_name', read_only=True)
    gstin = serializers.CharField(source='upload.gstin', read_only=True)
    bank_name = serializers.CharField(source='upload.bank_name', read_only=True)
    
    class Meta:
        model = BusinessBankAnalysisResult
        fields = '__all__'
        read_only_fields = ['id', 'upload', 'user', 'created_at', 'updated_at']


class BusinessBankAnalysisSummarySerializer(serializers.Serializer):
    """Summary serializer for quick overview"""
    
    business_name = serializers.CharField()
    gstin = serializers.CharField()
    cashflow_health_score = serializers.IntegerField()
    business_risk_category = serializers.CharField()
    average_bank_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_inflow = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_outflow = serializers.DecimalField(max_digits=15, decimal_places=2)
    inflow_outflow_ratio = serializers.DecimalField(max_digits=5, decimal_places=2)
    estimated_monthly_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)

