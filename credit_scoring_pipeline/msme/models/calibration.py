"""Probability calibration utilities"""

import numpy as np
from typing import Optional
from sklearn.isotonic import IsotonicRegression


class CalibratedModel:
    """
    Wrapper for probability calibration
    
    Calibration ensures predicted probabilities match observed frequencies.
    For example, if model predicts 10% default probability, approximately
    10% of those cases should actually default.
    """
    
    def __init__(self, method: str = 'isotonic'):
        """
        Initialize calibrator
        
        Args:
            method: Calibration method ('isotonic' or 'platt')
        """
        self.method = method
        
        if method == 'isotonic':
            self.calibrator = IsotonicRegression(out_of_bounds='clip')
        else:
            raise ValueError(f"Unknown calibration method: {method}")
        
        self.is_fitted = False
    
    def fit(self, y_true: np.ndarray, y_pred_proba: np.ndarray) -> 'CalibratedModel':
        """
        Fit calibrator on validation data
        
        Args:
            y_true: True labels (0 or 1)
            y_pred_proba: Predicted probabilities (0-1)
            
        Returns:
            self
        """
        print(f"\nCalibrating probabilities using {self.method} regression...")
        
        self.calibrator.fit(y_pred_proba, y_true)
        self.is_fitted = True
        
        # Calculate calibration improvement
        calibrated_probs = self.calibrator.transform(y_pred_proba)
        
        from sklearn.metrics import brier_score_loss
        brier_before = brier_score_loss(y_true, y_pred_proba)
        brier_after = brier_score_loss(y_true, calibrated_probs)
        
        print(f"  Brier score before calibration: {brier_before:.4f}")
        print(f"  Brier score after calibration: {brier_after:.4f}")
        print(f"  Improvement: {((brier_before - brier_after) / brier_before * 100):.2f}%")
        
        return self
    
    def transform(self, y_pred_proba: np.ndarray) -> np.ndarray:
        """
        Apply calibration to probabilities
        
        Args:
            y_pred_proba: Raw predicted probabilities
            
        Returns:
            Calibrated probabilities
        """
        if not self.is_fitted:
            raise ValueError("Calibrator must be fitted before transform")
        
        return self.calibrator.transform(y_pred_proba)
    
    def fit_transform(
        self,
        y_true: np.ndarray,
        y_pred_proba: np.ndarray
    ) -> np.ndarray:
        """Fit and transform in one step"""
        self.fit(y_true, y_pred_proba)
        return self.transform(y_pred_proba)


def calibrate_probabilities(
    y_true: np.ndarray,
    y_pred_proba: np.ndarray,
    method: str = 'isotonic'
) -> tuple[CalibratedModel, np.ndarray]:
    """
    Convenience function for probability calibration
    
    Args:
        y_true: True labels
        y_pred_proba: Predicted probabilities
        method: Calibration method
        
    Returns:
        Tuple of (calibrator, calibrated_probabilities)
    """
    calibrator = CalibratedModel(method=method)
    calibrated_probs = calibrator.fit_transform(y_true, y_pred_proba)
    
    return calibrator, calibrated_probs

