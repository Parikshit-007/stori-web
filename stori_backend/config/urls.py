"""
URL configuration for STORI NBFC Backend project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions

urlpatterns = [
    # Admin - Production URL: /api/admin/
    path('api/admin/', admin.site.urls),
    
    # Authentication
    path('api/auth/', include('knox.urls')),
    path('accounts/', include('allauth.urls')),
    
    # Customer Analysis APIs
    path('api/customer/itr/', include('apps.customer.itr_analysis.urls')),
    path('api/customer/bank-statement/', include('apps.customer.bank_statement_analysis.urls')),
    path('api/customer/credit-report/', include('apps.customer.credit_report_analysis.urls')),
    path('api/customer/ocr/', include('apps.customer.ocr_analysis.urls')),
    path('api/customer/asset-analysis/', include('apps.customer.asset_analysis.urls')),
    
    # KYC Document OCR API
    path('api/kyc/', include('apps.customer.ocr_analysis.urls')),
    
    # Credit Scoring API
    path('api/customer/credit-scoring/', include('apps.customer.credit_scoring.urls')),
    
    # MSME Credit Scoring API
    path('api/msme/', include('apps.msme.urls')),
    
    # API Documentation
    path('api/documentation/', include('api_docs.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "STORI NBFC Administration"
admin.site.site_title = "STORI NBFC Admin Portal"
admin.site.index_title = "Welcome to STORI NBFC Administration"

