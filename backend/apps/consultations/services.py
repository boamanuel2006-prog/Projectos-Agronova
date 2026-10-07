from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone
from .models import ConsultationRequest, AvailabilitySlot, ConsultationPayment, ConsultationReview
from apps.realtime.services import create_and_publish_notification

TRANSITIONS={
 'REQUESTED':{'ACCEPTED','REJECTED','CANCELLED'}, 'ACCEPTED':{'AWAITING_PAYMENT','CANCELLED'},
 'AWAITING_PAYMENT':{'PAID','CANCELLED'}, 'PAID':{'SCHEDULED','CANCELLED','REFUNDED'},
 'SCHEDULED':{'IN_PROGRESS','CANCELLED'}, 'IN_PROGRESS':{'COMPLETED','DISPUTED'},
 'DISPUTED':{'COMPLETED','REFUNDED'}, 'COMPLETED':set(), 'CANCELLED':set(), 'REJECTED':set(), 'REFUNDED':set()
}

@transaction.atomic
def transition(consultation, actor, new_status):
    c=ConsultationRequest.objects.select_for_update().select_related('client','consultant','service').get(pk=consultation.pk)
    if actor.id not in {c.client_id,c.consultant_id} and not actor.is_staff: raise PermissionError('Sem permissão.')
    if new_status not in TRANSITIONS.get(c.status,set()): raise ValidationError(f'Transição inválida: {c.status} -> {new_status}.')
    c.status=new_status; c.save(update_fields=['status','updated_at'])
    target=c.client if actor.id==c.consultant_id else c.consultant
    create_and_publish_notification(target,type='consultation.updated',title='Atualização da consultoria',message=f'A consultoria "{c.service.title}" mudou para {c.get_status_display()}.',payload={'consultation_id':str(c.id),'status':c.status})
    return c

@transaction.atomic
def create_request(*, service, client, slot=None, requested_starts_at=None, notes=''):
    if service.status!='PUBLISHED': raise ValidationError('O serviço não está disponível.')
    if service.consultant_id==client.id: raise ValidationError('O consultor não pode contratar o próprio serviço.')
    if slot:
        slot=AvailabilitySlot.objects.select_for_update().get(pk=slot.pk)
        if slot.service_id!=service.id or slot.is_booked: raise ValidationError('Horário indisponível.')
        slot.is_booked=True; slot.save(update_fields=['is_booked'])
    c=ConsultationRequest.objects.create(service=service,client=client,consultant=service.consultant,slot=slot,requested_starts_at=requested_starts_at,notes=notes,price=service.price,currency=service.currency)
    create_and_publish_notification(service.consultant,type='consultation.requested',title='Nova solicitação de consultoria',message=f'{client.profile.full_name} solicitou "{service.title}".',payload={'consultation_id':str(c.id)})
    return c

@transaction.atomic
def create_payment(*, consultation, client, provider='mock', idempotency_key=''):
    if consultation.client_id!=client.id: raise PermissionError('Sem permissão.')
    if consultation.status!='AWAITING_PAYMENT': raise ValidationError('A consultoria não está a aguardar pagamento.')
    if not idempotency_key: raise ValidationError('Idempotency-Key é obrigatória.')
    existing=ConsultationPayment.objects.filter(idempotency_key=idempotency_key).first()
    if existing: return existing, False
    payment=ConsultationPayment.objects.create(consultation=consultation,provider=provider,amount=consultation.price,currency=consultation.currency,idempotency_key=idempotency_key,provider_ref=f'CONS-{consultation.id}')
    return payment, True

@transaction.atomic
def confirm_payment(*, payment):
    payment=ConsultationPayment.objects.select_for_update().select_related('consultation').get(pk=payment.pk)
    if payment.status!='PENDING': return payment
    payment.status='PAID'; payment.save(update_fields=['status','updated_at'])
    transition(payment.consultation, payment.consultation.client, 'PAID')
    return payment

@transaction.atomic
def create_review(*, consultation, author, rating, comment=''):
    if consultation.status!='COMPLETED': raise ValidationError('A consultoria precisa estar concluída.')
    if author.id not in {consultation.client_id,consultation.consultant_id}: raise PermissionError('Sem permissão.')
    if ConsultationReview.objects.filter(consultation=consultation).exists(): raise ValidationError('Esta consultoria já possui avaliação.')
    target=consultation.consultant if author.id==consultation.client_id else consultation.client
    return ConsultationReview.objects.create(consultation=consultation,author=author,rating=rating,comment=comment)
