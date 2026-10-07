from django.test import TestCase
from rest_framework.test import APIClient
from .models import User

class AccountApiTests(TestCase):
    def test_register_and_login(self):
        client = APIClient()
        response = client.post('/api/v1/auth/register/', {'email':'teste@agronova.local','password':'SenhaForte123','full_name':'Produtor Teste','role':'FARMER'}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(User.objects.filter(email='teste@agronova.local').exists())
        response = client.post('/api/v1/auth/token/', {'email':'teste@agronova.local','password':'SenhaForte123'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
