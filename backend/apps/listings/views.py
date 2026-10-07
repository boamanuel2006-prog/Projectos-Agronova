from decimal import Decimal, InvalidOperation

from django.db import transaction
from django.db.models import Q
from django.db.models.expressions import RawSQL
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Listing, ListingImage, Favorite
from .serializers import ListingSerializer, ListingImageCreateSerializer, ListingImageReorderSerializer
from .validators import MAX_IMAGES_PER_LISTING


class ListingViewSet(viewsets.ModelViewSet):
    serializer_class = ListingSerializer
    filterset_fields = ['category', 'status', 'currency', 'location_text', 'province', 'municipality', 'seller']
    search_fields = ['title', 'description', 'location_text', 'province', 'municipality', 'unit']
    ordering_fields = ['created_at', 'price', 'quantity', 'title']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Listing.objects.select_related('seller__profile', 'category').prefetch_related('images')
        if self.request.user.is_authenticated:
            qs = qs.filter(Q(status=Listing.Status.PUBLISHED) | Q(seller=self.request.user)).distinct()
        else:
            qs = qs.filter(status=Listing.Status.PUBLISHED)

        params = self.request.query_params
        qs = self._decimal_filter(qs, params, 'price', 'min_price', 'gte')
        qs = self._decimal_filter(qs, params, 'price', 'max_price', 'lte')
        qs = self._decimal_filter(qs, params, 'quantity', 'min_quantity', 'gte')
        qs = self._decimal_filter(qs, params, 'quantity', 'max_quantity', 'lte')

        lat, lng, radius = self._geo_params(params)
        if lat is not None and lng is not None:
            # Bounding-box prefilter keeps the expensive Haversine expression small.
            delta_lat = radius / 111.0
            delta_lng = radius / max(111.0 * 0.2, 111.0 * abs(__import__('math').cos(__import__('math').radians(lat))))
            qs = qs.filter(
                latitude__isnull=False, longitude__isnull=False,
                latitude__gte=lat-delta_lat, latitude__lte=lat+delta_lat,
                longitude__gte=lng-delta_lng, longitude__lte=lng+delta_lng,
            )
            qs = qs.annotate(distance_km=RawSQL(
                "6371 * acos(least(1, greatest(-1, cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))))",
                [lat, lng, lat],
            )).filter(distance_km__lte=radius)
        return qs

    @staticmethod
    def _decimal_filter(qs, params, field, key, lookup):
        value = params.get(key)
        if value in (None, ''):
            return qs
        try:
            value = Decimal(value)
        except (InvalidOperation, TypeError):
            return qs.none()
        return qs.filter(**{f'{field}__{lookup}': value})

    @staticmethod
    def _geo_params(params):
        try:
            lat = float(params.get('lat')) if params.get('lat') not in (None, '') else None
            lng = float(params.get('lng')) if params.get('lng') not in (None, '') else None
            radius = float(params.get('radius_km', 25))
            if lat is None or lng is None or not (-90 <= lat <= 90 and -180 <= lng <= 180):
                return None, None, radius
            if not (0 < radius <= 500):
                return None, None, 25.0
            return lat, lng, radius
        except (TypeError, ValueError):
            return None, None, 25.0

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def perform_update(self, serializer):
        obj = self.get_object()
        if obj.seller != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied('Sem permissão para alterar este anúncio.')
        serializer.save()

    def _owner(self, listing):
        if listing.seller != self.request.user and not self.request.user.is_staff:
            raise permissions.PermissionDenied('Sem permissão para alterar este anúncio.')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def publish(self, request, pk=None):
        listing = self.get_object(); self._owner(listing)
        if not listing.title.strip() or not listing.category_id or listing.price < 0 or listing.quantity <= 0:
            return Response({'detail': 'Preencha título, categoria, preço e uma quantidade maior que zero.'}, status=400)
        if not listing.images.exists():
            return Response({'detail': 'Adicione pelo menos uma fotografia antes de publicar.'}, status=400)
        listing.status = Listing.Status.PUBLISHED
        listing.save(update_fields=['status','updated_at'])
        return Response(ListingSerializer(listing, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def pause(self, request, pk=None):
        listing = self.get_object(); self._owner(listing)
        if listing.status != Listing.Status.PUBLISHED:
            return Response({'detail': 'Apenas anúncios publicados podem ser pausados.'}, status=400)
        listing.status = Listing.Status.PAUSED; listing.save(update_fields=['status','updated_at'])
        return Response(ListingSerializer(listing, context={'request': request}).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def archive(self, request, pk=None):
        listing = self.get_object(); self._owner(listing)
        listing.status = Listing.Status.ARCHIVED; listing.save(update_fields=['status','updated_at'])
        return Response(ListingSerializer(listing, context={'request': request}).data)

    @action(detail=True, methods=['post','delete'], permission_classes=[permissions.IsAuthenticated])
    def favorite(self, request, pk=None):
        listing = self.get_object()
        if request.method == 'POST':
            Favorite.objects.get_or_create(user=request.user, listing=listing)
            return Response({'data': {'favorited': True}}, status=status.HTTP_201_CREATED)
        Favorite.objects.filter(user=request.user, listing=listing).delete()
        return Response({'data': {'favorited': False}})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def images(self, request, pk=None):
        listing = self.get_object(); self._owner(listing)
        if listing.images.count() >= MAX_IMAGES_PER_LISTING:
            return Response({'detail': f'Máximo de {MAX_IMAGES_PER_LISTING} imagens por anúncio.'}, status=400)
        serializer = ListingImageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(listing=listing)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path=r'images/(?P<image_id>[^/.]+)', permission_classes=[permissions.IsAuthenticated])
    def delete_image(self, request, pk=None, image_id=None):
        listing = self.get_object(); self._owner(listing)
        try: image = listing.images.get(pk=image_id)
        except ListingImage.DoesNotExist: return Response({'detail':'Imagem não encontrada.'}, status=404)
        image.delete()
        return Response(status=204)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def reorder_images(self, request, pk=None):
        listing = self.get_object(); self._owner(listing)
        serializer = ListingImageReorderSerializer(data=request.data); serializer.is_valid(raise_exception=True)
        ids = serializer.validated_data['image_ids']
        images = list(listing.images.filter(id__in=ids))
        if len(images) != len(ids) or len(set(ids)) != len(ids):
            return Response({'detail':'A lista deve conter exatamente IDs de imagens deste anúncio, sem duplicados.'}, status=400)
        with transaction.atomic():
            for index, image_id in enumerate(ids):
                listing.images.filter(id=image_id).update(sort_order=index)
        return Response(ListingSerializer(listing, context={'request': request}).data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.AllowAny])
    def nearby(self, request):
        """Explicit discovery endpoint; supports ?lat=&lng=&radius_km=."""
        qs = self.filter_queryset(self.get_queryset())
        if 'lat' not in request.query_params or 'lng' not in request.query_params:
            return Response({'detail': 'Informe lat e lng.'}, status=400)
        page = self.paginate_queryset(qs.order_by('distance_km'))
        serializer = self.get_serializer(page or qs.order_by('distance_km'), many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)
