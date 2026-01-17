"""
JSON-based Credit Report Analysis Views
For Account Aggregator integration - accepts JSON directly
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .analyzer import extract_credit_features
from datetime import datetime


def parse_bureau_format(data: dict) -> dict:
    """
    Parse CIBIL/Bureau credit report format and convert to standard format.
    
    Handles structure:
    {
        "result": {
            "result_json": {
                "INProfileResponse": {
                    "SCORE": {"BureauScore": "771"},
                    "CAIS_Account": {
                        "CAIS_Account_DETAILS": [...]
                    },
                    "TotalCAPS_Summary": {...}
                }
            }
        }
    }
    
    Returns:
        Standardized credit report format
    """
    standardized = {
        'score': 0,
        'bureau': 'CIBIL',
        'report_date': None,
        'accounts': [],
        'enquiries': []
    }
    
    # Navigate to INProfileResponse
    result_json = data.get('result', {}).get('result_json', {})
    if not result_json:
        # Try direct access
        result_json = data.get('INProfileResponse', {})
    
    if not result_json:
        return standardized
    
    in_profile = result_json.get('INProfileResponse', result_json)
    
    # Extract score
    score_section = in_profile.get('SCORE', {})
    bureau_score = score_section.get('BureauScore')
    if bureau_score:
        try:
            standardized['score'] = int(bureau_score)
        except (ValueError, TypeError):
            standardized['score'] = 0
    
    # Extract report date
    header = in_profile.get('Header', {})
    report_date_str = header.get('ReportDate')
    if report_date_str:
        try:
            # Format: YYYYMMDD
            standardized['report_date'] = datetime.strptime(report_date_str, '%Y%m%d').strftime('%Y-%m-%d')
        except:
            standardized['report_date'] = None
    
    # Extract accounts from CAIS_Account
    cais_account = in_profile.get('CAIS_Account', {})
    account_details = cais_account.get('CAIS_Account_DETAILS', [])
    
    # Account type mapping (CIBIL codes)
    account_type_map = {
        '01': 'credit_card',
        '02': 'home_loan',
        '03': 'personal_loan',
        '04': 'auto_loan',
        '05': 'consumer_loan',
        '06': 'gold_loan',
        '07': 'education_loan',
        '08': 'business_loan',
        '09': 'other_loan'
    }
    
    # Account status mapping
    status_map = {
        '00': 'closed',
        '01': 'closed',
        '10': 'active',
        '11': 'active',
        '12': 'active',
        '13': 'active',
        '20': 'delinquent',
        '21': 'delinquent',
        '22': 'delinquent',
        '30': 'written_off',
        '31': 'written_off',
        '32': 'written_off'
    }
    
    for acc in account_details:
        if not isinstance(acc, dict):
            continue
        
        # Map account type
        acc_type_code = acc.get('Account_Type', '')
        account_type = account_type_map.get(acc_type_code, 'other_loan')
        
        # Map status
        status_code = acc.get('Account_Status', '')
        status = status_map.get(status_code, 'unknown')
        
        # Extract outstanding
        current_balance = acc.get('Current_Balance')
        outstanding = 0
        if current_balance:
            try:
                outstanding = float(current_balance)
            except (ValueError, TypeError):
                outstanding = 0
        
        # Extract credit limit
        credit_limit = acc.get('Credit_Limit_Amount')
        limit = 0
        if credit_limit:
            try:
                limit = float(credit_limit)
            except (ValueError, TypeError):
                limit = 0
        
        # Extract DPD from Payment_History_Profile or Amount_Past_Due
        dpd = 0
        
        # First check CAIS_Account_History for actual DPD values
        history = acc.get('CAIS_Account_History', [])
        if history and isinstance(history, list):
            # Get most recent history entry
            for hist_entry in history:
                if isinstance(hist_entry, dict):
                    days_past_due = hist_entry.get('Days_Past_Due')
                    if days_past_due:
                        try:
                            dpd = max(dpd, int(days_past_due))
                        except (ValueError, TypeError):
                            pass
        
        # If no DPD from history, check Payment_History_Profile
        if dpd == 0:
            payment_history = acc.get('Payment_History_Profile', '')
            if payment_history and isinstance(payment_history, str):
                # Payment history: '?' = no data, '0' = on time, '1-9' = DPD bucket
                # Recent months are at the end
                recent_chars = payment_history[-6:] if len(payment_history) >= 6 else payment_history
                for char in reversed(recent_chars):  # Check most recent first
                    if char.isdigit():
                        dpd_bucket = int(char)
                        if dpd_bucket > 0:
                            # CIBIL DPD buckets: 1=1-30, 2=31-60, 3=61-90, 4=91-120, etc.
                            dpd = dpd_bucket * 30  # Approximate to middle of bucket
                            break
        
        # Check Amount_Past_Due as additional indicator
        amount_past_due = acc.get('Amount_Past_Due')
        if amount_past_due:
            try:
                past_due_amt = float(amount_past_due)
                if past_due_amt > 0 and dpd == 0:
                    # If there's past due but no DPD found, estimate based on status
                    if status in ['delinquent', 'written_off']:
                        dpd = 90  # Default estimate for delinquent accounts
            except (ValueError, TypeError):
                pass
        
        # Extract open date
        open_date = acc.get('Open_Date')
        opened_date_str = None
        if open_date:
            try:
                # Format: YYYYMMDD
                opened_date_str = datetime.strptime(str(open_date), '%Y%m%d').strftime('%Y-%m-%d')
            except:
                pass
        
        # Extract bank/subscriber name
        bank_name = acc.get('Subscriber_Name', 'Unknown')
        
        # Extract loan amount
        loan_amount = acc.get('Highest_Credit_or_Original_Loan_Amount')
        loan_amt = 0
        if loan_amount:
            try:
                loan_amt = float(loan_amount)
            except (ValueError, TypeError):
                loan_amt = 0
        
        standardized_account = {
            'account_type': account_type,
            'bank': bank_name,
            'status': status,
            'outstanding': outstanding,
            'credit_limit': limit if limit > 0 else loan_amt,  # Use loan amount if no credit limit
            'dpd': dpd,
            'account_number': acc.get('Account_Number', ''),
            'opened_date': opened_date_str,
            'loan_amount': loan_amt,
            'account_id': acc.get('Identification_Number', '')
        }
        
        standardized['accounts'].append(standardized_account)
    
    # Extract enquiries from CAPS
    caps_summary = in_profile.get('TotalCAPS_Summary', {})
    if caps_summary:
        # Count enquiries in different periods
        total_caps_30d = int(caps_summary.get('TotalCAPSLast30Days', 0) or 0)
        total_caps_90d = int(caps_summary.get('TotalCAPSLast90Days', 0) or 0)
        
        # Create enquiry entries (simplified)
        if total_caps_30d > 0 or total_caps_90d > 0:
            for i in range(total_caps_30d):
                standardized['enquiries'].append({
                    'bank': 'Unknown',
                    'date': standardized.get('report_date'),
                    'type': 'credit_enquiry',
                    'months_ago': 1
                })
    
    return standardized


class CreditReportJSONAnalysisView(APIView):
    """
    Direct JSON analysis for Credit Report data
    No file upload needed - accepts credit report JSON directly
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Analyze credit report from JSON data
        
        Request Body:
        {
            "score": 750,
            "bureau": "CIBIL",
            "report_date": "2024-01-15",
            "accounts": [
                {
                    "account_type": "credit_card",
                    "bank": "HDFC",
                    "status": "active",
                    "outstanding": 25000,
                    "credit_limit": 100000,
                    "dpd": 0,
                    "opened_date": "2020-01-15"
                },
                ...
            ],
            "enquiries": [
                {
                    "bank": "ICICI",
                    "date": "2024-01-10",
                    "type": "credit_card",
                    "months_ago": 1
                },
                ...
            ]
        }
        """
        try:
            credit_data = request.data
            
            # Validate input is a dictionary
            if not isinstance(credit_data, dict):
                return Response({
                    'success': False,
                    'message': f'Invalid data type. Expected JSON object (dictionary), got {type(credit_data).__name__}. Please send JSON object, not array.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if this is bureau format (CIBIL/Experian/etc.)
            is_bureau_format = (
                'result' in credit_data and 
                'result_json' in credit_data.get('result', {})
            ) or 'INProfileResponse' in credit_data
            
            if is_bureau_format:
                # Parse bureau format and convert to standard format
                try:
                    credit_data = parse_bureau_format(credit_data)
                except Exception as e:
                    return Response({
                        'success': False,
                        'message': f'Failed to parse bureau format: {str(e)}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate basic structure after conversion
            if 'score' not in credit_data and 'accounts' not in credit_data:
                return Response({
                    'success': False,
                    'message': 'Invalid credit report format. Expected "score" or "accounts" in JSON, or bureau format with "result.result_json.INProfileResponse"'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Extract features
            features = extract_credit_features(credit_data)
            
            # Create summary
            accounts = credit_data.get('accounts', [])
            enquiries = credit_data.get('enquiries', [])
            
            summary = {
                'credit_score': credit_data.get('score', features.get('credit_score', 0)),
                'bureau': credit_data.get('bureau', 'Unknown'),
                'report_date': credit_data.get('report_date', str(timezone.now().date())),
                'total_accounts': len(accounts),
                'active_accounts': features.get('active_accounts', 0),
                'closed_accounts': features.get('closed_accounts', 0),
                'total_outstanding': features.get('total_outstanding', 0),
                'total_credit_limit': features.get('total_credit_limit', 0),
                'credit_utilization': features.get('credit_utilization', 0),
                'delinquent_accounts': features.get('delinquent_accounts', 0),
                'max_dpd': features.get('max_dpd', 0),
                'total_enquiries': len(enquiries),
                'recent_enquiries_6m': features.get('recent_enquiries_6m', 0),
                'analysis_date': str(timezone.now())
            }
            
            # Account breakdown
            account_breakdown = {
                'credit_cards': features.get('credit_cards', 0),
                'loans': features.get('loans', 0),
                'by_status': {
                    'active': sum(1 for acc in accounts if acc.get('status') == 'active'),
                    'closed': sum(1 for acc in accounts if acc.get('status') == 'closed'),
                    'delinquent': sum(1 for acc in accounts if acc.get('dpd', 0) > 0)
                }
            }
            
            return Response({
                'success': True,
                'message': 'Credit report analyzed successfully',
                'data': {
                    'features': features,
                    'summary': summary,
                    'account_breakdown': account_breakdown,
                    'accounts': accounts[:10],  # First 10 accounts
                    'recent_enquiries': enquiries[:5]  # Recent 5 enquiries
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Analysis failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

