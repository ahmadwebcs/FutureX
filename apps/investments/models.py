
import uuid
from django.db import models
from apps.investors.models import Investor

class College(models.Model):
    college_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    total_valuation = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Investment(models.Model):
    investment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name="investments")
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name="investments")
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    share_percentage = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=50, default="Active")

    def __str__(self):
        return f"{self.investor.name} → {self.college.name} ({self.amount})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalculate total valuation for the college
        total = sum(inv.amount for inv in self.college.investments.filter(status='Active'))
        self.college.total_valuation = total
        self.college.save()
        # Recalculate share percentages for all investments in the college
        investments = list(self.college.investments.filter(status='Active'))
        if total > 0:
            for inv in investments:
                share = (inv.amount / total) * 100
                # update share percentage without triggering save() to avoid recursion
                Investment.objects.filter(pk=inv.pk).update(share_percentage=share)


class PortfolioEntry(models.Model):
    entry_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='portfolio')
    college = models.ForeignKey(College, on_delete=models.CASCADE, related_name='portfolio_entries')
    total_invested = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    current_share = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Portfolio {self.investor.email} in {self.college.name}"


class Withdrawal(models.Model):
    withdrawal_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor = models.ForeignKey(Investor, on_delete=models.CASCADE, related_name='withdrawals')
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return f"Withdrawal {self.amount} by {self.investor.email}"
    