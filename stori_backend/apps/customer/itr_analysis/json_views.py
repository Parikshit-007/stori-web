"""
JSON-based ITR Analysis Views
For Account Aggregator integration - accepts JSON directly
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .analyzer import extract_itr_features_single_year, load_itr_json
import tempfile
import os


class ITRJSONAnalysisView(APIView):
    """
    Direct JSON analysis for ITR data
    No file upload needed - accepts ITR JSON directly
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Analyze ITR from JSON data
        
        Request Body: Standard ITR JSON format from Income Tax Portal
        {
            "ITR": {
                "ITR1": {
                    "Form_ITR1": {
                        "AssessmentYear": "2024-25",
                        ...
                    },
                    "ITR1_IncomeDeductions": {
                        "GrossSalary": 1200000,
                        ...
                    },
                    ...
                }
            }
        }
        """
        try:
            itr_data = request.data
            
            # Validate input is a dictionary
            if not isinstance(itr_data, dict):
                return Response({
                    'success': False,
                    'message': f'Invalid data type. Expected JSON object (dictionary), got {type(itr_data).__name__}. Please send JSON object with "ITR" key, not a plain array.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate ITR structure
            if 'ITR' not in itr_data:
                return Response({
                    'success': False,
                    'message': 'Invalid ITR format. Expected "ITR" key in JSON'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Load and standardize ITR data
            # Create a temporary file to use with load_itr_json
            try:
                import json
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp_file:
                    json.dump(itr_data, tmp_file)
                    tmp_path = tmp_file.name
                
                try:
                    standardized_itr = load_itr_json(tmp_path)
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
            except Exception as e:
                return Response({
                    'success': False,
                    'message': f'Failed to parse ITR data: {str(e)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract features from standardized data
            features = extract_itr_features_single_year(standardized_itr)
            
            # Extract basic info
            itr_root = itr_data.get('ITR', {})
            form_type = 'ITR-1' if 'ITR1' in itr_root else 'ITR-4' if 'ITR4' in itr_root else 'Unknown'
            
            if form_type == 'ITR-1':
                form_data = itr_root.get('ITR1', {})
                form_info = form_data.get('Form_ITR1', {})
            elif form_type == 'ITR-4':
                form_data = itr_root.get('ITR4', {})
                form_info = form_data.get('Form_ITR4', {})
            else:
                form_info = {}
            
            assessment_year = form_info.get('AssessmentYear', 'Unknown')
            
            # Extract additional details from standardized ITR
            income_data = standardized_itr.get('income', {})
            tax_data = standardized_itr.get('tax', {})
            deductions_data = standardized_itr.get('deductions', {})
            
            # Create summary with all available data
            summary = {
                'assessment_year': assessment_year,
                'form_type': form_type,
                'net_taxable_income': features.get('itr_net_taxable_income', 0),
                'gross_total_income': features.get('itr_gross_total_income', 0),
                'tax_paid': features.get('itr_tax_paid', 0),
                'salary_income': features.get('itr_salary_income', 0),
                'business_income': features.get('itr_business_income', 0),
                'house_property_income': features.get('itr_house_property_income', 0),
                'capital_gains': features.get('itr_capital_gains', 0),
                'other_income': features.get('itr_other_income', 0),
                'income_type': 'Salaried' if features.get('income_type_salaried', 0) == 1 else 'Business',
                'total_deductions': features.get('itr_total_deductions', 0),
                'tds_deducted': features.get('itr_tds_deducted', 0),
                'tax_refund': features.get('itr_tax_refund', 0),
                'tax_outstanding': features.get('itr_tax_outstanding', 0),
                'income_source_reliability': features.get('income_source_reliability', 0.5),
                'analysis_date': str(timezone.now())
            }
            
            return Response({
                'success': True,
                'message': 'ITR analyzed successfully',
                'data': {
                    'features': features,
                    'summary': summary
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Analysis failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

