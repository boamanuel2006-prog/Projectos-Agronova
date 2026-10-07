from rest_framework.routers import DefaultRouter
from .views import ServiceViewSet, SlotViewSet, ConsultationRequestViewSet, PaymentViewSet, ReviewViewSet
router=DefaultRouter(); router.register('services',ServiceViewSet,basename='consultation-service'); router.register('slots',SlotViewSet,basename='consultation-slot'); router.register('requests',ConsultationRequestViewSet,basename='consultation-request'); router.register('payments',PaymentViewSet,basename='consultation-payment'); router.register('reviews',ReviewViewSet,basename='consultation-review')
urlpatterns=router.urls
