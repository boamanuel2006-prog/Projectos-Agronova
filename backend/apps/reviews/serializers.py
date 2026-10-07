from rest_framework import serializers
from .models import Review
class ReviewSerializer(serializers.ModelSerializer):
    author_email=serializers.EmailField(source='author.email',read_only=True)
    target_email=serializers.EmailField(source='target.email',read_only=True)
    class Meta:
        model=Review; fields=['id','order','author','author_email','target','target_email','rating','comment','status','created_at','updated_at']
        read_only_fields=['id','author','author_email','target','target_email','status','created_at','updated_at']
class CreateReviewSerializer(serializers.Serializer):
    rating=serializers.IntegerField(min_value=1,max_value=5)
    comment=serializers.CharField(required=False,allow_blank=True,max_length=2000)
