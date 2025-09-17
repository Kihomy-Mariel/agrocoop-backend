"""
Tests para API de Bitácora de Auditoría
Ejecutar con: python manage.py test test.test_bitacora
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class BitacoraAPITests(APITestCase):
    """Tests para API de Bitácora de Auditoría"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            ci_nit='987654321',
            nombres='Admin',
            apellidos='Sistema',
            email='admin@cooperativa.com',
            usuario='admin',
            password='admin123'
        )
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_list_bitacora(self):
        """Test listar bitácora de auditoría"""
        response = self.client.get('/api/bitacora/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF returns paginated response with 'results' key
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)