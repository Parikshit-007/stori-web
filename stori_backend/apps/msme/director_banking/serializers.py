"""
Director Banking Serializers
=============================
"""

from rest_framework import serializers
from .models import DirectorBankStatementUpload, DirectorBankAnalysisResult


class DirectorBankStatementUploadSerializer(serializers.ModelSerializer):
    """Serializer for director bank statement uploads"""
    
    class Meta:
        model = DirectorBankStatementUpload
        fields = [
            'id', 'director_name', 'director_pan', 'bank_name', 'account_number',
            'account_type', 'file', 'file_type', 'file_name', 'file_size',
            'statement_start_date', 'statement_end_date',
            'uploaded_at', 'processed', 'processed_at', 'processing_error'
        ]
        read_only_fields = ['id', 'uploaded_at', 'processed', 'processed_at', 'processing_error']
    
    def validate_director_pan(self, value):
        """Validate PAN format"""
        if len(value) != 10:
            raise serializers.ValidationError("PAN must be 10 characters")
        return value.upper()


class DirectorBankAnalysisResultSerializer(serializers.ModelSerializer):
    """Serializer for director bank analysis results"""
    
    director_name = serializers.CharField(source='upload.director_name', read_only=True)
    director_pan = serializers.CharField(source='upload.director_pan', read_only=True)
    bank_name = serializers.CharField(source='upload.bank_name', read_only=True)
    
    class Meta:
        model = DirectorBankAnalysisResult
        fields = '__all__'
        read_only_fields = ['id', 'upload', 'user', 'created_at', 'updated_at']


class DirectorBankAnalysisSummarySerializer(serializers.Serializer):
    """Summary serializer for quick overview"""
    
    director_name = serializers.CharField()
    director_pan = serializers.CharField()
    overall_score = serializers.IntegerField()
    risk_category = serializers.CharField()
    monthly_income = serializers.DecimalField(max_digits=15, decimal_places=2)
    monthly_expense = serializers.DecimalField(max_digits=15, decimal_places=2)
    avg_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    income_stability = serializers.DecimalField(max_digits=5, decimal_places=2)
    is_stable = serializers.BooleanField()
    estimated_emi = serializers.DecimalField(max_digits=15, decimal_places=2)

