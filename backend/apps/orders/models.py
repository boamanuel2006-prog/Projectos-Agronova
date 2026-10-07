import uuid
from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from apps.listings.models import Listing

class Order(models.Model):
    class Status(models.TextChoices):
        PENDING='PENDING','Pendente'; ACCEPTED='ACCEPTED','Aceite'; REJECTED='REJECTED','Rejeitado'
        AWAITING_PAYMENT='AWAITING_PAYMENT','A aguardar pagamento'; PAID='PAID','Pago'; PROCESSING='PROCESSING','Em processamento'
        READY_FOR_DELIVERY='READY_FOR_DELIVERY','Pronto para entrega'; IN_TRANSIT='IN_TRANSIT','Em trânsito'
        DELIVERED='DELIVERED','Entregue'; COMPLETED='COMPLETED','Concluído'; CANCELLED='CANCELLED','Cancelado'
        DISPUTED='DISPUTED','Em disputa'; REFUNDED='REFUNDED','Reembolsado'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    buyer=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='purchase_orders')
    seller=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='sales_orders')
    status=models.CharField(max_length=30,choices=Status.choices,default=Status.PENDING)
    subtotal=models.DecimalField(max_digits=16,decimal_places=2,default=0)
    fees=models.DecimalField(max_digits=16,decimal_places=2,default=0,validators=[MinValueValidator(0)])
    total=models.DecimalField(max_digits=16,decimal_places=2,default=0)
    currency=models.CharField(max_length=3,default='AOA')
    delivery_address=models.CharField(max_length=500,blank=True)
    notes=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['-created_at']

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items')
    listing=models.ForeignKey(Listing,on_delete=models.PROTECT,related_name='order_items')
    quantity=models.DecimalField(max_digits=14,decimal_places=3,validators=[MinValueValidator(0.001)])
    unit_price=models.DecimalField(max_digits=14,decimal_places=2,validators=[MinValueValidator(0)])
    unit=models.CharField(max_length=40)
    subtotal=models.DecimalField(max_digits=16,decimal_places=2)
    class Meta: constraints=[models.UniqueConstraint(fields=['order','listing'],name='unique_order_listing')]

class OrderStatusHistory(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='status_history')
    from_status=models.CharField(max_length=30,blank=True)
    to_status=models.CharField(max_length=30)
    actor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='order_status_changes')
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['created_at']

class Payment(models.Model):
    class Status(models.TextChoices): PENDING='PENDING','Pendente'; PAID='PAID','Pago'; FAILED='FAILED','Falhou'; REFUNDED='REFUNDED','Reembolsado'
    id= models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    order=models.ForeignKey(Order,on_delete=models.PROTECT,related_name='payments')
    provider=models.CharField(max_length=80)
    provider_ref=models.CharField(max_length=180,blank=True)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING)
    amount=models.DecimalField(max_digits=16,decimal_places=2)
    currency=models.CharField(max_length=3)
    idempotency_key=models.CharField(max_length=180,unique=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
