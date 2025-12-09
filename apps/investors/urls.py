from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import InvestorRegisterView, InvestorViewSet, KYCDocumentViewSet, DigitalSignatureViewSet, OnboardingApprovalViewSet

router = DefaultRouter()
router.register(r'investors', InvestorViewSet, basename='investor')
router.register(r'kyc-docs', KYCDocumentViewSet, basename='kyc-doc')
router.register(r'signatures', DigitalSignatureViewSet, basename='signature')
router.register(r'approvals', OnboardingApprovalViewSet, basename='approval')

urlpatterns = [
    path('register/', InvestorRegisterView.as_view(), name='investor-register'),
    path('', include(router.urls)),
]
