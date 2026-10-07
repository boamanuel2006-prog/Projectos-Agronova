import json
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from apps.orders.models import Order, Payment
from apps.orders.services import transition_order
from .models import PaymentAttempt, PaymentWebhookEvent
from .providers import get_provider

@transaction.atomic
def create_payment(*, order, buyer, provider_name='mock', idempotency_key='', return_url=''):
    order = Order.objects.select_for_update().get(pk=order.pk)
    if order.buyer_id != buyer.id:
        raise PermissionError('Apenas o comprador pode iniciar o pagamento.')
    if order.status != Order.Status.AWAITING_PAYMENT:
        raise ValidationError('O pedido não está a aguardar pagamento.')
    if not idempotency_key:
        raise ValidationError('Idempotency-Key é obrigatória.')
    existing = Payment.objects.filter(idempotency_key=idempotency_key).first()
    if existing:
        attempt = existing.attempts.order_by('-created_at').first()
        return existing, attempt, False
    provider = get_provider(provider_name)
    payment = Payment.objects.create(order=order, provider=provider.name, amount=order.total, currency=order.currency, idempotency_key=idempotency_key)
    result = provider.create_payment(payment=payment, return_url=return_url)
    payment.provider_ref = result.provider_ref
    payment.save(update_fields=['provider_ref', 'updated_at'])
    attempt = PaymentAttempt.objects.create(payment=payment, provider=provider.name, provider_ref=result.provider_ref, status=PaymentAttempt.Status.REDIRECT, checkout_url=result.checkout_url, raw_response=result.raw_response or {})
    return payment, attempt, True

@transaction.atomic
def handle_webhook(*, provider_name, body, signature=''):
    provider = get_provider(provider_name)
    payload = json.loads(body.decode('utf-8'))
    parsed = provider.parse_webhook(payload)
    event_id = parsed['event_id']
    if not event_id:
        raise ValidationError('Webhook sem event_id.')
    valid = provider.verify_webhook(body=body, signature=signature)
    event, created = PaymentWebhookEvent.objects.get_or_create(provider=provider_name, event_id=event_id, defaults={'event_type': parsed['event_type'], 'payload': payload, 'signature_valid': valid})
    if not valid:
        event.signature_valid = False; event.error_message = 'Assinatura inválida.'; event.save(update_fields=['signature_valid','error_message'])
        raise PermissionError('Assinatura do webhook inválida.')
    if event.processed:
        return event, False
    provider_ref = parsed['provider_ref']
    payment = Payment.objects.select_for_update().filter(provider=provider_name, provider_ref=provider_ref).first()
    if not payment:
        event.error_message = 'Pagamento não encontrado.'; event.save(update_fields=['error_message'])
        raise ValidationError('Pagamento não encontrado.')
    status = parsed['status'].upper()
    if status in {'PAID','SUCCEEDED','SUCCESS'} and payment.status == Payment.Status.PENDING:
        payment.status = Payment.Status.PAID; payment.save(update_fields=['status','updated_at'])
        if payment.order.status == Order.Status.AWAITING_PAYMENT:
            transition_order(order=payment.order, actor=payment.order.buyer, new_status=Order.Status.PAID)
        payment.attempts.filter(provider_ref=provider_ref).update(status=PaymentAttempt.Status.SUCCEEDED)
    elif status in {'FAILED','DECLINED','CANCELLED'} and payment.status == Payment.Status.PENDING:
        payment.status = Payment.Status.FAILED; payment.save(update_fields=['status','updated_at'])
        payment.attempts.filter(provider_ref=provider_ref).update(status=PaymentAttempt.Status.FAILED)
    elif status in {'REFUNDED'}:
        payment.status = Payment.Status.REFUNDED; payment.save(update_fields=['status','updated_at'])
    event.processed = True; event.processed_at = timezone.now(); event.save(update_fields=['processed','processed_at'])
    return event, True

@transaction.atomic
def refund_payment(*, payment, actor, amount=None):
    payment = Payment.objects.select_for_update().select_related('order').get(pk=payment.pk)
    if actor.id not in {payment.order.buyer_id, payment.order.seller_id} and not actor.is_staff:
        raise PermissionError('Sem permissão.')
    if payment.status != Payment.Status.PAID:
        raise ValidationError('Só é possível reembolsar um pagamento confirmado.')
    amount = Decimal(str(amount)) if amount is not None else payment.amount
    if amount <= 0 or amount > payment.amount:
        raise ValidationError('Valor de reembolso inválido.')
    provider = get_provider(payment.provider)
    result = provider.refund(payment=payment, amount=amount)
    payment.status = Payment.Status.REFUNDED
    payment.save(update_fields=['status','updated_at'])
    if payment.order.status not in {Order.Status.REFUNDED, Order.Status.COMPLETED}:
        try:
            transition_order(order=payment.order, actor=actor, new_status=Order.Status.REFUNDED)
        except ValidationError:
            pass
    return result
