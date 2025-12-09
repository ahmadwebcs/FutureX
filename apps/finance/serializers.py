from rest_framework import serializers
from .models import ROIDistribution, PaymentSchedule, Statement, Forecast
from apps.investments.models import Investment
from datetime import datetime
from decimal import Decimal
class ROIDistributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ROIDistribution
        fields = ['roi_id', 'investment', 'investor', 'month', 'roi_amount', 'payment_status', 'payment_date', 'created_at']


class PaymentScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentSchedule
        fields = ['schedule_id', 'investor', 'investment', 'amount', 'due_date', 'paid', 'paid_at']


class StatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statement
        fields = ['statement_id', 'investor', 'generated_at', 'content']


class ForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forecast
        fields = ['forecast_id', 'investor', 'generated_at', 'data']



class ROICalculationSerializer(serializers.Serializer):
    """
    Calculates monthly ROI (24% annual) for all active investments.
    """

    def create(self, validated_data):
        active_investments = Investment.objects.filter(status="Active")
        created_count = 0
        current_month = datetime.now().strftime("%B %Y")

        for investment in active_investments:
            annual_roi = investment.amount * Decimal('0.24')
            monthly_roi = round(annual_roi / 12, 2)

            ROIDistribution.objects.create(
                investment=investment,
                investor=investment.investor,
                month=current_month,
                roi_amount=monthly_roi,
                payment_status="Pending",
            )
            created_count += 1
            # log_action("Monthly ROI calculated", reference_id=str(investment.investment_id))

        return {"records_created": created_count, "month": current_month}
