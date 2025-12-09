from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.investments.models import Investment
from apps.finance.models import ROIDistribution, PaymentSchedule
from decimal import Decimal
import calendar


class Command(BaseCommand):
    help = 'Generate monthly ROI distributions and payment schedules (24% annual default)'

    def handle(self, *args, **options):
        today = timezone.now().date()
        month = today.strftime('%Y-%m')
        annual_rate = Decimal('0.24')
        monthly_rate = annual_rate / Decimal('12')

        investments = Investment.objects.filter(status='Active')
        for inv in investments:
            roi_amount = (Decimal(inv.amount) * monthly_rate).quantize(Decimal('0.01'))
            roi = ROIDistribution.objects.create(
                investment=inv,
                investor=inv.investor,
                month=month,
                roi_amount=roi_amount,
            )
            # schedule payment 7 days from now by default
            due_date = today + timezone.timedelta(days=7)
            PaymentSchedule.objects.create(
                investor=inv.investor,
                investment=inv,
                amount=roi_amount,
                due_date=due_date,
            )
        self.stdout.write(self.style.SUCCESS('Generated monthly ROI and payment schedules for %s investments' % investments.count()))
