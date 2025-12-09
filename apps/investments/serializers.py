
from rest_framework import serializers
from .models import Investment
from .models import PortfolioEntry, Withdrawal, College

class InvestmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investment
        fields = ['investor', 'college', 'amount', 'share_percentage']


class PortfolioEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioEntry
        fields = ['entry_id', 'investor', 'college', 'total_invested', 'current_share', 'updated_at']


class WithdrawalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdrawal
        fields = ['withdrawal_id', 'investor', 'amount', 'date', 'processed']


class CollegeSerializer(serializers.ModelSerializer):
    class Meta:
        model = College
        fields = ['college_id', 'name', 'total_valuation', 'created_at']
    