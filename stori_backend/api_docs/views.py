from django.shortcuts import render

def index(request):
    """Main API documentation page with Consumer and MSME sections"""
    return render(request, 'api_docs/index.html')

def authentication(request):
    """Authentication documentation page"""
    return render(request, 'api_docs/authentication.html')

# Consumer APIs
def consumer_bank_statement(request):
    """Consumer Bank Statement Analysis API documentation"""
    return render(request, 'api_docs/consumer/bank_statement.html')

def consumer_itr(request):
    """Consumer ITR Analysis API documentation"""
    return render(request, 'api_docs/consumer/itr.html')

def consumer_credit_report(request):
    """Consumer Credit Report Analysis API documentation"""
    return render(request, 'api_docs/consumer/credit_report.html')

def consumer_asset(request):
    """Consumer Asset Analysis API documentation"""
    return render(request, 'api_docs/consumer/asset.html')

def consumer_credit_score(request):
    """Consumer Final Credit Score API documentation"""
    return render(request, 'api_docs/consumer/credit_score.html')

def consumer_kyc_ocr(request):
    """Consumer KYC OCR API documentation"""
    return render(request, 'api_docs/consumer/kyc_ocr.html')

# MSME APIs
def msme_gst(request):
    """MSME GST Analysis API documentation"""
    return render(request, 'api_docs/msme/gst.html')

def msme_director_banking(request):
    """MSME Director Banking API documentation"""
    return render(request, 'api_docs/msme/director_banking.html')

def msme_business_banking(request):
    """MSME Business Banking API documentation"""
    return render(request, 'api_docs/msme/business_banking.html')

def msme_credit_score(request):
    """MSME Final Credit Score API documentation"""
    return render(request, 'api_docs/msme/credit_score.html')
