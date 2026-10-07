from urllib.parse import parse_qs
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from apps.accounts.models import User

@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return AnonymousUser()

class JWTAuthMiddleware:
    def __init__(self, app): self.app = app
    async def __call__(self, scope, receive, send):
        token = None
        headers = dict(scope.get('headers', []))
        auth = headers.get(b'authorization', b'').decode()
        if auth.lower().startswith('bearer '): token = auth[7:].strip()
        if not token:
            query = parse_qs(scope.get('query_string', b'').decode())
            token = (query.get('token') or [None])[0]
        scope['user'] = AnonymousUser()
        if token:
            try:
                validated = AccessToken(token)
                scope['user'] = await get_user(validated['user_id'])
            except (InvalidToken, TokenError, KeyError, ValueError):
                pass
        return await self.app(scope, receive, send)
