"""
GST Analysis Models
===================

Models for storing GST data and analysis results
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal


class GSTUpload(models.Model):
    """GST Return Upload Model"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gst_uploads')
    gstin = models.CharField(max_length=15, help_text="GST Identification Number")
    
    # File details
    file = models.FileField(upload_to='gst_returns/%Y/%m/%d/')
    file_type = models.CharField(max_length=20, choices=[
        ('json', 'JSON'),
        ('pdf', 'PDF'),
        ('excel', 'Excel')
    ])
    file_name = models.CharField(max_length=255)
    file_size = models.IntegerField(default=0, help_text="Size in bytes")
    
    # Return details
    return_type = models.CharField(max_length=20, choices=[
        ('gstr1', 'GSTR-1 (Outward Supply)'),
        ('gstr3b', 'GSTR-3B (Summary)'),
        ('gstr2a', 'GSTR-2A (Inward Supply)'),
        ('gstr2b', 'GSTR-2B (Auto-drafted ITC)')
    ])
    return_period = models.CharField(max_length=10, help_text="Format: MM-YYYY")
    financial_year = models.CharField(max_length=10, help_text="Format: YYYY-YY")
    
    # Status
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    processing_error = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'msme_gst_uploads'
        ordering = ['-uploaded_at']
        verbose_name = 'GST Upload'
        verbose_name_plural = 'GST Uploads'
        unique_together = ['gstin', 'return_type', 'return_period']
    
    def __str__(self):
        return f"{self.gstin} - {self.return_type} - {self.return_period}"


