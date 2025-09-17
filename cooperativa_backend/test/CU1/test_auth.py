"""
Tests para autenticación
Ejecutar con: python manage.py test test.test_auth
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class AuthTests(APITestCase):
    """Tests para autenticación"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            ci_nit='123456789',
            nombres='Test',
            apellidos='User',
            email='test@example.com',
            usuario='testuser',
            password='testpass123'
        )

    def test_login_success(self):
        """Test login exitoso"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('usuario', response.data)
        self.assertIn('mensaje', response.data)

    def test_login_invalid_credentials(self):
        """Test login con credenciales inválidas"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)