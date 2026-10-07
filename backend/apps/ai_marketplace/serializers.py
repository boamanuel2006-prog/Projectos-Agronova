from rest_framework import serializers
from apps.listings.models import Listing

class RecommendationSerializer(serializers.ModelSerializer):
    score = serializers.FloatField()
    reasons = serializers.ListField(child=serializers.CharField())
    class Meta:
        model = Listing
        fields = ['id','title','description','price','currency','unit','quantity','province','municipality','category','score','reasons']

class PriceEstimateInputSerializer(serializers.Serializer):
    listing_id = serializers.IntegerField(required=False)
    category_id = serializers.IntegerField(required=False)
    province = serializers.CharField(required=False, allow_blank=True)
    unit = serializers.CharField(required=False, allow_blank=True)
    currency = serializers.CharField(required=False, default='AOA')

class RiskSerializer(serializers.Serializer):
    listing_id = serializers.IntegerField()
