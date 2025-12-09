from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import AddInvestmentView, InvestmentViewSet, PortfolioViewSet, WithdrawalViewSet

router = DefaultRouter()
router.register(r'investments', InvestmentViewSet, basename='investment')
router.register(r'portfolio', PortfolioViewSet, basename='portfolio')
router.register(r'withdrawals', WithdrawalViewSet, basename='withdrawal')

urlpatterns = [
    path('add/', AddInvestmentView.as_view(), name='investment-add'),
    path('', include(router.urls)),
]