class GSTAnalysisResult(models.Model):
    """GST Analysis Results"""
    
    upload = models.OneToOneField(GSTUpload, on_delete=models.CASCADE, related_name='analysis_result')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gst_analysis_results')
    
    # ========== A) GST/ITR Discipline ==========
    
    # Filing regularity
    gst_filing_regularity = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Percentage of on-time filings in last 12 months"
    )
    total_expected_filings = models.IntegerField(default=12, help_text="Expected filings in period")
    actual_filings = models.IntegerField(default=0, help_text="Actual filings submitted")
    late_filings = models.IntegerField(default=0, help_text="Late submissions")
    missed_filings = models.IntegerField(default=0, help_text="Missed submissions")
    
    # ITR cross-check
    itr_filed = models.BooleanField(default=False, help_text="Income Tax Return filed for FY")
    itr_filing_date = models.DateField(null=True, blank=True)
    
    # ========== B) Revenue & Turnover ==========
    
    # Monthly revenue from GST
    monthly_revenue = models.JSONField(
        default=dict,
        help_text="Month-wise revenue: {MM-YYYY: amount}"
    )
    total_revenue_fy = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text="Total revenue for financial year"
    )
    avg_monthly_revenue = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    
    # Revenue trends
    mom_revenue_growth = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Month-over-Month revenue growth %"
    )
    qoq_revenue_growth = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Quarter-over-Quarter revenue growth %"
    )
    revenue_volatility = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Coefficient of variation in monthly revenue"
    )
    
    # ========== C) Tax & Compliance ==========
    
    # Tax amounts
    total_gst_liability = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text="Total GST payable in period"
    )
    total_gst_paid = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text="Total GST actually paid"
    )
    outstanding_gst = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text="Pending GST payment"
    )
    
    # Payment discipline
    tax_payment_regularity = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Score 0-1 for payment discipline"
    )
    
    # ========== D) Mismatch Checks ==========
    
    # GST R1 vs ITR
    gst_r1_revenue = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text="Revenue declared in GSTR-1"
    )
    itr_revenue = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text="Revenue in ITR"
    )
    gst_r1_itr_mismatch = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Percentage mismatch"
    )
    mismatch_flag = models.BooleanField(default=False, help_text="True if mismatch > 5%")
    
    # GST vs Platform sales (for e-commerce)
    platform_sales = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        null=True, blank=True,
        help_text="Sales from platform data (Shopify, Amazon, etc.)"
    )
    gst_platform_sales_mismatch = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Percentage mismatch"
    )
    
    # ========== E) Input Tax Credit (ITC) ==========
    
    # ITC claims
    total_itc_claimed = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text="Total Input Tax Credit claimed"
    )
    total_itc_utilized = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text="ITC actually utilized"
    )
    itc_balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=0,
        help_text="Unutilized ITC balance"
    )
    
    # ITC ratio
    itc_to_revenue_ratio = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="ITC claimed / Revenue %"
    )
    
    # ========== F) Vendor Analysis (from GSTR-2B) ==========
    
    # Vendor metrics
    total_vendors = models.IntegerField(default=0, help_text="Total unique vendors")
    verified_vendors = models.IntegerField(default=0, help_text="GST-verified vendors")
    vendor_verification_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Percentage of verified vendors"
    )
    
    # Vendor concentration
    top_vendor_concentration = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="% of purchases from top vendor"
    )
    top_3_vendor_concentration = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="% of purchases from top 3 vendors"
    )
    
    # Vendor stability
    long_term_vendors_count = models.IntegerField(
        default=0,
        help_text="Vendors transacting for > 6 months"
    )
    long_term_vendor_percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )
    
    # ========== G) Industry Benchmarks ==========
    
    industry = models.CharField(max_length=100, blank=True)
    effective_gst_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Effective GST rate = GST Liability / Revenue"
    )
    
    # ========== H) Risk Indicators ==========
    
    # Compliance score (0-100)
    compliance_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall compliance score"
    )
    
    # Risk flags
    risk_flags = models.JSONField(
        default=list,
        help_text="List of detected risk indicators"
    )
    risk_level = models.CharField(max_length=20, default='low', choices=[
        ('low', 'Low Risk'),
        ('medium', 'Medium Risk'),
        ('high', 'High Risk')
    ])
    
    # ========== I) Additional Data ==========
    
    # HSN/SAC code analysis
    hsn_sac_codes = models.JSONField(
        default=list,
        help_text="List of HSN/SAC codes used"
    )
    primary_business_activity = models.CharField(
        max_length=200, blank=True,
        help_text="Derived from HSN/SAC codes"
    )
    
    # Geographic spread
    gst_locations = models.JSONField(
        default=list,
        help_text="List of GST registration locations"
    )
    multi_state_operations = models.BooleanField(
        default=False,
        help_text="Operating in multiple states"
    )
    
    # Raw data
    raw_gst_data = models.JSONField(
        default=dict,
        help_text="Complete GST return data"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_gst_analysis_results'
        ordering = ['-created_at']
        verbose_name = 'GST Analysis Result'
        verbose_name_plural = 'GST Analysis Results'
    
    def __str__(self):
        return f"GST Analysis - {self.upload.gstin} - Score: {self.compliance_score}"


class GSTFilingHistory(models.Model):
    """Track GST filing history for regularity analysis"""
    
    gstin = models.CharField(max_length=15, db_index=True)
    return_type = models.CharField(max_length=20)
    return_period = models.CharField(max_length=10, help_text="MM-YYYY")
    due_date = models.DateField(help_text="Due date for this return")
    filed_date = models.DateField(null=True, blank=True, help_text="Actual filing date")
    
    # Status
    status = models.CharField(max_length=20, default='pending', choices=[
        ('filed_on_time', 'Filed On Time'),
        ('filed_late', 'Filed Late'),
        ('not_filed', 'Not Filed'),
        ('nil_return', 'Nil Return')
    ])
    
    days_delay = models.IntegerField(
        default=0,
        help_text="Days delayed from due date (negative if filed early)"
    )
    
    # Revenue for this period
    revenue_declared = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    gst_liability = models.DecimalField(
        max_digits=15, decimal_places=2, default=0
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'msme_gst_filing_history'
        ordering = ['-return_period']
        unique_together = ['gstin', 'return_type', 'return_period']
        verbose_name = 'GST Filing History'
        verbose_name_plural = 'GST Filing Histories'
    
    def __str__(self):
        return f"{self.gstin} - {self.return_type} - {self.return_period} - {self.status}"

