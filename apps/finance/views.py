from rest_framework import viewsets
from .models import ROIDistribution, PaymentSchedule, Statement, Forecast
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from apps.investors.models import Investor
from decimal import Decimal
from django.utils import timezone
from rest_framework.views import APIView
from .serializers import ROICalculationSerializer

class ROIDistributionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ROIDistribution.objects.all()
    serializer_class = None

    def get_serializer_class(self):
        from .serializers import ROIDistributionSerializer
        return ROIDistributionSerializer


class PaymentScheduleViewSet(viewsets.ModelViewSet):
    queryset = PaymentSchedule.objects.all()
    serializer_class = None

    def get_serializer_class(self):
        from .serializers import PaymentScheduleSerializer
        return PaymentScheduleSerializer


class StatementViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Statement.objects.all()
    serializer_class = None

    def get_serializer_class(self):
        from .serializers import StatementSerializer
        return StatementSerializer


class ForecastViewSet(viewsets.ModelViewSet):
    queryset = Forecast.objects.all()
    serializer_class = None

    def get_serializer_class(self):
        from .serializers import ForecastSerializer
        return ForecastSerializer

    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        investor_id = request.data.get('investor')
        if not investor_id:
            return Response({'detail': 'investor is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            investor = Investor.objects.get(pk=investor_id)
        except Investor.DoesNotExist:
            return Response({'detail': 'investor not found'}, status=status.HTTP_404_NOT_FOUND)

        # naive forecast: sum current investments and project 24% annual growth compounded monthly
        investments = investor.investments.filter(status='Active')
        total = sum(inv.amount for inv in investments)
        months = int(request.data.get('months', 12))
        rate = Decimal('0.24')
        monthly = rate / Decimal('12')
        projection = []
        current = Decimal(total)
        for m in range(1, months + 1):
            current = (current * (1 + monthly)).quantize(Decimal('0.01'))
            projection.append({'month': m, 'value': str(current)})

        forecast = Forecast.objects.create(investor=investor, data={'projection': projection, 'generated_at': str(timezone.now())})
        return Response({'forecast_id': str(forecast.forecast_id), 'projection': projection})


class CalculateMonthlyROIView(APIView):
    """
    POST /api/finance/calculate-monthly-roi/
    """

    permission_classes = []  # Admin access in production

    def post(self, request, *args, **kwargs):
        serializer = ROICalculationSerializer(data={})
        if serializer.is_valid():
            result = serializer.save()
            return Response(
                {
                    "message": "Monthly ROI calculated successfully.",
                    "month": result["month"],
                    "records_created": result["records_created"],
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
