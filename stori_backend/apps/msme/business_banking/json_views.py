"""
Business Banking JSON Views
============================

JSON-based APIs for business banking analysis
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# Reuse consumer bank analyzer but add business-specific fields
from apps.customer.bank_statement_analysis.json_views import BankStatementJSONAnalysisView

class BusinessBankingJSONAnalysisView(BankStatementJSONAnalysisView):
    """
    JSON-based business banking analysis
    
    POST /api/msme/business-banking/analyze-json/
    
    Reuses consumer bank statement JSON analysis with business context
    """
    pass  # Inherits from consumer, adds business-specific logic in future

