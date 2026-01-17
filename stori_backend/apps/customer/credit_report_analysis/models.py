from django.db import models
from django.contrib.auth.models import User


class CreditReportUpload(models.Model):
    """Model to store credit report upload records"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_report_uploads')
    file = models.FileField(upload_to='credit_reports/%Y/%m/%d/')
    file_type = models.CharField(max_length=10, choices=[('pdf', 'PDF'), ('json', 'JSON')])
    bureau_name = models.CharField(max_length=50, blank=True, choices=[
        ('cibil', 'CIBIL'),
        ('experian', 'Experian'),
        ('equifax', 'Equifax'),
        ('crif', 'CRIF'),
    ])
    report_date = models.DateField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'credit_report_uploads'
        ordering = ['-uploaded_at']
        verbose_name = 'Credit Report Upload'
        verbose_name_plural = 'Credit Report Uploads'
    
    def __str__(self):
        return f"Credit Report - {self.user.username} - {self.bureau_name}"


class CreditReportAnalysisResult(models.Model):
    """Model to store credit report analysis results"""
    
    upload = models.OneToOneField(CreditReportUpload, on_delete=models.CASCADE, related_name='analysis_result')
    features = models.JSONField(default=dict)
    summary = models.JSONField(default=dict)
    accounts = models.JSONField(default=list)
    enquiries = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'credit_report_analysis_results'
        ordering = ['-created_at']
        verbose_name = 'Credit Report Analysis Result'
        verbose_name_plural = 'Credit Report Analysis Results'
    
    def __str__(self):
        return f"Credit Analysis - {self.upload.user.username}"


