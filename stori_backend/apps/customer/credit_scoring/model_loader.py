"""
Model Loader - Singleton pattern to load GBM model once
"""
import os
import joblib
import json
import logging

logger = logging.getLogger(__name__)


class ModelLoader:
    """Singleton class to load and cache the trained model"""
    
    _instance = None
    _model = None
    _feature_names = None
    _metrics = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        """Get singleton instance"""
        if cls._instance is None:
            cls._instance = cls()
            cls._instance._load_model()
        return cls._instance
    
    def _load_model(self):
        """Load the trained model from disk"""
        try:
            # Path to model artifacts (go up to project root then to credit_scoring_pipeline)
            # stori_backend/apps/customer/credit_scoring -> go up 4 levels to stori-nbfc folder
            current_file = os.path.abspath(__file__)
            stori_backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
            stori_nbfc_dir = os.path.dirname(stori_backend_dir)
            
            model_dir = os.path.join(
                stori_nbfc_dir,
                'credit_scoring_pipeline',
                'consumer',
                'consumer_model_artifacts'
            )
            
            model_path = os.path.join(model_dir, 'consumer_credit_model.joblib')
            metrics_path = os.path.join(model_dir, 'training_metrics.json')
            
            if not os.path.exists(model_path):
                logger.warning(f"Model not found at {model_path}. Credit scoring will not be available.")
                return
            
            # Load model
            logger.info(f"Loading model from {model_path}")
            model_data = joblib.load(model_path)
            
            # Handle both dictionary format and direct model format
            if isinstance(model_data, dict):
                # Model saved as dictionary with keys: 'model', 'feature_names', 'version', etc.
                self._model = model_data.get('model')
                self._feature_names = model_data.get('feature_names') or model_data.get('feature_cols', [])
            else:
                # Model saved directly
                self._model = model_data
                # Get feature names from model if available
                if hasattr(self._model, 'feature_name_'):
                    self._feature_names = self._model.feature_name_
            
            # Load metrics
            if os.path.exists(metrics_path):
                with open(metrics_path, 'r') as f:
                    self._metrics = json.load(f)
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            self._model = None
    
    @property
    def model(self):
        """Get the loaded model"""
        return self._model
    
    @property
    def feature_names(self):
        """Get feature names"""
        return self._feature_names
    
    @property
    def metrics(self):
        """Get model metrics"""
        return self._metrics
    
    def is_loaded(self):
        """Check if model is loaded"""
        return self._model is not None

