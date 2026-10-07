from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from apps.notifications.models import Notification

def publish_user_event(user_id, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(f'user_{user_id}', {'type': 'notification.event', 'payload': payload})

def create_and_publish_notification(user, *, type, title, message, payload=None):
    notification = Notification.objects.create(user=user, type=type, title=title, message=message, payload=payload or {})
    event = {'type': 'notification.created', 'notification': {
        'id': str(notification.id), 'type': notification.type, 'title': notification.title,
        'message': notification.message, 'payload': notification.payload,
        'read_at': None, 'created_at': notification.created_at.isoformat(),
    }}
    publish_user_event(user.pk, event)
    return notification
