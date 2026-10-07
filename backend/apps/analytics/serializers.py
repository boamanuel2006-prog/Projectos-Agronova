from rest_framework import serializers

class AnalyticsQuerySerializer(serializers.Serializer):
    days = serializers.IntegerField(min_value=1, max_value=365, default=30, required=False)
