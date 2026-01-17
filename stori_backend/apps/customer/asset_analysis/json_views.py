"""
Asset Analysis JSON API View
Accepts Account Aggregator JSON and returns asset analysis
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import logging

from apps.authentication.authentication import APIKeyAuthentication
from .analyzer import AssetAnalyzer

logger = logging.getLogger(__name__)


class AssetAnalysisJSONView(APIView):
    """
    Analyze assets from Account Aggregator JSON
    Requires X-API-Key header for authentication
    """
    authentication_classes = [APIKeyAuthentication]
    """
    Analyze assets from Account Aggregator JSON
    
    POST /api/customer/asset-analysis/analyze-json/
    
    Request Body (JSON):
    {
        "demat": {
            "holdings": [...]
        },
        "mutual_funds": {
            "folios": [...]
        },
        "fixed_deposits": {
            "fixed_deposits": [...]
        },
        "gold": {
            "holdings": [...]
        },
        "real_estate": {
            "properties": [...]
        },
        "insurance": {
            "policies": [...]
        },
        "provident_fund": {
            "pf_accounts": [...]
        },
        "other_investments": {
            "investments": [...]
        }
    }
    """
    
    def post(self, request):
        """
        Analyze assets from AA JSON data
        
        Returns:
            {
                "success": true,
                "message": "Assets analyzed successfully",
                "data": {
                    "analysis": {
                        "total_asset_value": 1000000.0,
                        "highest_quantified_amount": {
                            "value": 500000.0,
                            "asset_type": "STOCKS",
                            "asset_name": "Reliance Industries",
                            "subtype": "NSE"
                        },
                        "survivability_asset_value": 800000.0,
                        ...
                    },
                    "summary": {...},
                    "processed_at": "2026-01-16T..."
                }
            }
        """
        try:
            # Get JSON data from request
            aa_data = request.data
            
            if not aa_data:
                return Response({
                    'success': False,
                    'message': 'No data provided. Please send Account Aggregator JSON data.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Initialize analyzer
            analyzer = AssetAnalyzer()
            
            # Load assets from AA JSON
            analyzer.load_from_aa_json(aa_data)
            
            # Calculate analysis
            analysis = analyzer.calculate_analysis()
            
            # Build summary
            summary = {
                'total_assets': analysis['num_assets'],
                'total_value': analysis['total_asset_value'],
                'survivability_value': analysis['survivability_asset_value'],
                'highest_asset': analysis['highest_quantified_amount'],
                'liquidity_breakdown': {
                    'liquid': analysis['liquid_assets'],
                    'semi_liquid': analysis['semi_liquid_assets'],
                    'illiquid': analysis['illiquid_assets'],
                    'liquidity_ratio': analysis['liquidity_ratio']
                },
                'asset_type_breakdown': {
                    'stocks': analysis['stocks_value'],
                    'mutual_funds': analysis['mutual_funds_value'],
                    'fixed_deposits': analysis['fixed_deposits_value'],
                    'gold': analysis['gold_value'],
                    'real_estate': analysis['real_estate_value'],
                    'insurance': analysis['insurance_value'],
                    'provident_fund': analysis['provident_fund_value'],
                    'bonds': analysis['bonds_value'],
                    'nps': analysis['nps_value'],
                    'crypto': analysis['crypto_value']
                },
                'portfolio_returns_pct': analysis['portfolio_returns_pct']
            }
            
            # Prepare response
            response_data = {
                'success': True,
                'message': 'Assets analyzed successfully',
                'data': {
                    'analysis': analysis,
                    'summary': summary,
                    'processed_at': timezone.now().isoformat()
                }
            }
            
            logger.info(f"Asset analysis completed. Total value: {analysis['total_asset_value']}, "
                       f"Highest asset: {analysis['highest_quantified_amount']['value']}")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Asset analysis failed: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': f'Asset analysis failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

