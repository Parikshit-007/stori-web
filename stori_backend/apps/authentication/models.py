from django.db import models
from django.contrib.auth.models import User
import secrets


def generate_api_key():
    """Generate a secure API key"""
    return f"stori_{secrets.token_urlsafe(32)}"


class APIKey(models.Model):
    """
    Model to store permanent API keys for client authentication
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    key = models.CharField(max_length=100, unique=True, default=generate_api_key)
    name = models.CharField(max_length=100, help_text="Name/description for this API key")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'api_keys'
        ordering = ['-created_at']
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"
    
    def save(self, *args, **kwargs):
        if not self.key:
            self.key = generate_api_key()
        super().save(*args, **kwargs)


class ClientSession(models.Model):
    """
    Model to store client sessions
    """
    client_id = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_sessions')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    last_accessed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'client_sessions'
        ordering = ['-created_at']
        verbose_name = 'Client Session'
        verbose_name_plural = 'Client Sessions'
    
    def __str__(self):
        return f"Session: {self.client_id} - {self.user.username}"


