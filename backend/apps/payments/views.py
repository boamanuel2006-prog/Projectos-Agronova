import json
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.core.exceptions import ValidationError as DjangoValidationError
from apps.orders.models import Order, Payment
from .models import PaymentAttempt
from .serializers import CreatePaymentSerializer, PaymentAttemptSerializer, RefundSerializer
from .services import create_payment, handle_webhook, refund_payment

class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentAttemptSerializer
    def get_queryset(self):
        return PaymentAttempt.objects.filter(payment__order__buyer=self.request.user).select_related('payment').order_by('-created_at')
    @action(detail=False, methods=['post'], url_path=r'orders/(?P<order_id>[^/.]+)/create')
    def create_for_order(self, request, order_id=None):
        data = CreatePaymentSerializer(data=request.data); data.is_valid(raise_exception=True)
        try:
            order = Order.objects.get(pk=order_id)
            payment, attempt, created = create_payment(order=order, buyer=request.user, provider_name=data.validated_data['provider'], idempotency_key=request.headers.get('Idempotency-Key',''), return_url=data.validated_data.get('return_url',''))
        except (Order.DoesNotExist, DjangoValidationError, PermissionError, ValueError) as exc:
            return Response({'error': {'code':'PAYMENT_INVALID','message':str(exc)}}, status=400)
        return Response({'payment_id': str(payment.id), 'status': payment.status, 'attempt': PaymentAttemptSerializer(attempt).data, 'created': created}, status=201 if created else 200)
    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        attempt = self.get_object()
        data = RefundSerializer(data=request.data); data.is_valid(raise_exception=True)
        try:
            result = refund_payment(payment=attempt.payment, actor=request.user, amount=data.validated_data.get('amount'))
        except (DjangoValidationError, PermissionError) as exc:
            return Response({'error': {'code':'REFUND_INVALID','message':str(exc)}}, status=400)
        return Response(result)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def provider_webhook(request, provider):
    try:
        handle_webhook(provider_name=provider, body=request.body, signature=request.headers.get('X-Payment-Signature',''))
    except (DjangoValidationError, PermissionError, json.JSONDecodeError, ValueError) as exc:
        return Response({'error': {'code':'WEBHOOK_INVALID','message':str(exc)}}, status=400)
    return Response({'received': True})
