from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.catalog.models import Category
from apps.listings.models import Listing
from apps.cart.models import Cart
from apps.orders.models import Order


class CriticalMarketplaceFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.seller = get_user_model().objects.create_user(email='seller@agronova.local', password='SenhaForte123')
        self.buyer = get_user_model().objects.create_user(email='buyer@agronova.local', password='SenhaForte123')
        self.category = Category.objects.create(name='Milho', slug='milho')
        self.listing = Listing.objects.create(
            seller=self.seller,
            category=self.category,
            title='Milho amarelo',
            description='Produto de teste',
            price=Decimal('350.00'),
            currency='AOA',
            unit='kg',
            quantity=Decimal('1000'),
            status=Listing.Status.PUBLISHED,
            location_text='Cuanza Norte',
        )

    def authenticate(self, user):
        response = self.client.post('/api/v1/auth/token/', {'email': user.email, 'password': 'SenhaForte123'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_health_and_readiness(self):
        self.assertEqual(self.client.get('/health/').status_code, 200)
        response = self.client.get('/readiness/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'ready')
        self.assertEqual(response.data['checks']['database'], 'ok')

    def test_buyer_can_add_and_checkout_published_listing(self):
        self.authenticate(self.buyer)
        response = self.client.post('/api/v1/cart/items/', {'listing': str(self.listing.id), 'quantity': '25'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Cart.objects.filter(user=self.buyer, items__listing=self.listing).exists())

        response = self.client.post('/api/v1/cart/checkout/', {'delivery_address': 'Luanda'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Order.objects.filter(buyer=self.buyer).count(), 1)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.quantity, Decimal('975'))
        self.assertFalse(Cart.objects.get(user=self.buyer).items.exists())

    def test_seller_cannot_add_own_listing_to_cart(self):
        self.authenticate(self.seller)
        response = self.client.post('/api/v1/cart/items/', {'listing': str(self.listing.id), 'quantity': '1'}, format='json')
        self.assertEqual(response.status_code, 400)
