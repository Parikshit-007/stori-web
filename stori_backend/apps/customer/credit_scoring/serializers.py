from rest_framework import serializers


class CreditScoreInputSerializer(serializers.Serializer):
    """
    Input serializer for credit scoring
    Accepts comprehensive consumer financial data
    """
    
    # Identity & Demographics
    name_dob_verified = serializers.IntegerField(required=False, min_value=0, max_value=1, default=0)
    pan_verified = serializers.IntegerField(required=False, min_value=0, max_value=1, default=0)
    aadhaar_verified = serializers.IntegerField(required=False, min_value=0, max_value=1, default=0)
    phone_verified = serializers.IntegerField(required=False, min_value=0, max_value=1, default=0)
    phone_age_months = serializers.FloatField(required=False, min_value=0, default=0)
    email_verified = serializers.IntegerField(required=False, min_value=0, max_value=1, default=0)
    email_age_months = serializers.FloatField(required=False, min_value=0, default=0)
    age = serializers.IntegerField(required=False, min_value=18, max_value=100, default=30)
    education_level = serializers.IntegerField(required=False, min_value=0, max_value=5, default=3)
    dependents_count = serializers.IntegerField(required=False, min_value=0, default=0)
    
    # Employment & Income
    employment_type = serializers.IntegerField(required=False, default=3)
    employment_tenure_months = serializers.FloatField(required=False, min_value=0, default=12)
    job_changes_3y = serializers.IntegerField(required=False, min_value=0, default=0)
    monthly_income = serializers.FloatField(required=False, min_value=0, default=50000)
    monthly_income_stability = serializers.FloatField(required=False, min_value=0, max_value=1, default=0.8)
    income_cv = serializers.FloatField(required=False, min_value=0, default=0.1)
    income_source_verification = serializers.IntegerField(required=False, min_value=0, max_value=1, default=0)
    employment_history_score = serializers.FloatField(required=False, min_value=0, max_value=100, default=70)
    
    # Assets & Liabilities
    total_financial_assets = serializers.FloatField(required=False, min_value=0, default=0)
    liquid_assets = serializers.FloatField(required=False, min_value=0, default=0)
    property_owned = serializers.IntegerField(required=False, min_value=0, max_value=1, default=0)
    vehicle_owned = serializers.IntegerField(required=False, min_value=0, max_value=1, default=0)
    
    # Credit Bureau Data
    credit_score = serializers.IntegerField(required=False, min_value=300, max_value=900, default=0)
    credit_accounts_total = serializers.IntegerField(required=False, min_value=0, default=0)
    credit_accounts_active = serializers.IntegerField(required=False, min_value=0, default=0)
    credit_utilization_ratio = serializers.FloatField(required=False, min_value=0, default=0)
    dpd_30_count = serializers.IntegerField(required=False, min_value=0, default=0)
    dpd_60_count = serializers.IntegerField(required=False, min_value=0, default=0)
    dpd_90_count = serializers.IntegerField(required=False, min_value=0, default=0)
    credit_enquiries_3m = serializers.IntegerField(required=False, min_value=0, default=0)
    credit_enquiries_6m = serializers.IntegerField(required=False, min_value=0, default=0)
    
    # Banking Behavior
    avg_monthly_credits = serializers.FloatField(required=False, min_value=0, default=0)
    avg_monthly_debits = serializers.FloatField(required=False, min_value=0, default=0)
    avg_balance = serializers.FloatField(required=False, default=0)
    min_balance = serializers.FloatField(required=False, default=0)
    balance_volatility = serializers.FloatField(required=False, min_value=0, default=0)
    negative_balance_days_ratio = serializers.FloatField(required=False, min_value=0, max_value=1, default=0)
    
    # Optional: Can add more fields as needed
    
    class Meta:
        fields = '__all__'


class CreditScoreOutputSerializer(serializers.Serializer):
    """Output serializer for credit score response"""
    
    success = serializers.BooleanField()
    credit_score = serializers.IntegerField()
    default_probability = serializers.FloatField()
    risk_tier = serializers.CharField()
    risk_description = serializers.CharField()
    recommendation = serializers.CharField()
    feature_importance = serializers.ListField()
    model_info = serializers.DictField()

