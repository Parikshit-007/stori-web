from django.db import models
from django.contrib.auth.models import User


class BankStatementUpload(models.Model):
    """Model to store bank statement upload records"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_statement_uploads')
    file = models.FileField(upload_to='bank_statements/%Y/%m/%d/')
    file_type = models.CharField(max_length=10, choices=[
        ('pdf', 'PDF'), 
        ('xlsx', 'Excel'), 
        ('xls', 'Excel Legacy'),
        ('csv', 'CSV')
    ])
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    statement_period = models.CharField(max_length=100, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'bank_statement_uploads'
        ordering = ['-uploaded_at']
        verbose_name = 'Bank Statement Upload'
        verbose_name_plural = 'Bank Statement Uploads'
    
    def __str__(self):
        return f"Bank Statement - {self.user.username} - {self.bank_name}"


class BankStatementAnalysisResult(models.Model):
    """Model to store bank statement analysis results"""
    
    upload = models.OneToOneField(BankStatementUpload, on_delete=models.CASCADE, related_name='analysis_result')
    features = models.JSONField(default=dict)
    summary = models.JSONField(default=dict)
    transactions = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bank_statement_analysis_results'
        ordering = ['-created_at']
        verbose_name = 'Bank Statement Analysis Result'
        verbose_name_plural = 'Bank Statement Analysis Results'
    
    def __str__(self):
        return f"Bank Analysis - {self.upload.user.username}"


