from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import OnboardingApproval


@receiver(post_save, sender=OnboardingApproval)
def onboarding_approval_email(sender, instance, created, **kwargs):
    if instance.approved:
        subject = 'Your onboarding is approved'
        message = f'Hello {instance.investor.name},\n\nYour onboarding has been approved.'
        send_mail(subject, message, None, [instance.investor.email])