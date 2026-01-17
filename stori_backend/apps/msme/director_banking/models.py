"""
Director Personal Banking Models
=================================

Models for director personal bank statement analysis
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class DirectorBankStatementUpload(models.Model):
    """Director personal bank statement upload"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='director_bank_uploads')
    
    # Director identification
    director_name = models.CharField(max_length=200)
    director_pan = models.CharField(max_length=10, help_text="Director's PAN")
    
    # Bank account details
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True, help_text="Last 4 digits only")
    account_type = models.CharField(max_length=20, choices=[
        ('savings', 'Savings'),
        ('current', 'Current'),
        ('salary', 'Salary'),
        ('other', 'Other')
    ], default='savings')
    
    # File details
    file = models.FileField(upload_to='director_bank_statements/%Y/%m/%d/')
    file_type = models.CharField(max_length=20, choices=[
        ('xlsx', 'Excel (.xlsx)'),
        ('xls', 'Excel (.xls)'),
        ('pdf', 'PDF'),
        ('csv', 'CSV')
    ])
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField(default=0, help_text="Size in bytes")
    
    # Statement period
    statement_start_date = models.DateField(null=True, blank=True)
    statement_end_date = models.DateField(null=True, blank=True)
    
    # Status
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'msme_director_bank_uploads'
        ordering = ['-uploaded_at']
        verbose_name = 'Director Bank Statement Upload'
        verbose_name_plural = 'Director Bank Statement Uploads'
    
    def __str__(self):
        return f"{self.director_name} ({self.director_pan}) - {self.bank_name}"


class DirectorBankAnalysisResult(models.Model):
    """
    Director personal banking analysis results
    
    Uses all features from consumer bank statement analysis
    """
    
    upload = models.OneToOneField(
        DirectorBankStatementUpload,
        on_delete=models.CASCADE,
        related_name='analysis_result'
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='director_bank_results')
    
    # ========== Core Financial Features (8) ==========
    
    monthly_income = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    monthly_expense = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    income_stability = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    spending_to_income = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    min_balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance_volatility = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    survivability_months = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # ========== Behavioral Features (2) ==========
    
    late_night_txn_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    weekend_txn_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # ========== EMI/Loan Features (2) ==========
    
    estimated_emi = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    emi_to_income = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # ========== Data Quality Features (4) ==========
    
    data_confidence = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    num_bank_accounts = models.IntegerField(default=1)
    txn_count = models.IntegerField(default=0)
    months_of_data = models.IntegerField(default=0)
    
    # ========== Risk Indicators (3) ==========
    
    bounce_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    max_inflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    max_outflow = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # ========== Advanced Transaction Analysis (8) ==========
    
    upi_p2p_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    utility_to_income = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    utility_payment_consistency = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    insurance_payment_detected = models.BooleanField(default=False)
    rent_to_income = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    inflow_time_consistency = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    manipulation_risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    expense_rigidity = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # ========== Behavioral & Impulse Features (5) ==========
    
    salary_retention_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    week1_vs_week4_spending_ratio = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    impulse_spending_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    upi_volume_spike_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_balance_drop_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # ========== Additional MSME-specific fields ==========
    
    # Assets & Liabilities derived from bank statement
    assets_derived = models.JSONField(default=dict, help_text="Assets breakdown")
    liabilities_derived = models.JSONField(default=dict, help_text="Liabilities breakdown")
    
    # Stability indicators
    regular_p2p_transactions = models.BooleanField(default=False)
    income_volatility = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Subscriptions & commitments
    subscriptions = models.JSONField(default=list, help_text="Recurring subscriptions detected")
    micro_commitments = models.JSONField(default=list, help_text="Small recurring payments")
    
    # Savings behavior
    savings_consistency_score = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    # Financial stability flag
    is_stable = models.BooleanField(default=True, help_text="Stable if income change < 30%")
    income_change_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # ========== Summary Score ==========
    
    overall_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall financial health score (0-100)"
    )
    risk_category = models.CharField(max_length=20, default='medium', choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk')
    ])
    
    # Raw features JSON (all 38 features)
    all_features = models.JSONField(default=dict, help_text="Complete feature vector")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_director_bank_results'
        ordering = ['-created_at']
        verbose_name = 'Director Bank Analysis Result'
        verbose_name_plural = 'Director Bank Analysis Results'
    
    def __str__(self):
        return f"Bank Analysis - {self.upload.director_name} - Score: {self.overall_score}"

