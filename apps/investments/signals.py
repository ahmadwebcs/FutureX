from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Investment, Withdrawal, PortfolioEntry


@receiver(post_save, sender=Investment)
def update_college_valuation(sender, instance, **kwargs):
    college = instance.college
    total = sum(inv.amount for inv in college.investments.filter(status='Active'))
    college.total_valuation = total
    college.save()
    # update portfolio entries
    for inv in college.investments.filter(status='Active'):
        portfolio, _ = PortfolioEntry.objects.get_or_create(investor=inv.investor, college=college)
        portfolio.total_invested = sum(i.amount for i in inv.investor.investments.filter(college=college, status='Active'))
        portfolio.current_share = (portfolio.total_invested / total) * 100 if total > 0 else 0
        portfolio.save()


@receiver(post_save, sender=Withdrawal)
def handle_withdrawal(sender, instance, **kwargs):
    # mark processed and recalc portfolio and college totals
    if instance.processed:
        return
    inv = instance.investor
    # reduce the investor's investments proportionally (simple approach)
    related_investments = list(inv.investments.filter(status='Active'))
    remaining = instance.amount
    for investment in related_investments:
        if remaining <= 0:
            break
        take = min(investment.amount, remaining)
        investment.amount -= take
        remaining -= take
        if investment.amount <= 0:
            investment.status = 'Withdrawn'
        investment.save()
    instance.processed = True
    instance.save()