from decimal import Decimal, ROUND_HALF_UP
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from apps.orders.models import Order
from .models import Wallet, LedgerEntry, Settlement

MONEY=Decimal('0.01')
def money(v): return Decimal(v).quantize(MONEY, rounding=ROUND_HALF_UP)

def commission_rate(): return Decimal(str(getattr(settings,'MARKETPLACE_COMMISSION_RATE',5))) / Decimal('100')

@transaction.atomic
def create_settlement_for_order(order_id):
    order=Order.objects.select_for_update().get(pk=order_id)
    if order.status not in [Order.Status.PAID, Order.Status.PROCESSING, Order.Status.READY_FOR_DELIVERY, Order.Status.IN_TRANSIT, Order.Status.DELIVERED, Order.Status.COMPLETED]:
        raise ValueError('O pedido ainda não está elegível para liquidação.')
    settlement,created=Settlement.objects.get_or_create(order=order,defaults={
        'seller':order.seller,'gross_amount':order.subtotal,'commission_amount':money(order.subtotal*commission_rate()),
        'fees_amount':money(order.fees),'net_amount':money(order.subtotal-order.subtotal*commission_rate()-order.fees),'currency':order.currency,
        'status':Settlement.Status.AVAILABLE,'available_at':timezone.now()})
    if created:
        wallet,_=Wallet.objects.get_or_create(user=order.seller,defaults={'currency':order.currency})
        wallet.pending_balance=money(wallet.pending_balance+settlement.net_amount); wallet.save(update_fields=['pending_balance','updated_at'])
        LedgerEntry.objects.create(wallet=wallet,order=order,entry_type=LedgerEntry.Type.SALE,amount=settlement.net_amount,currency=order.currency,reference=f'settlement:{settlement.id}')
        # Comissão é receita da plataforma; não é saldo do vendedor.
    return settlement
