"""
External Signals Analyzer
==========================

Analyzes:
- Online Reviews & Reputation
"""

import numpy as np
from typing import Dict, List, Any


class ExternalSignalsAnalyzer:
    """Analyzes external signals and reputation"""
    
    def __init__(self):
        pass
    
    def analyze_online_reviews(self, reviews_data: Dict) -> Dict[str, Any]:
        """
        Analyze online reviews and reputation
        
        Args:
            reviews_data: Reviews data including:
                - total_reviews: int
                - average_rating: float
                - positive_reviews: int
                - negative_reviews: int
                
        Returns:
            Dict with review metrics
        """
        try:
            total_reviews = reviews_data.get('total_reviews', 0)
            average_rating = reviews_data.get('average_rating', 0)
            positive_reviews = reviews_data.get('positive_reviews', 0)
            negative_reviews = reviews_data.get('negative_reviews', 0)
            
            # Calculate positive ratio
            if total_reviews > 0:
                positive_ratio = positive_reviews / total_reviews
            else:
                positive_ratio = 0
            
            # Score reviews
            rating_score = self._score_rating(average_rating)
            volume_score = self._score_review_volume(total_reviews)
            positive_ratio_score = self._score_positive_ratio(positive_ratio)
            
            score = (
                rating_score * 0.50 +
                volume_score * 0.30 +
                positive_ratio_score * 0.20
            )
            
            return {
                'total_reviews': int(total_reviews),
                'average_rating': float(average_rating),
                'positive_reviews': int(positive_reviews),
                'negative_reviews': int(negative_reviews),
                'positive_ratio': float(positive_ratio),
                'rating_score': rating_score,
                'volume_score': volume_score,
                'positive_ratio_score': positive_ratio_score,
                'score': score
            }
        except Exception as e:
            return {
                'total_reviews': 0,
                'average_rating': 0,
                'positive_reviews': 0,
                'negative_reviews': 0,
                'positive_ratio': 0,
                'score': 0.5,
                'error': str(e)
            }
    
    def calculate_overall_score(self, reviews_score: float) -> float:
        """Calculate overall external signals score"""
        return reviews_score
    
    # Helper Methods
    
    def _score_rating(self, rating: float) -> float:
        """Score average rating (out of 5)"""
        if rating >= 4.5:
            return 1.0
        elif rating >= 4.0:
            return 0.9
        elif rating >= 3.5:
            return 0.7
        elif rating >= 3.0:
            return 0.5
        elif rating >= 2.5:
            return 0.3
        elif rating >= 2.0:
            return 0.1
        else:
            return 0.0
    
    def _score_review_volume(self, count: int) -> float:
        """Score review volume"""
        if count >= 100:
            return 1.0
        elif count >= 50:
            return 0.8
        elif count >= 20:
            return 0.6
        elif count >= 10:
            return 0.4
        elif count >= 5:
            return 0.2
        else:
            return 0.1
    
    def _score_positive_ratio(self, ratio: float) -> float:
        """Score positive review ratio"""
        if ratio >= 0.9:
            return 1.0
        elif ratio >= 0.8:
            return 0.9
        elif ratio >= 0.7:
            return 0.7
        elif ratio >= 0.6:
            return 0.5
        elif ratio >= 0.5:
            return 0.3
        else:
            return 0.1

