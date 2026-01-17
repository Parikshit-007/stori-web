from django.db import models
from django.contrib.auth.models import User


class CreditScoreRequest(models.Model):
    """Model to store credit score requests"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_score_requests')
    request_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'credit_score_requests'
        ordering = ['-created_at']
        verbose_name = 'Credit Score Request'
        verbose_name_plural = 'Credit Score Requests'
    
    def __str__(self):
        return f"Credit Score Request - {self.user.username} - {self.created_at}"


class CreditScoreResult(models.Model):
    """Model to store credit score results"""
    
    request = models.OneToOneField(CreditScoreRequest, on_delete=models.CASCADE, related_name='result')
    credit_score = models.IntegerField()
    default_probability = models.FloatField()
    risk_tier = models.CharField(max_length=50)
    feature_importance = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'credit_score_results'
        ordering = ['-created_at']
        verbose_name = 'Credit Score Result'
        verbose_name_plural = 'Credit Score Results'
    
    def __str__(self):
        return f"Score: {self.credit_score} - {self.request.user.username}"

