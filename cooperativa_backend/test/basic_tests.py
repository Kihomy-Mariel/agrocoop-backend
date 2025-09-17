"""
Tests básicos para verificar funcionamiento del backend
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from cooperativa.models import Rol, Comunidad

User = get_user_model()


class BasicAPITests(APITestCase):
    """Tests básicos de la API"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            ci_nit='123456789',
            nombres='Admin',
            apellidos='Sistema',
            email='admin@test.com',
            usuario='admin',
            password='admin123'
        )
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_api_root(self):
        """Test que la API responde"""
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_auth_endpoints(self):
        """Test endpoints de autenticación"""
        # Login
        data = {'username': 'admin', 'password': 'admin123'}
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Status
        response = self.client.get('/api/auth/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crud_operations(self):
        """Test operaciones CRUD básicas"""
        # Crear comunidad
        comunidad_data = {
            'nombre': 'Test Comunidad',
            'municipio': 'Test Municipio',
            'departamento': 'Test Departamento'
        }
        response = self.client.post('/api/comunidades/', comunidad_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        comunidad_id = response.data['id']

        # Leer comunidad
        response = self.client.get(f'/api/comunidades/{comunidad_id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre'], 'Test Comunidad')

        # Actualizar comunidad
        update_data = {'nombre': 'Comunidad Actualizada'}
        response = self.client.put(f'/api/comunidades/{comunidad_id}/', update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Listar comunidades
        response = self.client.get('/api/comunidades/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)