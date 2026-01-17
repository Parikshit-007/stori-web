"""
GST Analysis Serializers
=========================
"""

from rest_framework import serializers
from .models import GSTUpload, GSTAnalysisResult, GSTFilingHistory


class GSTUploadSerializer(serializers.ModelSerializer):
    """Serializer for GST file uploads"""
    
    class Meta:
        model = GSTUpload
        fields = [
            'id', 'gstin', 'file', 'file_type', 'file_name', 'file_size',
            'return_type', 'return_period', 'financial_year',
            'uploaded_at', 'processed', 'processed_at', 'processing_error'
        ]
        read_only_fields = ['id', 'uploaded_at', 'processed', 'processed_at', 'processing_error']
    
    def validate_gstin(self, value):
        """Validate GSTIN format"""
        if len(value) != 15:
            raise serializers.ValidationError("GSTIN must be 15 characters")
        return value.upper()
    
    def validate_return_period(self, value):
        """Validate return period format (MM-YYYY)"""
        import re
        if not re.match(r'^\d{2}-\d{4}$', value):
            raise serializers.ValidationError("Return period must be in MM-YYYY format")
        return value


class GSTAnalysisResultSerializer(serializers.ModelSerializer):
    """Serializer for GST analysis results"""
    
    gstin = serializers.CharField(source='upload.gstin', read_only=True)
    return_period = serializers.CharField(source='upload.return_period', read_only=True)
    
    class Meta:
        model = GSTAnalysisResult
        fields = '__all__'
        read_only_fields = ['id', 'upload', 'user', 'created_at', 'updated_at']


class GSTFilingHistorySerializer(serializers.ModelSerializer):
    """Serializer for GST filing history"""
    
    class Meta:
        model = GSTFilingHistory
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class GSTAnalysisInputSerializer(serializers.Serializer):
    """Input serializer for GST analysis"""
    
    # Basic info
    gstin = serializers.CharField(max_length=15, required=True)
    return_type = serializers.ChoiceField(
        choices=['gstr1', 'gstr3b', 'gstr2a', 'gstr2b'],
        required=True
    )
    return_period = serializers.CharField(max_length=10, required=True)
    financial_year = serializers.CharField(max_length=10, required=True)
    
    # GST data (from uploaded file)
    gst_data = serializers.JSONField(required=True, help_text="Complete GST return data")
    
    # Optional: ITR data for cross-validation
    itr_data = serializers.JSONField(required=False, help_text="ITR data for mismatch check")
    
    # Optional: Platform sales data
    platform_sales_data = serializers.JSONField(
        required=False,
        help_text="Sales data from e-commerce platforms"
    )
    
    # Optional: Historical filing data
    filing_history = serializers.JSONField(
        required=False,
        help_text="Previous filing history for regularity analysis"
    )


class GSTSummarySerializer(serializers.Serializer):
    """Summary serializer for quick GST overview"""
    
    gstin = serializers.CharField()
    total_revenue_fy = serializers.DecimalField(max_digits=15, decimal_places=2)
    avg_monthly_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    compliance_score = serializers.IntegerField()
    risk_level = serializers.CharField()
    gst_filing_regularity = serializers.DecimalField(max_digits=5, decimal_places=2)
    outstanding_gst = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_vendors = serializers.IntegerField()
    verified_vendors = serializers.IntegerField()

