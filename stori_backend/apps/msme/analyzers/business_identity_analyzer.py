"""
Business Identity & Registration Analyzer
==========================================

Analyzes:
- Business Basics (entity type, vintage, registration)
- Verification (GSTIN, PAN, MCA)
- Locations (operational locations, address consistency)
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import re


class BusinessIdentityAnalyzer:
    """Analyzes business identity and registration details"""
    
    def __init__(self):
        self.weights = {
            'business_basics': 0.40,
            'verification': 0.40,
            'locations': 0.20
        }
    
    def analyze_business_basics(self, business_data: Dict) -> Dict[str, Any]:
        """
        Analyze business basics: entity type, vintage, registration status
        
        Args:
            business_data: Business registration data including:
                - entity_type: str (proprietorship, partnership, llp, pvt_ltd, etc.)
                - registration_date: str/datetime
                - business_name: str
                - industry: str
                - msme_category: str (micro, small, medium)
                
        Returns:
            Dict with business basics metrics
        """
        try:
            entity_type = business_data.get('entity_type', '').lower()
            registration_date = business_data.get('registration_date')
            business_name = business_data.get('business_name', '')
            industry = business_data.get('industry', '')
            msme_category = business_data.get('msme_category', 'micro').lower()
            
            # Calculate vintage (years in business)
            vintage_years = self._calculate_vintage(registration_date)
            
            # Score entity type
            entity_score = self._score_entity_type(entity_type)
            
            # Score vintage
            vintage_score = self._score_vintage(vintage_years)
            
            # Score business name quality
            name_score = self._score_business_name(business_name)
            
            # Score industry
            industry_score = self._score_industry(industry)
            
            # Overall basics score
            overall_score = (
                entity_score * 0.30 +
                vintage_score * 0.35 +
                name_score * 0.15 +
                industry_score * 0.20
            )
            
            return {
                'entity_type': entity_type,
                'entity_type_score': entity_score,
                'vintage_years': vintage_years,
                'vintage_score': vintage_score,
                'business_name': business_name,
                'name_score': name_score,
                'industry': industry,
                'industry_score': industry_score,
                'msme_category': msme_category,
                'overall_score': overall_score
            }
        except Exception as e:
            return {
                'entity_type': '',
                'vintage_years': 0,
                'overall_score': 0,
                'error': str(e)
            }
    
    def analyze_verification(self, verification_data: Dict) -> Dict[str, Any]:
        """
        Analyze verification status: GSTIN, PAN, MCA registration
        
        Args:
            verification_data: Verification data including:
                - gstin: str
                - gstin_status: str (active, cancelled, etc.)
                - pan: str
                - pan_status: str
                - mca_registration: bool
                - mca_status: str
                - gstin_match: bool (matches business name)
                - pan_match: bool (matches business name)
                
        Returns:
            Dict with verification metrics
        """
        try:
            gstin = verification_data.get('gstin', '')
            gstin_status = verification_data.get('gstin_status', '').lower()
            pan = verification_data.get('pan', '')
            pan_status = verification_data.get('pan_status', '').lower()
            mca_registration = verification_data.get('mca_registration', False)
            mca_status = verification_data.get('mca_status', '').lower()
            
            # GSTIN verification
            gstin_score = self._score_gstin_verification(gstin, gstin_status)
            
            # PAN verification
            pan_score = self._score_pan_verification(pan, pan_status)
            
            # MCA registration
            mca_score = self._score_mca_registration(mca_registration, mca_status)
            
            # Name matching (if provided)
            gstin_match = verification_data.get('gstin_match', True)
            pan_match = verification_data.get('pan_match', True)
            match_score = 1.0 if (gstin_match and pan_match) else 0.5
            
            # Overall verification score
            overall_score = (
                gstin_score * 0.40 +
                pan_score * 0.30 +
                mca_score * 0.20 +
                match_score * 0.10
            )
            
            return {
                'gstin': gstin,
                'gstin_status': gstin_status,
                'gstin_score': gstin_score,
                'pan': pan,
                'pan_status': pan_status,
                'pan_score': pan_score,
                'mca_registration': mca_registration,
                'mca_status': mca_status,
                'mca_score': mca_score,
                'name_match_score': match_score,
                'overall_score': overall_score
            }
        except Exception as e:
            return {
                'gstin': '',
                'pan': '',
                'overall_score': 0,
                'error': str(e)
            }
    
    def analyze_locations(self, business_data: Dict) -> Dict[str, Any]:
        """
        Analyze business locations: operational locations, address consistency
        
        Args:
            business_data: Business data including:
                - registered_address: str
                - operational_addresses: List[str]
                - address_consistency: bool
                - number_of_locations: int
                
        Returns:
            Dict with location metrics
        """
        try:
            registered_address = business_data.get('registered_address', '')
            operational_addresses = business_data.get('operational_addresses', [])
            address_consistency = business_data.get('address_consistency', True)
            number_of_locations = len(operational_addresses) if operational_addresses else 1
            
            # Score address completeness
            address_score = self._score_address_completeness(registered_address)
            
            # Score location count (more locations = better, but with diminishing returns)
            location_score = self._score_location_count(number_of_locations)
            
            # Score consistency
            consistency_score = 1.0 if address_consistency else 0.5
            
            # Overall location score
            score = (
                address_score * 0.40 +
                location_score * 0.30 +
                consistency_score * 0.30
            )
            
            return {
                'registered_address': registered_address,
                'number_of_locations': number_of_locations,
                'address_consistency': address_consistency,
                'address_score': address_score,
                'location_score': location_score,
                'consistency_score': consistency_score,
                'score': score
            }
        except Exception as e:
            return {
                'number_of_locations': 0,
                'score': 0,
                'error': str(e)
            }
    
    def calculate_overall_score(self, basics_score: float, 
                               verification_score: float, 
                               locations_score: float) -> float:
        """Calculate weighted overall business identity score"""
        return (
            basics_score * self.weights['business_basics'] +
            verification_score * self.weights['verification'] +
            locations_score * self.weights['locations']
        )
    
    # Helper Methods
    
    def _calculate_vintage(self, registration_date) -> float:
        """Calculate business vintage in years"""
        try:
            if not registration_date:
                return 0.0
            
            # Parse date
            if isinstance(registration_date, str):
                # Try common date formats
                for fmt in ['%Y-%m-%d', '%d-%m-%Y', '%Y/%m/%d', '%d/%m/%Y']:
                    try:
                        reg_date = datetime.strptime(registration_date, fmt)
                        break
                    except:
                        continue
                else:
                    return 0.0
            elif isinstance(registration_date, datetime):
                reg_date = registration_date
            else:
                return 0.0
            
            # Calculate years
            today = datetime.now()
            delta = today - reg_date
            years = delta.days / 365.25
            
            return max(0.0, years)
        except:
            return 0.0
    
    def _score_entity_type(self, entity_type: str) -> float:
        """Score entity type (higher for more formal structures)"""
        entity_scores = {
            'pvt_ltd': 1.0,
            'private_limited': 1.0,
            'llp': 0.9,
            'limited_liability_partnership': 0.9,
            'partnership': 0.7,
            'proprietorship': 0.6,
            'sole_proprietorship': 0.6,
            'huf': 0.5,
            'other': 0.4
        }
        
        return entity_scores.get(entity_type, 0.5)
    
    def _score_vintage(self, vintage_years: float) -> float:
        """Score vintage (more years = better, with diminishing returns)"""
        if vintage_years <= 0:
            return 0.0
        elif vintage_years < 1:
            return 0.3
        elif vintage_years < 2:
            return 0.5
        elif vintage_years < 3:
            return 0.7
        elif vintage_years < 5:
            return 0.85
        elif vintage_years < 10:
            return 0.95
        else:
            return 1.0
    
    def _score_business_name(self, business_name: str) -> float:
        """Score business name quality"""
        if not business_name or len(business_name.strip()) < 3:
            return 0.0
        
        name = business_name.strip()
        score = 0.5  # Base score
        
        # Length check (reasonable length)
        if 5 <= len(name) <= 50:
            score += 0.2
        
        # Check for proper formatting (not all caps, not all lowercase)
        if not (name.isupper() or name.islower()):
            score += 0.2
        
        # Check for common business suffixes
        business_suffixes = ['pvt', 'ltd', 'llp', 'limited', 'private', 'partners', 'solutions', 'services']
        if any(suffix.lower() in name.lower() for suffix in business_suffixes):
            score += 0.1
        
        return min(1.0, score)
    
    def _score_industry(self, industry: str) -> float:
        """Score industry (some industries are more stable)"""
        if not industry:
            return 0.5
        
        # Higher risk industries get lower scores
        high_risk_industries = ['gambling', 'casino', 'speculative', 'pyramid']
        if any(risk in industry.lower() for risk in high_risk_industries):
            return 0.2
        
        # Stable industries get higher scores
        stable_industries = ['manufacturing', 'retail', 'wholesale', 'services', 'trading']
        if any(stable in industry.lower() for stable in stable_industries):
            return 0.8
        
        return 0.6  # Default for unknown industries
    
    def _score_gstin_verification(self, gstin: str, status: str) -> float:
        """Score GSTIN verification"""
        if not gstin:
            return 0.0
        
        # Validate GSTIN format (15 characters, alphanumeric)
        if len(gstin) != 15 or not gstin.isalnum():
            return 0.3
        
        # Check status
        if status == 'active':
            return 1.0
        elif status == 'cancelled':
            return 0.2
        elif status == 'suspended':
            return 0.3
        else:
            return 0.5  # Unknown status
    
    def _score_pan_verification(self, pan: str, status: str) -> float:
        """Score PAN verification"""
        if not pan:
            return 0.0
        
        # Validate PAN format (10 characters: 5 letters, 4 digits, 1 letter)
        pan_pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        if not re.match(pan_pattern, pan.upper()):
            return 0.3
        
        # Check status
        if status == 'active' or status == 'valid':
            return 1.0
        elif status == 'invalid' or status == 'cancelled':
            return 0.2
        else:
            return 0.7  # Unknown status, but format is valid
    
    def _score_mca_registration(self, registered: bool, status: str) -> float:
        """Score MCA registration"""
        if not registered:
            return 0.5  # Not required for all entity types
        
        if status == 'active':
            return 1.0
        elif status == 'struck_off' or status == 'dissolved':
            return 0.1
        else:
            return 0.7
    
    def _score_address_completeness(self, address: str) -> float:
        """Score address completeness"""
        if not address or len(address.strip()) < 10:
            return 0.0
        
        address = address.strip()
        score = 0.3  # Base score for having an address
        
        # Check for key components
        if any(word in address.lower() for word in ['street', 'road', 'lane', 'nagar', 'colony']):
            score += 0.2
        
        if any(word in address.lower() for word in ['city', 'town', 'village']):
            score += 0.2
        
        if any(word in address.lower() for word in ['state', 'pradesh', 'district']):
            score += 0.15
        
        # Check for pincode (6 digits)
        if re.search(r'\b\d{6}\b', address):
            score += 0.15
        
        return min(1.0, score)
    
    def _score_location_count(self, count: int) -> float:
        """Score location count (more locations = better, with diminishing returns)"""
        if count <= 0:
            return 0.0
        elif count == 1:
            return 0.7
        elif count == 2:
            return 0.85
        elif count <= 5:
            return 0.95
        else:
            return 1.0

