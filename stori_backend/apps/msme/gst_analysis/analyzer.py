"""
GST Analyzer
============

Comprehensive GST analysis logic including:
- Filing regularity
- Revenue validation
- Compliance checks
- Vendor analysis
- Risk assessment
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
import statistics


class GSTAnalyzer:
    """
    Main GST Analyzer class
    """
    
    def __init__(self):
        self.risk_flags = []
    
    def analyze_gst_complete(self, input_data: Dict) -> Dict:
        """
        Complete GST analysis
        
        Args:
            input_data: Dictionary containing:
                - gstin: GST number
                - return_type: GSTR-1, GSTR-3B, etc.
                - return_period: MM-YYYY
                - gst_data: Complete GST return data
                - itr_data (optional): ITR data for cross-check
                - platform_sales_data (optional): Platform sales
                - filing_history (optional): Historical filings
        
        Returns:
            Complete analysis results dictionary
        """
        try:
            gstin = input_data['gstin']
            gst_data = input_data['gst_data']
            return_period = input_data['return_period']
            
            # Initialize results
            results = {
                'gstin': gstin,
                'return_period': return_period,
                'analysis_date': datetime.now().isoformat()
            }
            
            # A) Filing regularity
            results['filing_discipline'] = self.analyze_filing_regularity(
                input_data.get('filing_history', []),
                gstin
            )
            
            # B) Revenue analysis
            results['revenue_analysis'] = self.analyze_revenue(gst_data)
            
            # C) Tax compliance
            results['tax_compliance'] = self.analyze_tax_compliance(gst_data)
            
            # D) Mismatch checks
            results['mismatch_checks'] = self.analyze_mismatches(
                gst_data,
                input_data.get('itr_data'),
                input_data.get('platform_sales_data')
            )
            
            # E) Input Tax Credit analysis
            results['itc_analysis'] = self.analyze_itc(gst_data)
            
            # F) Vendor analysis
            results['vendor_analysis'] = self.analyze_vendors(gst_data)
            
            # G) Industry benchmarks
            results['industry_analysis'] = self.analyze_industry_metrics(gst_data)
            
            # H) Risk assessment
            results['risk_assessment'] = self.assess_risk()
            
            # I) Compliance score
            results['compliance_score'] = self.calculate_compliance_score(results)
            
            # Additional fields
            results['hsn_sac_analysis'] = self.analyze_hsn_sac(gst_data)
            results['geographic_analysis'] = self.analyze_geography(gst_data)
            
            return results
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def analyze_filing_regularity(
        self,
        filing_history: List[Dict],
        gstin: str
    ) -> Dict:
        """
        Analyze GST filing regularity
        
        Returns:
            - gst_filing_regularity: % of on-time filings
            - total_expected_filings
            - actual_filings
            - late_filings
            - missed_filings
        """
        if not filing_history:
            return {
                'gst_filing_regularity': 0.0,
                'total_expected_filings': 12,
                'actual_filings': 0,
                'late_filings': 0,
                'missed_filings': 0,
                'avg_delay_days': 0
            }
        
        total_expected = len(filing_history)
        actual_filed = sum(1 for f in filing_history if f.get('status') in ['filed_on_time', 'filed_late'])
        late_filed = sum(1 for f in filing_history if f.get('status') == 'filed_late')
        missed = sum(1 for f in filing_history if f.get('status') == 'not_filed')
        on_time = actual_filed - late_filed
        
        # Calculate regularity percentage
        regularity = (on_time / total_expected * 100) if total_expected > 0 else 0
        
        # Average delay for late filings
        delays = [f.get('days_delay', 0) for f in filing_history if f.get('days_delay', 0) > 0]
        avg_delay = statistics.mean(delays) if delays else 0
        
        # Risk flag if regularity < 80%
        if regularity < 80:
            self.risk_flags.append({
                'type': 'low_filing_regularity',
                'severity': 'high' if regularity < 60 else 'medium',
                'value': regularity,
                'message': f'GST filing regularity is only {regularity:.1f}%'
            })
        
        return {
            'gst_filing_regularity': round(regularity, 2),
            'total_expected_filings': total_expected,
            'actual_filings': actual_filed,
            'late_filings': late_filed,
            'missed_filings': missed,
            'on_time_filings': on_time,
            'avg_delay_days': round(avg_delay, 1)
        }
    
    def analyze_revenue(self, gst_data: Dict) -> Dict:
        """
        Analyze revenue from GST returns
        
        Returns:
            - monthly_revenue: Dict of monthly revenue
            - total_revenue_fy: Total FY revenue
            - avg_monthly_revenue
            - mom_revenue_growth
            - qoq_revenue_growth
            - revenue_volatility
        """
        # Extract revenue from GST data
        # Format varies by return type (GSTR-1, GSTR-3B)
        
        if 'b2b' in gst_data or 'b2c' in gst_data:
            # GSTR-1 format
            revenue = self._extract_revenue_from_gstr1(gst_data)
        elif 'taxable_turnover' in gst_data:
            # GSTR-3B format
            revenue = self._extract_revenue_from_gstr3b(gst_data)
        else:
            # Generic format
            revenue = self._extract_revenue_generic(gst_data)
        
        # Monthly revenue (last 12 months)
        monthly_revenue = revenue.get('monthly_revenue', {})
        
        if not monthly_revenue:
            return {
                'monthly_revenue': {},
                'total_revenue_fy': 0,
                'avg_monthly_revenue': 0,
                'mom_revenue_growth': 0,
                'qoq_revenue_growth': 0,
                'revenue_volatility': 0
            }
        
        # Calculate totals
        revenue_values = list(monthly_revenue.values())
        total_revenue_fy = sum(revenue_values)
        avg_monthly_revenue = total_revenue_fy / len(revenue_values) if revenue_values else 0
        
        # MoM growth (compare last 2 months)
        mom_growth = 0
        if len(revenue_values) >= 2:
            last_month = revenue_values[-1]
            prev_month = revenue_values[-2]
            if prev_month > 0:
                mom_growth = ((last_month - prev_month) / prev_month) * 100
        
        # QoQ growth (compare last 2 quarters)
        qoq_growth = 0
        if len(revenue_values) >= 6:
            last_quarter = sum(revenue_values[-3:])
            prev_quarter = sum(revenue_values[-6:-3])
            if prev_quarter > 0:
                qoq_growth = ((last_quarter - prev_quarter) / prev_quarter) * 100
        
        # Revenue volatility (coefficient of variation)
        volatility = 0
        if len(revenue_values) >= 3 and avg_monthly_revenue > 0:
            std_dev = statistics.stdev(revenue_values)
            volatility = (std_dev / avg_monthly_revenue) * 100
        
        # Risk flags
        if volatility > 50:
            self.risk_flags.append({
                'type': 'high_revenue_volatility',
                'severity': 'medium',
                'value': volatility,
                'message': f'Revenue volatility is {volatility:.1f}%'
            })
        
        if mom_growth < -20:
            self.risk_flags.append({
                'type': 'declining_revenue',
                'severity': 'high',
                'value': mom_growth,
                'message': f'Revenue declined by {abs(mom_growth):.1f}% last month'
            })
        
        return {
            'monthly_revenue': monthly_revenue,
            'total_revenue_fy': round(total_revenue_fy, 2),
            'avg_monthly_revenue': round(avg_monthly_revenue, 2),
            'mom_revenue_growth': round(mom_growth, 2),
            'qoq_revenue_growth': round(qoq_growth, 2),
            'revenue_volatility': round(volatility, 2)
        }
    
    def analyze_tax_compliance(self, gst_data: Dict) -> Dict:
        """
        Analyze tax payment compliance
        
        Returns:
            - total_gst_liability
            - total_gst_paid
            - outstanding_gst
            - tax_payment_regularity
        """
        # Extract tax data
        liability = gst_data.get('total_tax_liability', 0)
        paid = gst_data.get('total_tax_paid', 0)
        outstanding = liability - paid
        
        # Payment history
        payment_history = gst_data.get('payment_history', [])
        if payment_history:
            on_time_payments = sum(1 for p in payment_history if p.get('on_time', False))
            payment_regularity = on_time_payments / len(payment_history)
        else:
            payment_regularity = 1.0 if outstanding == 0 else 0.5
        
        # Risk flags
        if outstanding > 0:
            outstanding_percentage = (outstanding / liability * 100) if liability > 0 else 0
            if outstanding_percentage > 10:
                self.risk_flags.append({
                    'type': 'outstanding_gst',
                    'severity': 'high' if outstanding_percentage > 20 else 'medium',
                    'value': outstanding,
                    'message': f'Outstanding GST: ₹{outstanding:,.2f} ({outstanding_percentage:.1f}%)'
                })
        
        return {
            'total_gst_liability': round(liability, 2),
            'total_gst_paid': round(paid, 2),
            'outstanding_gst': round(outstanding, 2),
            'tax_payment_regularity': round(payment_regularity, 2)
        }
    
    def analyze_mismatches(
        self,
        gst_data: Dict,
        itr_data: Optional[Dict] = None,
        platform_data: Optional[Dict] = None
    ) -> Dict:
        """
        Check for mismatches between GST, ITR, and platform data
        
        Returns:
            - gst_r1_revenue
            - itr_revenue
            - gst_r1_itr_mismatch
            - platform_sales
            - gst_platform_sales_mismatch
        """
        # GST revenue
        gst_revenue = gst_data.get('total_revenue', 0)
        
        # ITR mismatch
        itr_revenue = 0
        gst_itr_mismatch = 0
        if itr_data:
            itr_revenue = itr_data.get('total_revenue', 0)
            if itr_revenue > 0:
                gst_itr_mismatch = abs(gst_revenue - itr_revenue) / itr_revenue * 100
                
                if gst_itr_mismatch > 5:
                    self.risk_flags.append({
                        'type': 'gst_itr_mismatch',
                        'severity': 'high' if gst_itr_mismatch > 10 else 'medium',
                        'value': gst_itr_mismatch,
                        'message': f'GST-ITR mismatch: {gst_itr_mismatch:.1f}%'
                    })
        
        # Platform sales mismatch
        platform_sales = 0
        gst_platform_mismatch = 0
        if platform_data:
            platform_sales = platform_data.get('total_sales', 0)
            if platform_sales > 0:
                gst_platform_mismatch = abs(gst_revenue - platform_sales) / platform_sales * 100
                
                if gst_platform_mismatch > 10:
                    self.risk_flags.append({
                        'type': 'gst_platform_mismatch',
                        'severity': 'medium',
                        'value': gst_platform_mismatch,
                        'message': f'GST-Platform mismatch: {gst_platform_mismatch:.1f}%'
                    })
        
        return {
            'gst_r1_revenue': round(gst_revenue, 2),
            'itr_revenue': round(itr_revenue, 2),
            'gst_r1_itr_mismatch': round(gst_itr_mismatch, 2),
            'mismatch_flag': gst_itr_mismatch > 5,
            'platform_sales': round(platform_sales, 2),
            'gst_platform_sales_mismatch': round(gst_platform_mismatch, 2)
        }
    
    def analyze_itc(self, gst_data: Dict) -> Dict:
        """
        Analyze Input Tax Credit
        
        Returns:
            - total_itc_claimed
            - total_itc_utilized
            - itc_balance
            - itc_to_revenue_ratio
        """
        itc_claimed = gst_data.get('itc_claimed', 0)
        itc_utilized = gst_data.get('itc_utilized', 0)
        itc_balance = itc_claimed - itc_utilized
        
        revenue = gst_data.get('total_revenue', 0)
        itc_ratio = (itc_claimed / revenue * 100) if revenue > 0 else 0
        
        # Risk flag if ITC ratio is unusually high
        if itc_ratio > 15:  # Industry average is typically 8-12%
            self.risk_flags.append({
                'type': 'high_itc_ratio',
                'severity': 'medium',
                'value': itc_ratio,
                'message': f'ITC ratio is {itc_ratio:.1f}%, higher than industry average'
            })
        
        return {
            'total_itc_claimed': round(itc_claimed, 2),
            'total_itc_utilized': round(itc_utilized, 2),
            'itc_balance': round(itc_balance, 2),
            'itc_to_revenue_ratio': round(itc_ratio, 2)
        }
    
    def analyze_vendors(self, gst_data: Dict) -> Dict:
        """
        Analyze vendor relationships from GSTR-2B
        
        Returns:
            - total_vendors
            - verified_vendors
            - vendor_verification_rate
            - top_vendor_concentration
            - long_term_vendors_count
        """
        vendors = gst_data.get('vendors', [])
        
        if not vendors:
            return {
                'total_vendors': 0,
                'verified_vendors': 0,
                'vendor_verification_rate': 0,
                'top_vendor_concentration': 0,
                'top_3_vendor_concentration': 0,
                'long_term_vendors_count': 0,
                'long_term_vendor_percentage': 0
            }
        
        total_vendors = len(vendors)
        verified_vendors = sum(1 for v in vendors if v.get('verified', False))
        verification_rate = (verified_vendors / total_vendors * 100) if total_vendors > 0 else 0
        
        # Vendor concentration
        vendor_amounts = [v.get('total_amount', 0) for v in vendors]
        total_purchases = sum(vendor_amounts)
        
        if vendor_amounts and total_purchases > 0:
            sorted_amounts = sorted(vendor_amounts, reverse=True)
            top_vendor_concentration = (sorted_amounts[0] / total_purchases * 100)
            top_3_concentration = (sum(sorted_amounts[:3]) / total_purchases * 100) if len(sorted_amounts) >= 3 else top_vendor_concentration
        else:
            top_vendor_concentration = 0
            top_3_concentration = 0
        
        # Long-term vendors (> 6 months)
        long_term_vendors = sum(1 for v in vendors if v.get('months_active', 0) >= 6)
        long_term_percentage = (long_term_vendors / total_vendors * 100) if total_vendors > 0 else 0
        
        # Risk flags
        if top_vendor_concentration > 40:
            self.risk_flags.append({
                'type': 'high_vendor_concentration',
                'severity': 'medium',
                'value': top_vendor_concentration,
                'message': f'Top vendor accounts for {top_vendor_concentration:.1f}% of purchases'
            })
        
        if verification_rate < 80:
            self.risk_flags.append({
                'type': 'low_vendor_verification',
                'severity': 'medium',
                'value': verification_rate,
                'message': f'Only {verification_rate:.1f}% vendors are GST-verified'
            })
        
        return {
            'total_vendors': total_vendors,
            'verified_vendors': verified_vendors,
            'vendor_verification_rate': round(verification_rate, 2),
            'top_vendor_concentration': round(top_vendor_concentration, 2),
            'top_3_vendor_concentration': round(top_3_concentration, 2),
            'long_term_vendors_count': long_term_vendors,
            'long_term_vendor_percentage': round(long_term_percentage, 2)
        }
    
    def analyze_industry_metrics(self, gst_data: Dict) -> Dict:
        """
        Calculate industry-specific metrics
        
        Returns:
            - industry
            - effective_gst_rate
        """
        revenue = gst_data.get('total_revenue', 0)
        gst_liability = gst_data.get('total_tax_liability', 0)
        
        effective_rate = (gst_liability / revenue * 100) if revenue > 0 else 0
        
        # Derive industry from HSN/SAC codes
        hsn_codes = gst_data.get('hsn_codes', [])
        industry = self._derive_industry_from_hsn(hsn_codes)
        
        return {
            'industry': industry,
            'effective_gst_rate': round(effective_rate, 2)
        }
    
    def analyze_hsn_sac(self, gst_data: Dict) -> Dict:
        """
        Analyze HSN/SAC codes
        
        Returns:
            - hsn_sac_codes: List of codes used
            - primary_business_activity
        """
        hsn_codes = gst_data.get('hsn_codes', [])
        sac_codes = gst_data.get('sac_codes', [])
        
        all_codes = hsn_codes + sac_codes
        primary_activity = self._derive_industry_from_hsn(hsn_codes) if hsn_codes else 'Unknown'
        
        return {
            'hsn_sac_codes': all_codes,
            'primary_business_activity': primary_activity,
            'total_codes_used': len(all_codes)
        }
    
    def analyze_geography(self, gst_data: Dict) -> Dict:
        """
        Analyze geographic presence
        
        Returns:
            - gst_locations: List of GST locations
            - multi_state_operations
        """
        locations = gst_data.get('locations', [])
        multi_state = len(set(loc.get('state') for loc in locations if loc.get('state'))) > 1
        
        return {
            'gst_locations': locations,
            'multi_state_operations': multi_state,
            'total_locations': len(locations)
        }
    
    def assess_risk(self) -> Dict:
        """
        Assess overall risk based on collected flags
        
        Returns:
            - risk_flags: List of detected issues
            - risk_level: low/medium/high
        """
        if not self.risk_flags:
            return {
                'risk_flags': [],
                'risk_level': 'low',
                'risk_score': 100
            }
        
        # Count severity
        high_severity = sum(1 for f in self.risk_flags if f.get('severity') == 'high')
        medium_severity = sum(1 for f in self.risk_flags if f.get('severity') == 'medium')
        
        # Determine risk level
        if high_severity >= 2:
            risk_level = 'high'
            risk_score = 40
        elif high_severity >= 1 or medium_severity >= 3:
            risk_level = 'medium'
            risk_score = 60
        else:
            risk_level = 'low'
            risk_score = 80
        
        return {
            'risk_flags': self.risk_flags,
            'risk_level': risk_level,
            'risk_score': risk_score,
            'high_severity_count': high_severity,
            'medium_severity_count': medium_severity
        }
    
    def calculate_compliance_score(self, analysis_results: Dict) -> int:
        """
        Calculate overall compliance score (0-100)
        
        Based on:
        - Filing regularity (30%)
        - Tax payment (25%)
        - Vendor verification (20%)
        - Mismatch checks (15%)
        - Risk flags (10%)
        """
        score = 0
        
        # Filing regularity (30 points)
        filing_regularity = analysis_results.get('filing_discipline', {}).get('gst_filing_regularity', 0)
        score += (filing_regularity / 100) * 30
        
        # Tax payment (25 points)
        tax_compliance = analysis_results.get('tax_compliance', {})
        payment_regularity = tax_compliance.get('tax_payment_regularity', 0)
        outstanding_ratio = 0
        if tax_compliance.get('total_gst_liability', 0) > 0:
            outstanding_ratio = tax_compliance.get('outstanding_gst', 0) / tax_compliance.get('total_gst_liability', 0)
        payment_score = payment_regularity * (1 - outstanding_ratio)
        score += payment_score * 25
        
        # Vendor verification (20 points)
        vendor_analysis = analysis_results.get('vendor_analysis', {})
        vendor_verification_rate = vendor_analysis.get('vendor_verification_rate', 0)
        score += (vendor_verification_rate / 100) * 20
        
        # Mismatch checks (15 points)
        mismatch = analysis_results.get('mismatch_checks', {})
        gst_itr_mismatch = mismatch.get('gst_r1_itr_mismatch', 0)
        mismatch_score = max(0, 1 - (gst_itr_mismatch / 100))
        score += mismatch_score * 15
        
        # Risk assessment (10 points)
        risk_score = analysis_results.get('risk_assessment', {}).get('risk_score', 100)
        score += (risk_score / 100) * 10
        
        return int(round(score))
    
    # ========== Helper Methods ==========
    
    def _extract_revenue_from_gstr1(self, gst_data: Dict) -> Dict:
        """Extract revenue from GSTR-1 format"""
        revenue = 0
        monthly_revenue = {}
        
        # B2B sales
        b2b = gst_data.get('b2b', [])
        for invoice in b2b:
            revenue += invoice.get('taxable_value', 0)
        
        # B2C sales
        b2c = gst_data.get('b2c', [])
        for invoice in b2c:
            revenue += invoice.get('taxable_value', 0)
        
        # For simplicity, assume this is for one month
        return_period = gst_data.get('return_period', 'Unknown')
        monthly_revenue[return_period] = revenue
        
        return {
            'total_revenue': revenue,
            'monthly_revenue': monthly_revenue
        }
    
    def _extract_revenue_from_gstr3b(self, gst_data: Dict) -> Dict:
        """Extract revenue from GSTR-3B format"""
        revenue = gst_data.get('taxable_turnover', 0)
        return_period = gst_data.get('return_period', 'Unknown')
        
        return {
            'total_revenue': revenue,
            'monthly_revenue': {return_period: revenue}
        }
    
    def _extract_revenue_generic(self, gst_data: Dict) -> Dict:
        """Extract revenue from generic format"""
        revenue = gst_data.get('total_revenue', 0)
        return {
            'total_revenue': revenue,
            'monthly_revenue': {}
        }
    
    def _derive_industry_from_hsn(self, hsn_codes: List) -> str:
        """Derive industry from HSN codes"""
        if not hsn_codes:
            return 'Unknown'
        
        # Simple mapping (expand as needed)
        hsn_industry_map = {
            '1': 'Agriculture',
            '2': 'Animal Products',
            '3': 'Animal/Vegetable Fats',
            '4': 'Food Products',
            '5': 'Mineral Products',
            '6': 'Chemical Products',
            '7': 'Plastics/Rubber',
            '8': 'Leather Products',
            '9': 'Wood Products',
            '10': 'Paper Products',
            '11': 'Textiles',
            '84': 'Machinery',
            '85': 'Electronics',
            '87': 'Vehicles',
            '99': 'Services'
        }
        
        # Get first HSN code
        first_hsn = str(hsn_codes[0]) if hsn_codes else ''
        
        # Match first 2 digits
        for key, industry in hsn_industry_map.items():
            if first_hsn.startswith(key):
                return industry
        
        return 'General Trade'

