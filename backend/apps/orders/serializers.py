from decimal import Decimal
from rest_framework import serializers
from .models import Order,OrderItem,OrderStatusHistory,Payment
class OrderItemSerializer(serializers.ModelSerializer):
    listing_title=serializers.CharField(source='listing.title',read_only=True)
    class Meta:
        model=OrderItem; fields=['id','listing','listing_title','quantity','unit_price','unit','subtotal']; read_only_fields=['id','unit_price','unit','subtotal','listing_title']
class OrderHistorySerializer(serializers.ModelSerializer):
    actor_email=serializers.EmailField(source='actor.email',read_only=True)
    class Meta:
        model=OrderStatusHistory; fields=['id','from_status','to_status','actor_email','created_at']
class OrderSerializer(serializers.ModelSerializer):
    items=OrderItemSerializer(many=True,read_only=True)
    status_history=OrderHistorySerializer(many=True,read_only=True)
    buyer_email=serializers.EmailField(source='buyer.email',read_only=True)
    seller_email=serializers.EmailField(source='seller.email',read_only=True)
    class Meta:
        model=Order; fields=['id','buyer','buyer_email','seller','seller_email','status','subtotal','fees','total','currency','delivery_address','notes','items','status_history','created_at','updated_at']; read_only_fields=['id','buyer','seller','status','subtotal','fees','total','currency','items','status_history','created_at','updated_at','buyer_email','seller_email']
class CreateOrderSerializer(serializers.Serializer):
    listing=serializers.CharField()
    quantity=serializers.DecimalField(max_digits=14,decimal_places=3,min_value=Decimal('0.001'))
    delivery_address=serializers.CharField(max_length=500,required=False,allow_blank=True)
    notes=serializers.CharField(required=False,allow_blank=True)
class StatusSerializer(serializers.Serializer): status=serializers.ChoiceField(choices=Order.Status.choices)
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Payment; fields=['id','provider','provider_ref','status','amount','currency','idempotency_key','created_at']; read_only_fields=['id','status','created_at']
