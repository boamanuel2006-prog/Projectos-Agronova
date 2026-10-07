from rest_framework import serializers
from .models import Wallet, LedgerEntry, Settlement, PayoutRequest
class WalletSerializer(serializers.ModelSerializer):
    class Meta: model=Wallet; fields=['id','currency','available_balance','pending_balance','updated_at']
class LedgerEntrySerializer(serializers.ModelSerializer):
    class Meta: model=LedgerEntry; fields='__all__'
class SettlementSerializer(serializers.ModelSerializer):
    class Meta: model=Settlement; fields='__all__'
class PayoutRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model=PayoutRequest; fields=['id','amount','currency','destination_type','destination_ref','status','provider_ref','idempotency_key','created_at','updated_at']; read_only_fields=['status','provider_ref']
