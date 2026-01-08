"""
Credit Scoring Pipeline - Monitoring Module
============================================

This module provides production monitoring utilities:
1. Population Stability Index (PSI) calculation
2. Feature drift detection
3. Calibration monitoring
4. Model performance tracking
5. Retraining recommendations
6. Bias/fairness checks

Author: ML Engineering Team
Version: 1.0.0
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
import json
import warnings

warnings.filterwarnings('ignore')


# ============================================================================
# POPULATION STABILITY INDEX (PSI)
# ============================================================================

def calculate_psi(expected: np.ndarray, actual: np.ndarray, 
                  n_bins: int = 10, epsilon: float = 1e-6) -> float:
    """
    Calculate Population Stability Index between expected and actual distributions.
    
    PSI measures shift in population distribution:
    - PSI < 0.10: No significant population change
    - PSI 0.10-0.25: Moderate population change (investigate)
    - PSI > 0.25: Significant population change (action required)
    
    Args:
        expected: Expected/baseline distribution (training data)
        actual: Actual/current distribution (production data)
        n_bins: Number of bins for discretization
        epsilon: Small value to prevent division by zero
        
    Returns:
        PSI value
    """
    # Create bins based on expected distribution
    breakpoints = np.percentile(expected, np.linspace(0, 100, n_bins + 1))
    breakpoints[0] = -np.inf
    breakpoints[-1] = np.inf
    
    # Make breakpoints unique
    breakpoints = np.unique(breakpoints)
    
    # Calculate proportions in each bin
    expected_counts = np.histogram(expected, bins=breakpoints)[0]
    actual_counts = np.histogram(actual, bins=breakpoints)[0]
    
    expected_pct = expected_counts / len(expected) + epsilon
    actual_pct = actual_counts / len(actual) + epsilon
    
    # Calculate PSI
    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    
    return float(psi)


def calculate_feature_psi(baseline_df: pd.DataFrame, 
                          current_df: pd.DataFrame,
                          feature_columns: List[str] = None,
                          n_bins: int = 10) -> Dict[str, float]:
    """
    Calculate PSI for all features between baseline and current data.
    
    Args:
        baseline_df: Baseline (training) data
        current_df: Current (production) data
        feature_columns: List of columns to analyze (default: all numeric)
        n_bins: Number of bins for PSI calculation
        
    Returns:
        Dict of feature name -> PSI value
    """
    if feature_columns is None:
        feature_columns = baseline_df.select_dtypes(include=[np.number]).columns.tolist()
    
    psi_results = {}
    
    for col in feature_columns:
        if col in baseline_df.columns and col in current_df.columns:
            baseline_vals = baseline_df[col].dropna().values
            current_vals = current_df[col].dropna().values
            
            if len(baseline_vals) > 0 and len(current_vals) > 0:
                psi = calculate_psi(baseline_vals, current_vals, n_bins)
                psi_results[col] = psi
    
    return psi_results


def psi_report(psi_values: Dict[str, float], 
               threshold_warning: float = 0.10,
               threshold_critical: float = 0.25) -> Dict:
    """
    Generate PSI report with recommendations.
    
    Args:
        psi_values: Dict of feature -> PSI value
        threshold_warning: Warning threshold
        threshold_critical: Critical threshold
        
    Returns:
        Report dict with categorized features and recommendations
    """
    stable = []
    warning = []
    critical = []
    
    for feature, psi in psi_values.items():
        if psi >= threshold_critical:
            critical.append({'feature': feature, 'psi': psi})
        elif psi >= threshold_warning:
            warning.append({'feature': feature, 'psi': psi})
        else:
            stable.append({'feature': feature, 'psi': psi})
    
    # Sort by PSI descending
    critical = sorted(critical, key=lambda x: x['psi'], reverse=True)
    warning = sorted(warning, key=lambda x: x['psi'], reverse=True)
    
    report = {
        'summary': {
            'total_features': len(psi_values),
            'stable_count': len(stable),
            'warning_count': len(warning),
            'critical_count': len(critical),
            'overall_status': 'CRITICAL' if critical else ('WARNING' if warning else 'STABLE')
        },
        'critical_features': critical,
        'warning_features': warning,
        'stable_features': stable,
        'recommendations': []
    }
    
    if critical:
        report['recommendations'].append(
            "URGENT: Critical feature drift detected. Investigate data pipeline and consider retraining."
        )
        for feat in critical[:3]:
            report['recommendations'].append(
                f"  - Investigate {feat['feature']} (PSI={feat['psi']:.3f})"
            )
    
    if warning:
        report['recommendations'].append(
            "Monitor warning features closely and plan for potential retraining."
        )
    
    return report


# ============================================================================
# CALIBRATION MONITORING
# ============================================================================

def calibration_metrics(y_true: np.ndarray, y_pred: np.ndarray, 
                        n_bins: int = 10) -> Dict:
    """
    Calculate calibration metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted probabilities
        n_bins: Number of calibration bins
        
    Returns:
        Dict with calibration metrics
    """
    from sklearn.calibration import calibration_curve
    from sklearn.metrics import brier_score_loss
    
    # Calibration curve
    prob_true, prob_pred = calibration_curve(y_true, y_pred, n_bins=n_bins)
    
    # Expected Calibration Error (ECE)
    bin_edges = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    
    for i in range(n_bins):
        mask = (y_pred >= bin_edges[i]) & (y_pred < bin_edges[i+1])
        if mask.sum() > 0:
            bin_acc = y_true[mask].mean()
            bin_conf = y_pred[mask].mean()
            bin_weight = mask.sum() / len(y_pred)
            ece += bin_weight * abs(bin_acc - bin_conf)
    
    # Brier score
    brier = brier_score_loss(y_true, y_pred)
    
    return {
        'brier_score': float(brier),
        'expected_calibration_error': float(ece),
        'calibration_curve': {
            'prob_true': prob_true.tolist(),
            'prob_pred': prob_pred.tolist()
        },
        'n_samples': len(y_true)
    }


def calibration_drift_check(baseline_metrics: Dict, 
                            current_metrics: Dict,
                            brier_threshold: float = 0.05,
                            ece_threshold: float = 0.03) -> Dict:
    """
    Check for calibration drift between baseline and current.
    
    Args:
        baseline_metrics: Baseline calibration metrics
        current_metrics: Current calibration metrics
        brier_threshold: Max allowed Brier score drift
        ece_threshold: Max allowed ECE drift
        
    Returns:
        Drift report
    """
    brier_drift = current_metrics['brier_score'] - baseline_metrics['brier_score']
    ece_drift = current_metrics['expected_calibration_error'] - baseline_metrics['expected_calibration_error']
    
    drift_detected = (abs(brier_drift) > brier_threshold or 
                     abs(ece_drift) > ece_threshold)
    
    return {
        'drift_detected': drift_detected,
        'brier_drift': float(brier_drift),
        'ece_drift': float(ece_drift),
        'baseline_brier': baseline_metrics['brier_score'],
        'current_brier': current_metrics['brier_score'],
        'baseline_ece': baseline_metrics['expected_calibration_error'],
        'current_ece': current_metrics['expected_calibration_error'],
        'recommendation': 'Recalibrate model' if drift_detected else 'No action required'
    }


# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

@dataclass
class PerformanceSnapshot:
    """Snapshot of model performance metrics"""
    timestamp: datetime
    auc: float
    gini: float
    ks_statistic: float
    brier_score: float
    n_samples: int
    default_rate: float


class PerformanceMonitor:
    """
    Track model performance over time and detect degradation.
    """
    
    def __init__(self, baseline_auc: float = None, 
                 degradation_threshold: float = 0.02):
        self.baseline_auc = baseline_auc
        self.degradation_threshold = degradation_threshold
        self.history: List[PerformanceSnapshot] = []
    
    def add_snapshot(self, y_true: np.ndarray, y_pred: np.ndarray,
                     timestamp: datetime = None) -> PerformanceSnapshot:
        """Add a performance snapshot"""
        from sklearn.metrics import roc_auc_score, brier_score_loss
        
        timestamp = timestamp or datetime.utcnow()
        
        auc = roc_auc_score(y_true, y_pred)
        gini = 2 * auc - 1
        
        # Calculate KS
        sorted_indices = np.argsort(y_pred)
        y_true_sorted = y_true[sorted_indices]
        n_pos = y_true.sum()
        n_neg = len(y_true) - n_pos
        tpr = np.cumsum(y_true_sorted) / n_pos
        fpr = np.cumsum(1 - y_true_sorted) / n_neg
        ks_stat = np.max(np.abs(tpr - fpr))
        
        snapshot = PerformanceSnapshot(
            timestamp=timestamp,
            auc=float(auc),
            gini=float(gini),
            ks_statistic=float(ks_stat),
            brier_score=float(brier_score_loss(y_true, y_pred)),
            n_samples=len(y_true),
            default_rate=float(y_true.mean())
        )
        
        self.history.append(snapshot)
        
        # Set baseline if first snapshot
        if self.baseline_auc is None:
            self.baseline_auc = auc
        
        return snapshot
    
    def check_degradation(self) -> Dict:
        """Check for performance degradation"""
        if not self.history or self.baseline_auc is None:
            return {'status': 'UNKNOWN', 'message': 'Insufficient history'}
        
        latest = self.history[-1]
        auc_drop = self.baseline_auc - latest.auc
        
        if auc_drop > self.degradation_threshold:
            return {
                'status': 'DEGRADED',
                'baseline_auc': self.baseline_auc,
                'current_auc': latest.auc,
                'auc_drop': float(auc_drop),
                'message': f'AUC dropped by {auc_drop:.4f}. Recommend investigation and potential retraining.',
                'timestamp': latest.timestamp.isoformat()
            }
        
        return {
            'status': 'HEALTHY',
            'baseline_auc': self.baseline_auc,
            'current_auc': latest.auc,
            'auc_drop': float(auc_drop),
            'message': 'Performance within acceptable range',
            'timestamp': latest.timestamp.isoformat()
        }
    
    def get_trend(self, window_days: int = 30) -> Dict:
        """Get performance trend over time"""
        if len(self.history) < 2:
            return {'trend': 'INSUFFICIENT_DATA', 'snapshots': len(self.history)}
        
        cutoff = datetime.utcnow() - timedelta(days=window_days)
        recent = [s for s in self.history if s.timestamp >= cutoff]
        
        if len(recent) < 2:
            return {'trend': 'INSUFFICIENT_DATA', 'snapshots': len(recent)}
        
        # Calculate trend (simple linear regression slope)
        aucs = [s.auc for s in recent]
        x = np.arange(len(aucs))
        slope = np.polyfit(x, aucs, 1)[0]
        
        if slope < -0.001:
            trend = 'DECLINING'
        elif slope > 0.001:
            trend = 'IMPROVING'
        else:
            trend = 'STABLE'
        
        return {
            'trend': trend,
            'slope': float(slope),
            'snapshots': len(recent),
            'auc_range': [min(aucs), max(aucs)],
            'latest_auc': aucs[-1]
        }


# ============================================================================
# FAIRNESS MONITORING
# ============================================================================

def demographic_parity_check(scores: np.ndarray, 
                             groups: np.ndarray,
                             threshold: float = 0.1) -> Dict:
    """
    Check demographic parity across groups.
    
    Measures if score distributions are similar across demographic groups.
    
    Args:
        scores: Credit scores
        groups: Group membership labels
        threshold: Maximum allowed difference in mean scores
        
    Returns:
        Fairness report
    """
    unique_groups = np.unique(groups)
    group_stats = {}
    
    for group in unique_groups:
        mask = groups == group
        group_stats[str(group)] = {
            'count': int(mask.sum()),
            'mean_score': float(scores[mask].mean()),
            'std_score': float(scores[mask].std()),
            'median_score': float(np.median(scores[mask]))
        }
    
    # Check parity
    means = [g['mean_score'] for g in group_stats.values()]
    max_diff = max(means) - min(means)
    
    parity_satisfied = max_diff <= (threshold * 600)  # Scale by score range
    
    return {
        'parity_satisfied': parity_satisfied,
        'max_mean_difference': float(max_diff),
        'threshold': threshold * 600,
        'group_statistics': group_stats,
        'recommendation': 'No action required' if parity_satisfied else 'Investigate group disparities'
    }


def equal_opportunity_check(y_true: np.ndarray, 
                            y_pred: np.ndarray,
                            groups: np.ndarray,
                            threshold: float = 0.05) -> Dict:
    """
    Check equal opportunity (TPR parity) across groups.
    
    Args:
        y_true: True labels
        y_pred: Predicted probabilities
        groups: Group membership labels
        threshold: Maximum allowed TPR difference
        
    Returns:
        Equal opportunity report
    """
    unique_groups = np.unique(groups)
    group_tpr = {}
    
    for group in unique_groups:
        mask = groups == group
        positives = y_true[mask] == 1
        
        if positives.sum() > 0:
            # TPR at 50% threshold
            tpr = ((y_pred[mask] >= 0.5) & positives).sum() / positives.sum()
            group_tpr[str(group)] = {
                'tpr': float(tpr),
                'n_positives': int(positives.sum())
            }
    
    if len(group_tpr) < 2:
        return {'status': 'INSUFFICIENT_GROUPS', 'group_tpr': group_tpr}
    
    tprs = [g['tpr'] for g in group_tpr.values()]
    max_diff = max(tprs) - min(tprs)
    
    return {
        'equal_opportunity_satisfied': max_diff <= threshold,
        'max_tpr_difference': float(max_diff),
        'threshold': threshold,
        'group_tpr': group_tpr,
        'recommendation': 'No action required' if max_diff <= threshold else 'Investigate TPR disparities'
    }


# ============================================================================
# RETRAINING RECOMMENDATIONS
# ============================================================================

@dataclass
class RetrainingRecommendation:
    """Retraining recommendation with justification"""
    should_retrain: bool
    urgency: str  # 'IMMEDIATE', 'PLANNED', 'MONITOR'
    reasons: List[str]
    estimated_improvement: Optional[str]


def get_retraining_recommendation(
    psi_report: Dict = None,
    calibration_report: Dict = None,
    performance_report: Dict = None,
    days_since_training: int = None,
    regular_retraining_days: int = 90
) -> RetrainingRecommendation:
    """
    Generate retraining recommendation based on monitoring results.
    
    Args:
        psi_report: PSI analysis report
        calibration_report: Calibration drift report
        performance_report: Performance degradation report
        days_since_training: Days since last training
        regular_retraining_days: Regular retraining cadence
        
    Returns:
        RetrainingRecommendation
    """
    reasons = []
    urgency = 'MONITOR'
    should_retrain = False
    
    # Check PSI
    if psi_report and psi_report.get('summary', {}).get('overall_status') == 'CRITICAL':
        reasons.append("Critical feature drift detected (PSI > 0.25)")
        urgency = 'IMMEDIATE'
        should_retrain = True
    elif psi_report and psi_report.get('summary', {}).get('warning_count', 0) > 5:
        reasons.append("Multiple features showing drift")
        if urgency != 'IMMEDIATE':
            urgency = 'PLANNED'
        should_retrain = True
    
    # Check calibration
    if calibration_report and calibration_report.get('drift_detected'):
        reasons.append("Calibration drift detected")
        if urgency != 'IMMEDIATE':
            urgency = 'PLANNED'
        should_retrain = True
    
    # Check performance
    if performance_report and performance_report.get('status') == 'DEGRADED':
        reasons.append(f"Performance degradation: AUC dropped by {performance_report.get('auc_drop', 0):.4f}")
        urgency = 'IMMEDIATE'
        should_retrain = True
    
    # Check time since training
    if days_since_training and days_since_training > regular_retraining_days:
        reasons.append(f"Regular retraining schedule ({regular_retraining_days} days) exceeded")
        if not should_retrain:
            urgency = 'PLANNED'
            should_retrain = True
    
    if not reasons:
        reasons.append("All monitoring metrics within acceptable ranges")
    
    return RetrainingRecommendation(
        should_retrain=should_retrain,
        urgency=urgency,
        reasons=reasons,
        estimated_improvement="2-5% AUC improvement expected" if should_retrain else None
    )


# ============================================================================
# COMPREHENSIVE MONITORING REPORT
# ============================================================================

def generate_monitoring_report(
    baseline_data: pd.DataFrame = None,
    current_data: pd.DataFrame = None,
    y_true: np.ndarray = None,
    y_pred: np.ndarray = None,
    baseline_calibration: Dict = None,
    current_calibration: Dict = None,
    days_since_training: int = None,
    output_path: str = None
) -> Dict:
    """
    Generate comprehensive monitoring report.
    
    Args:
        baseline_data: Baseline feature data
        current_data: Current feature data
        y_true: True labels (for current data)
        y_pred: Predicted probabilities (for current data)
        baseline_calibration: Baseline calibration metrics
        current_calibration: Current calibration metrics
        days_since_training: Days since model was trained
        output_path: Path to save report JSON
        
    Returns:
        Comprehensive monitoring report
    """
    report = {
        'timestamp': datetime.utcnow().isoformat(),
        'summary': {},
        'psi_analysis': None,
        'calibration_analysis': None,
        'performance_analysis': None,
        'retraining_recommendation': None
    }
    
    # PSI Analysis
    if baseline_data is not None and current_data is not None:
        psi_values = calculate_feature_psi(baseline_data, current_data)
        report['psi_analysis'] = psi_report(psi_values)
    
    # Calibration Analysis
    if baseline_calibration is not None and current_calibration is not None:
        report['calibration_analysis'] = calibration_drift_check(
            baseline_calibration, current_calibration
        )
    
    # Performance Analysis
    if y_true is not None and y_pred is not None:
        monitor = PerformanceMonitor()
        snapshot = monitor.add_snapshot(y_true, y_pred)
        report['performance_analysis'] = {
            'auc': snapshot.auc,
            'gini': snapshot.gini,
            'ks_statistic': snapshot.ks_statistic,
            'brier_score': snapshot.brier_score,
            'n_samples': snapshot.n_samples,
            'default_rate': snapshot.default_rate
        }
    
    # Retraining Recommendation
    recommendation = get_retraining_recommendation(
        psi_report=report.get('psi_analysis'),
        calibration_report=report.get('calibration_analysis'),
        performance_report=report.get('performance_analysis'),
        days_since_training=days_since_training
    )
    
    report['retraining_recommendation'] = {
        'should_retrain': recommendation.should_retrain,
        'urgency': recommendation.urgency,
        'reasons': recommendation.reasons,
        'estimated_improvement': recommendation.estimated_improvement
    }
    
    # Summary
    report['summary'] = {
        'overall_status': recommendation.urgency,
        'psi_status': report.get('psi_analysis', {}).get('summary', {}).get('overall_status', 'UNKNOWN'),
        'calibration_drift': report.get('calibration_analysis', {}).get('drift_detected', False),
        'retraining_required': recommendation.should_retrain,
        'days_since_training': days_since_training
    }
    
    # Save report
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        print(f"Monitoring report saved to {output_path}")
    
    return report


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("MONITORING MODULE DEMO")
    print("=" * 60)
    
    # Generate sample data
    np.random.seed(42)
    n = 1000
    
    # Baseline data
    baseline = pd.DataFrame({
        'feature1': np.random.normal(100, 20, n),
        'feature2': np.random.uniform(0, 1, n),
        'feature3': np.random.exponential(50, n)
    })
    
    # Current data (with some drift)
    current = pd.DataFrame({
        'feature1': np.random.normal(110, 25, n),  # Shifted mean and variance
        'feature2': np.random.uniform(0.1, 1, n),  # Shifted range
        'feature3': np.random.exponential(50, n)   # No change
    })
    
    # Calculate PSI
    print("\n1. PSI Analysis")
    print("-" * 40)
    psi_values = calculate_feature_psi(baseline, current)
    report = psi_report(psi_values)
    
    print(f"Overall Status: {report['summary']['overall_status']}")
    print(f"Critical features: {len(report['critical_features'])}")
    print(f"Warning features: {len(report['warning_features'])}")
    
    for feat in report['critical_features'] + report['warning_features']:
        print(f"  {feat['feature']}: PSI = {feat['psi']:.4f}")
    
    # Calibration check
    print("\n2. Calibration Analysis")
    print("-" * 40)
    
    y_true = np.random.binomial(1, 0.1, n)
    y_pred_baseline = np.random.beta(1, 9, n)  # Well calibrated
    y_pred_current = np.random.beta(0.8, 8, n)  # Slightly drifted
    
    baseline_cal = calibration_metrics(y_true, y_pred_baseline)
    current_cal = calibration_metrics(y_true, y_pred_current)
    
    drift = calibration_drift_check(baseline_cal, current_cal)
    print(f"Drift detected: {drift['drift_detected']}")
    print(f"Brier drift: {drift['brier_drift']:.4f}")
    print(f"ECE drift: {drift['ece_drift']:.4f}")
    
    # Retraining recommendation
    print("\n3. Retraining Recommendation")
    print("-" * 40)
    
    recommendation = get_retraining_recommendation(
        psi_report=report,
        calibration_report=drift,
        days_since_training=95
    )
    
    print(f"Should retrain: {recommendation.should_retrain}")
    print(f"Urgency: {recommendation.urgency}")
    print("Reasons:")
    for reason in recommendation.reasons:
        print(f"  - {reason}")


