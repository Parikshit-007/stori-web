"""
Custom authentication classes for API Key and Client ID authentication
"""
from rest_framework import authentication
from rest_framework import exceptions
from django.utils import timezone
from .models import APIKey, ClientSession


class APIKeyAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication using API Key in header
    Header format: X-API-Key: stori_xxxxxxxxxxxxx
    """
    keyword = 'X-API-Key'
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            return None
        
        return self.authenticate_credentials(api_key)
    
    def authenticate_credentials(self, key):
        try:
            api_key = APIKey.objects.select_related('user').get(key=key, is_active=True)
        except APIKey.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid API Key')
        
        if not api_key.user.is_active:
            raise exceptions.AuthenticationFailed('User account is disabled')
        
        # Update last used timestamp (non-blocking - don't fail auth if this fails)
        try:
            api_key.last_used_at = timezone.now()
            api_key.save(update_fields=['last_used_at'])
        except Exception:
            # Log the error but don't fail authentication
            # This is just a tracking field, not critical for auth
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Failed to update last_used_at for API key {api_key.id}', exc_info=True)
        
        return (api_key.user, api_key)
    
    def authenticate_header(self, request):
        return self.keyword


class ClientIDAuthentication(authentication.BaseAuthentication):
    """
    Custom authentication using Client ID in header
    Header format: X-Client-ID: client_xxxxxxxxxxxxx
    """
    keyword = 'X-Client-ID'
    
    def authenticate(self, request):
        client_id = request.META.get('HTTP_X_CLIENT_ID')
        
        if not client_id:
            return None
        
        return self.authenticate_credentials(client_id)
    
    def authenticate_credentials(self, client_id):
        try:
            session = ClientSession.objects.select_related('user').get(
                client_id=client_id, 
                is_active=True
            )
        except ClientSession.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid Client ID')
        
        # Check if expired
        if session.expires_at and session.expires_at < timezone.now():
            raise exceptions.AuthenticationFailed('Client session expired')
        
        if not session.user.is_active:
            raise exceptions.AuthenticationFailed('User account is disabled')
        
        # Update last accessed timestamp (non-blocking - don't fail auth if this fails)
        try:
            session.last_accessed_at = timezone.now()
            session.save(update_fields=['last_accessed_at'])
        except Exception:
            # Log the error but don't fail authentication
            # This is just a tracking field, not critical for auth
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Failed to update last_accessed_at for session {session.id}', exc_info=True)
        
        return (session.user, session)
    
    def authenticate_header(self, request):
        return self.keyword


class SharedSecretKeyAuthentication(authentication.BaseAuthentication):
    """
    Simple shared secret key authentication for ALL APIs (Consumer + MSME).
    
    Uses a single secret key from Django settings - same key for both APIs.
    Header format: X-API-Key: <your-secret-key>
    
    No database lookup required - fast and simple.
    """
    keyword = 'X-API-Key'
    
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        
        if not api_key:
            return None
        
        return self.authenticate_credentials(api_key)
    
    def authenticate_credentials(self, key):
        from django.conf import settings
        
        # Get shared secret key from settings
        shared_secret = getattr(settings, 'SHARED_API_SECRET_KEY', None)
        
        if not shared_secret:
            # Fallback: use Django SECRET_KEY if SHARED_API_SECRET_KEY not set
            shared_secret = getattr(settings, 'SECRET_KEY', None)
        
        if not shared_secret:
            # Return None to let other authenticators try
            return None
        
        # Constant-time comparison to prevent timing attacks
        # If key doesn't match shared secret, return None (don't raise exception)
        # This allows APIKeyAuthentication to try next
        if not self._constant_time_compare(key, shared_secret):
            return None
        
        # Return AnonymousUser (no user-specific auth needed)
        from django.contrib.auth.models import AnonymousUser
        return (AnonymousUser(), None)
    
    def _constant_time_compare(self, val1, val2):
        """Constant-time string comparison to prevent timing attacks."""
        import hmac
        return hmac.compare_digest(str(val1).encode('utf-8'), str(val2).encode('utf-8'))
    
    def authenticate_header(self, request):
        return self.keyword


