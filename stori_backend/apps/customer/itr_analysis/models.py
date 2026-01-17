from django.db import models
from django.contrib.auth.models import User


class ITRUpload(models.Model):
    """Model to store ITR upload records"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='itr_uploads')
    file = models.FileField(upload_to='itr_uploads/%Y/%m/%d/')
    file_type = models.CharField(max_length=10, choices=[('json', 'JSON'), ('pdf', 'PDF')])
    assessment_year = models.CharField(max_length=20, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'itr_uploads'
        ordering = ['-uploaded_at']
        verbose_name = 'ITR Upload'
        verbose_name_plural = 'ITR Uploads'
    
    def __str__(self):
        return f"ITR Upload - {self.user.username} - {self.assessment_year}"


class ITRAnalysisResult(models.Model):
    """Model to store ITR analysis results"""
    
    upload = models.OneToOneField(ITRUpload, on_delete=models.CASCADE, related_name='analysis_result')
    features = models.JSONField(default=dict)
    summary = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'itr_analysis_results'
        ordering = ['-created_at']
        verbose_name = 'ITR Analysis Result'
        verbose_name_plural = 'ITR Analysis Results'
    
    def __str__(self):
        return f"ITR Analysis - {self.upload.user.username}"


