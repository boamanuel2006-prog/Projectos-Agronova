from rest_framework import serializers
from .models import ConsultationService, AvailabilitySlot, ConsultationRequest, ConsultationPayment, ConsultationReview

class ServiceSerializer(serializers.ModelSerializer):
    consultant_name=serializers.CharField(source='consultant.profile.full_name',read_only=True)
    class Meta: model=ConsultationService; fields='__all__'; read_only_fields=['consultant','created_at','updated_at']

class SlotSerializer(serializers.ModelSerializer):
    class Meta: model=AvailabilitySlot; fields='__all__'; read_only_fields=['created_at']
    def validate(self,data):
        if data['ends_at']<=data['starts_at']: raise serializers.ValidationError('ends_at deve ser posterior a starts_at.')
        return data

class ConsultationRequestSerializer(serializers.ModelSerializer):
    client_name=serializers.CharField(source='client.profile.full_name',read_only=True)
    consultant_name=serializers.CharField(source='consultant.profile.full_name',read_only=True)
    service_title=serializers.CharField(source='service.title',read_only=True)
    class Meta: model=ConsultationRequest; fields='__all__'; read_only_fields=['client','consultant','price','currency','status','created_at','updated_at','meeting_url']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta: model=ConsultationPayment; fields='__all__'; read_only_fields=['id','provider','provider_ref','amount','currency','status','checkout_url','created_at','updated_at']

class ReviewSerializer(serializers.ModelSerializer):
    class Meta: model=ConsultationReview; fields='__all__'; read_only_fields=['author','created_at']
