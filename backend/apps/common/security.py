from django.http import JsonResponse


class SecurityHeadersMiddleware:
    """Adds defense-in-depth headers without changing API semantics."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault('X-Content-Type-Options', 'nosniff')
        response.setdefault('X-Frame-Options', 'DENY')
        response.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=(self._geo_policy(request))')
        if request.is_secure():
            response.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        return response

    @staticmethod
    def _geo_policy(request):
        return 'self'
