
import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings
from django.utils import timezone

class InvestorManager(BaseUserManager):
    def create_investor(self, email, name, cnic, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not cnic:
            raise ValueError("CNIC is required")
        email = self.normalize_email(email)
        investor = self.model(email=email, name=name, cnic=cnic, **extra_fields)
        investor.set_password(password)
        investor.save(using=self._db)
        return investor

    def create_user(self, email, name, cnic, password=None, **extra_fields):
        return self.create_investor(email, name, cnic, password, **extra_fields)

    def create_superuser(self, email, name, cnic, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_investor(email, name, cnic, password, **extra_fields)


class Investor(AbstractBaseUser, PermissionsMixin):
    investor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    cnic = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True)
    email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    objects = InvestorManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "cnic"]

    def __str__(self):
        return f"{self.name} ({self.email})"


class KYCDocument(models.Model):
    doc_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor = models.ForeignKey('Investor', on_delete=models.CASCADE, related_name='kyc_documents')
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='kyc_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"KYC {self.name} for {self.investor.email}"


class DocumentVersion(models.Model):
    version_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(KYCDocument, on_delete=models.CASCADE, related_name='versions')
    file = models.FileField(upload_to='document_versions/')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Version {self.version_id} of {self.document.name}"


class DigitalSignature(models.Model):
    sig_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor = models.ForeignKey('Investor', on_delete=models.CASCADE, related_name='signatures')
    document = models.ForeignKey(KYCDocument, on_delete=models.CASCADE, related_name='signatures')
    signature_data = models.TextField()  # could be base64 svg/png or a signature token
    signed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Signature by {self.investor.email} on {self.document.name}"


class OnboardingApproval(models.Model):
    approval_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    investor = models.ForeignKey('Investor', on_delete=models.CASCADE, related_name='approvals')
    approved = models.BooleanField(default=False)
    reviewed_by = models.CharField(max_length=255, blank=True, null=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def approve(self, reviewer_name='system'):
        self.approved = True
        self.reviewed_by = reviewer_name
        self.reviewed_at = timezone.now()
        self.save()

    