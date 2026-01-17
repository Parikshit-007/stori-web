"""
Director Banking JSON Views
============================

JSON-based APIs for director personal banking analysis
(Consumer flow reuse with JSON input)
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# Reuse consumer bank analyzer
from apps.customer.bank_statement_analysis.json_views import BankStatementJSONAnalysisView

class DirectorBankingJSONAnalysisView(BankStatementJSONAnalysisView):
    """
    JSON-based director banking analysis
    
    POST /api/msme/director-banking/analyze-json/
    
    Reuses consumer bank statement JSON analysis
    """
    pass  # Inherits everything from consumer flow

