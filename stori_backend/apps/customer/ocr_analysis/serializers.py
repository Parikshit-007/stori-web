from rest_framework import serializers
from .models import DocumentUpload, OCRResult, FaceMatchRequest, FaceMatchResult


class DocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentUpload
        fields = ['id', 'file', 'document_type', 'uploaded_at', 'processed', 'processed_at']
        read_only_fields = ['id', 'uploaded_at', 'processed', 'processed_at']
    
    def validate_file(self, value):
        """Validate file size and extension"""
        if value.size > 10 * 1024 * 1024:  # 10MB
            raise serializers.ValidationError("File size cannot exceed 10MB")
        
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.pdf']
        if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        return value


class OCRResultSerializer(serializers.ModelSerializer):
    document = DocumentUploadSerializer(read_only=True)
    
    class Meta:
        model = OCRResult
        fields = ['id', 'document', 'extracted_data', 'confidence_score', 
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class FaceMatchRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceMatchRequest
        fields = ['id', 'user_photo', 'aadhaar_photo', 'pan_photo', 'voter_id_photo',
                  'created_at', 'processed', 'processed_at']
        read_only_fields = ['id', 'created_at', 'processed', 'processed_at']
    
    def validate(self, data):
        """Ensure at least one document photo is provided"""
        if not any([data.get('aadhaar_photo'), data.get('pan_photo'), data.get('voter_id_photo')]):
            raise serializers.ValidationError(
                "At least one document photo (Aadhaar, PAN, or Voter ID) must be provided"
            )
        return data


class FaceMatchResultSerializer(serializers.ModelSerializer):
    request = FaceMatchRequestSerializer(read_only=True)
    
    class Meta:
        model = FaceMatchResult
        fields = ['id', 'request', 'overall_verdict', 'verdict_description', 
                  'results', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


