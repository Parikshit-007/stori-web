"""
MSME Views
==========

DRF ViewSets for MSME credit scoring and analysis
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import (
    MSMEApplication, DirectorProfile, BusinessIdentity, RevenuePerformance,
    CashFlowBanking, CreditRepayment, ComplianceTaxation, FraudVerification,
    ExternalSignals, VendorPayments, MSMEDocumentUpload, MSMEAnalysisResult
)
from .serializers import (
    MSMEApplicationSerializer, MSMEApplicationDetailSerializer,
    DirectorProfileSerializer, BusinessIdentitySerializer, RevenuePerformanceSerializer,
    CashFlowBankingSerializer, CreditRepaymentSerializer, ComplianceTaxationSerializer,
    FraudVerificationSerializer, ExternalSignalsSerializer, VendorPaymentsSerializer,
    MSMEDocumentUploadSerializer, MSMEAnalysisResultSerializer,
    MSMEAnalysisInputSerializer, DirectorAnalysisInputSerializer,
    RevenueAnalysisInputSerializer, CashFlowAnalysisInputSerializer,
    ComplianceAnalysisInputSerializer
)
from .analyzers.master_analyzer import MSMEMasterAnalyzer
from .analyzers import (
    DirectorAnalyzer, RevenueAnalyzer, CashFlowAnalyzer, ComplianceAnalyzer
)


class MSMEApplicationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MSME Application management and analysis
    
    Endpoints:
    - list: Get all applications for user
    - retrieve: Get specific application with all details
    - create: Create new MSME application
    - update/patch: Update application
    - delete: Delete application
    - analyze: Perform complete MSME analysis
    - quick_score: Get quick credit score estimate
    """
    
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return MSMEApplicationDetailSerializer
        return MSMEApplicationSerializer
    
    def get_queryset(self):
        """Filter applications by user"""
        return MSMEApplication.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create application for current user"""
        # Generate application number
        import uuid
        from datetime import datetime
        
        app_number = f"MSME-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        
        serializer.save(
            user=self.request.user,
            application_number=app_number
        )
    
    @action(detail=True, methods=['post'])
    def analyze(self, request, pk=None):
        """
        Perform comprehensive MSME analysis
        
        POST /api/msme/applications/{id}/analyze/
        
        Body: Complete MSME data for all sections
        """
        application = self.get_object()
        
        try:
            # Get analysis input
            input_serializer = MSMEAnalysisInputSerializer(data=request.data)
            
            if not input_serializer.is_valid():
                return Response({
                    'success': False,
                    'message': 'Invalid input data',
                    'errors': input_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            analysis_data = input_serializer.validated_data
            
            # Perform analysis using master analyzer
            master_analyzer = MSMEMasterAnalyzer()
            analysis_results = master_analyzer.analyze_complete_msme(analysis_data)
            
            if 'error' in analysis_results:
                return Response({
                    'success': False,
                    'message': f'Analysis failed: {analysis_results["error"]}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Update application with results
            application.final_credit_score = analysis_results['final_score']
            application.risk_tier = analysis_results['risk_tier']
            application.status = 'in_review'
            application.save()
            
            # Save detailed analysis results
            analysis_result, created = MSMEAnalysisResult.objects.update_or_create(
                application=application,
                defaults={
                    'all_features': analysis_results['all_features'],
                    'director_score': analysis_results['section_scores'].get('director', 0),
                    'business_identity_score': analysis_results['section_scores'].get('business_identity', 0),
                    'revenue_score': analysis_results['section_scores'].get('revenue', 0),
                    'cashflow_score': analysis_results['section_scores'].get('cashflow', 0),
                    'credit_score': analysis_results['section_scores'].get('credit', 0),
                    'compliance_score': analysis_results['section_scores'].get('compliance', 0),
                    'fraud_score': analysis_results['section_scores'].get('fraud', 0),
                    'external_score': analysis_results['section_scores'].get('external', 0),
                    'vendor_score': analysis_results['section_scores'].get('vendor', 0),
                    'final_credit_score': analysis_results['final_score'],
                    'default_probability': analysis_results['default_probability'],
                    'risk_tier': analysis_results['risk_tier'],
                }
            )
            
            # Save individual section data
            self._save_section_data(application, analysis_results, analysis_data)
            
            return Response({
                'success': True,
                'message': 'Analysis completed successfully',
                'data': {
                    'application_id': application.id,
                    'credit_score': analysis_results['final_score'],
                    'risk_tier': analysis_results['risk_tier'],
                    'default_probability': analysis_results['default_probability'],
                    'section_scores': analysis_results['section_scores'],
                    'section_results': analysis_results['section_results']
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Analysis failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def quick_score(self, request):
        """
        Get quick credit score without saving application
        
        POST /api/msme/applications/quick_score/
        """
        try:
            input_serializer = MSMEAnalysisInputSerializer(data=request.data)
            
            if not input_serializer.is_valid():
                return Response({
                    'success': False,
                    'errors': input_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Perform analysis
            master_analyzer = MSMEMasterAnalyzer()
            results = master_analyzer.analyze_complete_msme(input_serializer.validated_data)
            
            return Response({
                'success': True,
                'credit_score': results['final_score'],
                'risk_tier': results['risk_tier'],
                'default_probability': results['default_probability'],
                'section_scores': results['section_scores']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def analysis_result(self, request, pk=None):
        """
        Get detailed analysis result for an application
        
        GET /api/msme/applications/{id}/analysis_result/
        """
        application = self.get_object()
        
        try:
            result = application.analysis_result
            serializer = MSMEAnalysisResultSerializer(result)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except MSMEAnalysisResult.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Analysis not yet performed for this application'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def _save_section_data(self, application, analysis_results, input_data):
        """Save data to individual section models"""
        try:
            # Save director profiles
            if 'director_data' in input_data:
                director_results = analysis_results['section_results']['director']
                self._save_director_data(application, input_data['director_data'], director_results)
            
            # Save business identity
            if 'business_data' in input_data:
                business_results = analysis_results['section_results']['business_identity']
                self._save_business_identity(application, input_data, business_results)
            
            # Save revenue performance
            if 'revenue_data' in input_data:
                revenue_results = analysis_results['section_results']['revenue']
                self._save_revenue_performance(application, revenue_results)
            
            # Save cashflow banking
            if 'bank_data' in input_data:
                cashflow_results = analysis_results['section_results']['cashflow']
                self._save_cashflow_banking(application, cashflow_results)
            
            # Save credit repayment
            if 'credit_report' in input_data or 'bank_data' in input_data:
                credit_results = analysis_results['section_results']['credit']
                self._save_credit_repayment(application, credit_results)
            
            # Save compliance
            if 'gst_data' in input_data:
                compliance_results = analysis_results['section_results']['compliance']
                self._save_compliance(application, compliance_results)
            
            # Save fraud verification
            if 'kyc_data' in input_data or 'shop_data' in input_data:
                fraud_results = analysis_results['section_results']['fraud']
                self._save_fraud_verification(application, fraud_results)
            
            # Save external signals
            if 'reviews_data' in input_data:
                external_results = analysis_results['section_results']['external']
                self._save_external_signals(application, external_results)
            
            # Save vendor payments
            if 'gst2b_data' in input_data:
                vendor_results = analysis_results['section_results']['vendor']
                self._save_vendor_payments(application, vendor_results)
                
        except Exception as e:
            # Log error but don't fail the analysis
            print(f"Error saving section data: {str(e)}")
    
    def _save_director_data(self, application, director_data, results):
        """Save director profile data"""
        # This is simplified - you'd want to handle multiple directors
        DirectorProfile.objects.update_or_create(
            application=application,
            pan=director_data.get('pan', ''),
            defaults={
                'name': director_data.get('name', ''),
                'age': director_data.get('age', 30),
                'address': director_data.get('address', ''),
                'phone_number': director_data.get('phone', ''),
                'monthly_income': results['behavioral_signals'].get('monthly_income', 0),
                'monthly_inflow': results['behavioral_signals'].get('monthly_inflow', 0),
                'monthly_outflow': results['behavioral_signals'].get('monthly_outflow', 0),
                'savings_consistency_score': results['behavioral_signals'].get('savings_consistency_score', 0),
                'is_stable': results['financial_stability'].get('is_stable', True),
            }
        )
    
    def _save_business_identity(self, application, input_data, results):
        """Save business identity data"""
        business_data = input_data.get('business_data', {})
        verification_data = input_data.get('verification_data', {})
        
        BusinessIdentity.objects.update_or_create(
            application=application,
            defaults={
                'company_name': application.company_name,
                'industry': business_data.get('industry', ''),
                'business_vintage_years': results['business_basics'].get('business_vintage_years', 0),
                'legal_entity_type': business_data.get('legal_entity_type', 'proprietorship'),
                'msme_category': application.msme_category,
                'gstin': verification_data.get('gstin', ''),
                'pan': verification_data.get('pan', ''),
                'verification_status': 'verified' if results['verification'].get('gstin_valid') else 'pending',
            }
        )
    
    def _save_revenue_performance(self, application, results):
        """Save revenue performance data"""
        revenue_metrics = results['revenue_metrics']
        profitability = results['profitability']
        
        RevenuePerformance.objects.update_or_create(
            application=application,
            defaults={
                'weekly_gtv': revenue_metrics.get('weekly_gtv', 0),
                'monthly_gtv': revenue_metrics.get('monthly_gtv', 0),
                'mom_growth': revenue_metrics.get('mom_growth', 0),
                'qoq_growth': revenue_metrics.get('qoq_growth', 0),
                'gross_profit_margin': profitability.get('gross_profit_margin', 0),
                'net_profit_margin': profitability.get('net_profit_margin', 0),
            }
        )
    
    def _save_cashflow_banking(self, application, results):
        """Save cashflow banking data"""
        balance_metrics = results['balance_metrics']
        inflow_outflow = results['inflow_outflow']
        
        CashFlowBanking.objects.update_or_create(
            application=application,
            defaults={
                'average_bank_balance': balance_metrics.get('average_bank_balance', 0),
                'balance_trend': balance_metrics.get('balance_trend', 'stable'),
                'negative_balance_days': balance_metrics.get('negative_balance_days', 0),
                'inflow_amount': inflow_outflow.get('inflow_amount', 0),
                'outflow_amount': inflow_outflow.get('outflow_amount', 0),
                'inflow_outflow_ratio': inflow_outflow.get('inflow_outflow_ratio', 0),
            }
        )
    
    def _save_credit_repayment(self, application, results):
        """Save credit repayment data"""
        repayment = results['repayment_discipline']
        debt = results['debt_position']
        regular = results['regular_payments']
        
        CreditRepayment.objects.update_or_create(
            application=application,
            defaults={
                'on_time_repayment_ratio': repayment.get('on_time_repayment_ratio', 0),
                'bounced_cheques_count': repayment.get('bounced_cheques_count', 0),
                'current_debt': debt.get('current_debt', 0),
                'total_debt_status': debt.get('total_debt_status', 'low'),
                'rent_payment_regularity': regular.get('rent_payment_regularity', 0),
                'supplier_payment_regularity': regular.get('supplier_payment_regularity', 0),
                'utility_payment_on_time_ratio': regular.get('utility_payment_on_time_ratio', 0),
            }
        )
    
    def _save_compliance(self, application, results):
        """Save compliance taxation data"""
        filing = results['gst_itr_discipline']
        mismatch = results['mismatch_checks']
        
        ComplianceTaxation.objects.update_or_create(
            application=application,
            defaults={
                'gst_filing_regularity': filing.get('gst_filing_regularity', 0),
                'itr_filed': filing.get('itr_filed', False),
                'gst_filing_on_time_ratio': filing.get('gst_filing_on_time_ratio', 0),
                'gst_platform_sales_mismatch': mismatch.get('gst_platform_sales_mismatch', 0),
                'gst_r1_itr_mismatch': mismatch.get('gst_r1_itr_mismatch', 0),
            }
        )
    
    def _save_fraud_verification(self, application, results):
        """Save fraud verification data"""
        kyc = results['kyc_completion']
        shop = results['shop_verification']
        fraud = results['fraud_signals']
        
        FraudVerification.objects.update_or_create(
            application=application,
            defaults={
                'kyc_completion_score': kyc.get('kyc_completion_score', 0),
                'shop_image_verified': shop.get('shop_image_verified', False),
                'circular_transaction_detected': fraud.get('circular_transaction_detected', False),
                'font_variation_detected': fraud.get('font_variation_detected', False),
                'bank_statement_ocr_verified': fraud.get('bank_statement_ocr_verified', True),
                'overall_fraud_risk': fraud.get('overall_fraud_risk', 'low'),
            }
        )
    
    def _save_external_signals(self, application, results):
        """Save external signals data"""
        reviews = results['online_reviews']
        
        ExternalSignals.objects.update_or_create(
            application=application,
            defaults={
                'online_reviews_count': reviews.get('online_reviews_count', 0),
                'online_reviews_avg_rating': reviews.get('online_reviews_avg_rating', 0),
                'review_sentiment': reviews.get('review_sentiment', 'neutral'),
                'review_sentiment_score': reviews.get('review_sentiment_score', 0),
            }
        )
    
    def _save_vendor_payments(self, application, results):
        """Save vendor payments data"""
        payment = results['payment_behavior']
        strength = results['vendor_strength']
        analytics = results['transaction_analytics']
        
        VendorPayments.objects.update_or_create(
            application=application,
            defaults={
                'vendor_payment_consistency': payment.get('vendor_payment_consistency', 0),
                'verified_vendors_count': payment.get('verified_vendors_count', 0),
                'total_vendors_count': payment.get('total_vendors_count', 0),
                'vendor_verification_rate': payment.get('vendor_verification_rate', 0),
                'long_term_vendors_count': strength.get('long_term_vendors_count', 0),
                'avg_vendor_transaction_value': analytics.get('avg_vendor_transaction_value', 0),
                'vendor_concentration_ratio': analytics.get('vendor_concentration_ratio', 0),
            }
        )


class MSMEDocumentUploadViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MSME document uploads
    
    Supports uploading and processing:
    - Bank statements
    - GST returns
    - ITR
    - Shop images
    - Licenses
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = MSMEDocumentUploadSerializer
    
    def get_queryset(self):
        """Filter documents by user's applications"""
        user_applications = MSMEApplication.objects.filter(user=self.request.user)
        return MSMEDocumentUpload.objects.filter(application__in=user_applications)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """
        Process uploaded document
        
        POST /api/msme/documents/{id}/process/
        """
        document = self.get_object()
        
        if document.processed:
            return Response({
                'success': False,
                'message': 'Document already processed'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Process document based on type
            # This would integrate with OCR/parsing services
            
            document.processed = True
            document.processed_at = timezone.now()
            document.save()
            
            return Response({
                'success': True,
                'message': 'Document processed successfully'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Processing failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== SECTION-SPECIFIC ANALYSIS VIEWS ====================

class SectionAnalysisViewSet(viewsets.ViewSet):
    """
    ViewSet for individual section analysis
    
    Provides endpoints to analyze specific sections independently
    """
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def director(self, request):
        """Analyze director section only"""
        serializer = DirectorAnalysisInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        analyzer = DirectorAnalyzer()
        data = serializer.validated_data
        
        results = {
            'personal_banking': analyzer.analyze_personal_banking(data['personal_bank_data']),
            'behavioral_signals': analyzer.analyze_behavioral_signals(data['personal_bank_data']),
            'financial_stability': analyzer.analyze_financial_stability(data['personal_bank_data'])
        }
        
        return Response({'success': True, 'results': results}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def revenue(self, request):
        """Analyze revenue section only"""
        serializer = RevenueAnalysisInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        analyzer = RevenueAnalyzer()
        data = serializer.validated_data
        
        results = {
            'revenue_metrics': analyzer.analyze_revenue_metrics(
                data['revenue_data'],
                data['msme_category']
            ),
            'profitability': analyzer.analyze_profitability(data['financial_data'])
        }
        
        return Response({'success': True, 'results': results}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def cashflow(self, request):
        """Analyze cashflow section only"""
        serializer = CashFlowAnalysisInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        analyzer = CashFlowAnalyzer()
        data = serializer.validated_data
        
        results = {
            'balance_metrics': analyzer.analyze_bank_balance_metrics(data['bank_data']),
            'inflow_outflow': analyzer.analyze_inflow_outflow(data['bank_data'])
        }
        
        return Response({'success': True, 'results': results}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def compliance(self, request):
        """Analyze compliance section only"""
        serializer = ComplianceAnalysisInputSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        analyzer = ComplianceAnalyzer()
        data = serializer.validated_data
        
        results = {
            'gst_itr_discipline': analyzer.analyze_gst_itr_discipline(
                data['gst_data'],
                data.get('itr_data')
            )
        }
        
        return Response({'success': True, 'results': results}, status=status.HTTP_200_OK)
