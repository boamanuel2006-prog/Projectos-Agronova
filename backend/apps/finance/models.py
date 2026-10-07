import uuid
from decimal import Decimal
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from apps.orders.models import Order

class Wallet(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='finance_wallet')
    currency=models.CharField(max_length=3,default='AOA')
    available_balance=models.DecimalField(max_digits=18,decimal_places=2,default=0,validators=[MinValueValidator(Decimal('0'))])
    pending_balance=models.DecimalField(max_digits=18,decimal_places=2,default=0,validators=[MinValueValidator(Decimal('0'))])
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)

class LedgerEntry(models.Model):
    class Type(models.TextChoices):
        SALE='SALE','Venda'; COMMISSION='COMMISSION','Comissão'; REFUND='REFUND','Reembolso'; PAYOUT='PAYOUT','Levantamento'; ADJUSTMENT='ADJUSTMENT','Ajuste'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    wallet=models.ForeignKey(Wallet,on_delete=models.PROTECT,related_name='ledger')
    order=models.ForeignKey(Order,on_delete=models.PROTECT,null=True,blank=True,related_name='finance_entries')
    entry_type=models.CharField(max_length=20,choices=Type.choices)
    amount=models.DecimalField(max_digits=18,decimal_places=2)
    currency=models.CharField(max_length=3,default='AOA')
    reference=models.CharField(max_length=180,unique=True)
    metadata=models.JSONField(default=dict,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']

class Settlement(models.Model):
    class Status(models.TextChoices):
        PENDING='PENDING','Pendente'; AVAILABLE='AVAILABLE','Disponível'; PAID='PAID','Pago'; REVERSED='REVERSED','Revertido'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    order=models.OneToOneField(Order,on_delete=models.PROTECT,related_name='settlement')
    seller=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='settlements')
    gross_amount=models.DecimalField(max_digits=18,decimal_places=2)
    commission_amount=models.DecimalField(max_digits=18,decimal_places=2)
    fees_amount=models.DecimalField(max_digits=18,decimal_places=2,default=0)
    net_amount=models.DecimalField(max_digits=18,decimal_places=2)
    currency=models.CharField(max_length=3)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING)
    available_at=models.DateTimeField(null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)

class PayoutRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED='REQUESTED','Solicitado'; PROCESSING='PROCESSING','Processando'; PAID='PAID','Pago'; FAILED='FAILED','Falhou'; CANCELLED='CANCELLED','Cancelado'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    wallet=models.ForeignKey(Wallet,on_delete=models.PROTECT,related_name='payouts')
    amount=models.DecimalField(max_digits=18,decimal_places=2,validators=[MinValueValidator(Decimal('0.01'))])
    currency=models.CharField(max_length=3)
    destination_type=models.CharField(max_length=40)  # bank, mobile_money, provider_balance
    destination_ref=models.CharField(max_length=180)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.REQUESTED)
    provider_ref=models.CharField(max_length=180,blank=True)
    idempotency_key=models.CharField(max_length=180,unique=True)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
