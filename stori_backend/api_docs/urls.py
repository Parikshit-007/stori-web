from django.urls import path
from . import views

app_name = 'api_docs'

urlpatterns = [
    # Main page
    path('', views.index, name='index'),
    path('authentication/', views.authentication, name='authentication'),
    
    # Consumer APIs
    path('consumer/bank-statement/', views.consumer_bank_statement, name='consumer_bank_statement'),
    path('consumer/itr/', views.consumer_itr, name='consumer_itr'),
    path('consumer/credit-report/', views.consumer_credit_report, name='consumer_credit_report'),
    path('consumer/asset/', views.consumer_asset, name='consumer_asset'),
    path('consumer/credit-score/', views.consumer_credit_score, name='consumer_credit_score'),
    path('consumer/kyc-ocr/', views.consumer_kyc_ocr, name='consumer_kyc_ocr'),
    
    # MSME APIs
    path('msme/gst/', views.msme_gst, name='msme_gst'),
    path('msme/director-banking/', views.msme_director_banking, name='msme_director_banking'),
    path('msme/business-banking/', views.msme_business_banking, name='msme_business_banking'),
    path('msme/credit-score/', views.msme_credit_score, name='msme_credit_score'),
]

