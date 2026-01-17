from rest_framework import serializers
from .models import CreditReportUpload, CreditReportAnalysisResult


class CreditReportUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreditReportUpload
        fields = ['id', 'file', 'file_type', 'bureau_name', 'report_date', 
                  'uploaded_at', 'processed', 'processed_at']
        read_only_fields = ['id', 'uploaded_at', 'processed', 'processed_at']
    
    def validate_file(self, value):
        """Validate file size and extension"""
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        allowed_extensions = ['.pdf', '.json']
        if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        return value


class CreditReportAnalysisResultSerializer(serializers.ModelSerializer):
    upload = CreditReportUploadSerializer(read_only=True)
    
    class Meta:
        model = CreditReportAnalysisResult
        fields = ['id', 'upload', 'features', 'summary', 'accounts', 'enquiries',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


