"""
Production-grade Transaction Classifier for Indian Banking
Designed for accurate income/expense categorization in credit underwriting

Author: Credit Risk Engineering
Version: 2.0 - JSON-based keyword management for easy team collaboration
"""

import re
import json
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple


class MerchantDatabase:
    """
    Merchant keyword database for India
    Loads from merchant_keywords.json for easy non-technical team updates
    """
    
    def __init__(self, json_path: str = None):
        """Load keywords from JSON file"""
        if json_path is None:
            json_path = Path(__file__).parent / "merchant_keywords.json"
        
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Load all categories
            self.EXCLUDE_FROM_INCOME = data.get("EXCLUDE_FROM_INCOME", {}).get("keywords", [])
            self.SALARY_KEYWORDS = data.get("SALARY_INCOME", {}).get("keywords", [])
            self.ELECTRICITY_PROVIDERS = data.get("ELECTRICITY", {}).get("keywords", [])
            self.WATER_PROVIDERS = data.get("WATER", {}).get("keywords", [])
            self.GAS_PROVIDERS = data.get("GAS", {}).get("keywords", [])
            self.TELECOM_PROVIDERS = data.get("TELECOM", {}).get("keywords", [])
            self.FOOD_DELIVERY = data.get("FOOD_DELIVERY", {}).get("keywords", [])
            self.RESTAURANTS_QSR = data.get("RESTAURANTS_QSR", {}).get("keywords", [])
            self.GROCERIES_SUPERMARKETS = data.get("GROCERIES", {}).get("keywords", [])
            self.TRANSPORT_PUBLIC = data.get("TRANSPORT_PUBLIC", {}).get("keywords", [])
            self.TRANSPORT_CABS = data.get("TRANSPORT_CAB", {}).get("keywords", [])
            self.FUEL_STATIONS = data.get("FUEL", {}).get("keywords", [])
            self.ECOMMERCE = data.get("ECOMMERCE", {}).get("keywords", [])
            self.FASHION_RETAIL = data.get("FASHION_RETAIL", {}).get("keywords", [])
            self.ELECTRONICS_RETAIL = data.get("ELECTRONICS", {}).get("keywords", [])
            self.PHARMACIES = data.get("PHARMACY", {}).get("keywords", [])
            self.HOSPITALS_DIAGNOSTICS = data.get("HOSPITAL", {}).get("keywords", [])
            self.OTT_STREAMING = data.get("OTT_STREAMING", {}).get("keywords", [])
            self.MUSIC_STREAMING = data.get("MUSIC_STREAMING", {}).get("keywords", [])
            self.CINEMA_TICKETING = data.get("CINEMA", {}).get("keywords", [])
            self.GAMING = data.get("GAMING", {}).get("keywords", [])
            self.EDUCATION = data.get("EDUCATION", {}).get("keywords", [])
            self.INSURANCE = data.get("INSURANCE", {}).get("keywords", [])
            self.INVESTMENT_PLATFORMS = data.get("INVESTMENT", {}).get("keywords", [])
            self.CREDIT_CARDS_LOAN_PAYMENTS = data.get("CREDIT_CARD_LOAN", {}).get("keywords", [])
            self.REFUND_PATTERNS = data.get("REFUND", {}).get("keywords", [])
            
            print(f"[OK] Loaded {len(data)} merchant categories from JSON")
            
        except FileNotFoundError:
            print(f"Warning: {json_path} not found. Using minimal fallback keywords.")
            self._load_fallback()
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}. Using fallback keywords.")
            self._load_fallback()
    
    def _load_fallback(self):
        """Minimal fallback if JSON not available"""
        self.EXCLUDE_FROM_INCOME = ['CLEARING CORPORATION', 'DIVIDEND', 'TAX REFUND']
        self.SALARY_KEYWORDS = ['SALARY', 'PAYROLL']
        self.ELECTRICITY_PROVIDERS = ['ELECTRICITY', 'POWER']
        self.WATER_PROVIDERS = ['WATER']
        self.GAS_PROVIDERS = ['GAS']
        self.TELECOM_PROVIDERS = ['AIRTEL', 'JIO']
        self.FOOD_DELIVERY = ['ZOMATO', 'SWIGGY']
        self.RESTAURANTS_QSR = ['MCDONALD', 'KFC']
        self.GROCERIES_SUPERMARKETS = ['DMART']
        self.TRANSPORT_PUBLIC = ['METRO']
        self.TRANSPORT_CABS = ['UBER', 'OLA']
        self.FUEL_STATIONS = ['PETROL']
        self.ECOMMERCE = ['AMAZON', 'FLIPKART']
        self.FASHION_RETAIL = ['WESTSIDE']
        self.ELECTRONICS_RETAIL = ['CROMA']
        self.PHARMACIES = ['PHARMACY']
        self.HOSPITALS_DIAGNOSTICS = ['HOSPITAL']
        self.OTT_STREAMING = ['NETFLIX']
        self.MUSIC_STREAMING = ['SPOTIFY']
        self.CINEMA_TICKETING = ['PVR']
        self.GAMING = ['DREAM11']
        self.EDUCATION = ['BYJU']
        self.INSURANCE = ['LIC']
        self.INVESTMENT_PLATFORMS = ['ZERODHA']
        self.CREDIT_CARDS_LOAN_PAYMENTS = ['CRED']
        self.REFUND_PATTERNS = ['^REV-', 'REFUND']


