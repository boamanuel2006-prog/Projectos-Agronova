from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from apps.listings.models import Listing
from .models import Order, OrderItem, OrderStatusHistory

TRANSITIONS = {
    Order.Status.PENDING: {Order.Status.ACCEPTED, Order.Status.REJECTED, Order.Status.CANCELLED},
    Order.Status.ACCEPTED: {Order.Status.AWAITING_PAYMENT, Order.Status.CANCELLED},
    Order.Status.AWAITING_PAYMENT: {Order.Status.PAID, Order.Status.CANCELLED},
    Order.Status.PAID: {Order.Status.PROCESSING, Order.Status.REFUNDED},
    Order.Status.PROCESSING: {Order.Status.READY_FOR_DELIVERY},
    Order.Status.READY_FOR_DELIVERY: {Order.Status.IN_TRANSIT, Order.Status.CANCELLED},
    Order.Status.IN_TRANSIT: {Order.Status.DELIVERED, Order.Status.DISPUTED},
    Order.Status.DELIVERED: {Order.Status.COMPLETED, Order.Status.DISPUTED},
    Order.Status.DISPUTED: {Order.Status.REFUNDED, Order.Status.COMPLETED},
}

@transaction.atomic
def create_order(*, buyer, listing, quantity, delivery_address='', notes=''):
    listing = Listing.objects.select_for_update().select_related('seller').get(pk=listing.pk)
    if listing.seller_id == buyer.id:
        raise ValidationError('Não pode comprar o próprio anúncio.')
    if listing.status != Listing.Status.PUBLISHED:
        raise ValidationError('O anúncio não está disponível.')
    quantity = Decimal(str(quantity))
    if quantity <= 0:
        raise ValidationError('A quantidade deve ser positiva.')
    if quantity > listing.quantity:
        raise ValidationError('Quantidade indisponível.')
    subtotal = quantity * listing.price
    order = Order.objects.create(
        buyer=buyer, seller=listing.seller, status=Order.Status.PENDING,
        subtotal=subtotal, total=subtotal, currency=listing.currency,
        delivery_address=delivery_address, notes=notes,
    )
    OrderItem.objects.create(order=order, listing=listing, quantity=quantity,
                             unit_price=listing.price, unit=listing.unit, subtotal=subtotal)
    listing.quantity -= quantity
    if listing.quantity == 0:
        listing.status = Listing.Status.SOLD_OUT
    listing.save(update_fields=['quantity', 'status', 'updated_at'])
    OrderStatusHistory.objects.create(order=order, from_status='', to_status=order.status, actor=buyer)
    return order

@transaction.atomic
def transition_order(*, order, actor, new_status):
    order = Order.objects.select_for_update().get(pk=order.pk)
    allowed = TRANSITIONS.get(order.status, set())
    if new_status not in allowed:
        raise ValidationError(f'Transição inválida: {order.status} -> {new_status}.')
    if actor.id not in {order.buyer_id, order.seller_id} and not actor.is_staff:
        raise PermissionError('Sem permissão.')
    seller_only = {Order.Status.ACCEPTED, Order.Status.REJECTED, Order.Status.PROCESSING,
                   Order.Status.READY_FOR_DELIVERY, Order.Status.IN_TRANSIT, Order.Status.DELIVERED}
    if new_status in seller_only and actor.id != order.seller_id and not actor.is_staff:
        raise PermissionError('Apenas o vendedor pode atualizar esta etapa.')
    if new_status == Order.Status.PAID and actor.id != order.buyer_id and not actor.is_staff:
        raise PermissionError('Apenas o comprador pode confirmar pagamento.')
    if new_status == Order.Status.CANCELLED and actor.id not in {order.buyer_id, order.seller_id} and not actor.is_staff:
        raise PermissionError('Apenas os participantes podem cancelar.')

    old = order.status
    order.status = new_status
    order.save(update_fields=['status', 'updated_at'])

    # A reservation is released when a pre-delivery order is rejected/cancelled.
    if new_status in {Order.Status.REJECTED, Order.Status.CANCELLED}:
        for item in order.items.select_related('listing').select_for_update():
            listing = Listing.objects.select_for_update().get(pk=item.listing_id)
            listing.quantity += item.quantity
            if listing.status == Listing.Status.SOLD_OUT and listing.quantity > 0:
                listing.status = Listing.Status.PUBLISHED
            listing.save(update_fields=['quantity', 'status', 'updated_at'])

    OrderStatusHistory.objects.create(order=order, from_status=old, to_status=new_status, actor=actor)
    return order
