
from django.contrib import admin
from .models import Investment, College
from .models import PortfolioEntry, Withdrawal

admin.site.register(Investment)
admin.site.register(College)
admin.site.register(PortfolioEntry)
admin.site.register(Withdrawal)
    