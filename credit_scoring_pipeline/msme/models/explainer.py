"""SHAP explainability utilities"""

import pandas as pd
import numpy as np
from typing import Optional
import warnings

warnings.filterwarnings('ignore')


def get_shap_explanations(
    model,
    X: pd.DataFrame,
    max_samples: int = 100
) -> Optional[object]:
    """
    Generate SHAP explanations for model predictions
    
    SHAP (SHapley Additive exPlanations) shows how each feature
    contributes to individual predictions.
    
    Args:
        model: Trained LightGBM model
        X: Feature data
        max_samples: Maximum samples for explanation
        
    Returns:
        SHAP explainer object
    """
    try:
        import shap
        
        print(f"\nGenerating SHAP explanations for {min(len(X), max_samples)} samples...")
        
        # Create explainer
        explainer = shap.TreeExplainer(model)
        
        # Calculate SHAP values
        X_sample = X.iloc[:max_samples] if len(X) > max_samples else X
        shap_values = explainer.shap_values(X_sample)
        
        print("✓ SHAP explanations generated")
        
        return {
            'explainer': explainer,
            'shap_values': shap_values,
            'data': X_sample,
            'base_value': explainer.expected_value
        }
    
    except ImportError:
        print("⚠ SHAP library not installed. Run: pip install shap")
        return None
    except Exception as e:
        print(f"⚠ Error generating SHAP explanations: {e}")
        return None


def plot_feature_importance(
    feature_importance: pd.DataFrame,
    top_n: int = 20,
    save_path: Optional[str] = None
):
    """
    Plot feature importance
    
    Args:
        feature_importance: DataFrame with feature importance
        top_n: Number of top features to show
        save_path: Path to save plot (if None, displays plot)
    """
    try:
        import matplotlib.pyplot as plt
        
        # Get top features
        top_features = feature_importance.head(top_n)
        
        # Create plot
        plt.figure(figsize=(10, 8))
        plt.barh(range(len(top_features)), top_features['importance'])
        plt.yticks(range(len(top_features)), top_features['feature'])
        plt.xlabel('Importance')
        plt.title(f'Top {top_n} Feature Importance')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Feature importance plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    except ImportError:
        print("⚠ Matplotlib not installed. Run: pip install matplotlib")
    except Exception as e:
        print(f"⚠ Error plotting feature importance: {e}")

