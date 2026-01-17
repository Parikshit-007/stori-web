"""
Asset Analysis Module for Credit Underwriting
==============================================
Analyzes all consumer assets to determine financial strength and collateral capacity

Supported Asset Types:
1. Stocks & Equity (Demat account holdings)
2. Mutual Funds (SIP, Lumpsum investments)
3. Fixed Deposits (Bank FDs, Corporate FDs)
4. Gold (Physical gold, Digital gold, Gold ETF, Sovereign Gold Bonds)
5. Real Estate (Owned property, invested property)
6. Insurance (LIC, ULIPs with maturity value)
7. Provident Fund (EPF, PPF, VPF)
8. Other Investments (Bonds, NPS, cryptocurrency, etc.)

Author: Credit Risk Engineering
Version: 1.0 - Production Grade
Date: 13-Jan-2026
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime, timedelta
import warnings

# Asset liquidity constants (days to convert to cash)
LIQUIDITY_SCORING = {
    'STOCKS': 1,           # T+2 settlement
    'MUTUAL_FUNDS': 3,     # 3-4 days redemption
    'LIQUID_FUNDS': 1,     # Same day/next day
    'GOLD_DIGITAL': 2,     # 2-3 days
    'BANK_FD': 7,          # Immediate but with penalty
    'CORPORATE_FD': 14,    # 1-2 weeks
    'PPF': 365,            # Lock-in, partial withdrawal after 7 years
    'EPF': 60,             # 2 months notice for withdrawal
    'REAL_ESTATE': 180,    # 6 months minimum to sell
    'INSURANCE': 90,       # 3 months surrender process
    'GOLD_PHYSICAL': 3,    # 3-5 days to sell
    'BONDS': 7,            # Listed bonds
    'NPS': 1825,           # Lock-in till retirement
    'CRYPTO': 1            # Instant (but high volatility)
}

# Asset risk scoring (0-1, higher = riskier)
RISK_SCORING = {
    'BANK_FD': 0.1,
    'PPF': 0.1,
    'EPF': 0.1,
    'CORPORATE_FD': 0.3,
    'GOLD_PHYSICAL': 0.4,
    'GOLD_DIGITAL': 0.4,
    'LIQUID_FUNDS': 0.2,
    'DEBT_FUNDS': 0.3,
    'HYBRID_FUNDS': 0.5,
    'EQUITY_FUNDS': 0.7,
    'STOCKS': 0.8,
    'REAL_ESTATE': 0.5,
    'INSURANCE': 0.3,
    'BONDS': 0.4,
    'NPS': 0.5,
    'CRYPTO': 0.95
}


class AssetAnalyzer:
    """
    Production-grade asset analyzer for credit underwriting
    Handles multiple data sources and formats
    """
    
    def __init__(self):
        self.assets = []
        self.total_value = 0.0
        self.liquid_assets = 0.0
        self.illiquid_assets = 0.0
        
    def load_from_cams(self, cams_json: Union[str, Dict]) -> None:
        """
        Load mutual fund holdings from CAMS (Computer Age Management Services)
        This is the standard format from Account Aggregator for MF data
        
        Args:
            cams_json: Path to CAMS JSON or dict
        """
        if isinstance(cams_json, str):
            with open(cams_json, 'r') as f:
                data = json.load(f)
        else:
            data = cams_json
        
        # Parse CAMS format
        folios = data.get('folios', [])
        
        for folio in folios:
            schemes = folio.get('schemes', [])
            for scheme in schemes:
                asset = {
                    'type': 'MUTUAL_FUNDS',
                    'subtype': self._classify_mf_type(scheme.get('schemeName', '')),
                    'name': scheme.get('schemeName', 'Unknown Fund'),
                    'units': float(scheme.get('units', 0)),
                    'current_value': float(scheme.get('currentValue', 0)),
                    'invested_value': float(scheme.get('investedValue', 0)),
                    'purchase_date': scheme.get('purchaseDate'),
                    'amc': folio.get('amc', 'Unknown'),
                    'folio_number': folio.get('folioNumber', '')
                }
                
                # Calculate returns
                if asset['invested_value'] > 0:
                    asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                           / asset['invested_value'] * 100)
                else:
                    asset['returns_pct'] = 0.0
                
                self.assets.append(asset)
    
    def load_from_demat(self, demat_json: Union[str, Dict]) -> None:
        """
        Load stock holdings from Demat account (CDSL/NSDL format)
        Standard format from Account Aggregator or broker APIs
        
        Args:
            demat_json: Path to demat holdings JSON or dict
        """
        if isinstance(demat_json, str):
            with open(demat_json, 'r') as f:
                data = json.load(f)
        else:
            data = demat_json
        
        holdings = data.get('holdings', [])
        
        for holding in holdings:
            asset = {
                'type': 'STOCKS',
                'subtype': holding.get('exchange', 'NSE'),
                'name': holding.get('companyName', 'Unknown'),
                'symbol': holding.get('symbol', ''),
                'quantity': float(holding.get('quantity', 0)),
                'avg_price': float(holding.get('avgPrice', 0)),
                'ltp': float(holding.get('ltp', 0)),  # Last traded price
                'current_value': float(holding.get('currentValue', 0)),
                'invested_value': float(holding.get('investedValue', 0))
            }
            
            # Calculate returns
            if asset['invested_value'] > 0:
                asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                       / asset['invested_value'] * 100)
            else:
                asset['returns_pct'] = 0.0
            
            self.assets.append(asset)
    
    def load_from_fd_statement(self, fd_json: Union[str, Dict]) -> None:
        """
        Load Fixed Deposit details from bank statements or FD certificates
        
        Args:
            fd_json: Path to FD details JSON or dict
        """
        if isinstance(fd_json, str):
            with open(fd_json, 'r') as f:
                data = json.load(f)
        else:
            data = fd_json
        
        fds = data.get('fixed_deposits', [])
        
        for fd in fds:
            asset = {
                'type': 'FIXED_DEPOSIT',
                'subtype': fd.get('type', 'BANK_FD'),  # BANK_FD or CORPORATE_FD
                'name': f"{fd.get('bank', 'Unknown')} FD",
                'principal': float(fd.get('principal', 0)),
                'interest_rate': float(fd.get('interestRate', 0)),
                'tenure_months': int(fd.get('tenureMonths', 0)),
                'start_date': fd.get('startDate'),
                'maturity_date': fd.get('maturityDate'),
                'maturity_amount': float(fd.get('maturityAmount', 0)),
                'current_value': float(fd.get('maturityAmount', 0)),  # Use maturity as current
                'invested_value': float(fd.get('principal', 0))
            }
            
            # Calculate effective returns
            if asset['invested_value'] > 0:
                asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                       / asset['invested_value'] * 100)
            else:
                asset['returns_pct'] = 0.0
            
            self.assets.append(asset)
    
    def load_gold_holdings(self, gold_json: Union[str, Dict]) -> None:
        """
        Load gold holdings (physical, digital gold, gold ETF, SGB)
        
        Args:
            gold_json: Path to gold holdings JSON or dict
        """
        if isinstance(gold_json, str):
            with open(gold_json, 'r') as f:
                data = json.load(f)
        else:
            data = gold_json
        
        holdings = data.get('gold_holdings', [])
        
        for holding in holdings:
            asset = {
                'type': 'GOLD',
                'subtype': holding.get('type', 'PHYSICAL'),  # PHYSICAL, DIGITAL, ETF, SGB
                'name': holding.get('name', 'Gold'),
                'weight_grams': float(holding.get('weightGrams', 0)),
                'units': float(holding.get('units', 0)),  # For ETF/SGB
                'purchase_price': float(holding.get('purchasePrice', 0)),
                'current_price': float(holding.get('currentPrice', 0)),
                'current_value': float(holding.get('currentValue', 0)),
                'invested_value': float(holding.get('investedValue', 0)),
                'purchase_date': holding.get('purchaseDate')
            }
            
            # Calculate returns
            if asset['invested_value'] > 0:
                asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                       / asset['invested_value'] * 100)
            else:
                asset['returns_pct'] = 0.0
            
            self.assets.append(asset)
    
    def load_real_estate(self, property_json: Union[str, Dict]) -> None:
        """
        Load real estate holdings (owned/invested properties)
        
        Args:
            property_json: Path to property details JSON or dict
        """
        if isinstance(property_json, str):
            with open(property_json, 'r') as f:
                data = json.load(f)
        else:
            data = property_json
        
        properties = data.get('properties', [])
        
        for prop in properties:
            asset = {
                'type': 'REAL_ESTATE',
                'subtype': prop.get('type', 'RESIDENTIAL'),  # RESIDENTIAL, COMMERCIAL, LAND
                'name': f"{prop.get('type', 'Property')} - {prop.get('location', 'Unknown')}",
                'location': prop.get('location', ''),
                'size_sqft': float(prop.get('sizeSqft', 0)),
                'purchase_price': float(prop.get('purchasePrice', 0)),
                'current_value': float(prop.get('currentValue', 0)),
                'invested_value': float(prop.get('purchasePrice', 0)),
                'purchase_date': prop.get('purchaseDate'),
                'has_loan': prop.get('hasLoan', False),
                'outstanding_loan': float(prop.get('outstandingLoan', 0))
            }
            
            # Calculate returns (property appreciation)
            if asset['invested_value'] > 0:
                asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                       / asset['invested_value'] * 100)
            else:
                asset['returns_pct'] = 0.0
            
            # Net value after loan
            asset['net_value'] = asset['current_value'] - asset['outstanding_loan']
            
            self.assets.append(asset)
    
    def load_insurance_policies(self, insurance_json: Union[str, Dict]) -> None:
        """
        Load insurance policies (LIC, ULIPs with investment component)
        
        Args:
            insurance_json: Path to insurance details JSON or dict
        """
        if isinstance(insurance_json, str):
            with open(insurance_json, 'r') as f:
                data = json.load(f)
        else:
            data = insurance_json
        
        policies = data.get('policies', [])
        
        for policy in policies:
            # Only consider policies with investment value (exclude term insurance)
            if policy.get('hasInvestmentValue', False):
                asset = {
                    'type': 'INSURANCE',
                    'subtype': policy.get('type', 'LIC'),  # LIC, ULIP, ENDOWMENT
                    'name': policy.get('policyName', 'Insurance Policy'),
                    'policy_number': policy.get('policyNumber', ''),
                    'sum_assured': float(policy.get('sumAssured', 0)),
                    'maturity_value': float(policy.get('maturityValue', 0)),
                    'surrender_value': float(policy.get('surrenderValue', 0)),
                    'current_value': float(policy.get('surrenderValue', 0)),  # Use surrender value
                    'invested_value': float(policy.get('totalPremiumPaid', 0)),
                    'start_date': policy.get('startDate'),
                    'maturity_date': policy.get('maturityDate')
                }
                
                # Calculate returns
                if asset['invested_value'] > 0:
                    asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                           / asset['invested_value'] * 100)
                else:
                    asset['returns_pct'] = 0.0
                
                self.assets.append(asset)
    
    def load_pf_holdings(self, pf_json: Union[str, Dict]) -> None:
        """
        Load Provident Fund holdings (EPF, PPF, VPF)
        
        Args:
            pf_json: Path to PF details JSON or dict
        """
        if isinstance(pf_json, str):
            with open(pf_json, 'r') as f:
                data = json.load(f)
        else:
            data = pf_json
        
        pf_accounts = data.get('pf_accounts', [])
        
        for pf in pf_accounts:
            asset = {
                'type': 'PROVIDENT_FUND',
                'subtype': pf.get('type', 'EPF'),  # EPF, PPF, VPF
                'name': f"{pf.get('type', 'PF')} Account",
                'account_number': pf.get('accountNumber', ''),
                'employee_contribution': float(pf.get('employeeContribution', 0)),
                'employer_contribution': float(pf.get('employerContribution', 0)),
                'interest_earned': float(pf.get('interestEarned', 0)),
                'current_value': float(pf.get('currentBalance', 0)),
                'invested_value': float(pf.get('totalContribution', 0)),
                'start_date': pf.get('startDate')
            }
            
            # Calculate returns
            if asset['invested_value'] > 0:
                asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                       / asset['invested_value'] * 100)
            else:
                asset['returns_pct'] = 0.0
            
            self.assets.append(asset)
    
    def add_manual_asset(self, asset_type: str, name: str, current_value: float, 
                        invested_value: float = None, **kwargs) -> None:
        """
        Add asset manually (for assets not from structured data sources)
        
        Args:
            asset_type: Type of asset (STOCKS, GOLD, etc.)
            name: Asset name
            current_value: Current market value
            invested_value: Original investment (optional)
            **kwargs: Additional asset-specific fields
        """
        asset = {
            'type': asset_type,
            'name': name,
            'current_value': float(current_value),
            'invested_value': float(invested_value) if invested_value else float(current_value),
            **kwargs
        }
        
        # Calculate returns if invested value provided
        if asset['invested_value'] > 0:
            asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                   / asset['invested_value'] * 100)
        else:
            asset['returns_pct'] = 0.0
        
        self.assets.append(asset)
    
    def calculate_asset_features(self) -> Dict[str, float]:
        """
        Calculate comprehensive asset-based features for ML model
        
        Returns:
            Dict with stable feature names for credit scoring
        """
        if len(self.assets) == 0:
            return self._get_default_features()
        
        features = {}
        
        # Convert to DataFrame for easier calculation
        df = pd.DataFrame(self.assets)
        
        # 1. Total asset value
        features['total_asset_value'] = float(df['current_value'].sum())
        features['total_invested_value'] = float(df['invested_value'].sum())
        
        # 2. Asset diversification (number of asset types)
        features['num_asset_types'] = int(df['type'].nunique())
        features['num_assets'] = len(df)
        
        # 3. Liquidity analysis
        liquid_assets = []
        semi_liquid_assets = []
        illiquid_assets = []
        
        for _, asset in df.iterrows():
            asset_type = asset.get('subtype', asset.get('type', 'UNKNOWN'))
            liquidity_days = LIQUIDITY_SCORING.get(asset_type, 30)
            value = asset['current_value']
            
            if liquidity_days <= 7:
                liquid_assets.append(value)
            elif liquidity_days <= 90:
                semi_liquid_assets.append(value)
            else:
                illiquid_assets.append(value)
        
        features['liquid_assets'] = float(sum(liquid_assets))
        features['semi_liquid_assets'] = float(sum(semi_liquid_assets))
        features['illiquid_assets'] = float(sum(illiquid_assets))
        
        # Liquidity ratio (higher = more liquid)
        total_assets = features['total_asset_value']
        if total_assets > 0:
            features['liquidity_ratio'] = features['liquid_assets'] / total_assets
        else:
            features['liquidity_ratio'] = 0.0
        
        # 4. Portfolio returns
        if features['total_invested_value'] > 0:
            features['portfolio_returns_pct'] = (
                (features['total_asset_value'] - features['total_invested_value']) 
                / features['total_invested_value'] * 100
            )
        else:
            features['portfolio_returns_pct'] = 0.0
        
        # 5. Asset-specific breakdowns
        asset_breakdown = df.groupby('type')['current_value'].sum()
        
        features['stocks_value'] = float(asset_breakdown.get('STOCKS', 0))
        features['mf_value'] = float(asset_breakdown.get('MUTUAL_FUNDS', 0))
        features['fd_value'] = float(asset_breakdown.get('FIXED_DEPOSIT', 0))
        features['gold_value'] = float(asset_breakdown.get('GOLD', 0))
        features['real_estate_value'] = float(asset_breakdown.get('REAL_ESTATE', 0))
        features['pf_value'] = float(asset_breakdown.get('PROVIDENT_FUND', 0))
        features['insurance_value'] = float(asset_breakdown.get('INSURANCE', 0))
        
        # 6. Risk profile (weighted average risk score)
        total_risk_weighted = 0.0
        for _, asset in df.iterrows():
            asset_type = asset.get('subtype', asset.get('type', 'UNKNOWN'))
            risk_score = RISK_SCORING.get(asset_type, 0.5)
            total_risk_weighted += asset['current_value'] * risk_score
        
        if total_assets > 0:
            features['portfolio_risk_score'] = total_risk_weighted / total_assets
        else:
            features['portfolio_risk_score'] = 0.5
        
        # 7. Gold as % of assets (important for Indian market)
        if total_assets > 0:
            features['gold_to_assets_pct'] = (features['gold_value'] / total_assets) * 100
        else:
            features['gold_to_assets_pct'] = 0.0
        
        # 8. Real estate as % of assets
        if total_assets > 0:
            features['real_estate_to_assets_pct'] = (features['real_estate_value'] / total_assets) * 100
        else:
            features['real_estate_to_assets_pct'] = 0.0
        
        # 9. Safe assets (FD + PF + Insurance)
        safe_assets = features['fd_value'] + features['pf_value'] + features['insurance_value']
        if total_assets > 0:
            features['safe_assets_pct'] = (safe_assets / total_assets) * 100
        else:
            features['safe_assets_pct'] = 0.0
        
        # 10. Market-linked assets (Stocks + MF)
        market_assets = features['stocks_value'] + features['mf_value']
        if total_assets > 0:
            features['market_linked_pct'] = (market_assets / total_assets) * 100
        else:
            features['market_linked_pct'] = 0.0
        
        # Sanitize all values
        for key in features:
            features[key] = self._safe_float(features[key])
        
        return features
    
    def get_asset_summary(self) -> pd.DataFrame:
        """
        Get detailed summary of all assets
        
        Returns:
            DataFrame with asset details
        """
        if len(self.assets) == 0:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.assets)
        
        # Add liquidity and risk scores
        df['liquidity_days'] = df.apply(
            lambda row: LIQUIDITY_SCORING.get(row.get('subtype', row['type']), 30),
            axis=1
        )
        df['risk_score'] = df.apply(
            lambda row: RISK_SCORING.get(row.get('subtype', row['type']), 0.5),
            axis=1
        )
        
        return df
    
    def _classify_mf_type(self, scheme_name: str) -> str:
        """Classify mutual fund into equity/debt/hybrid/liquid"""
        scheme_name = scheme_name.upper()
        
        if any(x in scheme_name for x in ['LIQUID', 'OVERNIGHT', 'ULTRA SHORT']):
            return 'LIQUID_FUNDS'
        elif any(x in scheme_name for x in ['DEBT', 'BOND', 'INCOME', 'GILT']):
            return 'DEBT_FUNDS'
        elif any(x in scheme_name for x in ['EQUITY', 'LARGE CAP', 'MID CAP', 'SMALL CAP', 
                                             'FLEXI', 'MULTI CAP', 'INDEX']):
            return 'EQUITY_FUNDS'
        elif any(x in scheme_name for x in ['HYBRID', 'BALANCED', 'AGGRESSIVE']):
            return 'HYBRID_FUNDS'
        else:
            return 'EQUITY_FUNDS'  # Default
    
    def _get_default_features(self) -> Dict[str, float]:
        """Return default values when no assets"""
        return {
            'total_asset_value': 0.0,
            'total_invested_value': 0.0,
            'num_asset_types': 0,
            'num_assets': 0,
            'liquid_assets': 0.0,
            'semi_liquid_assets': 0.0,
            'illiquid_assets': 0.0,
            'liquidity_ratio': 0.0,
            'portfolio_returns_pct': 0.0,
            'stocks_value': 0.0,
            'mf_value': 0.0,
            'fd_value': 0.0,
            'gold_value': 0.0,
            'real_estate_value': 0.0,
            'pf_value': 0.0,
            'insurance_value': 0.0,
            'portfolio_risk_score': 0.5,
            'gold_to_assets_pct': 0.0,
            'real_estate_to_assets_pct': 0.0,
            'safe_assets_pct': 0.0,
            'market_linked_pct': 0.0
        }
    
    def _safe_float(self, value: Union[float, int, np.number], default: float = 0.0) -> float:
        """Convert to safe float, handling NaN/Inf"""
        try:
            f = float(value)
            if np.isnan(f) or np.isinf(f):
                return default
            return f
        except (TypeError, ValueError):
            return default


# =========================================================
# MAIN ANALYSIS FUNCTION
# =========================================================

def analyze_consumer_assets(
    cams_path: Optional[str] = None,
    demat_path: Optional[str] = None,
    fd_path: Optional[str] = None,
    gold_path: Optional[str] = None,
    property_path: Optional[str] = None,
    insurance_path: Optional[str] = None,
    pf_path: Optional[str] = None,
    manual_assets: Optional[List[Dict]] = None,
    export_path: Optional[str] = None
) -> Dict[str, float]:
    """
    Complete asset analysis from multiple sources
    
    Args:
        cams_path: Path to CAMS mutual fund statement JSON
        demat_path: Path to Demat holdings JSON
        fd_path: Path to FD details JSON
        gold_path: Path to gold holdings JSON
        property_path: Path to property details JSON
        insurance_path: Path to insurance policies JSON
        pf_path: Path to PF details JSON
        manual_assets: List of manually added assets
        export_path: Path to export feature CSV
    
    Returns:
        Dict with 21 asset features for ML model
    """
    analyzer = AssetAnalyzer()
    
    # Load from various sources
    if cams_path and Path(cams_path).exists():
        analyzer.load_from_cams(cams_path)
    
    if demat_path and Path(demat_path).exists():
        analyzer.load_from_demat(demat_path)
    
    if fd_path and Path(fd_path).exists():
        analyzer.load_from_fd_statement(fd_path)
    
    if gold_path and Path(gold_path).exists():
        analyzer.load_gold_holdings(gold_path)
    
    if property_path and Path(property_path).exists():
        analyzer.load_real_estate(property_path)
    
    if insurance_path and Path(insurance_path).exists():
        analyzer.load_insurance_policies(insurance_path)
    
    if pf_path and Path(pf_path).exists():
        analyzer.load_pf_holdings(pf_path)
    
    # Add manual assets
    if manual_assets:
        for asset in manual_assets:
            analyzer.add_manual_asset(**asset)
    
    # Calculate features
    features = analyzer.calculate_asset_features()
    
    # Export if requested
    if export_path:
        df = pd.DataFrame([features])
        df.to_csv(export_path, index=False)
        print(f"Asset features exported to: {export_path}")
    
    # Print summary
    print("\n" + "="*80)
    print("ASSET ANALYSIS SUMMARY")
    print("="*80)
    print(f"\nTotal Assets: Rs {features['total_asset_value']:,.2f}")
    print(f"Liquid Assets: Rs {features['liquid_assets']:,.2f} ({features['liquidity_ratio']*100:.1f}%)")
    print(f"Number of Assets: {features['num_assets']}")
    print(f"Portfolio Returns: {features['portfolio_returns_pct']:.2f}%")
    print(f"\nAsset Breakdown:")
    print(f"  Stocks: Rs {features['stocks_value']:,.2f}")
    print(f"  Mutual Funds: Rs {features['mf_value']:,.2f}")
    print(f"  Fixed Deposits: Rs {features['fd_value']:,.2f}")
    print(f"  Gold: Rs {features['gold_value']:,.2f}")
    print(f"  Real Estate: Rs {features['real_estate_value']:,.2f}")
    print(f"  Provident Fund: Rs {features['pf_value']:,.2f}")
    print(f"  Insurance: Rs {features['insurance_value']:,.2f}")
    print("\n" + "="*80)
    
    return features


# =========================================================
# CLI INTERFACE
# =========================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze consumer assets for credit underwriting')
    parser.add_argument('--cams', help='Path to CAMS MF statement JSON')
    parser.add_argument('--demat', help='Path to Demat holdings JSON')
    parser.add_argument('--fd', help='Path to FD details JSON')
    parser.add_argument('--gold', help='Path to gold holdings JSON')
    parser.add_argument('--property', help='Path to property details JSON')
    parser.add_argument('--insurance', help='Path to insurance policies JSON')
    parser.add_argument('--pf', help='Path to PF details JSON')
    parser.add_argument('--export', help='Export features to CSV')
    
    args = parser.parse_args()
    
    features = analyze_consumer_assets(
        cams_path=args.cams,
        demat_path=args.demat,
        fd_path=args.fd,
        gold_path=args.gold,
        property_path=args.property,
        insurance_path=args.insurance,
        pf_path=args.pf,
        export_path=args.export
    )
    
    print("\nFeatures ready for ML model!")

