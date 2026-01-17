from django.db import models
from django.contrib.auth.models import User


class DocumentUpload(models.Model):
    """Model to store document uploads for OCR"""
    
    DOCUMENT_TYPES = [
        ('aadhaar', 'Aadhaar Card'),
        ('pan', 'PAN Card'),
        ('voter_id', 'Voter ID'),
        ('passport', 'Passport'),
        ('driving_license', 'Driving License'),
        ('user_photo', 'User Photo'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_uploads')
    file = models.ImageField(upload_to='documents/%Y/%m/%d/')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'document_uploads'
        ordering = ['-uploaded_at']
        verbose_name = 'Document Upload'
        verbose_name_plural = 'Document Uploads'
    
    def __str__(self):
        return f"{self.get_document_type_display()} - {self.user.username}"


class OCRResult(models.Model):
    """Model to store OCR extraction results"""
    
    document = models.OneToOneField(DocumentUpload, on_delete=models.CASCADE, related_name='ocr_result')
    extracted_data = models.JSONField(default=dict)
    confidence_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ocr_results'
        ordering = ['-created_at']
        verbose_name = 'OCR Result'
        verbose_name_plural = 'OCR Results'
    
    def __str__(self):
        return f"OCR - {self.document.get_document_type_display()}"


class FaceMatchRequest(models.Model):
    """Model to store face matching requests"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='face_match_requests')
    user_photo = models.ForeignKey(
        DocumentUpload, 
        on_delete=models.CASCADE, 
        related_name='face_match_as_user_photo'
    )
    aadhaar_photo = models.ForeignKey(
        DocumentUpload, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='face_match_as_aadhaar'
    )
    pan_photo = models.ForeignKey(
        DocumentUpload, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='face_match_as_pan'
    )
    voter_id_photo = models.ForeignKey(
        DocumentUpload, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='face_match_as_voter_id'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'face_match_requests'
        ordering = ['-created_at']
        verbose_name = 'Face Match Request'
        verbose_name_plural = 'Face Match Requests'
    
    def __str__(self):
        return f"Face Match - {self.user.username}"


class FaceMatchResult(models.Model):
    """Model to store face matching results"""
    
    request = models.OneToOneField(FaceMatchRequest, on_delete=models.CASCADE, related_name='result')
    overall_verdict = models.CharField(max_length=50)
    verdict_description = models.TextField()
    results = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'face_match_results'
        ordering = ['-created_at']
        verbose_name = 'Face Match Result'
        verbose_name_plural = 'Face Match Results'
    
    def __str__(self):
        return f"Face Match Result - {self.request.user.username} - {self.overall_verdict}"


