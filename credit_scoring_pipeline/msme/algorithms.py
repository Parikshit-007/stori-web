"""
MSME Credit Scoring Pipeline - Algorithm & Formula Documentation
=================================================================

This module contains detailed formulas, mathematical models, and industry-standard
algorithms used in the MSME credit scoring and overdraft recommendation system.

SCORING METHODOLOGY
===================

The MSME credit scoring system uses a hybrid approach:
1. Gradient Boosting Machine (GBM) for pattern recognition
2. Rule-based segment subscore with exact parameter weights
3. Alpha-blending of both scores
4. Probability-to-score mapping

REFERENCE STANDARDS:
- RBI Guidelines for MSME Lending
- Basel III Capital Adequacy Norms
- CGTMSE (Credit Guarantee Trust for MSMEs)
- Tandon Committee Recommendations
- IND AS 109 (Expected Credit Loss)
- CIBIL MSME Rank methodology

Author: ML Engineering Team
Version: 2.0.0
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import math


# ============================================================================
# PARAMETER WEIGHTS (EXACT VALUES FROM SPECIFICATION)
# Total weightage: 100
# ============================================================================

PARAMETER_WEIGHTS = {
    # ========== CATEGORY A: BUSINESS IDENTITY & REGISTRATION (10%) ==========
    # Helps in fraud detection and business stability assessment
    
    "legal_entity_type": {
        "weight": 0.5,
        "category": "A",
        "why_it_matters": "Is the business registered or not. Helps in fraud detection.",
        "scoring_logic": {
            "public_limited": 1.0,
            "private_limited": 0.9,
            "llp": 0.8,
            "partnership": 0.6,
            "proprietorship": 0.4,
            "trust": 0.5,
            "society": 0.5,
            "unregistered": 0.0
        }
    },
    
    "business_formation_date": {
        "weight": 2.0,
        "category": "A",
        "why_it_matters": "Older businesses have lower default risk and more stable cashflows.",
        "formula": "score = min(1.0, business_age_years / 10)",
        "scoring_logic": {
            "bounds": {"min": 0, "max": 15},  # Cap at 15 years
            "breakpoints": [
                (0, 1, 0.0, 0.3),    # 0-1 year: 0-30%
                (1, 2, 0.3, 0.5),    # 1-2 years: 30-50%
                (2, 3, 0.5, 0.65),   # 2-3 years: 50-65%
                (3, 5, 0.65, 0.8),   # 3-5 years: 65-80%
                (5, 10, 0.8, 0.95),  # 5-10 years: 80-95%
                (10, 15, 0.95, 1.0)  # 10+ years: 95-100%
            ]
        }
    },
    
    "business_address_geolocation": {
        "weight": 1.0,
        "category": "A",
        "why_it_matters": "Links business to local economic conditions and verifies authenticity.",
        "scoring_logic": {
            "verified_and_match": 1.0,
            "verified_minor_mismatch": 0.7,
            "partially_verified": 0.4,
            "not_verified": 0.0
        }
    },
    
    "industry": {
        "weight": 2.0,
        "category": "A",
        "why_it_matters": "Some industries have inherently higher volatility and risk.",
        "risk_scores": {
            "healthcare": 0.90,
            "technology": 0.85,
            "essential_retail": 0.80,
            "manufacturing": 0.75,
            "services": 0.70,
            "trading": 0.65,
            "logistics": 0.60,
            "retail": 0.55,
            "hospitality": 0.40,
            "construction": 0.35,
            "agriculture": 0.30,
            "real_estate": 0.25
        }
    },
    
    "num_business_locations": {
        "weight": 0.5,
        "category": "A",
        "why_it_matters": "Signals scale, diversification, and stability.",
        "formula": "score = min(1.0, (num_locations - 1) / 9)",
        "scoring_logic": {
            "bounds": {"min": 1, "max": 10}
        }
    },
    
    "employees_count": {
        "weight": 0.5,
        "category": "A",
        "why_it_matters": "Indicates operational size and payroll obligations.",
        "formula": "score = min(1.0, employees / 100)",
        "bounds": {"min": 0, "max": 100}
    },
    
    "gstin_pan_verification": {
        "weight": 1.0,
        "category": "A",
        "why_it_matters": "Detects identity mismatches and potential fraud.",
        "scoring_logic": {
            "both_verified_match": 1.0,
            "both_verified_mismatch": 0.5,
            "one_verified": 0.4,
            "neither_verified": 0.0
        }
    },
    
    "msme_registration": {
        "weight": 0.5,
        "category": "A",
        "why_it_matters": "Indicates structured operations and compliance. Determines MSME type.",
        "scoring_logic": {
            "udyam_registered": 1.0,
            "udyog_aadhar": 0.8,
            "provisional": 0.5,
            "not_registered": 0.2
        }
    },
    
    "business_structure": {
        "weight": 0.5,
        "category": "A",
        "why_it_matters": "Physical presence reduces fraud and improves stability.",
        "scoring_logic": {
            "factory": 1.0,
            "multiple": 0.95,
            "warehouse": 0.85,
            "office": 0.80,
            "shop": 0.65,
            "home_based": 0.40,
            "virtual": 0.20
        }
    },
    
    "licenses_certificates": {
        "weight": 1.0,
        "category": "A",
        "why_it_matters": "Information on property ownership, professional licenses lowers fraud risk.",
        "formula": "score = num_valid_licenses / max_expected_licenses"
    },
    
    # ========== CATEGORY B: REVENUE & BUSINESS PERFORMANCE (20%) ==========
    
    "weekly_gtv": {
        "weight": 7.0,
        "category": "B",
        "why_it_matters": "Direct measure of revenue capacity and ability to repay.",
        "formula": """
            # Normalize GTV based on MSME category
            if msme_category == 'micro':
                score = min(1.0, weekly_gtv / 2_500_000)  # Cap at 25L/week
            elif msme_category == 'small':
                score = min(1.0, weekly_gtv / 10_000_000)  # Cap at 1Cr/week
            else:
                score = min(1.0, weekly_gtv / 50_000_000)  # Cap at 5Cr/week
        """,
        "percentile_scoring": {
            "p90": 1.0,
            "p75": 0.85,
            "p50": 0.65,
            "p25": 0.40,
            "p10": 0.20
        }
    },
    
    "transaction_count_value_per_day": {
        "weight": 3.0,
        "category": "B",
        "why_it_matters": "Higher frequency indicates healthier cashflow.",
        "formula": """
            # Combined score from transaction count and average value
            count_score = min(1.0, daily_txn_count / 100)
            
            # Optimal transaction size varies by industry
            value_score = gaussian_score(avg_txn_value, optimal_for_industry, std_dev)
            
            score = 0.6 * count_score + 0.4 * value_score
        """
    },
    
    "revenue_concentration_peak_day": {
        "weight": 1.0,
        "category": "B",
        "why_it_matters": "High dependence on few days increases cashflow risk.",
        "formula": """
            # Herfindahl-Hirschman Index for daily revenue
            hhi = sum(daily_share^2 for each day)
            
            # Lower HHI = more diversified = better score
            score = 1 - min(1.0, (hhi - 0.14) / 0.86)
            
            # 0.14 is HHI for perfectly uniform distribution across 7 days
        """,
        "bounds": {"lower_is_better": True, "min": 0, "max": 0.5}
    },
    
    "refund_chargeback_rate": {
        "weight": 2.0,
        "category": "B",
        "why_it_matters": "Strong predictor of fraud and business instability.",
        "formula": """
            # Refund rate penalty
            if chargeback_rate > 0.05:
                score = 0.0  # High risk
            elif chargeback_rate > 0.02:
                score = 0.3
            elif chargeback_rate > 0.01:
                score = 0.6
            else:
                score = 1.0 - (chargeback_rate * 20)
        """,
        "bounds": {"lower_is_better": True, "max_acceptable": 0.05}
    },
    
    "revenue_growth_rate_mom_qoq": {
        "weight": 2.0,
        "category": "B",
        "why_it_matters": "Positive, consistent growth indicates strong repayment ability.",
        "formula": """
            # Penalize negative growth, reward moderate positive growth
            # Excessive growth can also be risky (unsustainable)
            
            mom_score = sigmoid_transform(growth_mom, center=0.05, scale=0.10)
            qoq_score = sigmoid_transform(growth_qoq, center=0.15, scale=0.20)
            
            # Weight recent growth more heavily
            score = 0.6 * mom_score + 0.4 * qoq_score
            
            # Penalize high volatility
            if std_dev(monthly_growth) > 0.3:
                score *= 0.8
        """
    },
    
    "bank_average_balance_trend": {
        "weight": 4.0,  # Combining avg balance (3) + trend (1)
        "category": "B",
        "why_it_matters": "Shows liquidity cushion.",
        "formula": """
            # Balance score based on months of expenses coverage
            coverage_months = avg_balance / monthly_expenses
            balance_score = min(1.0, coverage_months / 3)  # 3 months ideal
            
            # Trend score (positive trend is good)
            trend_score = sigmoid_transform(balance_trend, center=0, scale=0.2)
            
            score = 0.75 * balance_score + 0.25 * trend_score
        """
    },
    
    "profit_margin_trends": {
        "weight": 1.0,
        "category": "B",
        "why_it_matters": "Low or falling margins increase default risk.",
        "formula": """
            # Margin score
            margin_score = min(1.0, max(0, (profit_margin - (-0.10)) / 0.30))
            
            # Trend adjustment
            if margin_trend < -0.1:  # Declining
                trend_multiplier = 0.7
            elif margin_trend > 0.1:  # Improving
                trend_multiplier = 1.1
            else:
                trend_multiplier = 1.0
            
            score = min(1.0, margin_score * trend_multiplier)
        """
    },
    
    "inventory_turnover_ratio": {
        "weight": 1.0,
        "category": "B",
        "why_it_matters": "Low turnover means cash stuck in inventory.",
        "formula": """
            # Optimal turnover varies by industry
            if industry in ['retail', 'trading']:
                optimal = 12  # Monthly turnover
            elif industry == 'manufacturing':
                optimal = 6  # Bi-monthly
            else:
                optimal = 8
            
            score = min(1.0, turnover_ratio / optimal)
        """
    },
    
    "value_of_assets": {
        "weight": 3.0,
        "category": "B",
        "why_it_matters": "Determines the safety net and business value.",
        "formula": """
            # Asset score relative to debt
            asset_to_debt = total_assets / (total_debt + 1)
            score = min(1.0, asset_to_debt / 3)  # 3x coverage ideal
        """
    },
    
    "operational_leverage_ratio": {
        "weight": 2.0,
        "category": "B",
        "why_it_matters": "More fixed costs = more risky the business is.",
        "formula": """
            # Lower operational leverage is better
            # OL = (Revenue - Variable Costs) / Operating Income
            
            if operational_leverage > 3:
                score = 0.2
            elif operational_leverage > 2:
                score = 0.4
            elif operational_leverage > 1.5:
                score = 0.6
            elif operational_leverage > 1:
                score = 0.8
            else:
                score = 1.0
        """,
        "bounds": {"lower_is_better": True}
    },
    
    # ========== CATEGORY C: CASH FLOW & BANKING (25%) ==========
    
    "weekly_inflow_outflow_ratio": {
        "weight": 4.0,
        "category": "C",
        "why_it_matters": "Helps understand working capital health.",
        "formula": """
            # Ratio > 1 means positive cash flow
            if ratio < 0.8:
                score = 0.0  # Critical
            elif ratio < 0.95:
                score = 0.3  # Concerning
            elif ratio < 1.05:
                score = 0.6  # Neutral
            elif ratio < 1.2:
                score = 0.85  # Good
            else:
                score = 1.0  # Excellent
        """,
        "optimal_range": [1.05, 1.30]
    },
    
    "overdraft_days_amount": {
        "weight": 3.0,  # Combining days (1.5) + amount (1.5)
        "category": "C",
        "why_it_matters": "Indicates working capital stress and risk.",
        "formula": """
            # Days component
            days_score = max(0, 1 - (overdraft_days / 30))
            
            # Amount component (relative to monthly GTV)
            amount_ratio = overdraft_amount / (monthly_gtv + 1)
            amount_score = max(0, 1 - amount_ratio * 5)
            
            score = 0.5 * days_score + 0.5 * amount_score
        """,
        "bounds": {"lower_is_better": True}
    },
    
    "cash_buffer_days": {
        "weight": 3.0,
        "category": "C",
        "why_it_matters": "Critical for determining repayment capability.",
        "formula": """
            # Days of operating expenses covered by cash
            cash_buffer_days = avg_cash_balance / daily_operating_expenses
            
            if buffer_days < 7:
                score = 0.2
            elif buffer_days < 15:
                score = 0.4
            elif buffer_days < 30:
                score = 0.6
            elif buffer_days < 60:
                score = 0.8
            else:
                score = 1.0
        """
    },
    
    "average_daily_closing_balance": {
        "weight": 2.0,
        "category": "C",
        "why_it_matters": "The more the balance is, risk becomes low.",
        "formula": "score = min(1.0, avg_daily_balance / (monthly_gtv * 0.3))"
    },
    
    "cash_balance_std_dev": {
        "weight": 1.0,
        "category": "C",
        "why_it_matters": "More volatility in cash flows indicate more risk.",
        "formula": """
            # Coefficient of variation
            cv = std_dev / avg_balance
            
            if cv > 1.0:
                score = 0.2
            elif cv > 0.5:
                score = 0.5
            elif cv > 0.3:
                score = 0.75
            else:
                score = 1.0
        """,
        "bounds": {"lower_is_better": True}
    },
    
    "negative_balance_days": {
        "weight": 2.0,
        "category": "C",
        "why_it_matters": "More number of days, higher is the liquidity risk.",
        "formula": """
            if negative_days == 0:
                score = 1.0
            elif negative_days <= 3:
                score = 0.8
            elif negative_days <= 7:
                score = 0.5
            elif negative_days <= 15:
                score = 0.2
            else:
                score = 0.0
        """,
        "bounds": {"lower_is_better": True, "max_acceptable": 15}
    },
    
    "daily_min_balance_pattern": {
        "weight": 2.0,
        "category": "C",
        "why_it_matters": "Low balance indicates cash flow risk.",
        "formula": """
            # Ratio of minimum to average balance
            min_avg_ratio = daily_min / avg_daily_balance
            
            score = min(1.0, min_avg_ratio * 2)  # 50% ratio = perfect score
        """
    },
    
    "consistent_deposits": {
        "weight": 1.0,
        "category": "C",
        "why_it_matters": "Determines cash revenues and their trend.",
        "formula": """
            # Regularity score based on deposit frequency
            expected_deposits = trading_days
            actual_deposits = deposit_count
            
            regularity = actual_deposits / expected_deposits
            score = min(1.0, regularity)
        """
    },
    
    "cashflow_regularity_trend": {
        "weight": 2.0,
        "category": "C",
        "why_it_matters": "Determines daily cash flow volatility.",
        "formula": """
            # Coefficient of variation of daily cash flows
            cv = std_dev_daily_cf / mean_daily_cf
            
            regularity_score = max(0, 1 - cv)
            
            # Trend component
            if trend > 0.05:
                trend_score = 1.0
            elif trend > 0:
                trend_score = 0.8
            elif trend > -0.05:
                trend_score = 0.5
            else:
                trend_score = 0.2
            
            score = 0.7 * regularity_score + 0.3 * trend_score
        """
    },
    
    "receivables_aging": {
        "weight": 0.5,
        "category": "C",
        "why_it_matters": "Old receivables indicate cashflow problems.",
        "formula": """
            # Days Sales Outstanding (DSO) based scoring
            if dso <= 30:
                score = 1.0
            elif dso <= 45:
                score = 0.8
            elif dso <= 60:
                score = 0.6
            elif dso <= 90:
                score = 0.3
            else:
                score = 0.1
        """,
        "bounds": {"lower_is_better": True}
    },
    
    "payables_aging": {
        "weight": 0.5,
        "category": "C",
        "why_it_matters": "Overdue payables indicate liquidity crunch.",
        "formula": """
            # Days Payable Outstanding (DPO) based scoring
            if dpo <= 30:
                score = 1.0  # Paying on time
            elif dpo <= 45:
                score = 0.85
            elif dpo <= 60:
                score = 0.6  # Some delay
            elif dpo <= 90:
                score = 0.3  # Concerning
            else:
                score = 0.1  # Severe liquidity issues
        """,
        "bounds": {"lower_is_better": True}
    },
    
    # ========== CATEGORY D: CREDIT & REPAYMENT BEHAVIOR (22%) ==========
    
    "bounced_cheques": {
        "weight": 3.0,
        "category": "D",
        "why_it_matters": "Direct predictor of default behaviour.",
        "formula": """
            # Bounced cheque penalty
            if bounce_count == 0:
                score = 1.0
            elif bounce_count == 1:
                score = 0.7
            elif bounce_count == 2:
                score = 0.4
            elif bounce_count <= 5:
                score = 0.1
            else:
                score = 0.0
            
            # Also consider bounce rate
            if bounce_rate > 0.1:
                score *= 0.5
        """,
        "critical_threshold": {"count": 3, "rate": 0.05}
    },
    
    "on_time_repayment_ratio_overdrafts": {
        "weight": 4.0,
        "category": "D",
        "why_it_matters": "Strongest indicator of repayment culture.",
        "formula": """
            # Direct mapping with penalty curve
            if ratio >= 0.95:
                score = 1.0
            elif ratio >= 0.90:
                score = 0.85
            elif ratio >= 0.80:
                score = 0.65
            elif ratio >= 0.70:
                score = 0.40
            elif ratio >= 0.50:
                score = 0.15
            else:
                score = 0.0
        """
    },
    
    "previous_defaults_writeoffs": {
        "weight": 2.0,
        "category": "D",
        "why_it_matters": "Direct predictor of future defaults.",
        "formula": """
            # Severe penalty for defaults
            if defaults_count == 0 and writeoffs_count == 0:
                score = 1.0
            elif writeoffs_count > 0:
                score = 0.0  # Any writeoff is critical
            elif defaults_count == 1:
                score = 0.3
            elif defaults_count == 2:
                score = 0.1
            else:
                score = 0.0
            
            # Consider recency - older defaults have less impact
            if last_default_months > 36:
                score = min(1.0, score + 0.2)
        """
    },
    
    "num_loans_outstanding": {
        "weight": 2.0,
        "category": "D",
        "why_it_matters": "Higher credit burden reduces repayment capacity.",
        "formula": """
            # Penalty increases with loan count
            if loans <= 1:
                score = 1.0
            elif loans == 2:
                score = 0.85
            elif loans == 3:
                score = 0.65
            elif loans <= 5:
                score = 0.40
            else:
                score = 0.15
        """
    },
    
    "historical_loan_utilization": {
        "weight": 1.5,
        "category": "D",
        "why_it_matters": "High utilisation indicates need for capital but also higher risk.",
        "formula": """
            # Moderate utilization is optimal
            if utilization < 0.30:
                score = 0.7  # Under-utilization
            elif utilization < 0.60:
                score = 1.0  # Optimal
            elif utilization < 0.80:
                score = 0.7  # High but acceptable
            elif utilization < 0.95:
                score = 0.4  # Concerning
            else:
                score = 0.1  # Maxed out
        """,
        "optimal_range": [0.30, 0.60]
    },
    
    "utility_payments_behaviour": {
        "weight": 3.0,
        "category": "D",
        "why_it_matters": "Determines repayment behaviour (TV, Electricity, Water, Gas, etc.).",
        "formula": """
            # On-time payment ratio
            score = on_time_ratio ** 2  # Square to penalize delays more
            
            # Days before due adjustment
            if avg_days_before_due > 5:
                score *= 1.1
            elif avg_days_before_due < 0:  # Late
                score *= max(0.5, 1 + avg_days_before_due * 0.05)
        """
    },
    
    "mobile_recharge_behaviour": {
        "weight": 2.0,
        "category": "D",
        "why_it_matters": "Determines repayment behaviour.",
        "formula": """
            # Regularity score
            regularity_score = recharge_frequency / expected_frequency
            
            # Timing score
            timing_score = on_time_ratio
            
            score = 0.6 * regularity_score + 0.4 * timing_score
        """
    },
    
    "rent_payment_behaviour": {
        "weight": 2.0,
        "category": "D",
        "why_it_matters": "Timely rent payments determine repayment probabilities.",
        "formula": """
            # Combine regularity and timeliness
            if rent_paid_on_time_ratio >= 0.95:
                score = 1.0
            elif rent_paid_on_time_ratio >= 0.85:
                score = 0.75
            elif rent_paid_on_time_ratio >= 0.70:
                score = 0.5
            else:
                score = 0.2
            
            # Penalty for missed months
            if missed_months > 0:
                score *= max(0.3, 1 - missed_months * 0.2)
        """
    },
    
    "supplier_vendor_payments": {
        "weight": 3.0,
        "category": "D",
        "why_it_matters": "Timely payments indicate responsible financial behavior and reliable operations.",
        "formula": """
            # Supplier payment discipline is critical for MSMEs
            regularity = payment_count / expected_payments
            timeliness = on_time_ratio
            
            # Weighted combination
            score = 0.4 * regularity + 0.6 * timeliness
            
            # Penalty for any default to key suppliers
            if supplier_default:
                score *= 0.5
        """
    },
    
    # ========== CATEGORY E: COMPLIANCE & TAXATION (12%) ==========
    
    "gst_filing_regularity": {
        "weight": 1.5,
        "category": "E",
        "why_it_matters": "Discipline and compliance correlate with repayment behaviour.",
        "formula": """
            # Calculate compliance rate
            filed_on_time = gst_filings_on_time / total_gst_periods
            
            if filed_on_time >= 0.95:
                score = 1.0
            elif filed_on_time >= 0.85:
                score = 0.8
            elif filed_on_time >= 0.70:
                score = 0.5
            else:
                score = 0.2
        """
    },
    
    "gst_vs_platform_sales_mismatch": {
        "weight": 1.5,
        "category": "E",
        "why_it_matters": "High mismatch indicates concealment or revenue manipulation.",
        "formula": """
            # Calculate mismatch percentage
            mismatch = abs(gst_sales - platform_sales) / (platform_sales + 1)
            
            if mismatch < 0.05:
                score = 1.0  # Acceptable
            elif mismatch < 0.15:
                score = 0.7  # Minor discrepancy
            elif mismatch < 0.30:
                score = 0.4  # Concerning
            else:
                score = 0.0  # Major fraud risk
        """,
        "bounds": {"lower_is_better": True, "fraud_threshold": 0.30}
    },
    
    "outstanding_taxes_dues": {
        "weight": 2.0,
        "category": "E",
        "why_it_matters": "Indicates financial stress or non-compliance.",
        "formula": """
            # Outstanding tax burden relative to revenue
            tax_burden = outstanding_taxes / (annual_revenue + 1)
            
            if tax_burden == 0:
                score = 1.0
            elif tax_burden < 0.02:
                score = 0.8
            elif tax_burden < 0.05:
                score = 0.5
            elif tax_burden < 0.10:
                score = 0.2
            else:
                score = 0.0
        """,
        "bounds": {"lower_is_better": True}
    },
    
    "itr_filing_data": {
        "weight": 2.0,
        "category": "E",
        "why_it_matters": "Determines income of the business.",
        "formula": """
            # ITR compliance and accuracy
            if itr_filed:
                # Compare declared income with estimated
                income_accuracy = min(itr_income / estimated_income, 1.0)
                score = 0.5 + (income_accuracy * 0.5)
            else:
                score = 0.2  # Penalty for non-filing
            
            # Consistency bonus
            if itr_filed_3_years:
                score *= 1.1
        """
    },
    
    "gst_r1_vs_itr_mismatch": {
        "weight": 1.0,
        "category": "E",
        "why_it_matters": "Low reporting indicates fraud risk.",
        "formula": """
            # Revenue reconciliation check
            gst_revenue = gst_r1_total
            itr_revenue = itr_gross_receipts
            
            mismatch = abs(gst_revenue - itr_revenue) / max(gst_revenue, itr_revenue, 1)
            
            score = max(0, 1 - mismatch * 3)  # 33% mismatch = 0 score
        """
    },
    
    "tax_payments": {
        "weight": 2.0,
        "category": "E",
        "why_it_matters": "Tax liens indicate government claims against property.",
        "formula": """
            # Tax payment discipline
            on_time_tax = tax_paid_on_time / total_tax_due
            
            if on_time_tax >= 0.95:
                score = 1.0
            elif on_time_tax >= 0.80:
                score = 0.7
            elif on_time_tax >= 0.60:
                score = 0.4
            else:
                score = 0.1
            
            # Major penalty for tax liens
            if has_tax_lien:
                score *= 0.3
        """
    },
    
    # ========== CATEGORY F: FRAUD & VERIFICATION (7%) ==========
    
    "kyc_completion_behaviour": {
        "weight": 0.5,
        "category": "F",
        "why_it_matters": "Multiple attempts or delays indicate risk.",
        "formula": """
            # Penalize multiple attempts
            if kyc_attempts == 1:
                score = 1.0
            elif kyc_attempts == 2:
                score = 0.8
            elif kyc_attempts == 3:
                score = 0.5
            else:
                score = 0.2
            
            # Time to complete adjustment
            if days_to_complete > 7:
                score *= 0.8
        """
    },
    
    "device_consistency": {
        "weight": 0.5,
        "category": "F",
        "why_it_matters": "Frequent device changes increase fraud risk.",
        "formula": """
            # Device fingerprint consistency
            unique_devices = count_unique_devices_90_days
            
            if unique_devices == 1:
                score = 1.0
            elif unique_devices == 2:
                score = 0.9
            elif unique_devices <= 3:
                score = 0.7
            else:
                score = 0.4
            
            # Check for known fraud devices
            if fraud_device_flag:
                score = 0.0
        """
    },
    
    "ip_stability": {
        "weight": 0.5,
        "category": "F",
        "why_it_matters": "Changing locations indicates identity issues.",
        "formula": """
            # IP geolocation stability
            location_changes = count_location_changes
            
            if location_changes <= 2:
                score = 1.0
            elif location_changes <= 5:
                score = 0.8
            elif location_changes <= 10:
                score = 0.5
            else:
                score = 0.2
            
            # VPN/proxy detection penalty
            if uses_vpn:
                score *= 0.6
        """
    },
    
    "kyc_mismatch_pan_address_bank": {
        "weight": 1.0,
        "category": "F",
        "why_it_matters": "Strong fraud signal.",
        "formula": """
            # Critical check for identity fraud
            if all_match:
                score = 1.0
            elif name_matches and (address_mismatch or bank_mismatch):
                score = 0.5  # Minor mismatch
            elif pan_matches_bank:
                score = 0.3
            else:
                score = 0.0  # Potential fraud
        """
    },
    
    "image_ocr_checks": {
        "weight": 1.0,
        "category": "F",
        "why_it_matters": "Confirms physical existence of business.",
        "formula": """
            # Document verification score
            docs_verified = verified_count / total_docs_submitted
            
            # OCR confidence adjustment
            avg_confidence = mean(ocr_confidence_scores)
            
            score = docs_verified * (0.5 + avg_confidence * 0.5)
        """
    },
    
    "error_rate_reporting_revenue": {
        "weight": 0.5,
        "category": "F",
        "why_it_matters": "Can indicate fraud risk.",
        "formula": """
            # Reporting accuracy
            errors = reporting_corrections / total_reports
            
            if errors == 0:
                score = 1.0
            elif errors < 0.05:
                score = 0.8
            elif errors < 0.10:
                score = 0.5
            else:
                score = 0.2
        """,
        "bounds": {"lower_is_better": True}
    },
    
    "incoming_funds_verification": {
        "weight": 2.0,
        "category": "F",
        "why_it_matters": "Indicates fraud risk.",
        "formula": """
            # Source of funds verification
            verified_inflows = verified_amount / total_inflows
            
            if verified_inflows >= 0.90:
                score = 1.0
            elif verified_inflows >= 0.70:
                score = 0.7
            elif verified_inflows >= 0.50:
                score = 0.4
            else:
                score = 0.1
            
            # Suspicious transaction penalty
            if suspicious_txn_flag:
                score *= 0.3
        """
    },
    
    "insurance_data": {
        "weight": 2.0,
        "category": "F",
        "why_it_matters": "Maintaining insurance indicates financial responsibility and risk management.",
        "formula": """
            # Insurance coverage score
            if has_business_insurance:
                coverage_score = 0.5
                
                # Premium payment timeliness
                if premium_paid_on_time >= 0.90:
                    coverage_score += 0.4
                elif premium_paid_on_time >= 0.70:
                    coverage_score += 0.2
                
                # Renewal consistency
                if renewal_on_time:
                    coverage_score += 0.1
                
                score = coverage_score
            else:
                score = 0.2  # No insurance
        """
    },
    
    # ========== CATEGORY G: EXTERNAL SIGNALS (4%) ==========
    
    "local_economic_health_score": {
        "weight": 1.0,
        "category": "G",
        "why_it_matters": "Businesses in booming areas perform better.",
        "formula": """
            # External economic indicators for business location
            # Combines: local GDP growth, employment rate, business density
            
            score = (local_gdp_percentile * 0.4 + 
                    employment_rate_percentile * 0.3 +
                    business_density_score * 0.3)
        """
    },
    
    "customer_concentration": {
        "weight": 1.0,
        "category": "G",
        "why_it_matters": "Reliance on few customers increases risk.",
        "formula": """
            # Herfindahl-Hirschman Index for customer concentration
            hhi = sum(customer_share^2 for each customer)
            
            if hhi < 0.10:
                score = 1.0  # Highly diversified
            elif hhi < 0.20:
                score = 0.8
            elif hhi < 0.35:
                score = 0.5  # Moderately concentrated
            else:
                score = 0.2  # High concentration risk
        """
    },
    
    "public_records_legal_proceedings": {
        "weight": 1.0,
        "category": "G",
        "why_it_matters": "Foreclosure proceedings and legal disputes indicate risk.",
        "formula": """
            # Legal issues scoring
            if no_legal_issues:
                score = 1.0
            elif minor_dispute:
                score = 0.7
            elif pending_litigation:
                score = 0.4
            elif foreclosure_proceedings:
                score = 0.1
            else:
                score = 0.0
        """
    },
    
    "social_media_data": {
        "weight": 1.5,
        "category": "G",
        "why_it_matters": "Analysis of social media provides supplementary information.",
        "formula": """
            # Social media presence and sentiment
            presence_score = min(1.0, (followers / 1000) * 0.5)
            
            # Sentiment analysis
            if sentiment_score > 0.7:
                sentiment_adj = 1.2
            elif sentiment_score > 0.5:
                sentiment_adj = 1.0
            else:
                sentiment_adj = 0.8
            
            # Review scores
            review_score = avg_rating / 5.0
            
            score = (presence_score * 0.3 + review_score * 0.7) * sentiment_adj
        """
    }
}


# ============================================================================
# CATEGORY WEIGHT CONFIGURATION
# ============================================================================

CATEGORY_WEIGHTS = {
    "A": {"name": "Business Identity & Registration", "weight": 0.10, "total_param_weight": 10.0},
    "B": {"name": "Revenue & Business Performance", "weight": 0.20, "total_param_weight": 26.0},
    "C": {"name": "Cash Flow & Banking", "weight": 0.25, "total_param_weight": 22.5},
    "D": {"name": "Credit & Repayment Behavior", "weight": 0.22, "total_param_weight": 24.5},
    "E": {"name": "Compliance & Taxation", "weight": 0.12, "total_param_weight": 10.0},
    "F": {"name": "Fraud & Verification", "weight": 0.07, "total_param_weight": 8.0},
    "G": {"name": "External Signals", "weight": 0.04, "total_param_weight": 4.5}
}


# ============================================================================
# SCORING FORMULAS
# ============================================================================

def sigmoid_transform(x: float, center: float = 0, scale: float = 1, 
                      min_val: float = 0, max_val: float = 1) -> float:
    """
    Sigmoid transformation for smooth scoring.
    
    Formula: f(x) = 1 / (1 + exp(-(x - center) / scale))
    
    Args:
        x: Input value
        center: Center point of sigmoid (inflection point)
        scale: Controls steepness (smaller = steeper)
        min_val: Minimum output value
        max_val: Maximum output value
    
    Returns:
        Transformed value in [min_val, max_val]
    """
    sigmoid = 1 / (1 + np.exp(-(x - center) / scale))
    return min_val + (max_val - min_val) * sigmoid


def gaussian_score(x: float, optimal: float, std_dev: float) -> float:
    """
    Gaussian scoring - maximum score at optimal value.
    
    Formula: f(x) = exp(-0.5 * ((x - optimal) / std_dev)^2)
    
    Args:
        x: Input value
        optimal: Optimal value (peak of gaussian)
        std_dev: Standard deviation (controls width)
    
    Returns:
        Score in [0, 1], maximum at optimal value
    """
    return np.exp(-0.5 * ((x - optimal) / std_dev) ** 2)


def piecewise_linear_score(x: float, breakpoints: List[Tuple[float, float]]) -> float:
    """
    Piecewise linear scoring with breakpoints.
    
    Args:
        x: Input value
        breakpoints: List of (x_value, score) tuples, sorted by x_value
    
    Returns:
        Interpolated score
    """
    if not breakpoints:
        return 0.5
    
    # Below first breakpoint
    if x <= breakpoints[0][0]:
        return breakpoints[0][1]
    
    # Above last breakpoint
    if x >= breakpoints[-1][0]:
        return breakpoints[-1][1]
    
    # Interpolate between breakpoints
    for i in range(len(breakpoints) - 1):
        x1, y1 = breakpoints[i]
        x2, y2 = breakpoints[i + 1]
        
        if x1 <= x <= x2:
            # Linear interpolation
            slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0
            return y1 + slope * (x - x1)
    
    return 0.5


def normalize_score(value: float, min_val: float, max_val: float, 
                   higher_is_better: bool = True) -> float:
    """
    Min-max normalization with direction handling.
    
    Formula:
        if higher_is_better: (value - min) / (max - min)
        else: (max - value) / (max - min)
    
    Args:
        value: Input value
        min_val: Minimum expected value
        max_val: Maximum expected value
        higher_is_better: Direction of scoring
    
    Returns:
        Normalized score in [0, 1]
    """
    # Clip to bounds
    value = np.clip(value, min_val, max_val)
    
    if max_val == min_val:
        return 0.5
    
    if higher_is_better:
        return (value - min_val) / (max_val - min_val)
    else:
        return (max_val - value) / (max_val - min_val)


# ============================================================================
# OVERDRAFT CALCULATION FORMULAS
# ============================================================================

class OverdraftFormulas:
    """
    Industry-standard formulas for overdraft limit calculation.
    """
    
    @staticmethod
    def turnover_method(annual_turnover: float, risk_tier_multiplier: float) -> float:
        """
        RBI Recommended Turnover Method.
        
        Formula: OD Limit = Annual Turnover × Risk-Based Multiplier
        
        Multiplier ranges by credit score:
        - Prime (750+): 40% (0.40)
        - Near Prime (650-749): 30% (0.30)
        - Standard (550-649): 25% (0.25)
        - Subprime (450-549): 15% (0.15)
        - High Risk (<450): 0% (0.00)
        
        Args:
            annual_turnover: Annual gross turnover
            risk_tier_multiplier: Multiplier based on risk tier
        
        Returns:
            Maximum overdraft limit
        """
        return annual_turnover * risk_tier_multiplier
    
    @staticmethod
    def mpbf_tandon_method(current_assets: float, current_liabilities: float,
                          existing_bank_debt: float) -> float:
        """
        Maximum Permissible Bank Finance (MPBF) - Tandon Committee Method II.
        
        Formula: MPBF = 0.75 × (Current Assets - Current Liabilities) - Existing Debt
        
        This method requires the borrower to maintain 25% of working capital
        from long-term sources.
        
        Args:
            current_assets: Total current assets
            current_liabilities: Total current liabilities  
            existing_bank_debt: Existing bank borrowings
        
        Returns:
            Maximum permissible bank finance
        """
        working_capital_gap = current_assets - current_liabilities
        mpbf = (working_capital_gap * 0.75) - existing_bank_debt
        return max(0, mpbf)
    
    @staticmethod
    def mpbf_chore_method(current_assets: float, inventory: float,
                         receivables: float, existing_debt: float) -> float:
        """
        MPBF - Chore Committee Method (Asset-based).
        
        Formula: MPBF = 0.60 × Inventory + 0.75 × Receivables - Existing Debt
        
        More conservative approach based on liquidation value of assets.
        
        Args:
            current_assets: Total current assets
            inventory: Inventory value
            receivables: Receivables value
            existing_debt: Existing bank debt
        
        Returns:
            Asset-based overdraft limit
        """
        asset_based = (inventory * 0.60) + (receivables * 0.75)
        return max(0, asset_based - existing_debt)
    
    @staticmethod
    def cash_flow_method(monthly_surplus: float, dscr_required: float,
                        tenure_months: int) -> float:
        """
        Cash Flow Coverage Method.
        
        Formula: 
            Serviceable_EMI = Monthly_Surplus / DSCR_Required
            OD_Limit = Serviceable_EMI / 0.03  (assuming 3% EMI per month)
        
        Args:
            monthly_surplus: Monthly cash surplus after expenses
            dscr_required: Required DSCR (varies by risk tier)
            tenure_months: Loan tenure in months
        
        Returns:
            Cash flow based limit
        """
        if monthly_surplus <= 0:
            return 0
        
        serviceable_emi = monthly_surplus / dscr_required
        # Approximate EMI as 3% of principal per month
        limit = serviceable_emi / 0.03
        return max(0, limit)
    
    @staticmethod
    def dscr(net_operating_income: float, debt_service: float) -> float:
        """
        Debt Service Coverage Ratio.
        
        Formula: DSCR = Net Operating Income / Total Debt Service
        
        Thresholds:
        - DSCR < 1.0: Cannot service debt
        - 1.0 ≤ DSCR < 1.20: Marginal
        - 1.20 ≤ DSCR < 1.50: Acceptable
        - DSCR ≥ 1.50: Good
        
        Args:
            net_operating_income: NOI (EBITDA or similar)
            debt_service: Total debt service (principal + interest)
        
        Returns:
            DSCR value
        """
        if debt_service <= 0:
            return 999.0
        return net_operating_income / debt_service
    
    @staticmethod
    def emi_calculation(principal: float, annual_rate: float, 
                       tenure_months: int) -> float:
        """
        EMI (Equated Monthly Installment) calculation.
        
        Formula: EMI = P × r × (1+r)^n / ((1+r)^n - 1)
        
        Where:
        - P = Principal amount
        - r = Monthly interest rate (annual_rate / 12 / 100)
        - n = Number of monthly installments
        
        Args:
            principal: Loan principal amount
            annual_rate: Annual interest rate (percentage)
            tenure_months: Loan tenure in months
        
        Returns:
            Monthly EMI amount
        """
        if tenure_months <= 0 or principal <= 0:
            return 0
        
        r = annual_rate / 100 / 12  # Monthly rate
        n = tenure_months
        
        if r == 0:
            return principal / n
        
        emi = principal * r * (1 + r)**n / ((1 + r)**n - 1)
        return emi
    
    @staticmethod
    def interest_rate_pricing(base_rate: float, 
                             risk_premium: float,
                             vintage_adjustment: float,
                             industry_adjustment: float,
                             payment_behavior_discount: float) -> float:
        """
        Interest Rate Pricing Model.
        
        Formula: 
            Final_Rate = Base_Rate + Risk_Premium + Vintage_Adj + Industry_Adj - Behavior_Discount
        
        Components:
        - Base Rate: Lender's base lending rate
        - Risk Premium: Based on credit score tier (0-10%)
        - Vintage Adjustment: Based on business age (-1% to +2%)
        - Industry Adjustment: Based on industry risk (-0.5% to +1.5%)
        - Behavior Discount: For good payment history (0% to -1%)
        
        Args:
            base_rate: Lender's base rate
            risk_premium: Premium based on risk tier
            vintage_adjustment: Adjustment for business age
            industry_adjustment: Adjustment for industry
            payment_behavior_discount: Discount for good behavior
        
        Returns:
            Final interest rate (percentage)
        """
        final_rate = (base_rate + risk_premium + vintage_adjustment + 
                     industry_adjustment - payment_behavior_discount)
        
        # Cap rate within reasonable bounds
        return np.clip(final_rate, 10.0, 26.0)


# ============================================================================
# SCORE BLENDING FORMULA
# ============================================================================

def blend_scores(gbm_prob: float, segment_subscore: float, 
                alpha: float = 0.7) -> float:
    """
    Blend GBM prediction with segment subscore.
    
    Formula: 
        final_prob = α × GBM_prob + (1-α) × (1 - segment_subscore)
    
    Where:
    - GBM_prob: Probability from gradient boosting model
    - segment_subscore: Rule-based subscore (higher = lower risk)
    - α (alpha): Weight for GBM model (default 0.7)
    
    Note: segment_subscore is inverted because higher subscore = lower risk,
    but we need to output a probability (higher = higher risk).
    
    Args:
        gbm_prob: GBM model default probability
        segment_subscore: Segment-based subscore [0,1]
        alpha: Blending weight for GBM
    
    Returns:
        Blended default probability
    """
    # Convert subscore to risk probability
    segment_risk = 1 - segment_subscore
    
    # Blend
    final_prob = alpha * gbm_prob + (1 - alpha) * segment_risk
    
    return np.clip(final_prob, 0, 1)


def probability_to_score(prob: float, min_score: int = 300, 
                        max_score: int = 900) -> int:
    """
    Map default probability to credit score.
    
    Formula: Uses piecewise linear mapping with these anchor points:
    
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
    
    This mapping is calibrated to match industry standard default rates
    for each score bucket.
    
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


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_weights():
    """Validate that all parameter weights sum correctly by category."""
    category_totals = {cat: 0.0 for cat in CATEGORY_WEIGHTS.keys()}
    
    for param, config in PARAMETER_WEIGHTS.items():
        category = config["category"]
        weight = config["weight"]
        category_totals[category] += weight
    
    print("Category Weight Validation:")
    print("=" * 50)
    
    total = 0
    for cat, total_weight in category_totals.items():
        expected = CATEGORY_WEIGHTS[cat]["total_param_weight"]
        status = "✓" if abs(total_weight - expected) < 0.1 else "✗"
        print(f"Category {cat}: {total_weight:.1f} (expected: {expected}) {status}")
        total += total_weight
    
    print(f"\nTotal weight: {total:.1f} (expected: ~100)")
    return category_totals


