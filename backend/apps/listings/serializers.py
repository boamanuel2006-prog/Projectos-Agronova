from rest_framework import serializers
from .models import Listing, ListingImage, Favorite
from .validators import validate_listing_image

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'image', 'sort_order', 'created_at']
        read_only_fields = ['id', 'created_at']

class ListingSerializer(serializers.ModelSerializer):
    images = ListingImageSerializer(many=True, read_only=True)
    seller_name = serializers.CharField(source='seller.profile.full_name', read_only=True)
    is_favorite = serializers.SerializerMethodField()
    class Meta:
        model = Listing
        fields = ['id','seller','seller_name','category','title','description','price','currency','unit','quantity','status','location_text','province','municipality','latitude','longitude','images','is_favorite','created_at','updated_at']
        read_only_fields = ['id','seller','created_at','updated_at','images','is_favorite']
    def validate(self, attrs):
        if 'price' in attrs and attrs['price'] < 0:
            raise serializers.ValidationError({'price': 'O preço não pode ser negativo.'})
        if 'quantity' in attrs and attrs['quantity'] < 0:
            raise serializers.ValidationError({'quantity': 'A quantidade não pode ser negativa.'})
        return attrs
    def get_is_favorite(self, obj):
        user = self.context['request'].user
        return user.is_authenticated and Favorite.objects.filter(user=user, listing=obj).exists()

class ListingImageCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(validators=[validate_listing_image])
    class Meta:
        model = ListingImage
        fields = ['id','image','sort_order']
        read_only_fields = ['id']

class ListingImageReorderSerializer(serializers.Serializer):
    image_ids = serializers.ListField(child=serializers.IntegerField(min_value=1), allow_empty=False)
