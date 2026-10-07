from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransporterProfileViewSet, VehicleViewSet, DeliveryViewSet, DeliveryQuoteViewSet

router = DefaultRouter()
router.register('transporters', TransporterProfileViewSet, basename='transporter')
router.register('vehicles', VehicleViewSet, basename='vehicle')
router.register('deliveries', DeliveryViewSet, basename='delivery')
router.register('quotes', DeliveryQuoteViewSet, basename='delivery-quote')

urlpatterns = [
    path('', include(router.urls)),
]
