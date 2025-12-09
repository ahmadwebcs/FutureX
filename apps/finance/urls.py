from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import ROIDistributionViewSet, PaymentScheduleViewSet, StatementViewSet, ForecastViewSet, CalculateMonthlyROIView

router = DefaultRouter()
router.register(r'roi', ROIDistributionViewSet, basename='roi')
router.register(r'payments', PaymentScheduleViewSet, basename='payments')
router.register(r'statements', StatementViewSet, basename='statements')
router.register(r'forecasts', ForecastViewSet, basename='forecasts')

urlpatterns = [
    path('', include(router.urls)),
    path("calculate-monthly-roi/", CalculateMonthlyROIView.as_view())
]
