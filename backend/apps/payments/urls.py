from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, provider_webhook
router = DefaultRouter(); router.register('', PaymentViewSet, basename='payments')
urlpatterns = [path('webhooks/<str:provider>/', provider_webhook), path('', include(router.urls))]
