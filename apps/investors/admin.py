
from django.contrib import admin
from .models import Investor
from .models import KYCDocument, DocumentVersion, DigitalSignature, OnboardingApproval

admin.site.register(Investor)
admin.site.register(KYCDocument)
admin.site.register(DocumentVersion)
admin.site.register(DigitalSignature)
admin.site.register(OnboardingApproval)
    