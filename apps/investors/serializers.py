
from rest_framework import serializers
from .models import Investor
from .models import KYCDocument, DigitalSignature, OnboardingApproval

class InvestorRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Investor
        fields = ["name", "cnic", "email", "phone", "address", "password"]

    def validate(self, attrs):
        cnic = attrs.get("cnic")
        email = attrs.get("email")
        if Investor.objects.filter(cnic=cnic).exists():
            raise serializers.ValidationError({"cnic": "Investor with this CNIC already exists."})
        if Investor.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Investor with this email already exists."})
        return attrs


class KYCDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = KYCDocument
        fields = ['doc_id', 'investor', 'name', 'file', 'uploaded_at', 'verified']


class DigitalSignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalSignature
        fields = ['sig_id', 'investor', 'document', 'signature_data', 'signed_at']


class OnboardingApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnboardingApproval
        fields = ['approval_id', 'investor', 'approved', 'reviewed_by', 'reviewed_at', 'notes']
    