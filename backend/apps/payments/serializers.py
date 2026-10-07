from decimal import Decimal
from rest_framework import serializers
from .models import PaymentAttempt

class CreatePaymentSerializer(serializers.Serializer):
    provider = serializers.ChoiceField(choices=['mock','bitpay_ao','gpaygo_ao','mollie','mercadopago_br','stripe'], default='mock')
    return_url = serializers.URLField(required=False, allow_blank=True)
    country = serializers.ChoiceField(choices=['AO','PT','BR'], required=False)
    payment_method = serializers.CharField(max_length=60, required=False, allow_blank=True)

class PaymentAttemptSerializer(serializers.ModelSerializer):
    class Meta:
        model=PaymentAttempt
        fields=['id','payment','provider','provider_ref','status','checkout_url','created_at']

class RefundSerializer(serializers.Serializer):
    amount=serializers.DecimalField(max_digits=16,decimal_places=2,required=False,min_value=Decimal('0.01'))
