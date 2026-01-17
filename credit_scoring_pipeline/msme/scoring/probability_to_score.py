"""
Probability to Score Conversion Module
======================================

Converts default probability to credit score using calibrated mapping.

Author: ML Engineering Team
Version: 2.0.0
"""

import numpy as np
from typing import Tuple, List


def probability_to_score(
    prob: float,
    min_score: int = 300,
    max_score: int = 900
) -> int:
    """
    Map default probability to credit score.
    
    Uses piecewise linear mapping with calibrated anchor points:
    
    | Probability | Score |
    |-------------|-------|
    | 0.00        | 900   |
    | 0.02        | 750   |
    | 0.05        | 650   |
    | 0.12        | 550   |
    | 0.25        | 450   |
    | 0.40        | 400   |
    | 0.60        | 350   |
    | 1.00        | 300   |
    
    Args:
        prob: Default probability [0, 1]
        min_score: Minimum credit score
        max_score: Maximum credit score
        
    Returns:
        Credit score integer
    """
    prob = np.clip(prob, 0, 1)
    
    # MSME-specific breakpoints
    breakpoints = [
        (0.00, 900),
        (0.02, 750),
        (0.05, 650),
        (0.12, 550),
        (0.25, 450),
        (0.40, 400),
        (0.60, 350),
        (1.00, 300)
    ]
    
    # Find segment and interpolate
    for i in range(len(breakpoints) - 1):
        p1, s1 = breakpoints[i]
        p2, s2 = breakpoints[i + 1]
        
        if p1 <= prob <= p2:
            if p2 == p1:
                return int(s1)
            slope = (s2 - s1) / (p2 - p1)
            score = s1 + slope * (prob - p1)
            return int(np.clip(round(score), min_score, max_score))
    
    return min_score


def msme_prob_to_score(prob: float) -> int:
    """
    MSME-specific probability to score conversion.
    
    Args:
        prob: Default probability
        
    Returns:
        MSME credit score (300-900)
    """
    return probability_to_score(prob, 300, 900)


def score_to_tier(score: int) -> str:
    """
    Convert credit score to risk tier.
    
    Args:
        score: Credit score
        
    Returns:
        Risk tier name
    """
    if score >= 750:
        return "Prime"
    elif score >= 650:
        return "Near Prime"
    elif score >= 550:
        return "Standard"
    elif score >= 450:
        return "Subprime"
    else:
        return "High Risk"


def batch_probability_to_score(
    probs: np.ndarray
) -> np.ndarray:
    """
    Convert array of probabilities to scores.
    
    Args:
        probs: Array of default probabilities
        
    Returns:
        Array of credit scores
    """
    return np.array([probability_to_score(p) for p in probs])
