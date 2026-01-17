"""
Business Bank Statement Models
===============================

Models for MSME business current account analysis
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class BusinessBankStatementUpload(models.Model):
    """Business bank statement upload (current account)"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_bank_uploads')
    
    # Business identification
    business_name = models.CharField(max_length=200)
    gstin = models.CharField(max_length=15, blank=True, help_text="GST Number")
    
    # Bank account details
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50, blank=True, help_text="Last 4 digits only")
    account_type = models.CharField(max_length=20, default='current', choices=[
        ('current', 'Current Account'),
        ('cc_od', 'Cash Credit / Overdraft'),
        ('savings', 'Savings'),
        ('other', 'Other')
    ])
    
    # File details
    file = models.FileField(upload_to='business_bank_statements/%Y/%m/%d/')
    file_type = models.CharField(max_length=20, choices=[
        ('xlsx', 'Excel (.xlsx)'),
        ('xls', 'Excel (.xls)'),
        ('pdf', 'PDF'),
        ('csv', 'CSV')
    ])
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField(default=0)
    
    # Statement period
    statement_start_date = models.DateField(null=True, blank=True)
    statement_end_date = models.DateField(null=True, blank=True)
    
    # Status
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'msme_business_bank_uploads'
        ordering = ['-uploaded_at']
        verbose_name = 'Business Bank Statement Upload'
        verbose_name_plural = 'Business Bank Statement Uploads'
    
    def __str__(self):
        return f"{self.business_name} - {self.bank_name}"


class BusinessBankAnalysisResult(models.Model):
    """
    Business banking analysis results
    
    Focused on cash flow, revenue patterns, and business health
    """
    
    upload = models.OneToOneField(
        BusinessBankStatementUpload,
        on_delete=models.CASCADE,
        related_name='analysis_result'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='business_bank_results')
    
    # ========== A) Bank Balance Metrics ==========
    
    average_bank_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    min_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    max_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    balance_trend = models.CharField(max_length=20, default='stable', choices=[
        ('increasing', 'Increasing'),
        ('stable', 'Stable'),
        ('decreasing', 'Decreasing')
    ])
    
    negative_balance_days = models.IntegerField(default=0, help_text="Days with negative/OD balance")
    avg_daily_closing_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Balance volatility
    balance_volatility = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Standard deviation / mean"
    )
    
    # ========== B) Inflow/Outflow Analysis ==========
    
    total_inflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_outflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    net_cashflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    monthly_inflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monthly_outflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    inflow_outflow_ratio = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Healthy if > 1.0"
    )
    
    # Inflow/outflow patterns
    inflow_trend = models.CharField(max_length=20, default='stable', choices=[
        ('increasing', 'Increasing'),
        ('stable', 'Stable'),
        ('decreasing', 'Decreasing')
    ])
    
    # ========== C) Revenue Patterns ==========
    
    # Estimated monthly revenue (from credits)
    estimated_monthly_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Revenue consistency
    revenue_consistency_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="0-1, higher is better"
    )
    
    # Revenue growth
    mom_revenue_growth = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Month-over-month revenue growth %"
    )
    
    # Cash vs digital ratio
    cash_inflow_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    digital_inflow_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # ========== D) Expense Patterns ==========
    
    # Monthly operating expenses
    monthly_operating_expenses = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Major expense categories
    salary_payments = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    rent_payments = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    vendor_payments = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    utility_payments = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Expense regularity
    fixed_expense_ratio = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Fixed expenses / Total expenses"
    )
    
    # ========== E) Transaction Analysis ==========
    
    total_transactions = models.IntegerField(default=0)
    avg_transaction_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Daily transaction patterns
    avg_daily_transactions = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Credit/debit split
    credit_transactions = models.IntegerField(default=0)
    debit_transactions = models.IntegerField(default=0)
    
    # ========== F) Deposit Consistency ==========
    
    deposit_consistency_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Display only - NOT for scoring"
    )
    
    deposit_frequency_days = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Average days between deposits"
    )
    
    # ========== G) P2P & Cash Handling ==========
    
    # P2P transactions (should be excluded from revenue)
    p2p_inflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    p2p_outflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    p2p_net = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Cash deposits (red flag if too high)
    cash_deposit_ratio = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="% of inflow from cash deposits"
    )
    
    # ========== H) Bounce & Risk Indicators ==========
    
    bounce_count = models.IntegerField(default=0, help_text="Check/ECS bounces")
    bounce_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Circular transactions
    circular_transaction_detected = models.BooleanField(
        default=False,
        help_text="First 7 vs last 7 days check"
    )
    
    # ========== I) Loan/Credit Facility Usage ==========
    
    # OD/CC usage
    od_cc_usage_detected = models.BooleanField(default=False)
    avg_od_cc_utilization = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Average OD/CC utilization %"
    )
    
    # Loan EMIs detected
    loan_emi_detected = models.BooleanField(default=False)
    estimated_monthly_emi = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # ========== J) Data Quality ==========
    
    months_of_data = models.IntegerField(default=0)
    data_completeness_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # ========== K) Summary Metrics ==========
    
    # Overall health score
    cashflow_health_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall cash flow health (0-100)"
    )
    
    business_risk_category = models.CharField(max_length=20, default='medium', choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk')
    ])
    
    # Monthly data breakdown
    monthly_data = models.JSONField(
        default=dict,
        help_text="Month-wise breakdown of key metrics"
    )
    
    # All extracted features
    all_features = models.JSONField(default=dict)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_business_bank_results'
        ordering = ['-created_at']
        verbose_name = 'Business Bank Analysis Result'
        verbose_name_plural = 'Business Bank Analysis Results'
    
    def __str__(self):
        return f"Business Banking - {self.upload.business_name} - Score: {self.cashflow_health_score}"