class TransactionClassifier:
    """Enterprise-grade transaction classifier"""
    
    def __init__(self, merchant_db: MerchantDatabase = None):
        self.db = merchant_db if merchant_db else MerchantDatabase()
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Pre-compile regex for performance"""
        self.patterns = {
            'exclude': self._build_regex(self.db.EXCLUDE_FROM_INCOME),
            'salary': self._build_regex(self.db.SALARY_KEYWORDS),
            'electricity': self._build_regex(self.db.ELECTRICITY_PROVIDERS),
            'water': self._build_regex(self.db.WATER_PROVIDERS),
            'gas': self._build_regex(self.db.GAS_PROVIDERS),
            'telecom': self._build_regex(self.db.TELECOM_PROVIDERS),
            'food_delivery': self._build_regex(self.db.FOOD_DELIVERY),
            'restaurant': self._build_regex(self.db.RESTAURANTS_QSR),
            'groceries': self._build_regex(self.db.GROCERIES_SUPERMARKETS),
            'transport_public': self._build_regex(self.db.TRANSPORT_PUBLIC),
            'transport_cab': self._build_regex(self.db.TRANSPORT_CABS),
            'fuel': self._build_regex(self.db.FUEL_STATIONS),
            'ecommerce': self._build_regex(self.db.ECOMMERCE),
            'fashion': self._build_regex(self.db.FASHION_RETAIL),
            'electronics': self._build_regex(self.db.ELECTRONICS_RETAIL),
            'pharmacy': self._build_regex(self.db.PHARMACIES),
            'hospital': self._build_regex(self.db.HOSPITALS_DIAGNOSTICS),
            'ott': self._build_regex(self.db.OTT_STREAMING),
            'music': self._build_regex(self.db.MUSIC_STREAMING),
            'cinema': self._build_regex(self.db.CINEMA_TICKETING),
            'gaming': self._build_regex(self.db.GAMING),
            'education': self._build_regex(self.db.EDUCATION),
            'insurance': self._build_regex(self.db.INSURANCE),
            'investment': self._build_regex(self.db.INVESTMENT_PLATFORMS),
            'credit_card': self._build_regex(self.db.CREDIT_CARDS_LOAN_PAYMENTS),
            'refund': self._build_regex(self.db.REFUND_PATTERNS),
        }
        
        # P2P detection
        self.p2p_pattern = re.compile(
            r'UPI-.*@(?:OKHDFCBANK|OKICICI|OKAXIS|OKSBI|OKPAYTM|YBL|PAYTM)'
            r'|UPI-\d{10}@'
            r'|UPI-[A-Z\s]+(PAREKH|SHAH|PATEL|KUMAR|SINGH|YADAV|GUPTA|JOSHI|MEHTA|AGARWAL|REDDY)',
            re.IGNORECASE
        )
    
    def _build_regex(self, keywords: list) -> re.Pattern:
        """Build optimized regex from keyword list"""
        if not keywords:
            return re.compile('(?!.*)')  # Never match
        pattern = '|'.join(re.escape(k) if not any(c in k for c in r'.*+?[]{}()^$|\\') else k for k in keywords)
        return re.compile(pattern, re.IGNORECASE)
    
    def classify(self, description: str, amount: float, txn_type: str) -> Tuple[str, str, bool, bool]:
        """
        Classify transaction
        Returns: (category, subcategory, is_income, is_expense)
        """
        desc = str(description).upper() if description and not pd.isna(description) else ""
        
        # Refunds first
        if self.patterns['refund'].search(desc):
            return ('REFUND', 'REVERSAL', False, False)
        
        # CREDIT transactions
        if txn_type == 'CR':
            # Check exclusions FIRST - trading, dividends, refunds etc
            if self.patterns['exclude'].search(desc):
                return ('EXCLUDED', 'NON_INCOME', False, False)
            
            if self.patterns['salary'].search(desc):
                # Exclude very large one-time payments (> 75k) as they're likely bonuses/settlements
                if amount > 75000:
                    return ('EXCLUDED', 'LARGE_ONE_TIME', False, False)
                return ('INCOME', 'SALARY', True, False)
            if self.p2p_pattern.search(desc):
                return ('P2P', 'TRANSFER_IN', False, False)
            if self.patterns['investment'].search(desc):
                return ('INVESTMENT', 'RETURN', False, False)
            return ('OTHER', 'UNKNOWN_CREDIT', False, False)
        
        # DEBIT transactions
        if self.p2p_pattern.search(desc):
            return ('P2P', 'TRANSFER_OUT', False, False)
        
        # Utilities
        if self.patterns['electricity'].search(desc):
            return ('UTILITY', 'ELECTRICITY', False, True)
        if self.patterns['water'].search(desc):
            return ('UTILITY', 'WATER', False, True)
        if self.patterns['gas'].search(desc):
            return ('UTILITY', 'GAS', False, True)
        if self.patterns['telecom'].search(desc):
            return ('UTILITY', 'TELECOM', False, True)
        
        # Food
        if self.patterns['food_delivery'].search(desc):
            return ('FOOD', 'DELIVERY', False, True)
        if self.patterns['restaurant'].search(desc):
            return ('FOOD', 'RESTAURANT', False, True)
        if self.patterns['groceries'].search(desc):
            return ('FOOD', 'GROCERIES', False, True)
        
        # Transport
        if self.patterns['transport_public'].search(desc):
            return ('TRANSPORT', 'PUBLIC', False, True)
        if self.patterns['transport_cab'].search(desc):
            return ('TRANSPORT', 'CAB', False, True)
        if self.patterns['fuel'].search(desc):
            return ('TRANSPORT', 'FUEL', False, True)
        
        # Shopping
        if self.patterns['ecommerce'].search(desc):
            return ('SHOPPING', 'ECOMMERCE', False, True)
        if self.patterns['fashion'].search(desc):
            return ('SHOPPING', 'FASHION', False, True)
        if self.patterns['electronics'].search(desc):
            return ('SHOPPING', 'ELECTRONICS', False, True)
        
        # Healthcare
        if self.patterns['pharmacy'].search(desc):
            return ('HEALTHCARE', 'PHARMACY', False, True)
        if self.patterns['hospital'].search(desc):
            return ('HEALTHCARE', 'HOSPITAL', False, True)
        
        # Entertainment
        if self.patterns['ott'].search(desc):
            return ('ENTERTAINMENT', 'OTT', False, True)
        if self.patterns['music'].search(desc):
            return ('ENTERTAINMENT', 'MUSIC', False, True)
        if self.patterns['cinema'].search(desc):
            return ('ENTERTAINMENT', 'CINEMA', False, True)
        if self.patterns['gaming'].search(desc):
            return ('ENTERTAINMENT', 'GAMING', False, True)
        
        # Education
        if self.patterns['education'].search(desc):
            return ('EDUCATION', 'COURSE', False, True)
        
        # Financial (not expense)
        if self.patterns['insurance'].search(desc):
            return ('FINANCIAL', 'INSURANCE', False, False)
        if self.patterns['investment'].search(desc):
            return ('FINANCIAL', 'INVESTMENT', False, False)
        if self.patterns['credit_card'].search(desc):
            return ('FINANCIAL', 'CREDIT_CARD', False, False)
        
        return ('EXPENSE', 'OTHER', False, True)
    
    def process_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add classification columns"""
        desc_col = 'description' if 'description' in df.columns else 'narration'
        
        results = df.apply(
            lambda row: self.classify(row[desc_col], row['amount'], row['type']),
            axis=1
        )
        
        df['category'] = results.apply(lambda x: x[0])
        df['subcategory'] = results.apply(lambda x: x[1])
        df['is_income'] = results.apply(lambda x: x[2])
        df['is_expense'] = results.apply(lambda x: x[3])
        
        return df


