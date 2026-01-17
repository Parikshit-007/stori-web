from django.apps import AppConfig


class CreditScoringConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.customer.credit_scoring'
    verbose_name = 'Credit Scoring'
    
    def ready(self):
        """Load model when Django starts"""
        from .model_loader import ModelLoader
        ModelLoader.get_instance()

