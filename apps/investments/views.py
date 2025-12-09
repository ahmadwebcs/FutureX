
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, viewsets
from apps.investments.models import Investment, PortfolioEntry, Withdrawal
from apps.investments.serializers import InvestmentCreateSerializer


class AddInvestmentView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = InvestmentCreateSerializer(data=request.data)
        if serializer.is_valid():
            investment = serializer.save()
            return Response({"message": "Investment added successfully.", "investment_id": str(investment.investment_id)},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvestmentViewSet(viewsets.ModelViewSet):
    queryset = Investment.objects.all()
    serializer_class = InvestmentCreateSerializer


class PortfolioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PortfolioEntry.objects.all()
    serializer_class = None

    def get_serializer_class(self):
        from .serializers import PortfolioEntrySerializer
        return PortfolioEntrySerializer


class WithdrawalViewSet(viewsets.ModelViewSet):
    queryset = Withdrawal.objects.all()
    serializer_class = None

    def get_serializer_class(self):
        from .serializers import WithdrawalSerializer
        return WithdrawalSerializer
    