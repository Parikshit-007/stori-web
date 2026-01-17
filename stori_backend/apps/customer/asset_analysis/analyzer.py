"""
Asset Analysis for Account Aggregator Data
Analyzes assets from AA JSON to calculate highest quantified amount and features
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Asset liquidity constants (days to convert to cash)
LIQUIDITY_SCORING = {
    'STOCKS': 1,           # T+2 settlement
    'MUTUAL_FUNDS': 3,     # 3-4 days redemption
    'LIQUID_FUNDS': 1,     # Same day/next day
    'GOLD_DIGITAL': 2,     # 2-3 days
    'GOLD_ETF': 2,         # 2-3 days
    'BANK_FD': 7,          # Immediate but with penalty
    'CORPORATE_FD': 14,    # 1-2 weeks
    'PPF': 365,            # Lock-in, partial withdrawal after 7 years
    'EPF': 60,             # 2 months notice for withdrawal
    'VPF': 60,             # 2 months notice
    'REAL_ESTATE': 180,    # 6 months minimum to sell
    'INSURANCE': 90,       # 3 months surrender process
    'GOLD_PHYSICAL': 3,    # 3-5 days to sell
    'BONDS': 7,            # Listed bonds
    'NPS': 1825,           # Lock-in till retirement
    'CRYPTO': 1            # Instant (but high volatility)
}

# Assets to exclude from survivability calculation
EXCLUDE_FROM_SURVIVABILITY = ['PPF', 'EPF', 'VPF', 'NPS', 'BONDS']


class AssetAnalyzer:
    """Analyze assets from Account Aggregator JSON data"""
    
    def __init__(self):
        self.assets = []
        
    def load_from_aa_json(self, aa_data: Dict) -> None:
        """
        Load assets from Account Aggregator JSON format
        
        Args:
            aa_data: AA JSON containing all asset types
        """
        # Check if this is SEBI format (has FIPS array)
        if 'FIPS' in aa_data and isinstance(aa_data.get('FIPS'), list):
            self._load_from_sebi_format(aa_data)
            return
        
        # Standard AA format
        # 1. Stocks & Equity (Demat holdings)
        if 'demat' in aa_data or 'stocks' in aa_data:
            self._load_stocks(aa_data.get('demat') or aa_data.get('stocks', {}))
        
        # 2. Mutual Funds (CAMS statements)
        if 'mutual_funds' in aa_data or 'cams' in aa_data:
            self._load_mutual_funds(aa_data.get('mutual_funds') or aa_data.get('cams', {}))
        
        # 3. Fixed Deposits
        if 'fixed_deposits' in aa_data or 'fds' in aa_data:
            self._load_fixed_deposits(aa_data.get('fixed_deposits') or aa_data.get('fds', {}))
        
        # 4. Gold (Digital, ETF only - not physical)
        if 'gold' in aa_data:
            self._load_gold(aa_data.get('gold', {}))
        
        # 5. Real Estate (manual input field)
        if 'real_estate' in aa_data or 'properties' in aa_data:
            self._load_real_estate(aa_data.get('real_estate') or aa_data.get('properties', {}))
        
        # 6. Insurance (LIC, ULIPs)
        if 'insurance' in aa_data:
            self._load_insurance(aa_data.get('insurance', {}))
        
        # 7. Provident Fund (EPF, PPF, VPF)
        if 'provident_fund' in aa_data or 'pf' in aa_data:
            self._load_provident_fund(aa_data.get('provident_fund') or aa_data.get('pf', {}))
        
        # 8. Other Investments (Bonds, NPS, Crypto)
        if 'other_investments' in aa_data:
            self._load_other_investments(aa_data.get('other_investments', {}))
    
    def _load_from_sebi_format(self, sebi_data: Dict) -> None:
        """
        Load assets from SEBI format (FIPS array structure)
        
        SEBI format:
        {
            "FIPS": [
                {
                    "source_of_fip": "CAMSRTAFIP" | "kfinmf-fip" | "CDSLFIP",
                    "accounts": [
                        {
                            "investment_details": {
                                "mutualfunds": {...},
                                "equities": {...},
                                "etf": {...}
                            }
                        }
                    ]
                }
            ]
        }
        """
        fips = sebi_data.get('FIPS', [])
        
        for fip in fips:
            source = fip.get('source_of_fip', '').upper()
            accounts = fip.get('accounts', [])
            
            for account in accounts:
                investment_details = account.get('investment_details', {})
                
                # Process mutual funds (from CAMS/kfin)
                if 'mutualfunds' in investment_details:
                    mf_data = investment_details.get('mutualfunds', {})
                    if mf_data and mf_data.get('holdings'):
                        self._load_mutual_funds_sebi(mf_data, source)
                
                # Process equities/stocks (from CDSL)
                if 'equities' in investment_details:
                    equities_data = investment_details.get('equities', {})
                    if equities_data and equities_data.get('holdings'):
                        self._load_stocks_sebi(equities_data)
                
                # Process ETF (if present)
                if 'etf' in investment_details:
                    etf_data = investment_details.get('etf', {})
                    if etf_data and etf_data.get('holdings'):
                        self._load_etf_sebi(etf_data)
    
    def _load_mutual_funds_sebi(self, mf_data: Dict, source: str) -> None:
        """Load mutual funds from SEBI format"""
        holdings = mf_data.get('holdings', [])
        amc = mf_data.get('amc', '')
        folio_number = mf_data.get('masked_folio_number', '')
        
        for holding in holdings:
            try:
                current_value = float(holding.get('current_value', 0))
                invested_value = float(holding.get('total invested', holding.get('total_invested', 0)))
                units = float(holding.get('qty', 0))
                isin_id = holding.get('isin_id', '')
                isin_description = holding.get('isinDescription', '')
                
                # Skip if no value
                if current_value == 0 and invested_value == 0:
                    continue
                
                # Use invested value if current value is 0
                if current_value == 0:
                    current_value = invested_value
                
                asset = {
                    'type': 'MUTUAL_FUNDS',
                    'subtype': self._classify_mf_type(isin_description or ''),
                    'name': isin_description or f'MF {isin_id}',
                    'units': units,
                    'current_value': current_value,
                    'invested_value': invested_value if invested_value > 0 else current_value,
                    'amc': amc,
                    'folio_number': folio_number,
                    'isin_id': isin_id
                }
                
                if asset['invested_value'] > 0:
                    asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                          / asset['invested_value'] * 100)
                else:
                    asset['returns_pct'] = 0.0
                
                self.assets.append(asset)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error loading SEBI MF holding: {e}")
                continue
    
    def _load_stocks_sebi(self, equities_data: Dict) -> None:
        """Load stocks/equities from SEBI format (CDSL)"""
        holdings = equities_data.get('holdings', [])
        
        for holding in holdings:
            try:
                qty = float(holding.get('qty', 0))
                current_rate = float(holding.get('current_rate', 0))
                rate = float(holding.get('Rate', 0))  # Average price
                total_invested = float(holding.get('total_invested', 0))
                current_value = float(holding.get('current_value', 0))
                isin_description = holding.get('isinDescription', '')
                isin_id = holding.get('isin_id', '')
                
                # Calculate current value if not provided
                if current_value == 0 and current_rate > 0 and qty > 0:
                    current_value = qty * current_rate
                
                # Use invested value if current value is 0
                if current_value == 0:
                    current_value = total_invested
                
                # Skip if no value
                if current_value == 0:
                    continue
                
                asset = {
                    'type': 'STOCKS',
                    'subtype': 'NSE',  # Default, can be enhanced
                    'name': isin_description or f'Stock {isin_id}',
                    'symbol': isin_id,
                    'quantity': qty,
                    'current_value': current_value,
                    'invested_value': total_invested if total_invested > 0 else current_value,
                    'ltp': current_rate if current_rate > 0 else rate,
                    'avg_price': rate
                }
                
                if asset['invested_value'] > 0:
                    asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                          / asset['invested_value'] * 100)
                else:
                    asset['returns_pct'] = 0.0
                
                self.assets.append(asset)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error loading SEBI equity holding: {e}")
                continue
    
    def _load_etf_sebi(self, etf_data: Dict) -> None:
        """Load ETF from SEBI format"""
        holdings = etf_data.get('holdings', [])
        
        for holding in holdings:
            try:
                current_value = float(holding.get('current_value', 0))
                invested_value = float(holding.get('total_invested', 0))
                units = float(holding.get('qty', 0))
                isin_description = holding.get('isinDescription', '')
                isin_id = holding.get('isin_id', '')
                
                # Skip if no value
                if current_value == 0 and invested_value == 0:
                    continue
                
                if current_value == 0:
                    current_value = invested_value
                
                # Check if it's Gold ETF
                if 'GOLD' in (isin_description or '').upper() or 'GOLD' in (isin_id or '').upper():
                    asset = {
                        'type': 'GOLD',
                        'subtype': 'ETF',
                        'name': isin_description or f'Gold ETF {isin_id}',
                        'units': units,
                        'current_value': current_value,
                        'invested_value': invested_value if invested_value > 0 else current_value
                    }
                else:
                    # Regular ETF - treat as mutual fund
                    asset = {
                        'type': 'MUTUAL_FUNDS',
                        'subtype': 'ETF',
                        'name': isin_description or f'ETF {isin_id}',
                        'units': units,
                        'current_value': current_value,
                        'invested_value': invested_value if invested_value > 0 else current_value
                    }
                
                if asset['invested_value'] > 0:
                    asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                          / asset['invested_value'] * 100)
                else:
                    asset['returns_pct'] = 0.0
                
                self.assets.append(asset)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error loading SEBI ETF holding: {e}")
                continue
    
    def _load_stocks(self, stocks_data: Union[Dict, List]) -> None:
        """Load stocks from demat holdings"""
        if isinstance(stocks_data, dict):
            holdings = stocks_data.get('holdings', [])
        else:
            holdings = stocks_data if isinstance(stocks_data, list) else []
        
        for holding in holdings:
            try:
                current_value = float(holding.get('currentValue', holding.get('current_value', 0)))
                quantity = float(holding.get('quantity', 0))
                
                asset = {
                    'type': 'STOCKS',
                    'subtype': holding.get('exchange', 'NSE'),
                    'name': holding.get('companyName', holding.get('company_name', 'Unknown')),
                    'symbol': holding.get('symbol', ''),
                    'quantity': quantity,
                    'current_value': current_value,
                    'invested_value': float(holding.get('investedValue', holding.get('invested_value', current_value))),
                    'ltp': float(holding.get('ltp', holding.get('lastTradedPrice', 0)))
                }
                
                if asset['invested_value'] > 0:
                    asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                          / asset['invested_value'] * 100)
                else:
                    asset['returns_pct'] = 0.0
                
                self.assets.append(asset)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error loading stock holding: {e}")
                continue
    
    def _load_mutual_funds(self, mf_data: Union[Dict, List]) -> None:
        """Load mutual funds from CAMS format"""
        if isinstance(mf_data, dict):
            folios = mf_data.get('folios', [])
        else:
            folios = mf_data if isinstance(mf_data, list) else []
        
        for folio in folios:
            schemes = folio.get('schemes', [])
            for scheme in schemes:
                try:
                    current_value = float(scheme.get('currentValue', scheme.get('current_value', 0)))
                    units = float(scheme.get('units', 0))
                    
                    asset = {
                        'type': 'MUTUAL_FUNDS',
                        'subtype': self._classify_mf_type(scheme.get('schemeName', scheme.get('scheme_name', ''))),
                        'name': scheme.get('schemeName', scheme.get('scheme_name', 'Unknown Fund')),
                        'units': units,
                        'current_value': current_value,
                        'invested_value': float(scheme.get('investedValue', scheme.get('invested_value', current_value))),
                        'amc': folio.get('amc', 'Unknown'),
                        'folio_number': folio.get('folioNumber', folio.get('folio_number', ''))
                    }
                    
                    if asset['invested_value'] > 0:
                        asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                              / asset['invested_value'] * 100)
                    else:
                        asset['returns_pct'] = 0.0
                    
                    self.assets.append(asset)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Error loading MF scheme: {e}")
                    continue
    
    def _load_fixed_deposits(self, fd_data: Union[Dict, List]) -> None:
        """Load fixed deposits"""
        if isinstance(fd_data, dict):
            fds = fd_data.get('fixed_deposits', fd_data.get('fds', []))
        else:
            fds = fd_data if isinstance(fd_data, list) else []
        
        for fd in fds:
            try:
                fd_type = fd.get('type', 'BANK_FD')  # BANK_FD or CORPORATE_FD
                maturity_amount = float(fd.get('maturityAmount', fd.get('maturity_amount', 0)))
                principal = float(fd.get('principal', 0))
                
                asset = {
                    'type': 'FIXED_DEPOSIT',
                    'subtype': fd_type,
                    'name': f"{fd.get('bank', 'Unknown')} FD",
                    'principal': principal,
                    'current_value': maturity_amount,
                    'invested_value': principal,
                    'interest_rate': float(fd.get('interestRate', fd.get('interest_rate', 0))),
                    'maturity_date': fd.get('maturityDate', fd.get('maturity_date'))
                }
                
                if asset['invested_value'] > 0:
                    asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                          / asset['invested_value'] * 100)
                else:
                    asset['returns_pct'] = 0.0
                
                self.assets.append(asset)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error loading FD: {e}")
                continue
    
    def _load_gold(self, gold_data: Union[Dict, List]) -> None:
        """Load gold holdings (only Digital and ETF, not physical)"""
        if isinstance(gold_data, dict):
            holdings = gold_data.get('holdings', gold_data.get('gold_holdings', []))
        else:
            holdings = gold_data if isinstance(gold_data, list) else []
        
        for holding in holdings:
            try:
                gold_type = holding.get('type', 'PHYSICAL').upper()
                # Only process DIGITAL, ETF, SGB - skip PHYSICAL
                if gold_type in ['PHYSICAL', 'GOLD_PHYSICAL']:
                    continue
                
                current_value = float(holding.get('currentValue', holding.get('current_value', 0)))
                
                asset = {
                    'type': 'GOLD',
                    'subtype': gold_type,  # DIGITAL, ETF, SGB
                    'name': holding.get('name', 'Gold'),
                    'units': float(holding.get('units', 0)),
                    'weight_grams': float(holding.get('weightGrams', holding.get('weight_grams', 0))),
                    'current_value': current_value,
                    'invested_value': float(holding.get('investedValue', holding.get('invested_value', current_value))),
                    'current_price': float(holding.get('currentPrice', holding.get('current_price', 0)))
                }
                
                if asset['invested_value'] > 0:
                    asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                          / asset['invested_value'] * 100)
                else:
                    asset['returns_pct'] = 0.0
                
                self.assets.append(asset)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error loading gold holding: {e}")
                continue
    
    def _load_real_estate(self, property_data: Union[Dict, List]) -> None:
        """Load real estate (manual input field)"""
        if isinstance(property_data, dict):
            properties = property_data.get('properties', [])
        else:
            properties = property_data if isinstance(property_data, list) else []
        
        for prop in properties:
            try:
                current_value = float(prop.get('currentValue', prop.get('current_value', 0)))
                outstanding_loan = float(prop.get('outstandingLoan', prop.get('outstanding_loan', 0)))
                
                asset = {
                    'type': 'REAL_ESTATE',
                    'subtype': prop.get('type', 'RESIDENTIAL'),
                    'name': f"{prop.get('type', 'Property')} - {prop.get('location', 'Unknown')}",
                    'location': prop.get('location', ''),
                    'current_value': current_value,
                    'invested_value': float(prop.get('purchasePrice', prop.get('purchase_price', current_value))),
                    'outstanding_loan': outstanding_loan,
                    'net_value': current_value - outstanding_loan
                }
                
                if asset['invested_value'] > 0:
                    asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                          / asset['invested_value'] * 100)
                else:
                    asset['returns_pct'] = 0.0
                
                self.assets.append(asset)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error loading property: {e}")
                continue
    
    def _load_insurance(self, insurance_data: Union[Dict, List]) -> None:
        """Load insurance policies (LIC, ULIPs with maturity value)"""
        if isinstance(insurance_data, dict):
            policies = insurance_data.get('policies', [])
        else:
            policies = insurance_data if isinstance(insurance_data, list) else []
        
        for policy in policies:
            try:
                # Only consider policies with investment value
                if not policy.get('hasInvestmentValue', policy.get('has_investment_value', False)):
                    continue
                
                surrender_value = float(policy.get('surrenderValue', policy.get('surrender_value', 0)))
                total_premium = float(policy.get('totalPremiumPaid', policy.get('total_premium_paid', 0)))
                
                asset = {
                    'type': 'INSURANCE',
                    'subtype': policy.get('type', 'LIC'),
                    'name': policy.get('policyName', policy.get('policy_name', 'Insurance Policy')),
                    'policy_number': policy.get('policyNumber', policy.get('policy_number', '')),
                    'current_value': surrender_value,
                    'invested_value': total_premium,
                    'maturity_value': float(policy.get('maturityValue', policy.get('maturity_value', 0))),
                    'maturity_date': policy.get('maturityDate', policy.get('maturity_date')),
                    'due_date': policy.get('dueDate', policy.get('due_date')),  # For future use
                    'late_payment': policy.get('latePayment', policy.get('late_payment', False))  # For future use
                }
                
                if asset['invested_value'] > 0:
                    asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                          / asset['invested_value'] * 100)
                else:
                    asset['returns_pct'] = 0.0
                
                self.assets.append(asset)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error loading insurance policy: {e}")
                continue
    
    def _load_provident_fund(self, pf_data: Union[Dict, List]) -> None:
        """Load Provident Fund (EPF, PPF, VPF) - excluded from survivability"""
        if isinstance(pf_data, dict):
            pf_accounts = pf_data.get('pf_accounts', pf_data.get('accounts', []))
        else:
            pf_accounts = pf_data if isinstance(pf_data, list) else []
        
        for pf in pf_accounts:
            try:
                pf_type = pf.get('type', 'EPF').upper()
                current_balance = float(pf.get('currentBalance', pf.get('current_balance', 0)))
                total_contribution = float(pf.get('totalContribution', pf.get('total_contribution', current_balance)))
                
                asset = {
                    'type': 'PROVIDENT_FUND',
                    'subtype': pf_type,  # EPF, PPF, VPF
                    'name': f"{pf_type} Account",
                    'account_number': pf.get('accountNumber', pf.get('account_number', '')),
                    'current_value': current_balance,
                    'invested_value': total_contribution,
                    'employee_contribution': float(pf.get('employeeContribution', pf.get('employee_contribution', 0))),
                    'employer_contribution': float(pf.get('employerContribution', pf.get('employer_contribution', 0)))
                }
                
                if asset['invested_value'] > 0:
                    asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                          / asset['invested_value'] * 100)
                else:
                    asset['returns_pct'] = 0.0
                
                self.assets.append(asset)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error loading PF account: {e}")
                continue
    
    def _load_other_investments(self, other_data: Union[Dict, List]) -> None:
        """Load other investments (Bonds, NPS, Crypto) - exclude NPS and Bonds from survivability"""
        if isinstance(other_data, dict):
            investments = other_data.get('investments', [])
        else:
            investments = other_data if isinstance(other_data, list) else []
        
        for inv in investments:
            try:
                inv_type = inv.get('type', '').upper()
                current_value = float(inv.get('currentValue', inv.get('current_value', 0)))
                
                # Map to asset types
                if inv_type in ['BOND', 'BONDS']:
                    asset_type = 'BONDS'
                elif inv_type == 'NPS':
                    asset_type = 'NPS'
                elif inv_type in ['CRYPTO', 'CRYPTOCURRENCY']:
                    asset_type = 'CRYPTO'
                else:
                    asset_type = 'OTHER'
                
                asset = {
                    'type': asset_type,
                    'subtype': inv_type,
                    'name': inv.get('name', f'{asset_type} Investment'),
                    'current_value': current_value,
                    'invested_value': float(inv.get('investedValue', inv.get('invested_value', current_value)))
                }
                
                if asset['invested_value'] > 0:
                    asset['returns_pct'] = ((asset['current_value'] - asset['invested_value']) 
                                          / asset['invested_value'] * 100)
                else:
                    asset['returns_pct'] = 0.0
                
                self.assets.append(asset)
            except (ValueError, TypeError) as e:
                logger.warning(f"Error loading other investment: {e}")
                continue
    
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
    
    def calculate_analysis(self) -> Dict:
        """
        Calculate comprehensive asset analysis
        
        Returns:
            Dict with analysis including highest quantified amount
        """
        if len(self.assets) == 0:
            return self._get_default_analysis()
        
        df = pd.DataFrame(self.assets)
        
        # Calculate total values
        total_value = float(df['current_value'].sum())
        total_invested = float(df['invested_value'].sum())
        
        # Find highest quantified amount (quantity/value)
        highest_asset = None
        highest_value = 0.0
        
        for asset in self.assets:
            value = asset.get('current_value', 0)
            # Also check quantity for stocks
            if asset.get('type') == 'STOCKS':
                quantity = asset.get('quantity', 0)
                ltp = asset.get('ltp', 0)
                if quantity > 0 and ltp > 0:
                    value = quantity * ltp
            
            if value > highest_value:
                highest_value = value
                highest_asset = asset
        
        # Calculate survivability assets (exclude PF, NPS, Bonds)
        survivability_assets = [
            a for a in self.assets 
            if a.get('subtype', a.get('type', '')) not in EXCLUDE_FROM_SURVIVABILITY
        ]
        survivability_value = sum(a.get('current_value', 0) for a in survivability_assets)
        
        # Liquidity analysis
        liquid_value = 0.0
        semi_liquid_value = 0.0
        illiquid_value = 0.0
        
        for asset in self.assets:
            asset_type = asset.get('subtype', asset.get('type', 'UNKNOWN'))
            liquidity_days = LIQUIDITY_SCORING.get(asset_type, 30)
            value = asset.get('current_value', 0)
            
            if liquidity_days <= 7:
                liquid_value += value
            elif liquidity_days <= 90:
                semi_liquid_value += value
            else:
                illiquid_value += value
        
        # Asset breakdown by type
        asset_breakdown = df.groupby('type')['current_value'].sum().to_dict()
        
        # Portfolio returns
        portfolio_returns = 0.0
        if total_invested > 0:
            portfolio_returns = ((total_value - total_invested) / total_invested) * 100
        
        # Build analysis result
        analysis = {
            'total_asset_value': float(total_value),
            'total_invested_value': float(total_invested),
            'survivability_asset_value': float(survivability_value),
            'portfolio_returns_pct': float(portfolio_returns),
            'num_assets': len(self.assets),
            'num_asset_types': int(df['type'].nunique()),
            
            # Highest quantified amount
            'highest_quantified_amount': {
                'value': float(highest_value) if highest_asset else 0.0,
                'asset_type': highest_asset.get('type') if highest_asset else None,
                'asset_name': highest_asset.get('name') if highest_asset else None,
                'subtype': highest_asset.get('subtype') if highest_asset else None
            },
            
            # Liquidity breakdown
            'liquid_assets': float(liquid_value),
            'semi_liquid_assets': float(semi_liquid_value),
            'illiquid_assets': float(illiquid_value),
            'liquidity_ratio': float(liquid_value / total_value) if total_value > 0 else 0.0,
            
            # Asset type breakdown
            'stocks_value': float(asset_breakdown.get('STOCKS', 0)),
            'mutual_funds_value': float(asset_breakdown.get('MUTUAL_FUNDS', 0)),
            'fixed_deposits_value': float(asset_breakdown.get('FIXED_DEPOSIT', 0)),
            'gold_value': float(asset_breakdown.get('GOLD', 0)),
            'real_estate_value': float(asset_breakdown.get('REAL_ESTATE', 0)),
            'insurance_value': float(asset_breakdown.get('INSURANCE', 0)),
            'provident_fund_value': float(asset_breakdown.get('PROVIDENT_FUND', 0)),
            'bonds_value': float(asset_breakdown.get('BONDS', 0)),
            'nps_value': float(asset_breakdown.get('NPS', 0)),
            'crypto_value': float(asset_breakdown.get('CRYPTO', 0)),
            
            # Detailed asset list
            'assets': self.assets
        }
        
        return analysis
    
    def _get_default_analysis(self) -> Dict:
        """Return default analysis when no assets"""
        return {
            'total_asset_value': 0.0,
            'total_invested_value': 0.0,
            'survivability_asset_value': 0.0,
            'portfolio_returns_pct': 0.0,
            'num_assets': 0,
            'num_asset_types': 0,
            'highest_quantified_amount': {
                'value': 0.0,
                'asset_type': None,
                'asset_name': None,
                'subtype': None
            },
            'liquid_assets': 0.0,
            'semi_liquid_assets': 0.0,
            'illiquid_assets': 0.0,
            'liquidity_ratio': 0.0,
            'stocks_value': 0.0,
            'mutual_funds_value': 0.0,
            'fixed_deposits_value': 0.0,
            'gold_value': 0.0,
            'real_estate_value': 0.0,
            'insurance_value': 0.0,
            'provident_fund_value': 0.0,
            'bonds_value': 0.0,
            'nps_value': 0.0,
            'crypto_value': 0.0,
            'assets': []
        }

