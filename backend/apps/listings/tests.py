from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.catalog.models import Category
from .models import Listing

class ListingModelTests(TestCase):
    def test_listing_defaults_to_draft(self):
        user = get_user_model().objects.create_user(email='a@b.com', password='SenhaForte123')
        category = Category.objects.create(name='Milho', slug='milho')
        listing = Listing.objects.create(seller=user, category=category, title='Milho', price=350, quantity=1000)
        self.assertEqual(listing.status, Listing.Status.DRAFT)
