"""
Revenue & Business Performance Analyzer
========================================

Analyzes:
- Revenue Metrics (GTV, growth, trends)
- Profitability
- Transaction Analytics
- Concentration Risk (HHI)
- Cost Efficiency
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime, timedelta


class RevenueAnalyzer:
    """Analyzes revenue and business performance"""
    
    def __init__(self):
        self.weights = {
            'revenue_metrics': 0.35,
            'profitability': 0.25,
            'transaction_analytics': 0.15,
            'concentration_risk': 0.15,
            'cost_efficiency': 0.10
        }
    
    def analyze_revenue_metrics(self, revenue_data: Dict, msme_category: str = 'micro') -> Dict[str, Any]:
        """
        Analyze revenue metrics: GTV, growth, trends
        
        Args:
            revenue_data: Revenue data including:
                - monthly_revenue: List[Dict] or Dict with monthly data
                - total_revenue: float
                - revenue_trend: str
            msme_category: MSME category (micro, small, medium)
            
        Returns:
            Dict with revenue metrics
        """
        try:
            monthly_revenue = revenue_data.get('monthly_revenue', [])
            total_revenue = revenue_data.get('total_revenue', 0)
            revenue_trend = revenue_data.get('revenue_trend', 'stable')
            
            # Calculate monthly revenue series
            if isinstance(monthly_revenue, list):
                revenue_series = pd.Series([r.get('amount', 0) if isinstance(r, dict) else r for r in monthly_revenue])
            elif isinstance(monthly_revenue, dict):
                revenue_series = pd.Series(list(monthly_revenue.values()))
            else:
                revenue_series = pd.Series([])
            
            # Calculate growth metrics
            if len(revenue_series) >= 2:
                growth_rate = ((revenue_series.iloc[-1] - revenue_series.iloc[0]) / revenue_series.iloc[0] * 100) if revenue_series.iloc[0] > 0 else 0
                avg_monthly_revenue = revenue_series.mean()
                revenue_volatility = (revenue_series.std() / revenue_series.mean() * 100) if revenue_series.mean() > 0 else 0
            else:
                growth_rate = 0
                avg_monthly_revenue = total_revenue / 12 if total_revenue > 0 else 0
                revenue_volatility = 0
            
            # Score revenue against MSME category benchmarks
            category_benchmarks = {
                'micro': {'min': 0, 'good': 500000, 'excellent': 2000000},
                'small': {'min': 2000000, 'good': 10000000, 'excellent': 50000000},
                'medium': {'min': 50000000, 'good': 200000000, 'excellent': 1000000000}
            }
            benchmark = category_benchmarks.get(msme_category.lower(), category_benchmarks['micro'])
            
            revenue_score = self._score_revenue_amount(avg_monthly_revenue, benchmark)
            growth_score = self._score_growth_rate(growth_rate)
            volatility_score = self._score_volatility(revenue_volatility)
            
            overall_score = (
                revenue_score * 0.50 +
                growth_score * 0.30 +
                volatility_score * 0.20
            )
            
            return {
                'total_revenue': float(total_revenue),
                'avg_monthly_revenue': float(avg_monthly_revenue),
                'growth_rate': float(growth_rate),
                'revenue_volatility': float(revenue_volatility),
                'revenue_trend': revenue_trend,
                'revenue_score': revenue_score,
                'growth_score': growth_score,
                'volatility_score': volatility_score,
                'overall_score': overall_score
            }
        except Exception as e:
            return {
                'total_revenue': 0,
                'avg_monthly_revenue': 0,
                'growth_rate': 0,
                'overall_score': 0,
                'error': str(e)
            }
    
    def analyze_profitability(self, financial_data: Dict) -> Dict[str, Any]:
        """
        Analyze profitability metrics
        
        Args:
            financial_data: Financial data including:
                - revenue: float
                - expenses: float
                - profit: float
                - profit_margin: float
                
        Returns:
            Dict with profitability metrics
        """
        try:
            revenue = financial_data.get('revenue', 0)
            expenses = financial_data.get('expenses', 0)
            profit = financial_data.get('profit', revenue - expenses)
            profit_margin = financial_data.get('profit_margin', (profit / revenue * 100) if revenue > 0 else 0)
            
            # Calculate if not provided
            if profit_margin == 0 and revenue > 0:
                profit_margin = (profit / revenue * 100)
            
            # Score profitability
            margin_score = self._score_profit_margin(profit_margin)
            profit_score = self._score_profit_amount(profit)
            
            score = (margin_score * 0.60 + profit_score * 0.40)
            
            return {
                'revenue': float(revenue),
                'expenses': float(expenses),
                'profit': float(profit),
                'profit_margin': float(profit_margin),
                'margin_score': margin_score,
                'profit_score': profit_score,
                'score': score
            }
        except Exception as e:
            return {
                'revenue': 0,
                'expenses': 0,
                'profit': 0,
                'profit_margin': 0,
                'score': 0,
                'error': str(e)
            }
    
    def analyze_transaction_analytics(self, revenue_data: Dict) -> Dict[str, Any]:
        """
        Analyze transaction analytics: volume, frequency, patterns
        
        Args:
            revenue_data: Revenue data including:
                - transaction_count: int
                - avg_transaction_value: float
                - transaction_frequency: str
                
        Returns:
            Dict with transaction analytics
        """
        try:
            transaction_count = revenue_data.get('transaction_count', 0)
            avg_transaction_value = revenue_data.get('avg_transaction_value', 0)
            transaction_frequency = revenue_data.get('transaction_frequency', 'low')
            
            # Score transaction metrics
            volume_score = self._score_transaction_volume(transaction_count)
            value_score = self._score_transaction_value(avg_transaction_value)
            frequency_score = self._score_transaction_frequency(transaction_frequency)
            
            score = (
                volume_score * 0.40 +
                value_score * 0.35 +
                frequency_score * 0.25
            )
            
            return {
                'transaction_count': int(transaction_count),
                'avg_transaction_value': float(avg_transaction_value),
                'transaction_frequency': transaction_frequency,
                'volume_score': volume_score,
                'value_score': value_score,
                'frequency_score': frequency_score,
                'score': score
            }
        except Exception as e:
            return {
                'transaction_count': 0,
                'avg_transaction_value': 0,
                'score': 0,
                'error': str(e)
            }
    
    def analyze_concentration_risk(self, revenue_data: Dict) -> Dict[str, Any]:
        """
        Analyze concentration risk using Herfindahl-Hirschman Index (HHI)
        
        Args:
            revenue_data: Revenue data including:
                - customer_revenue: Dict[str, float] (customer -> revenue)
                - top_customers: List[Dict]
                
        Returns:
            Dict with concentration risk metrics
        """
        try:
            customer_revenue = revenue_data.get('customer_revenue', {})
            top_customers = revenue_data.get('top_customers', [])
            
            # Calculate HHI
            if customer_revenue:
                revenues = list(customer_revenue.values())
                total_revenue = sum(revenues)
                if total_revenue > 0:
                    market_shares = [r / total_revenue for r in revenues]
                    hhi = sum(share ** 2 for share in market_shares) * 10000  # Scale to 0-10000
                else:
                    hhi = 0
            elif top_customers:
                revenues = [c.get('revenue', 0) if isinstance(c, dict) else 0 for c in top_customers]
                total_revenue = sum(revenues)
                if total_revenue > 0:
                    market_shares = [r / total_revenue for r in revenues]
                    hhi = sum(share ** 2 for share in market_shares) * 10000
                else:
                    hhi = 0
            else:
                hhi = 0
            
            # Calculate top customer concentration
            if customer_revenue:
                sorted_revenues = sorted(customer_revenue.values(), reverse=True)
                top_3_concentration = sum(sorted_revenues[:3]) / sum(sorted_revenues) if sorted_revenues else 0
            elif top_customers:
                sorted_revenues = sorted([c.get('revenue', 0) if isinstance(c, dict) else 0 for c in top_customers], reverse=True)
                top_3_concentration = sum(sorted_revenues[:3]) / sum(sorted_revenues) if sorted_revenues else 0
            else:
                top_3_concentration = 0
            
            # Score concentration risk (lower HHI = better diversification)
            hhi_score = self._score_hhi(hhi)
            concentration_score = self._score_top_customer_concentration(top_3_concentration)
            
            score = (hhi_score * 0.60 + concentration_score * 0.40)
            
            return {
                'hhi_index': float(hhi),
                'top_3_customer_concentration': float(top_3_concentration),
                'hhi_score': hhi_score,
                'concentration_score': concentration_score,
                'score': score
            }
        except Exception as e:
            return {
                'hhi_index': 0,
                'top_3_customer_concentration': 0,
                'score': 0,
                'error': str(e)
            }
    
    def analyze_cost_efficiency(self, financial_data: Dict) -> Dict[str, Any]:
        """
        Analyze cost efficiency metrics
        
        Args:
            financial_data: Financial data including:
                - revenue: float
                - operating_expenses: float
                - cost_of_goods_sold: float
                
        Returns:
            Dict with cost efficiency metrics
        """
        try:
            revenue = financial_data.get('revenue', 0)
            operating_expenses = financial_data.get('operating_expenses', 0)
            cogs = financial_data.get('cost_of_goods_sold', 0)
            
            # Calculate efficiency ratios
            if revenue > 0:
                operating_ratio = (operating_expenses / revenue) * 100
                cogs_ratio = (cogs / revenue) * 100
            else:
                operating_ratio = 0
                cogs_ratio = 0
            
            # Score efficiency (lower ratios = better)
            operating_score = self._score_operating_ratio(operating_ratio)
            cogs_score = self._score_cogs_ratio(cogs_ratio)
            
            score = (operating_score * 0.50 + cogs_score * 0.50)
            
            return {
                'operating_expense_ratio': float(operating_ratio),
                'cogs_ratio': float(cogs_ratio),
                'operating_score': operating_score,
                'cogs_score': cogs_score,
                'score': score
            }
        except Exception as e:
            return {
                'operating_expense_ratio': 0,
                'cogs_ratio': 0,
                'score': 0,
                'error': str(e)
            }
    
    def calculate_overall_score(self, revenue_score: float, profitability_score: float,
                               transaction_score: float, concentration_score: float,
                               cost_efficiency_score: float) -> float:
        """Calculate weighted overall revenue score"""
        return (
            revenue_score * self.weights['revenue_metrics'] +
            profitability_score * self.weights['profitability'] +
            transaction_score * self.weights['transaction_analytics'] +
            concentration_score * self.weights['concentration_risk'] +
            cost_efficiency_score * self.weights['cost_efficiency']
        )
    
    # Helper Methods
    
    def _score_revenue_amount(self, revenue: float, benchmark: Dict) -> float:
        """Score revenue amount against benchmarks"""
        if revenue >= benchmark['excellent']:
            return 1.0
        elif revenue >= benchmark['good']:
            return 0.8
        elif revenue >= benchmark['min']:
            return 0.5
        else:
            return 0.2
    
    def _score_growth_rate(self, growth_rate: float) -> float:
        """Score growth rate"""
        if growth_rate >= 20:
            return 1.0
        elif growth_rate >= 10:
            return 0.8
        elif growth_rate >= 5:
            return 0.6
        elif growth_rate >= 0:
            return 0.4
        elif growth_rate >= -10:
            return 0.2
        else:
            return 0.0
    
    def _score_volatility(self, volatility: float) -> float:
        """Score volatility (lower is better)"""
        if volatility < 10:
            return 1.0
        elif volatility < 20:
            return 0.8
        elif volatility < 30:
            return 0.6
        elif volatility < 50:
            return 0.4
        else:
            return 0.2
    
    def _score_profit_margin(self, margin: float) -> float:
        """Score profit margin"""
        if margin >= 20:
            return 1.0
        elif margin >= 15:
            return 0.9
        elif margin >= 10:
            return 0.7
        elif margin >= 5:
            return 0.5
        elif margin >= 0:
            return 0.3
        else:
            return 0.0
    
    def _score_profit_amount(self, profit: float) -> float:
        """Score profit amount"""
        if profit >= 1000000:
            return 1.0
        elif profit >= 500000:
            return 0.8
        elif profit >= 100000:
            return 0.6
        elif profit >= 0:
            return 0.4
        else:
            return 0.0
    
    def _score_transaction_volume(self, count: int) -> float:
        """Score transaction volume"""
        if count >= 1000:
            return 1.0
        elif count >= 500:
            return 0.8
        elif count >= 100:
            return 0.6
        elif count >= 50:
            return 0.4
        else:
            return 0.2
    
    def _score_transaction_value(self, value: float) -> float:
        """Score average transaction value"""
        if value >= 10000:
            return 1.0
        elif value >= 5000:
            return 0.8
        elif value >= 1000:
            return 0.6
        elif value >= 500:
            return 0.4
        else:
            return 0.2
    
    def _score_transaction_frequency(self, frequency: str) -> float:
        """Score transaction frequency"""
        frequency_scores = {
            'high': 1.0,
            'medium': 0.7,
            'low': 0.4,
            'very_low': 0.2
        }
        return frequency_scores.get(frequency.lower(), 0.5)
    
    def _score_hhi(self, hhi: float) -> float:
        """Score HHI (lower = better diversification)"""
        # HHI ranges: 0-1500 (competitive), 1500-2500 (moderate), 2500+ (concentrated)
        if hhi < 1500:
            return 1.0
        elif hhi < 2500:
            return 0.7
        elif hhi < 5000:
            return 0.4
        else:
            return 0.1
    
    def _score_top_customer_concentration(self, concentration: float) -> float:
        """Score top customer concentration (lower = better)"""
        if concentration < 0.30:
            return 1.0
        elif concentration < 0.50:
            return 0.7
        elif concentration < 0.70:
            return 0.4
        else:
            return 0.1
    
    def _score_operating_ratio(self, ratio: float) -> float:
        """Score operating expense ratio (lower = better)"""
        if ratio < 20:
            return 1.0
        elif ratio < 30:
            return 0.8
        elif ratio < 40:
            return 0.6
        elif ratio < 50:
            return 0.4
        else:
            return 0.2
    
    def _score_cogs_ratio(self, ratio: float) -> float:
        """Score COGS ratio (lower = better)"""
        if ratio < 40:
            return 1.0
        elif ratio < 50:
            return 0.8
        elif ratio < 60:
            return 0.6
        elif ratio < 70:
            return 0.4
        else:
            return 0.2

