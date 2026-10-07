from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import TransporterProfile, Vehicle, Delivery, DeliveryQuote
from .serializers import TransporterProfileSerializer, VehicleSerializer, DeliverySerializer, DeliveryQuoteSerializer

class TransporterProfileViewSet(viewsets.ModelViewSet):
    queryset = TransporterProfile.objects.all()
    serializer_class = TransporterProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class VehicleViewSet(viewsets.ModelViewSet):
    queryset = Vehicle.objects.all()
    serializer_class = VehicleSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'], url_path='quote')
    def quote(self, request, pk=None):
        delivery = self.get_object()
        price = request.data.get('price', '1000.00')
        transporter_id = request.data.get('transporter')
        transporter = TransporterProfile.objects.filter(id=transporter_id).first()
        if not transporter:
            transporter = TransporterProfile.objects.first()
        quote = DeliveryQuote.objects.create(
            delivery=delivery,
            transporter=transporter,
            price=price,
            distance_km=request.data.get('distance_km', 10),
            estimated_hours=request.data.get('estimated_hours', 24)
        )
        return Response(DeliveryQuoteSerializer(quote).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], url_path='track')
    def track(self, request, pk=None):
        delivery = self.get_object()
        notes = request.data.get('notes', '')
        delivery.tracking_notes = f"{delivery.tracking_notes}\n{timezone.now().isoformat()}: {notes}".strip()
        delivery.save()
        return Response(DeliverySerializer(delivery).data)

    @action(detail=True, methods=['post'], url_path='proof-of-delivery')
    def proof_of_delivery(self, request, pk=None):
        delivery = self.get_object()
        delivery.proof_of_delivery_note = request.data.get('note', '')
        if 'image' in request.FILES:
            delivery.proof_of_delivery_image = request.FILES['image']
        delivery.status = Delivery.Status.DELIVERED
        delivery.delivered_at = timezone.now()
        delivery.save()
        return Response(DeliverySerializer(delivery).data)

class DeliveryQuoteViewSet(viewsets.ModelViewSet):
    queryset = DeliveryQuote.objects.all()
    serializer_class = DeliveryQuoteSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        quote = self.get_object()
        quote.is_accepted = True
        quote.save()
        delivery = quote.delivery
        delivery.transporter = quote.transporter
        delivery.status = Delivery.Status.ACCEPTED
        delivery.save()
        return Response(DeliveryQuoteSerializer(quote).data)
