from django.apps import AppConfig


class MsmeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.msme'
    verbose_name = 'MSME Credit Scoring'
    
    def ready(self):
        """Initialize MSME app components"""
        pass
