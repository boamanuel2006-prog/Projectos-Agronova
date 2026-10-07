from django.contrib import admin
from django.urls import include, path
from django.http import JsonResponse
from django.conf import settings
from django.db import connection
import redis
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(['GET'])
@permission_classes([AllowAny])
def health(_request):
    return Response({'status': 'ok', 'service': 'agronova-api'})

@api_view(['GET'])
@permission_classes([AllowAny])
def readiness(_request):
    checks = {}
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            checks['database'] = 'ok'
    except Exception:
        checks['database'] = 'error'
    try:
        redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1, socket_timeout=1).ping()
        checks['redis'] = 'ok'
    except Exception:
        checks['redis'] = 'error'
    ready = all(value == 'ok' for value in checks.values())
    return Response({'status': 'ready' if ready else 'not_ready', 'checks': checks}, status=200 if ready else 503)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health),
    path('readiness/', readiness),
    path('api/v1/auth/', include('apps.accounts.urls')),
    path('api/v1/catalog/', include('apps.catalog.urls')),
    path('api/v1/listings/', include('apps.listings.urls')),
    path('api/v1/cart/', include('apps.cart.urls')),
    path('api/v1/orders/', include('apps.orders.urls')),
    path('api/v1/payments/', include('apps.payments.urls')),
    path('api/v1/finance/', include('apps.finance.urls')),
    path('api/v1/logistics/', include('apps.logistics.urls')),
    path('api/v1/notifications/', include('apps.notifications.urls')),
    path('api/v1/realtime/', include('apps.realtime.urls')),
    path('api/v1/consultations/', include('apps.consultations.urls')),
    path('api/v1/messaging/', include('apps.messaging.urls')),
    path('api/v1/reviews/', include('apps.reviews.urls')),
    path('api/v1/moderation/', include('apps.moderation.urls')),
    path('api/v1/admin-analytics/', include('apps.analytics.urls')),
    path('api/v1/ai/', include('apps.ai_marketplace.urls')),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
