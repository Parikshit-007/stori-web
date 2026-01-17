"""
Director/Promoter Profile & Behavioral Signals Analyzer
========================================================

Analyzes:
- Personal Banking Summary
- Behavioral & Stability Signals
- Financial Stability
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any
from decimal import Decimal
from datetime import datetime, timedelta


class DirectorAnalyzer:
    """Analyzes director/promoter profile and behavioral signals"""
    
    def __init__(self):
        self.weights = {
            'personal_banking': 0.30,
            'behavioral_signals': 0.40,
            'financial_stability': 0.30
        }
    
    def analyze_personal_banking(self, bank_data: Dict) -> Dict[str, Any]:
        """
        Analyze personal banking summary for all directors
        
        Calculates average balance by checking specific days (7th, 14th, 22nd, 31st)
        across all accounts for consistency.
        
        Args:
            bank_data: Personal bank statement data with multiple accounts
            
        Returns:
            Dict with personal banking metrics
        """
        try:
            # Calculate average account balance on specific days across all accounts
            avg_balance = self._calculate_avg_balance_on_specific_days(bank_data)
            
            # Derive assets and liabilities from transaction patterns
            assets = self._derive_assets(bank_data)
            liabilities = self._derive_liabilities(bank_data)
            
            return {
                'avg_account_balance_personal': float(avg_balance),
                'balance_calculation_method': 'specific_days_average',
                'balance_check_days': [7, 14, 22, 31],
                'assets_derived': assets,
                'liabilities_derived': liabilities,
                'score': self._score_personal_banking(avg_balance, assets, liabilities)
            }
        except Exception as e:
            return {
                'avg_account_balance_personal': 0,
                'assets_derived': {},
                'liabilities_derived': {},
                'score': 0,
                'error': str(e)
            }
    
    def analyze_behavioral_signals(self, bank_data: Dict) -> Dict[str, Any]:
        """
        Analyze behavioral and stability signals
        
        Args:
            bank_data: Personal bank statement data
            
        Returns:
            Dict with behavioral metrics
        """
        try:
            transactions = pd.DataFrame(bank_data.get('transactions', []))
            
            if transactions.empty:
                return self._empty_behavioral_signals()
            
            # Regular P2P Transactions
            p2p_count = self._detect_p2p_transactions(transactions)
            regular_p2p = p2p_count > 5  # More than 5 P2P per month
            
            # Monthly Income/Inflow/Outflow
            credits = transactions[transactions['type'] == 'credit']['amount'].sum()
            debits = transactions[transactions['type'] == 'debit']['amount'].sum()
            
            # Identify salary credits
            monthly_income = self._identify_monthly_income(transactions)
            monthly_inflow = float(credits)
            monthly_outflow = float(debits)
            
            # Income Volatility (Coefficient of Variation)
            income_series = self._get_monthly_income_series(transactions)
            income_volatility = (income_series.std() / income_series.mean() * 100) if len(income_series) > 0 and income_series.mean() > 0 else 0
            
            # Subscriptions
            subscriptions = self._detect_subscriptions(transactions)
            
            # Micro-commitments (Display only)
            micro_commitments = self._detect_micro_commitments(transactions)
            
            # Late-night transactions (Emotional indicator)
            late_night_count = self._count_late_night_transactions(transactions)
            
            # Savings Consistency
            savings_consistency = self._calculate_savings_consistency(transactions)
            
            # NEW: Impulse Behavioral Features
            impulse_features = self._compute_impulse_behavioral_features(
                transactions, monthly_income, monthly_outflow
            )
            
            # NEW: Improved Inflow Time Consistency
            inflow_consistency = self._compute_improved_inflow_consistency(
                transactions, monthly_income
            )
            
            # NEW: Manipulation Detection
            manipulation_risk = self._detect_manipulation_patterns(transactions)
            
            return {
                'regular_p2p_transactions': regular_p2p,
                'monthly_income': float(monthly_income),
                'monthly_inflow': monthly_inflow,
                'monthly_outflow': monthly_outflow,
                'income_volatility': float(income_volatility),
                'subscriptions': subscriptions,
                'micro_commitments': micro_commitments,
                'late_night_transactions_count': late_night_count,
                'savings_consistency_score': float(savings_consistency),
                # NEW: Impulse & Behavioral Features
                'salary_retention_ratio': impulse_features.get('salary_retention_ratio', 0.5),
                'week1_vs_week4_spending_ratio': impulse_features.get('week1_vs_week4_spending_ratio', 1.0),
                'impulse_spending_score': impulse_features.get('impulse_spending_score', 0.0),
                'upi_volume_spike_score': impulse_features.get('upi_volume_spike_score', 0.0),
                'avg_balance_drop_rate': impulse_features.get('avg_balance_drop_rate', 0.5),
                # NEW: Inflow Consistency
                'inflow_time_consistency': float(inflow_consistency),
                # NEW: Manipulation Risk
                'manipulation_risk_score': float(manipulation_risk.get('total_risk', 0.0)),
                'circular_transaction_risk': float(manipulation_risk.get('circular_risk', 0.0)),
                'p2p_manipulation_risk': float(manipulation_risk.get('p2p_risk', 0.0)),
                'balance_manipulation_risk': float(manipulation_risk.get('balance_risk', 0.0)),
                'score': self._score_behavioral_signals(
                    income_volatility, savings_consistency, late_night_count
                )
            }
        except Exception as e:
            return {**self._empty_behavioral_signals(), 'error': str(e)}
    
    def analyze_financial_stability(self, bank_data: Dict) -> Dict[str, Any]:
        """
        Analyze financial stability based on income changes
        
        Rule: Stable if income change < 30%, Unstable if >= 30%
        Only decreases stability score (not boosts it)
        
        Args:
            bank_data: Personal bank statement data
            
        Returns:
            Dict with stability metrics
        """
        try:
            transactions = pd.DataFrame(bank_data.get('transactions', []))
            
            if transactions.empty:
                return {'is_stable': True, 'income_change_percentage': 0, 'score': 0.5}
            
            # Get income over time
            income_series = self._get_monthly_income_series(transactions)
            
            if len(income_series) < 2:
                return {'is_stable': True, 'income_change_percentage': 0, 'score': 0.5}
            
            # Calculate income change
            recent_income = income_series[-3:].mean()  # Last 3 months
            previous_income = income_series[-6:-3].mean() if len(income_series) >= 6 else income_series[:3].mean()
            
            income_change_pct = abs((recent_income - previous_income) / previous_income * 100) if previous_income > 0 else 0
            
            is_stable = income_change_pct < 30
            
            # Only decrease score if unstable
            if is_stable:
                score = 1.0
            else:
                # Penalize based on severity
                if income_change_pct >= 50:
                    score = 0.2
                elif income_change_pct >= 40:
                    score = 0.4
                else:  # 30-40%
                    score = 0.6
            
            return {
                'is_stable': is_stable,
                'income_change_percentage': float(income_change_pct),
                'score': score
            }
        except Exception as e:
            return {
                'is_stable': True,
                'income_change_percentage': 0,
                'score': 0.5,
                'error': str(e)
            }
    
    def calculate_overall_score(self, personal_banking_score: float, 
                               behavioral_score: float, 
                               stability_score: float) -> float:
        """Calculate weighted overall director score"""
        return (
            personal_banking_score * self.weights['personal_banking'] +
            behavioral_score * self.weights['behavioral_signals'] +
            stability_score * self.weights['financial_stability']
        )
    
    # Helper Methods
    
    def _calculate_avg_balance_on_specific_days(self, bank_data: Dict) -> float:
        """
        Calculate average account balance by checking specific days (7th, 14th, 22nd, 31st)
        across all accounts.
        
        This provides a consistent measure by sampling balances at specific points
        rather than averaging all transactions.
        
        Args:
            bank_data: Bank statement data (can contain multiple accounts)
            
        Returns:
            Average balance across all accounts and specific days
        """
        try:
            # Days to check each month
            check_days = [7, 14, 22, 31]
            
            # Handle multiple account formats
            all_balances_on_days = []
            
            # Check if data has multiple accounts
            accounts_data = bank_data.get('accounts', [])
            
            if accounts_data:
                # Multiple accounts format
                for account in accounts_data:
                    transactions = pd.DataFrame(account.get('transactions', []))
                    if not transactions.empty:
                        balances = self._get_balances_on_specific_days(transactions, check_days)
                        all_balances_on_days.extend(balances)
            else:
                # Single account or simple format
                transactions = pd.DataFrame(bank_data.get('transactions', []))
                if not transactions.empty:
                    balances = self._get_balances_on_specific_days(transactions, check_days)
                    all_balances_on_days.extend(balances)
                
                # Also check if account_balances array is provided (legacy format)
                account_balances = bank_data.get('account_balances', [])
                if account_balances and not all_balances_on_days:
                    # Fallback to simple average if no transaction data
                    return np.mean(account_balances)
            
            # Calculate average
            if all_balances_on_days:
                return float(np.mean(all_balances_on_days))
            else:
                return 0.0
                
        except Exception as e:
            # Fallback to simple average if calculation fails
            account_balances = bank_data.get('account_balances', [])
            return float(np.mean(account_balances)) if account_balances else 0.0
    
    def _get_balances_on_specific_days(self, transactions: pd.DataFrame, check_days: list) -> list:
        """
        Extract balances on specific days from transaction DataFrame.
        
        Args:
            transactions: DataFrame with transactions
            check_days: List of days to check (e.g., [7, 14, 22, 31])
            
        Returns:
            List of balances found on those specific days
        """
        balances_found = []
        
        try:
            # Ensure date column exists and is datetime
            if 'date' not in transactions.columns:
                return balances_found
            
            transactions['date'] = pd.to_datetime(transactions['date'])
            transactions['day'] = transactions['date'].dt.day
            transactions['month_year'] = transactions['date'].dt.to_period('M')
            
            # Group by month
            for month_year, month_data in transactions.groupby('month_year'):
                # For each check day, find the balance
                for check_day in check_days:
                    # Get transactions on or before this day
                    day_data = month_data[month_data['day'] <= check_day]
                    
                    if not day_data.empty:
                        # Get the closest transaction to the check day
                        closest_day_data = month_data[month_data['day'] == check_day]
                        
                        if not closest_day_data.empty:
                            # Balance on exact day found
                            if 'balance' in closest_day_data.columns:
                                balance = closest_day_data.iloc[-1]['balance']
                                balances_found.append(float(balance))
                        else:
                            # Find closest previous day
                            prev_days = month_data[month_data['day'] < check_day]
                            if not prev_days.empty and 'balance' in prev_days.columns:
                                balance = prev_days.iloc[-1]['balance']
                                balances_found.append(float(balance))
            
            return balances_found
            
        except Exception as e:
            return balances_found
    
    def _derive_assets(self, bank_data: Dict) -> Dict:
        """Derive assets from transaction patterns"""
        assets = {
            'investment_transactions': 0,
            'mutual_fund_sip': 0,
            'fixed_deposits': 0,
            'estimated_total': 0
        }
        
        transactions = bank_data.get('transactions', [])
        for txn in transactions:
            narration = txn.get('narration', '').lower()
            amount = txn.get('amount', 0)
            
            if any(keyword in narration for keyword in ['mutual fund', 'mf', 'sip']):
                assets['mutual_fund_sip'] += amount
            elif any(keyword in narration for keyword in ['fd', 'fixed deposit']):
                assets['fixed_deposits'] += amount
            elif any(keyword in narration for keyword in ['shares', 'demat', 'trading']):
                assets['investment_transactions'] += amount
        
        assets['estimated_total'] = sum([v for k, v in assets.items() if k != 'estimated_total'])
        return assets
    
    def _derive_liabilities(self, bank_data: Dict) -> Dict:
        """Derive liabilities from transaction patterns"""
        liabilities = {
            'loan_emi': 0,
            'credit_card_payments': 0,
            'estimated_total': 0
        }
        
        transactions = bank_data.get('transactions', [])
        for txn in transactions:
            narration = txn.get('narration', '').lower()
            amount = txn.get('amount', 0)
            
            if any(keyword in narration for keyword in ['emi', 'loan']):
                liabilities['loan_emi'] += amount
            elif any(keyword in narration for keyword in ['credit card', 'cc payment']):
                liabilities['credit_card_payments'] += amount
        
        liabilities['estimated_total'] = sum([v for k, v in liabilities.items() if k != 'estimated_total'])
        return liabilities
    
    def _detect_p2p_transactions(self, transactions: pd.DataFrame) -> int:
        """Count P2P transactions (UPI, IMPS, NEFT to individuals)"""
        p2p_keywords = ['upi', 'imps', 'neft', 'paytm', 'phonepe', 'gpay']
        count = 0
        
        for _, txn in transactions.iterrows():
            narration = str(txn.get('narration', '')).lower()
            if any(keyword in narration for keyword in p2p_keywords):
                count += 1
        
        return count
    
    def _identify_monthly_income(self, transactions: pd.DataFrame) -> float:
        """Identify regular monthly income (salary)"""
        credits = transactions[transactions['type'] == 'credit']
        
        # Look for salary keywords
        salary_keywords = ['salary', 'sal credit', 'pay credit']
        salary_txns = credits[credits['narration'].str.lower().str.contains('|'.join(salary_keywords), na=False)]
        
        if not salary_txns.empty:
            return salary_txns['amount'].mean()
        
        # Otherwise, take mean of top regular credits
        return credits['amount'].quantile(0.75) if not credits.empty else 0
    
    def _get_monthly_income_series(self, transactions: pd.DataFrame) -> pd.Series:
        """Get monthly income time series"""
        try:
            transactions['date'] = pd.to_datetime(transactions['date'])
            transactions['month'] = transactions['date'].dt.to_period('M')
            
            credits = transactions[transactions['type'] == 'credit']
            monthly_income = credits.groupby('month')['amount'].sum()
            
            return monthly_income
        except:
            return pd.Series([])
    
    def _detect_subscriptions(self, transactions: pd.DataFrame) -> List[Dict]:
        """Detect recurring subscriptions"""
        subscription_keywords = ['netflix', 'amazon prime', 'spotify', 'youtube', 'google one']
        subscriptions = []
        
        for keyword in subscription_keywords:
            matches = transactions[transactions['narration'].str.lower().str.contains(keyword, na=False)]
            if len(matches) > 1:
                subscriptions.append({
                    'name': keyword.title(),
                    'frequency': len(matches),
                    'avg_amount': float(matches['amount'].mean())
                })
        
        return subscriptions
    
    def _detect_micro_commitments(self, transactions: pd.DataFrame) -> List[Dict]:
        """Detect micro-commitments (small regular payments)"""
        # Find recurring small debits (< 500)
        small_debits = transactions[
            (transactions['type'] == 'debit') & 
            (transactions['amount'] < 500)
        ]
        
        # Group by similar amounts and narration patterns
        micro_commitments = []
        
        # This is a simplified version - you'd want more sophisticated pattern matching
        if not small_debits.empty:
            micro_commitments.append({
                'count': len(small_debits),
                'avg_amount': float(small_debits['amount'].mean()),
                'total_amount': float(small_debits['amount'].sum())
            })
        
        return micro_commitments
    
    def _count_late_night_transactions(self, transactions: pd.DataFrame) -> int:
        """Count late-night transactions (11 PM - 3 AM) as emotional indicator"""
        try:
            if 'time' in transactions.columns or 'timestamp' in transactions.columns:
                time_col = 'time' if 'time' in transactions.columns else 'timestamp'
                transactions['hour'] = pd.to_datetime(transactions[time_col]).dt.hour
                
                late_night = transactions[
                    (transactions['hour'] >= 23) | (transactions['hour'] <= 3)
                ]
                return len(late_night)
        except:
            pass
        
        return 0
    
    def _calculate_savings_consistency(self, transactions: pd.DataFrame) -> float:
        """Calculate savings consistency score (0-1)"""
        try:
            transactions['date'] = pd.to_datetime(transactions['date'])
            transactions['month'] = transactions['date'].dt.to_period('M')
            
            monthly_data = transactions.groupby('month').agg({
                'amount': lambda x: x[transactions['type'] == 'credit'].sum() - x[transactions['type'] == 'debit'].sum()
            })
            
            # Positive balance months
            positive_months = (monthly_data['amount'] > 0).sum()
            total_months = len(monthly_data)
            
            consistency_score = positive_months / total_months if total_months > 0 else 0
            
            return min(1.0, consistency_score)
        except:
            return 0.5
    
    def _score_personal_banking(self, avg_balance: float, assets: Dict, liabilities: Dict) -> float:
        """Score personal banking health (0-1)"""
        # Balance score
        balance_score = min(1.0, avg_balance / 100000)  # Normalize to 1 lakh
        
        # Asset-Liability ratio
        total_assets = assets.get('estimated_total', 0)
        total_liabilities = liabilities.get('estimated_total', 0)
        
        if total_liabilities > 0:
            al_ratio = total_assets / total_liabilities
            al_score = min(1.0, al_ratio / 2)  # 2:1 ratio is excellent
        else:
            al_score = 1.0 if total_assets > 0 else 0.5
        
        return (balance_score * 0.6 + al_score * 0.4)
    
    def _compute_impulse_behavioral_features(self, transactions: pd.DataFrame, 
                                           monthly_income: float, 
                                           monthly_expense: float) -> Dict[str, float]:
        """
        Compute impulse spending and behavioral patterns for MSME directors.
        Same logic as consumer pipeline.
        """
        try:
            if transactions.empty or 'date' not in transactions.columns:
                return {
                    'salary_retention_ratio': 0.5,
                    'week1_vs_week4_spending_ratio': 1.0,
                    'impulse_spending_score': 0.0,
                    'upi_volume_spike_score': 0.0,
                    'avg_balance_drop_rate': 0.5
                }
            
            transactions = transactions.copy()
            transactions['date'] = pd.to_datetime(transactions['date'])
            transactions = transactions.sort_values('date')
            
            features = {}
            transactions['month'] = transactions['date'].dt.to_period('M')
            transactions['day_of_month'] = transactions['date'].dt.day
            
            # Normalize type column
            if 'type' in transactions.columns:
                transactions['type'] = transactions['type'].str.upper()
                transactions['type'] = transactions['type'].replace({
                    'CREDIT': 'CR', 'DEBIT': 'DR', 'CR': 'CR', 'DR': 'DR'
                })
            
            salary_retention_ratios = []
            week1_vs_week4_ratios = []
            
            for month, month_df in transactions.groupby('month'):
                month_credits = month_df[month_df['type'] == 'CR']
                if len(month_credits) == 0:
                    continue
                
                salary_amount = month_credits['amount'].max()
                salary_date = month_credits[month_credits['amount'] == salary_amount]['date'].iloc[0]
                
                week1_end = salary_date + timedelta(days=7)
                week1_spending = month_df[
                    (month_df['date'] > salary_date) &
                    (month_df['date'] <= week1_end) &
                    (month_df['type'] == 'DR')
                ]['amount'].sum()
                
                week4_spending = month_df[
                    (month_df['day_of_month'] >= 22) &
                    (month_df['day_of_month'] <= 31) &
                    (month_df['type'] == 'DR')
                ]['amount'].sum()
                
                if salary_amount > 0:
                    retention = (salary_amount - week1_spending) / salary_amount
                    salary_retention_ratios.append(max(0, min(1, retention)))
                
                if week4_spending > 0 and week1_spending > 0:
                    ratio = week1_spending / week4_spending
                    week1_vs_week4_ratios.append(ratio)
            
            features['salary_retention_ratio'] = float(
                np.mean(salary_retention_ratios) if salary_retention_ratios else 0.5
            )
            features['week1_vs_week4_spending_ratio'] = float(
                np.mean(week1_vs_week4_ratios) if week1_vs_week4_ratios else 1.0
            )
            
            # Impulse spending score
            impulse_indicators = 0.0
            transactions['date_only'] = transactions['date'].dt.date
            debits_by_date = transactions[transactions['type'] == 'DR'].groupby('date_only')['amount'].agg(['count', 'sum'])
            
            if len(debits_by_date) > 0:
                high_frequency_days = (debits_by_date['count'] > 5).sum()
                total_days = len(debits_by_date)
                impulse_indicators += (high_frequency_days / total_days) * 0.3
            
            mean_debit = transactions[transactions['type'] == 'DR']['amount'].mean()
            if mean_debit > 0:
                large_debits = transactions[(transactions['type'] == 'DR') & (transactions['amount'] > mean_debit * 2)]
                large_debit_ratio = len(large_debits) / len(transactions[transactions['type'] == 'DR'])
                impulse_indicators += large_debit_ratio * 0.3
            
            if features['week1_vs_week4_spending_ratio'] > 1.5:
                impulse_indicators += 0.2
            
            features['impulse_spending_score'] = float(min(impulse_indicators, 1.0))
            
            # UPI volume spike
            if 'description' in transactions.columns:
                transactions['is_upi'] = transactions['description'].astype(str).str.contains('UPI|IMPS|NEFT', case=False, na=False)
                transactions['week'] = transactions['date'].dt.isocalendar().week
                upi_weekly = transactions[transactions['is_upi']].groupby('week')['amount'].agg(['sum', 'count'])
                
                if len(upi_weekly) >= 4:
                    upi_amounts = upi_weekly['sum']
                    median_amount = upi_amounts.median()
                    if median_amount > 0:
                        spike_weeks = (upi_amounts > median_amount * 2).sum()
                        spike_ratio = spike_weeks / len(upi_weekly)
                        features['upi_volume_spike_score'] = float(min(spike_ratio * 2, 1.0))
                    else:
                        features['upi_volume_spike_score'] = 0.0
                else:
                    features['upi_volume_spike_score'] = 0.0
            else:
                features['upi_volume_spike_score'] = 0.0
            
            # Balance drop rate
            if 'balance' in transactions.columns:
                major_inflows = transactions[
                    (transactions['type'] == 'CR') & 
                    (transactions['amount'] > monthly_income * 0.5)
                ]
                
                balance_drop_rates = []
                for idx, inflow in major_inflows.iterrows():
                    inflow_date = inflow['date']
                    inflow_balance = inflow['balance']
                    
                    future_txns = transactions[
                        (transactions['date'] > inflow_date) &
                        (transactions['date'] <= inflow_date + timedelta(days=7))
                    ]
                    
                    if len(future_txns) > 0:
                        balance_after_7days = future_txns.iloc[-1]['balance']
                        if inflow_balance > 0:
                            drop_rate = (inflow_balance - balance_after_7days) / inflow_balance
                            balance_drop_rates.append(max(0, min(1, drop_rate)))
                
                if balance_drop_rates:
                    features['avg_balance_drop_rate'] = float(np.mean(balance_drop_rates))
                else:
                    features['avg_balance_drop_rate'] = float(
                        min(monthly_expense / monthly_income, 1.0) if monthly_income > 0 else 0.5
                    )
            else:
                features['avg_balance_drop_rate'] = 0.5
            
            return features
        except Exception as e:
            return {
                'salary_retention_ratio': 0.5,
                'week1_vs_week4_spending_ratio': 1.0,
                'impulse_spending_score': 0.0,
                'upi_volume_spike_score': 0.0,
                'avg_balance_drop_rate': 0.5
            }
    
    def _compute_improved_inflow_consistency(self, transactions: pd.DataFrame, monthly_income: float) -> float:
        """
        Check if salary/income comes on the same date every month.
        Improved version for MSME directors.
        """
        try:
            if transactions.empty or 'date' not in transactions.columns:
                return 0.0
            
            transactions = transactions.copy()
            transactions['date'] = pd.to_datetime(transactions['date'])
            transactions['month'] = transactions['date'].dt.to_period('M')
            transactions['day_of_month'] = transactions['date'].dt.day
            
            if 'type' in transactions.columns:
                transactions['type'] = transactions['type'].str.upper()
            
            salary_dates = []
            
            for month, month_df in transactions.groupby('month'):
                month_credits = month_df[month_df['type'] == 'CR']
                if len(month_credits) == 0:
                    continue
                
                largest_credit = month_credits['amount'].max()
                if largest_credit >= monthly_income * 0.3:
                    salary_day = month_credits[month_credits['amount'] == largest_credit]['day_of_month'].iloc[0]
                    salary_dates.append(salary_day)
            
            if len(salary_dates) < 2:
                return 0.0
            
            date_std = np.std(salary_dates)
            
            if date_std <= 2:
                consistency = 1.0
            elif date_std >= 5:
                consistency = 0.0
            else:
                consistency = 1.0 - ((date_std - 2) / 3)
            
            return float(consistency)
        except Exception:
            return 0.0
    
    def _detect_manipulation_patterns(self, transactions: pd.DataFrame) -> Dict[str, float]:
        """
        Detect manipulation patterns: circular transactions, P2P manipulation, balance manipulation.
        """
        try:
            if transactions.empty:
                return {'total_risk': 0.0, 'circular_risk': 0.0, 'p2p_risk': 0.0, 'balance_risk': 0.0}
            
            transactions = transactions.copy()
            if 'date' not in transactions.columns:
                return {'total_risk': 0.0, 'circular_risk': 0.0, 'p2p_risk': 0.0, 'balance_risk': 0.0}
            
            transactions['date'] = pd.to_datetime(transactions['date'])
            transactions = transactions.sort_values('date')
            
            if 'type' in transactions.columns:
                transactions['type'] = transactions['type'].str.upper()
            
            total_risk = 0.0
            
            # Circular transaction detection
            circular_risk = self._detect_circular_transactions(transactions)
            total_risk += circular_risk
            
            # P2P manipulation
            p2p_risk = self._detect_p2p_manipulation(transactions)
            total_risk += p2p_risk
            
            # Balance manipulation
            balance_risk = self._detect_balance_manipulation(transactions)
            total_risk += balance_risk
            
            return {
                'total_risk': min(total_risk, 1.0),
                'circular_risk': circular_risk,
                'p2p_risk': p2p_risk,
                'balance_risk': balance_risk
            }
        except Exception:
            return {'total_risk': 0.0, 'circular_risk': 0.0, 'p2p_risk': 0.0, 'balance_risk': 0.0}
    
    def _detect_circular_transactions(self, df: pd.DataFrame) -> float:
        """Detect circular transactions (first 7 vs last 7 days)"""
        try:
            if len(df) < 14:
                return 0.0
            
            dates = df['date'].dt.date.unique()
            if len(dates) < 14:
                return 0.0
            
            first_7_dates = dates[:7]
            last_7_dates = dates[-7:]
            
            first_7_txns = df[df['date'].dt.date.isin(first_7_dates)]
            last_7_txns = df[df['date'].dt.date.isin(last_7_dates)]
            
            first_credits = first_7_txns[first_7_txns['type'] == 'CR']['amount'].sum()
            first_debits = first_7_txns[first_7_txns['type'] == 'DR']['amount'].sum()
            last_credits = last_7_txns[last_7_txns['type'] == 'CR']['amount'].sum()
            last_debits = last_7_txns[last_7_txns['type'] == 'DR']['amount'].sum()
            
            if first_credits == 0 or last_credits == 0:
                return 0.0
            
            credit_ratio = min(first_credits, last_credits) / max(first_credits, last_credits)
            debit_ratio = min(first_debits, last_debits) / max(first_debits, last_debits) if first_debits > 0 and last_debits > 0 else 0
            
            if credit_ratio > 0.90 and debit_ratio > 0.90:
                first_net = abs(first_credits - first_debits)
                last_net = abs(last_credits - last_debits)
                
                first_net_ratio = first_net / first_credits if first_credits > 0 else 1.0
                last_net_ratio = last_net / last_credits if last_credits > 0 else 1.0
                
                if first_net_ratio < 0.10 and last_net_ratio < 0.10:
                    return 0.3
            
            return 0.0
        except Exception:
            return 0.0
    
    def _detect_p2p_manipulation(self, df: pd.DataFrame) -> float:
        """Detect regular P2P to same person"""
        try:
            if len(df) < 10 or 'description' not in df.columns:
                return 0.0
            
            credits = df[df['type'] == 'CR'].copy()
            if len(credits) < 5:
                return 0.0
            
            upi_pattern = 'UPI|IMPS|NEFT'
            p2p_credits = credits[
                credits['description'].astype(str).str.contains(upi_pattern, case=False, regex=True, na=False)
            ]
            
            if len(p2p_credits) < 3:
                return 0.0
            
            p2p_credits['desc_clean'] = p2p_credits['description'].astype(str).str.lower().str.strip()
            desc_counts = p2p_credits['desc_clean'].value_counts()
            
            if len(desc_counts) > 0:
                max_repeat = desc_counts.iloc[0]
                total_p2p = len(p2p_credits)
                
                if max_repeat > total_p2p * 0.4 and max_repeat >= 5:
                    most_common_desc = desc_counts.index[0]
                    same_source = p2p_credits[p2p_credits['desc_clean'] == most_common_desc]
                    
                    amount_std = same_source['amount'].std()
                    amount_mean = same_source['amount'].mean()
                    
                    if amount_mean > 0:
                        cv = amount_std / amount_mean
                        if cv < 0.15:
                            return 0.2
                        elif cv < 0.30:
                            return 0.1
            
            return 0.0
        except Exception:
            return 0.0
    
    def _detect_balance_manipulation(self, df: pd.DataFrame) -> float:
        """Detect balance manipulation indicators"""
        try:
            if len(df) < 10 or 'balance' not in df.columns:
                return 0.0
            
            df = df.sort_values('date')
            risk = 0.0
            
            for i in range(len(df) - 1):
                if df.iloc[i]['type'] == 'CR' and df.iloc[i+1]['type'] == 'DR':
                    credit_amt = df.iloc[i]['amount']
                    debit_amt = df.iloc[i+1]['amount']
                    
                    if credit_amt > 50000 and abs(credit_amt - debit_amt) / credit_amt < 0.10:
                        time_diff = (df.iloc[i+1]['date'] - df.iloc[i]['date']).days
                        if time_diff <= 2:
                            risk += 0.05
                            if risk >= 0.15:
                                break
            
            last_7_days = df.tail(min(30, len(df)))
            last_7_avg_balance = last_7_days['balance'].mean()
            overall_avg_balance = df['balance'].mean()
            
            if overall_avg_balance > 0:
                ratio = last_7_avg_balance / overall_avg_balance
                if ratio > 2.0:
                    risk += 0.05
            
            return min(risk, 0.2)
        except Exception:
            return 0.0
    
    def _score_behavioral_signals(self, income_volatility: float, 
                                  savings_consistency: float, 
                                  late_night_count: int) -> float:
        """Score behavioral health (0-1)"""
        # Income volatility (lower is better)
        volatility_score = max(0, 1 - (income_volatility / 100))
        
        # Savings consistency (higher is better)
        # Already 0-1
        
        # Late night transactions (penalize excessive)
        late_night_score = max(0, 1 - (late_night_count / 20))
        
        return (volatility_score * 0.4 + savings_consistency * 0.5 + late_night_score * 0.1)
    
    def _empty_behavioral_signals(self) -> Dict:
        """Return empty behavioral signals"""
        return {
            'regular_p2p_transactions': False,
            'monthly_income': 0,
            'monthly_inflow': 0,
            'monthly_outflow': 0,
            'income_volatility': 0,
            'subscriptions': [],
            'micro_commitments': [],
            'late_night_transactions_count': 0,
            'savings_consistency_score': 0.5,
            'score': 0
        }

