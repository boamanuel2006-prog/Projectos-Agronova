from rest_framework.routers import DefaultRouter
from .views import PushDeviceViewSet

router = DefaultRouter()
router.register("devices", PushDeviceViewSet, basename="push-device")
urlpatterns = router.urls
