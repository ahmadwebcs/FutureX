import os
import django
import json
from django.core import management

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'futurex.settings')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from apps.investors.models import Investor
from apps.investments.models import College, Investment
from apps.finance.models import PaymentSchedule

User = get_user_model()

print('--- Admin token ---')
try:
    admin = User.objects.get(email='admin@example.com')
    token, _ = Token.objects.get_or_create(user=admin)
    print('ADMIN_TOKEN:', token.key)
except Exception as e:
    print('Admin user not found:', e)

print('\n--- Create investor (if not exists) ---')
try:
    inv, created = Investor.objects.get_or_create(email='auto@example.com', defaults={
        'name': 'Auto Investor', 'cnic': '99999-9999999-9', 'phone': '0123456789', 'address': '123 Test St'
    })
    if created:
        inv.set_password('testpass')
        inv.save()
    print('Investor:', inv.email, 'created=', created)
except Exception as e:
    print('Error creating investor:', e)

print('\n--- Create college and investment ---')
try:
    college = College.objects.create(name='Auto College')
    investment = Investment.objects.create(investor=inv, college=college, amount=1000)
    print('Created investment id:', investment.investment_id)
except Exception as e:
    print('Error creating investment:', e)

print('\n--- Running generate_monthly_roi command ---')
try:
    management.call_command('generate_monthly_roi')
    print('generate_monthly_roi executed')
except Exception as e:
    print('Error running generate_monthly_roi:', e)

print('\n--- Listing payment schedules ---')
try:
    schedules = PaymentSchedule.objects.all()
    out = []
    for s in schedules:
        out.append({
            'id': str(s.schedule_id),
            'investor': s.investor.email,
            'investment': str(s.investment.investment_id),
            'amount': str(s.amount),
            'due_date': str(s.due_date),
            'paid': s.paid,
        })
    print(json.dumps(out, indent=2))
except Exception as e:
    print('Error listing payment schedules:', e)
