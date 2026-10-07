import uuid
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

class ConsultationService(models.Model):
    class Category(models.TextChoices):
        AGRONOMY='AGRONOMY','Agronomia'; VETERINARY='VETERINARY','Veterinária'; BIOLOGY='BIOLOGY','Biologia/Ambiente'; TECHNOLOGY='TECHNOLOGY','Tecnologia'
    class Status(models.TextChoices):
        DRAFT='DRAFT','Rascunho'; PUBLISHED='PUBLISHED','Publicado'; PAUSED='PAUSED','Pausado'; ARCHIVED='ARCHIVED','Arquivado'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    consultant=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='consultation_services')
    category=models.CharField(max_length=20,choices=Category.choices)
    title=models.CharField(max_length=180)
    description=models.TextField()
    price=models.DecimalField(max_digits=14,decimal_places=2,validators=[MinValueValidator(0)])
    currency=models.CharField(max_length=3,default='AOA')
    duration_minutes=models.PositiveIntegerField(default=60,validators=[MinValueValidator(15),MaxValueValidator(1440)])
    location_mode=models.CharField(max_length=20,choices=[('ONLINE','Online'),('ONSITE','No local'),('HYBRID','Híbrido')],default='ONLINE')
    province=models.CharField(max_length=100,blank=True)
    municipality=models.CharField(max_length=100,blank=True)
    status=models.CharField(max_length=15,choices=Status.choices,default=Status.DRAFT)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['-created_at']

class AvailabilitySlot(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    service=models.ForeignKey(ConsultationService,on_delete=models.CASCADE,related_name='availability')
    starts_at=models.DateTimeField(); ends_at=models.DateTimeField()
    is_booked=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['starts_at']; constraints=[models.UniqueConstraint(fields=['service','starts_at','ends_at'],name='unique_consultation_slot')]

class ConsultationRequest(models.Model):
    class Status(models.TextChoices):
        REQUESTED='REQUESTED','Solicitada'; ACCEPTED='ACCEPTED','Aceite'; AWAITING_PAYMENT='AWAITING_PAYMENT','A aguardar pagamento'; PAID='PAID','Paga'; SCHEDULED='SCHEDULED','Agendada'; IN_PROGRESS='IN_PROGRESS','Em atendimento'; COMPLETED='COMPLETED','Concluída'; CANCELLED='CANCELLED','Cancelada'; REJECTED='REJECTED','Rejeitada'; DISPUTED='DISPUTED','Em disputa'; REFUNDED='REFUNDED','Reembolsada'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    service=models.ForeignKey(ConsultationService,on_delete=models.PROTECT,related_name='requests')
    client=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='consultation_requests')
    consultant=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='received_consultation_requests')
    slot=models.OneToOneField(AvailabilitySlot,on_delete=models.PROTECT,related_name='booking',null=True,blank=True)
    requested_starts_at=models.DateTimeField(null=True,blank=True)
    notes=models.TextField(blank=True)
    price=models.DecimalField(max_digits=14,decimal_places=2)
    currency=models.CharField(max_length=3)
    status=models.CharField(max_length=25,choices=Status.choices,default=Status.REQUESTED)
    meeting_url=models.URLField(blank=True)
    cancellation_reason=models.CharField(max_length=500,blank=True)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)
    class Meta: ordering=['-created_at']

class ConsultationPayment(models.Model):
    class Status(models.TextChoices):
        PENDING='PENDING','Pendente'; PAID='PAID','Pago'; FAILED='FAILED','Falhou'; REFUNDED='REFUNDED','Reembolsado'; CANCELLED='CANCELLED','Cancelado'
    id=models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    consultation=models.OneToOneField(ConsultationRequest,on_delete=models.PROTECT,related_name='payment')
    provider=models.CharField(max_length=80,default='mock')
    provider_ref=models.CharField(max_length=180,blank=True)
    amount=models.DecimalField(max_digits=14,decimal_places=2)
    currency=models.CharField(max_length=3)
    status=models.CharField(max_length=20,choices=Status.choices,default=Status.PENDING)
    idempotency_key=models.CharField(max_length=180,unique=True)
    checkout_url=models.URLField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True); updated_at=models.DateTimeField(auto_now=True)

class ConsultationReview(models.Model):
    consultation=models.OneToOneField(ConsultationRequest,on_delete=models.CASCADE,related_name='consultation_review')
    author=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,related_name='consultation_reviews')
    rating=models.PositiveSmallIntegerField(validators=[MinValueValidator(1),MaxValueValidator(5)])
    comment=models.TextField(blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
