from rest_framework import serializers
from .models import TransporterProfile, Vehicle, Delivery, DeliveryQuote

class TransporterProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransporterProfile
        fields = '__all__'

class VehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = '__all__'

class DeliveryQuoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryQuote
        fields = '__all__'

class DeliverySerializer(serializers.ModelSerializer):
    quotes = DeliveryQuoteSerializer(many=True, read_only=True)
    class Meta:
        model = Delivery
        fields = '__all__'
