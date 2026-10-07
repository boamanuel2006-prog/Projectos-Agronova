from rest_framework import generics, permissions
from .models import Wallet, LedgerEntry, Settlement, PayoutRequest
from .serializers import WalletSerializer, LedgerEntrySerializer, SettlementSerializer, PayoutRequestSerializer
from django.db import transaction
class WalletView(generics.RetrieveAPIView):
    serializer_class=WalletSerializer; permission_classes=[permissions.IsAuthenticated]
    def get_object(self):
        wallet,_=Wallet.objects.get_or_create(user=self.request.user,defaults={'currency':'AOA'}); return wallet
class LedgerList(generics.ListAPIView):
    serializer_class=LedgerEntrySerializer; permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self): return LedgerEntry.objects.filter(wallet__user=self.request.user)
class SettlementList(generics.ListAPIView):
    serializer_class=SettlementSerializer; permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self): return Settlement.objects.filter(seller=self.request.user)
class PayoutListCreate(generics.ListCreateAPIView):
    serializer_class=PayoutRequestSerializer; permission_classes=[permissions.IsAuthenticated]
    def get_queryset(self): return PayoutRequest.objects.filter(wallet__user=self.request.user)
    @transaction.atomic
    def perform_create(self,serializer):
        wallet=Wallet.objects.select_for_update().get_or_create(user=self.request.user,defaults={'currency':serializer.validated_data['currency']})[0]
        amount=serializer.validated_data['amount']
        if serializer.validated_data['currency'] != wallet.currency: raise ValueError('Moeda da carteira incompatível.')
        if amount > wallet.available_balance: raise ValueError('Saldo disponível insuficiente.')
        wallet.available_balance -= amount; wallet.save(update_fields=['available_balance','updated_at'])
        payout=serializer.save(wallet=wallet)
        LedgerEntry.objects.create(wallet=wallet,entry_type=LedgerEntry.Type.PAYOUT,amount=-amount,currency=wallet.currency,reference=f'payout:{payout.id}')