# ============================================================================
# MAIN (Demo)
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MSME CREDIT SCORING ALGORITHM DOCUMENTATION")
    print("=" * 70)
    
    # Validate weights
    validate_weights()
    
    print("\n" + "=" * 70)
    print("SAMPLE CALCULATIONS")
    print("=" * 70)
    
    # Demo calculations
    print("\n1. Sigmoid Transform Example:")
    for x in [-0.1, 0, 0.05, 0.1, 0.2]:
        score = sigmoid_transform(x, center=0.05, scale=0.10)
        print(f"   Growth rate {x:.2%} → Score: {score:.3f}")
    
    print("\n2. Overdraft Turnover Method:")
    turnover = 12_000_000  # 1.2 Cr annual
    for tier, mult in [("Prime", 0.40), ("Near Prime", 0.30), ("Standard", 0.25)]:
        limit = OverdraftFormulas.turnover_method(turnover, mult)
        print(f"   {tier}: ₹{limit:,.0f}")
    
    print("\n3. DSCR Calculation:")
    for noi, debt in [(100000, 60000), (100000, 80000), (100000, 100000)]:
        dscr = OverdraftFormulas.dscr(noi, debt)
        print(f"   NOI: ₹{noi:,}, Debt: ₹{debt:,} → DSCR: {dscr:.2f}")
    
    print("\n4. Probability to Score Mapping:")
    for prob in [0.01, 0.05, 0.12, 0.25, 0.40]:
        score = probability_to_score(prob)
        print(f"   Prob: {prob:.2%} → Score: {score}")
    
    print("\n5. EMI Calculation:")
    principal = 1_000_000
    for rate, tenure in [(12, 24), (14, 18), (16, 12)]:
        emi = OverdraftFormulas.emi_calculation(principal, rate, tenure)
        print(f"   ₹{principal:,} @ {rate}% for {tenure}mo → EMI: ₹{emi:,.0f}")


