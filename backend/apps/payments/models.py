import uuid
from django.db import models
from apps.orders.models import Order, Payment

class PaymentWebhookEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    provider = models.CharField(max_length=80)
    event_id = models.CharField(max_length=180)
    event_type = models.CharField(max_length=100)
    payload = models.JSONField(default=dict)
    signature_valid = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        constraints = [models.UniqueConstraint(fields=['provider', 'event_id'], name='unique_payment_webhook_event')]
        ordering = ['-created_at']

class PaymentAttempt(models.Model):
    class Status(models.TextChoices):
        CREATED='CREATED','Criada'; REDIRECT='REDIRECT','Redirecionamento'; SUCCEEDED='SUCCEEDED','Sucesso'; FAILED='FAILED','Falhou'; EXPIRED='EXPIRED','Expirada'
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.ForeignKey(Payment, on_delete=models.PROTECT, related_name='attempts')
    provider = models.CharField(max_length=80)
    provider_ref = models.CharField(max_length=180, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CREATED)
    checkout_url = models.URLField(blank=True)
    raw_response = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
