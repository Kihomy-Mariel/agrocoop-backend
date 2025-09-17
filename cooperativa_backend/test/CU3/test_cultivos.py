"""
Tests para API de Cultivos
Ejecutar con: python manage.py test test.test_cultivos
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from cooperativa.models import Rol, Comunidad, Socio, Parcela, Cultivo

User = get_user_model()


class CultivosAPITests(APITestCase):
    """Tests para API de Cultivos"""

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

        # Crear parcela
        self.rol = Rol.objects.create(
            nombre='Socio',
            descripcion='Miembro de la cooperativa'
        )
        self.comunidad = Comunidad.objects.create(
            nombre='Comunidad Test',
            municipio='Municipio Test',
            departamento='Departamento Test'
        )
        self.socio_user = User.objects.create_user(
            ci_nit='111111111',
            nombres='Juan',
            apellidos='Pérez',
            email='juan@example.com',
            usuario='socio1',
            password='pass123'
        )
        self.socio = Socio.objects.create(
            usuario=self.socio_user,
            comunidad=self.comunidad,
            codigo_interno='001',
            fecha_nacimiento='1990-01-01'
        )
        self.parcela = Parcela.objects.create(
            socio=self.socio,
            nombre='Parcela 001',
            superficie_hectareas=5.5,
            latitud=Decimal('-16.50000000'),
            longitud=Decimal('-68.10000000'),
            estado='ACTIVA'
        )

    def test_create_cultivo(self):
        """Test crear cultivo"""
        data = {
            'parcela': self.parcela.id,
            'especie': 'Maíz',
            'variedad': 'Variedad A',
            'tipo_semilla': 'Híbrida',
            'fecha_estimada_siembra': '2026-03-01',
            'hectareas_sembradas': 3.0,
            'estado': 'ACTIVO'
        }
        response = self.client.post('/api/cultivos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['especie'], 'Maíz')

    def test_list_cultivos(self):
        """Test listar cultivos"""
        response = self.client.get('/api/cultivos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # DRF returns paginated response
        self.assertIn('results', response.data)
        self.assertIsInstance(response.data['results'], list)