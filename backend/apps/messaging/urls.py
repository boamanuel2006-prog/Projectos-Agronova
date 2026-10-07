from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, BlockViewSet
router = DefaultRouter()
router.register('conversations', ConversationViewSet, basename='conversation')
router.register('blocks', BlockViewSet, basename='block')
urlpatterns = router.urls
