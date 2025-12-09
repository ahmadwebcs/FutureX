
from django.contrib import admin
from .models import ROIDistribution
from .models import PaymentSchedule, Statement, Forecast

admin.site.register(ROIDistribution)
admin.site.register(PaymentSchedule)
admin.site.register(Statement)
admin.site.register(Forecast)
    