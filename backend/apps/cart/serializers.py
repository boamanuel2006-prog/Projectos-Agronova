from decimal import Decimal
from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    listing_title = serializers.CharField(source='listing.title', read_only=True)
    unit_price = serializers.DecimalField(source='listing.price', max_digits=14, decimal_places=2, read_only=True)
    unit = serializers.CharField(source='listing.unit', read_only=True)
    currency = serializers.CharField(source='listing.currency', read_only=True)
    available_quantity = serializers.DecimalField(source='listing.quantity', max_digits=14, decimal_places=3, read_only=True)
    seller_id = serializers.UUIDField(source='listing.seller_id', read_only=True)
    line_total = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'listing', 'listing_title', 'quantity', 'unit_price', 'unit', 'currency', 'available_quantity', 'seller_id', 'line_total', 'created_at', 'updated_at']
        read_only_fields = ['id', 'listing_title', 'unit_price', 'unit', 'currency', 'available_quantity', 'seller_id', 'line_total', 'created_at', 'updated_at']

    def get_line_total(self, obj):
        return obj.quantity * obj.listing.price

class AddCartItemSerializer(serializers.Serializer):
    listing = serializers.CharField()
    quantity = serializers.DecimalField(max_digits=14, decimal_places=3, min_value=Decimal('0.001'))

class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.DecimalField(max_digits=14, decimal_places=3, min_value=Decimal('0.001'))

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    subtotal = serializers.SerializerMethodField()
    currencies = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'subtotal', 'currencies', 'created_at', 'updated_at']

    def get_subtotal(self, obj):
        return sum((item.quantity * item.listing.price for item in obj.items.select_related('listing').all()), 0)

    def get_currencies(self, obj):
        return sorted(set(obj.items.select_related('listing').values_list('listing__currency', flat=True)))
