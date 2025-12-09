
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.investors.models import Investor, KYCDocument, DigitalSignature, OnboardingApproval
from apps.investors.serializers import InvestorRegisterSerializer


class InvestorRegisterView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = InvestorRegisterSerializer(data=request.data)
        if serializer.is_valid():
            investor = serializer.save()
            return Response({"message": "Registration successful.", "investor_id": str(investor.investor_id)},
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvestorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Investor.objects.all()
    serializer_class = InvestorRegisterSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        user = request.user
        if user.is_anonymous:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(user)
        return Response(serializer.data)


class KYCDocumentViewSet(viewsets.ModelViewSet):
    queryset = KYCDocument.objects.all()
    serializer_class = None

    def get_serializer_class(self):
        from .serializers import KYCDocumentSerializer
        return KYCDocumentSerializer


class DigitalSignatureViewSet(viewsets.ModelViewSet):
    queryset = DigitalSignature.objects.all()
    serializer_class = None

    def get_serializer_class(self):
        from .serializers import DigitalSignatureSerializer
        return DigitalSignatureSerializer


class OnboardingApprovalViewSet(viewsets.ModelViewSet):
    queryset = OnboardingApproval.objects.all()
    serializer_class = None

    def get_serializer_class(self):
        from .serializers import OnboardingApprovalSerializer
        return OnboardingApprovalSerializer
    