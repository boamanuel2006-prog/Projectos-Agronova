from decimal import Decimal
from django.core.exceptions import ValidationError
from django.db import transaction
from apps.listings.models import Listing
from .models import Cart, CartItem

@transaction.atomic
def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart

@transaction.atomic
def add_item(*, user, listing_id=None, listing=None, quantity):
    cart = get_or_create_cart(user)
    target_id = listing_id or listing
    listing = Listing.objects.select_for_update().get(pk=target_id)
    quantity = Decimal(str(quantity))
    if listing.seller_id == user.id:
        raise ValidationError('Não pode adicionar o próprio anúncio ao carrinho.')
    if listing.status != Listing.Status.PUBLISHED:
        raise ValidationError('O anúncio não está disponível.')
    if quantity <= 0 or quantity > listing.quantity:
        raise ValidationError('Quantidade indisponível.')
    item, _ = CartItem.objects.get_or_create(cart=cart, listing=listing, defaults={'quantity': quantity})
    if item.pk and item.quantity != quantity:
        if quantity > listing.quantity:
            raise ValidationError('Quantidade indisponível.')
        item.quantity = quantity
        item.save(update_fields=['quantity', 'updated_at'])
    return item

@transaction.atomic
def update_item(*, user, item_id, quantity):
    cart = get_or_create_cart(user)
    item = CartItem.objects.select_for_update().select_related('listing').get(pk=item_id, cart=cart)
    quantity = Decimal(str(quantity))
    if item.listing.status != Listing.Status.PUBLISHED or quantity > item.listing.quantity:
        raise ValidationError('Quantidade indisponível.')
    item.quantity = quantity
    item.save(update_fields=['quantity', 'updated_at'])
    return item

@transaction.atomic
def remove_item(*, user, item_id):
    cart = get_or_create_cart(user)
    item = CartItem.objects.get(pk=item_id, cart=cart)
    item.delete()

@transaction.atomic
def checkout(*, user, delivery_address='', notes=''):
    cart = get_or_create_cart(user)
    items = list(cart.items.select_related('listing', 'listing__seller').select_for_update().all())
    if not items:
        raise ValidationError('O carrinho está vazio.')

    # Re-read listings under lock and group the checkout into one order per seller.
    locked = []
    for item in items:
        listing = Listing.objects.select_for_update().select_related('seller').get(pk=item.listing_id)
        if listing.seller_id == user.id:
            raise ValidationError('O carrinho contém um anúncio do próprio comprador.')
        if listing.status != Listing.Status.PUBLISHED or item.quantity > listing.quantity:
            raise ValidationError(f'Quantidade indisponível para: {listing.title}.')
        locked.append((item, listing))

    from apps.orders.models import Order, OrderItem, OrderStatusHistory
    orders = []
    by_seller = {}
    for item, listing in locked:
        by_seller.setdefault(listing.seller_id, []).append((item, listing))

    for seller_id, seller_items in by_seller.items():
        currency = seller_items[0][1].currency
        if any(listing.currency != currency for _, listing in seller_items):
            raise ValidationError('Todos os itens de um vendedor devem usar a mesma moeda.')
        subtotal = sum((item.quantity * listing.price for item, listing in seller_items), Decimal('0'))
        order = Order.objects.create(
            buyer=user, seller=seller_items[0][1].seller, status=Order.Status.PENDING,
            subtotal=subtotal, fees=Decimal('0'), total=subtotal, currency=currency,
            delivery_address=delivery_address, notes=notes,
        )
        for item, listing in seller_items:
            OrderItem.objects.create(order=order, listing=listing, quantity=item.quantity,
                                     unit_price=listing.price, unit=listing.unit,
                                     subtotal=item.quantity * listing.price)
            listing.quantity -= item.quantity
            if listing.quantity == 0:
                listing.status = Listing.Status.SOLD_OUT
            listing.save(update_fields=['quantity', 'status', 'updated_at'])
        OrderStatusHistory.objects.create(order=order, from_status='', to_status=order.status, actor=user)
        orders.append(order)

    cart.items.all().delete()
    return orders
