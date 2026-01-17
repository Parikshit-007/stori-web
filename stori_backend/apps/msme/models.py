from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class MSMEApplication(models.Model):
    """Main MSME Application Model - Links all sections together"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='msme_applications')
    application_number = models.CharField(max_length=50, unique=True)
    company_name = models.CharField(max_length=200)
    msme_category = models.CharField(max_length=20, choices=[
        ('micro', 'Micro'),
        ('small', 'Small'),
        ('medium', 'Medium')
    ])
    
    # Overall scoring
    final_credit_score = models.IntegerField(null=True, blank=True)
    risk_tier = models.CharField(max_length=20, null=True, blank=True, choices=[
        ('prime', 'Prime'),
        ('near_prime', 'Near Prime'),
        ('standard', 'Standard'),
        ('subprime', 'Subprime'),
        ('high_risk', 'High Risk')
    ])
    overdraft_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('more_info_required', 'More Info Required')
    ])
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_applications'
        ordering = ['-created_at']
        verbose_name = 'MSME Application'
        verbose_name_plural = 'MSME Applications'
    
    def __str__(self):
        return f"{self.company_name} - {self.application_number}"


# ==================== A) DIRECTOR / PROMOTER PROFILE ====================

class DirectorProfile(models.Model):
    """Director/Promoter Profile & Behavioral Signals"""
    
    application = models.ForeignKey(MSMEApplication, on_delete=models.CASCADE, related_name='directors')
    
    # 1. Identity (KYC)
    name = models.CharField(max_length=200)
    age = models.IntegerField(validators=[MinValueValidator(18), MaxValueValidator(100)])
    address = models.TextField()
    pan = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    
    # 2. Personal Banking Summary
    avg_account_balance_personal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    assets_derived = models.JSONField(default=dict, help_text="Assets breakdown")
    liabilities_derived = models.JSONField(default=dict, help_text="Liabilities breakdown")
    
    # 3. Behavioral & Stability Signals
    regular_p2p_transactions = models.BooleanField(default=False)
    monthly_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monthly_inflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monthly_outflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    income_volatility = models.DecimalField(max_digits=5, decimal_places=2, default=0, 
                                           help_text="Coefficient of variation")
    subscriptions = models.JSONField(default=list, help_text="List of recurring subscriptions")
    micro_commitments = models.JSONField(default=list, help_text="Display only - NOT for scoring")
    late_night_transactions_count = models.IntegerField(default=0, help_text="Emotional indicator")
    savings_consistency_score = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                    validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # 4. Financial Stability
    is_stable = models.BooleanField(default=True, help_text="Stable if income change < 30%")
    income_change_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_director_profiles'
        ordering = ['name']
        verbose_name = 'Director Profile'
        verbose_name_plural = 'Director Profiles'
    
    def __str__(self):
        return f"{self.name} - {self.application.company_name}"


# ==================== B) BUSINESS IDENTITY & REGISTRATION ====================

class BusinessIdentity(models.Model):
    """Business Identity & Registration Details"""
    
    application = models.OneToOneField(MSMEApplication, on_delete=models.CASCADE, related_name='business_identity')
    
    # 1. Basic Details
    company_name = models.CharField(max_length=200)
    industry = models.CharField(max_length=100)
    business_vintage_years = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    legal_entity_type = models.CharField(max_length=50, choices=[
        ('proprietorship', 'Proprietorship'),
        ('partnership', 'Partnership'),
        ('llp', 'Limited Liability Partnership'),
        ('private_limited', 'Private Limited'),
        ('public_limited', 'Public Limited'),
        ('trust', 'Trust'),
        ('society', 'Society'),
        ('unregistered', 'Unregistered')
    ])
    
    # 2. MSME & Compliance IDs
    msme_category = models.CharField(max_length=20, choices=[
        ('micro', 'Micro'),
        ('small', 'Small'),
        ('medium', 'Medium')
    ])
    gstin = models.CharField(max_length=15, blank=True)
    pan = models.CharField(max_length=10)
    gst_locations = models.JSONField(default=list, help_text="GST-based locations")
    business_structure = models.CharField(max_length=100, blank=True)
    verification_status = models.CharField(max_length=20, default='pending', choices=[
        ('verified', 'Verified'),
        ('pending', 'Pending'),
        ('failed', 'Failed')
    ])
    
    # 3. Licenses & Certificates
    licenses_certificates = models.JSONField(default=list, help_text="Verified licenses and certificates")
    
    # 4. Employees & Locations
    employees_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    locations = models.JSONField(default=list, help_text="Business locations")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_business_identity'
        verbose_name = 'Business Identity'
        verbose_name_plural = 'Business Identities'
    
    def __str__(self):
        return f"{self.company_name} - {self.legal_entity_type}"


# ==================== C) REVENUE & BUSINESS PERFORMANCE ====================

class RevenuePerformance(models.Model):
    """Revenue & Business Performance Metrics"""
    
    application = models.OneToOneField(MSMEApplication, on_delete=models.CASCADE, related_name='revenue_performance')
    
    # 1. Sales / Revenue Metrics
    weekly_gtv = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text="Gross Transaction Value")
    monthly_gtv = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    mom_growth = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Month-over-Month Growth %")
    qoq_growth = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Quarter-over-Quarter Growth %")
    
    # 2. Profitability
    gross_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    net_profit_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    profit_margin_roinet = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # 3. Cash Handling
    weekly_cash_in_hand = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monthly_cash_in_hand = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # 4. Transaction Analytics
    daily_transactions_count = models.IntegerField(default=0)
    average_transaction_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # 5. Revenue Risk Concentration
    revenue_concentration_data = models.JSONField(default=dict, help_text="Monthly revenue distribution")
    peak_day_dependency_data = models.JSONField(default=dict, help_text="Daily revenue peak analysis")
    
    # 6. Cost Efficiency
    operational_leverage = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                              help_text="Fixed Cost / Total Cost")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_revenue_performance'
        verbose_name = 'Revenue Performance'
        verbose_name_plural = 'Revenue Performances'
    
    def __str__(self):
        return f"Revenue - {self.application.company_name}"


# ==================== D) CASH FLOW & BANKING BEHAVIOR ====================

class CashFlowBanking(models.Model):
    """Cash Flow & Banking Behavior"""
    
    application = models.OneToOneField(MSMEApplication, on_delete=models.CASCADE, related_name='cashflow_banking')
    
    # 1. Bank Balance Metrics
    average_bank_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance_trend = models.CharField(max_length=20, choices=[
        ('increasing', 'Increasing'),
        ('stable', 'Stable'),
        ('decreasing', 'Decreasing')
    ], default='stable')
    negative_balance_days = models.IntegerField(default=0)
    avg_daily_closing_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    daily_min_balance_pattern = models.JSONField(default=dict, help_text="Daily minimum balance patterns")
    
    # 2. Inflow/Outflow Health (Exclude P2P)
    inflow_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    outflow_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    inflow_outflow_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # 3. Deposit Consistency (Display Only)
    deposit_consistency_score = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                    help_text="Display only - NOT for scoring")
    deposit_trend_data = models.JSONField(default=dict, help_text="Deposit patterns over time")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_cashflow_banking'
        verbose_name = 'Cash Flow & Banking'
        verbose_name_plural = 'Cash Flow & Banking'
    
    def __str__(self):
        return f"CashFlow - {self.application.company_name}"


# ==================== E) CREDIT & REPAYMENT BEHAVIOR ====================

class CreditRepayment(models.Model):
    """Credit & Repayment Behavior"""
    
    application = models.OneToOneField(MSMEApplication, on_delete=models.CASCADE, related_name='credit_repayment')
    
    # 1. Repayment Discipline
    on_time_repayment_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                  validators=[MinValueValidator(0), MaxValueValidator(1)])
    last_6_months_payment_history = models.JSONField(default=list, help_text="Monthly payment status")
    bounced_cheques_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    # 2. Debt Position
    current_debt = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_debt_status = models.CharField(max_length=20, choices=[
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High')
    ], default='low')
    historical_loan_utilization = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # 3. Regular Payments
    rent_payment_regularity = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    supplier_payment_regularity = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    utility_payment_on_time_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_credit_repayment'
        verbose_name = 'Credit & Repayment'
        verbose_name_plural = 'Credit & Repayment'
    
    def __str__(self):
        return f"Credit - {self.application.company_name}"


# ==================== F) COMPLIANCE & TAXATION ====================

class ComplianceTaxation(models.Model):
    """Compliance & Taxation Metrics"""
    
    application = models.OneToOneField(MSMEApplication, on_delete=models.CASCADE, related_name='compliance_taxation')
    
    # 1. GST / ITR Discipline
    gst_filing_regularity = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                               help_text="Percentage of on-time GST filings")
    itr_filed = models.BooleanField(default=False, help_text="Income Tax Return filed")
    gst_filing_on_time_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # 2. Mismatch Checks
    gst_platform_sales_mismatch = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                      help_text="Percentage mismatch")
    gst_r1_itr_mismatch = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                              help_text="Percentage mismatch between GST R1 and ITR")
    
    # 3. Tax Payments
    tax_payment_regularity = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # 4. Refund Risk
    refund_chargeback_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_compliance_taxation'
        verbose_name = 'Compliance & Taxation'
        verbose_name_plural = 'Compliance & Taxation'
    
    def __str__(self):
        return f"Compliance - {self.application.company_name}"


# ==================== G) FRAUD & VERIFICATION ====================

class FraudVerification(models.Model):
    """Fraud & Verification Checks"""
    
    application = models.OneToOneField(MSMEApplication, on_delete=models.CASCADE, related_name='fraud_verification')
    
    # 1. KYC & Identity
    kyc_completion_score = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                              validators=[MinValueValidator(0), MaxValueValidator(1)])
    
    # 2. Shop Verification
    shop_image_verified = models.BooleanField(default=False)
    shop_verification_data = models.JSONField(default=dict, help_text="Photo + geolocation data")
    
    # 3. Banking Fraud Signals
    circular_transaction_detected = models.BooleanField(default=False, 
                                                        help_text="First 7 vs last 7 days check")
    font_variation_detected = models.BooleanField(default=False, help_text="Bank statement font check")
    bank_statement_ocr_verified = models.BooleanField(default=False)
    
    # Fraud risk score
    overall_fraud_risk = models.CharField(max_length=20, default='low', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_fraud_verification'
        verbose_name = 'Fraud & Verification'
        verbose_name_plural = 'Fraud & Verification'
    
    def __str__(self):
        return f"Fraud Check - {self.application.company_name}"


# ==================== H) EXTERNAL SIGNALS ====================

class ExternalSignals(models.Model):
    """External Signals & Market Reputation"""
    
    application = models.OneToOneField(MSMEApplication, on_delete=models.CASCADE, related_name='external_signals')
    
    # Reviews & Online Reputation
    online_reviews_count = models.IntegerField(default=0)
    online_reviews_avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0,
                                                    validators=[MinValueValidator(0), MaxValueValidator(5)])
    review_sentiment = models.CharField(max_length=20, choices=[
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative')
    ], default='neutral')
    review_sentiment_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_external_signals'
        verbose_name = 'External Signals'
        verbose_name_plural = 'External Signals'
    
    def __str__(self):
        return f"External - {self.application.company_name}"


# ==================== I) VENDOR PAYMENTS & EXPENSE SIGNALS ====================

class VendorPayments(models.Model):
    """Vendor Payments & Expense Analysis"""
    
    application = models.OneToOneField(MSMEApplication, on_delete=models.CASCADE, related_name='vendor_payments')
    
    # 1. Vendor Payment Behavior
    vendor_payment_consistency = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    verified_vendors_count = models.IntegerField(default=0)
    total_vendors_count = models.IntegerField(default=0)
    vendor_verification_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # 2. Vendor Strength (GST2B)
    long_term_vendors_count = models.IntegerField(default=0, help_text="Vendors > 12 months")
    long_term_vendors_data = models.JSONField(default=list)
    
    # 3. Vendor Transaction Analytics
    avg_vendor_transaction_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    vendor_concentration_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                                     help_text="Top vendor dependency")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_vendor_payments'
        verbose_name = 'Vendor Payments'
        verbose_name_plural = 'Vendor Payments'
    
    def __str__(self):
        return f"Vendors - {self.application.company_name}"


# ==================== DATA UPLOADS ====================

class MSMEDocumentUpload(models.Model):
    """Document uploads for MSME applications"""
    
    application = models.ForeignKey(MSMEApplication, on_delete=models.CASCADE, related_name='documents')
    
    document_type = models.CharField(max_length=50, choices=[
        ('bank_statement', 'Bank Statement'),
        ('gst_return', 'GST Return'),
        ('itr', 'Income Tax Return'),
        ('shop_image', 'Shop Image'),
        ('license', 'License/Certificate'),
        ('other', 'Other')
    ])
    file = models.FileField(upload_to='msme_documents/%Y/%m/%d/')
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField(default=0, help_text="Size in bytes")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'msme_document_uploads'
        ordering = ['-uploaded_at']
        verbose_name = 'MSME Document Upload'
        verbose_name_plural = 'MSME Document Uploads'
    
    def __str__(self):
        return f"{self.document_type} - {self.application.company_name}"


# ==================== ANALYSIS RESULTS ====================

class MSMEAnalysisResult(models.Model):
    """Complete MSME Analysis Results"""
    
    application = models.OneToOneField(MSMEApplication, on_delete=models.CASCADE, related_name='analysis_result')
    
    # Aggregated Features
    all_features = models.JSONField(default=dict, help_text="All extracted features")
    
    # Section Scores
    director_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    business_identity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    revenue_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    cashflow_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    credit_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    compliance_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    fraud_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    external_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    vendor_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Final Results
    final_credit_score = models.IntegerField(null=True, blank=True)
    default_probability = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True)
    risk_tier = models.CharField(max_length=20, null=True, blank=True)
    overdraft_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    recommended_interest_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # SHAP Explainability
    shap_values = models.JSONField(default=dict, help_text="SHAP explanation values")
    feature_importance = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_analysis_results'
        verbose_name = 'MSME Analysis Result'
        verbose_name_plural = 'MSME Analysis Results'
    
    def __str__(self):
        return f"Analysis - {self.application.company_name} - Score: {self.final_credit_score}"
