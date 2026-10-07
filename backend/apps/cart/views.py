from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, AddCartItemSerializer, UpdateCartItemSerializer
from .services import get_or_create_cart, add_item, update_item, remove_item, checkout

class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        cart = get_or_create_cart(request.user)
        cart = Cart.objects.prefetch_related('items__listing').get(pk=cart.pk)
        return Response(CartSerializer(cart).data)

    @action(detail=False, methods=['post'], url_path='items')
    def add(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            item = add_item(user=request.user, **serializer.validated_data)
        except DjangoValidationError as exc:
            return Response({'error': {'code': 'CART_INVALID', 'message': str(exc)}}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'id': str(item.id), 'message': 'Item adicionado ao carrinho.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['patch'], url_path=r'items/(?P<item_id>[^/.]+)')
    def update_item(self, request, item_id=None):
        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            item = update_item(user=request.user, item_id=item_id, **serializer.validated_data)
        except CartItem.DoesNotExist:
            return Response({'error': {'code': 'NOT_FOUND', 'message': 'Item não encontrado.'}}, status=404)
        except DjangoValidationError as exc:
            return Response({'error': {'code': 'CART_INVALID', 'message': str(exc)}}, status=400)
        return Response({'id': str(item.id), 'quantity': item.quantity})

    @action(detail=False, methods=['delete'], url_path=r'items/(?P<item_id>[^/.]+)')
    def remove(self, request, item_id=None):
        try:
            remove_item(user=request.user, item_id=item_id)
        except CartItem.DoesNotExist:
            return Response({'error': {'code': 'NOT_FOUND', 'message': 'Item não encontrado.'}}, status=404)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'])
    def checkout(self, request):
        try:
            orders = checkout(user=request.user, delivery_address=request.data.get('delivery_address', ''), notes=request.data.get('notes', ''))
        except DjangoValidationError as exc:
            return Response({'error': {'code': 'CHECKOUT_INVALID', 'message': str(exc)}}, status=400)
        return Response({'orders': [str(order.id) for order in orders], 'message': 'Checkout concluído; pedidos aguardam confirmação do vendedor.'}, status=201)
