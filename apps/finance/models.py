
import uuid
from django.db import models
from apps.investments.models import Investment
from apps.investors.models import Investor

class ROIDistribution(models.Model):
    roi_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name="roi_records")
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name="roi_records")
    month = models.CharField(max_length=20)
    roi_amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_status = models.CharField(max_length=50, default="Pending")
    payment_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ROI {self.month} – {self.investor.name} ({self.roi_amount})"


class PaymentSchedule(models.Model):
    schedule_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='payment_schedules')
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='payment_schedules')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    due_date = models.DateField()
    paid = models.BooleanField(default=False)
    paid_at = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.amount} to {self.investor.email} due {self.due_date}"


class Statement(models.Model):
    statement_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='statements')
    generated_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField()  # Could store JSON or textual ledger

    def __str__(self):
        return f"Statement {self.statement_id} for {self.investor.email}"


class Forecast(models.Model):
    forecast_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='forecasts')
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()

    def __str__(self):
        return f"Forecast for {self.investor.email} at {self.generated_at}"
    