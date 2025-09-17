"""
Tests para API de Socios
Ejecutar con: python manage.py test test.test_socios
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from cooperativa.models import Rol, Comunidad, Socio

User = get_user_model()


class SociosAPITests(APITestCase):
    """Tests para API de Socios"""

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

        # Crear datos relacionados
        self.rol = Rol.objects.create(
            nombre='Socio',
            descripcion='Miembro de la cooperativa'
        )
        self.comunidad = Comunidad.objects.create(
            nombre='Comunidad Test',
            municipio='Municipio Test',
            departamento='Departamento Test'
        )

    def test_create_socio(self):
        """Test crear socio"""
        # Crear usuario primero
        usuario_data = {
            'ci_nit': '222222222',
            'nombres': 'Juan',
            'apellidos': 'Pérez',
            'email': 'juan@example.com',
            'usuario': 'socio1',
            'password': 'pass123'
        }
        usuario_response = self.client.post('/api/usuarios/', usuario_data, format='json')
        self.assertEqual(usuario_response.status_code, status.HTTP_201_CREATED)
        usuario_id = usuario_response.data.get('id') or usuario_response.data.get('pk')

        # Verificar que el usuario se creó correctamente
        self.assertIsNotNone(usuario_id, "Usuario ID should not be None")

        # Crear socio con el usuario existente
        data = {
            'usuario': usuario_id,
            'comunidad': self.comunidad.id,
            'codigo_interno': '001',
            'fecha_nacimiento': '1990-01-01',
            'sexo': 'M',
            'direccion': 'Dirección de prueba'
        }
        response = self.client.post('/api/socios/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['codigo_interno'], '001')

    def test_list_socios(self):
        """Test listar socios"""
        response = self.client.get('/api/socios/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF returns paginated response
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)