def calculate_accurate_cashflow(df: pd.DataFrame) -> Tuple[Dict[str, float], pd.DataFrame]:
    """
    Calculate accurate income/expense excluding P2P and noise
    Returns: (metrics_dict, classified_dataframe)
    """
    classifier = TransactionClassifier()
    df_classified = classifier.process_dataframe(df.copy())
    
    # Calculate months
    df_classified['txn_date'] = pd.to_datetime(df_classified['txn_date'], errors='coerce')
    date_range = (df_classified['txn_date'].max() - df_classified['txn_date'].min()).days
    months = max(date_range / 30.44, 1)
    
    # TRUE INCOME
    income_txns = df_classified[df_classified['is_income'] == True]
    monthly_income = income_txns['amount'].sum() / months
    
    # TRUE EXPENSES
    expense_txns = df_classified[df_classified['is_expense'] == True]
    monthly_expense = expense_txns['amount'].sum() / months
    
    result = {
        'monthly_income': monthly_income,
        'monthly_expense': monthly_expense,
        'total_months': months,
        'salary_income': df_classified[df_classified['subcategory'] == 'SALARY']['amount'].sum() / months,
        'utility_expense': df_classified[df_classified['category'] == 'UTILITY']['amount'].sum() / months,
        'food_expense': df_classified[df_classified['category'] == 'FOOD']['amount'].sum() / months,
        'transport_expense': df_classified[df_classified['category'] == 'TRANSPORT']['amount'].sum() / months,
        'shopping_expense': df_classified[df_classified['category'] == 'SHOPPING']['amount'].sum() / months,
        'healthcare_expense': df_classified[df_classified['category'] == 'HEALTHCARE']['amount'].sum() / months,
        'entertainment_expense': df_classified[df_classified['category'] == 'ENTERTAINMENT']['amount'].sum() / months,
        'education_expense': df_classified[df_classified['category'] == 'EDUCATION']['amount'].sum() / months,
        'p2p_inflow': df_classified[
            (df_classified['category'] == 'P2P') & (df_classified['subcategory'] == 'TRANSFER_IN')
        ]['amount'].sum() / months,
        'p2p_outflow': df_classified[
            (df_classified['category'] == 'P2P') & (df_classified['subcategory'] == 'TRANSFER_OUT')
        ]['amount'].sum() / months,
        'income_txn_count': len(income_txns),
        'expense_txn_count': len(expense_txns),
        'p2p_txn_count': len(df_classified[df_classified['category'] == 'P2P']),
        'refund_txn_count': len(df_classified[df_classified['category'] == 'REFUND']),
    }
    
    return result, df_classified
