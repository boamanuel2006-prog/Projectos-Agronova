from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from apps.accounts.models import User


class SecurityApiTests(TestCase):
    def test_health_exposes_security_headers(self):
        response = APIClient().get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['Referrer-Policy'], 'strict-origin-when-cross-origin')

    def test_anonymous_user_cannot_access_protected_order_endpoint(self):
        response = APIClient().get('/api/v1/orders/')
        self.assertIn(response.status_code, (401, 403))

    def test_non_staff_cannot_access_admin_analytics(self):
        user = User.objects.create_user(email='user@agronova.local', password='SenhaForte123')
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/api/v1/admin-analytics/dashboard/')
        self.assertIn(response.status_code, (403, 404))
