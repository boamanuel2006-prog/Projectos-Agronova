from rest_framework import serializers
from .models import PushDevice

class PushDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushDevice
        fields = ("id", "token", "platform", "active", "created_at")
        read_only_fields = ("id", "created_at")
