from rest_framework import serializers
from .models import BankStatementUpload, BankStatementAnalysisResult


class BankStatementUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankStatementUpload
        fields = ['id', 'file', 'file_type', 'bank_name', 'account_number', 
                  'statement_period', 'uploaded_at', 'processed', 'processed_at']
        read_only_fields = ['id', 'uploaded_at', 'processed', 'processed_at']
    
    def validate_file(self, value):
        """Validate file size and extension"""
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        allowed_extensions = ['.pdf', '.xlsx', '.xls', '.csv']
        if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        return value


class BankStatementAnalysisResultSerializer(serializers.ModelSerializer):
    upload = BankStatementUploadSerializer(read_only=True)
    
    class Meta:
        model = BankStatementAnalysisResult
        fields = ['id', 'upload', 'features', 'summary', 'transactions', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


