"""
Tests para API de Parcelas
Ejecutar con: python manage.py test test.test_parcelas
"""

from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from cooperativa.models import Rol, Comunidad, Socio, Parcela

User = get_user_model()


class ParcelasAPITests(APITestCase):
    """Tests para API de Parcelas"""

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

        # Crear socio
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

    def test_create_parcela(self):
        """Test crear parcela"""
        data = {
            'socio': self.socio.id,
            'nombre': 'Parcela 001',
            'superficie_hectareas': 5.5,
            'tipo_suelo': 'Arcilloso',
            'ubicacion': 'Ubicación de prueba',
            'latitud': Decimal('-16.50000000'),
            'longitud': Decimal('-68.10000000'),
            'estado': 'ACTIVA'
        }
        response = self.client.post('/api/parcelas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nombre'], 'Parcela 001')

    def test_create_parcela_invalid_superficie(self):
        """Test crear parcela con superficie inválida"""
        data = {
            'socio': self.socio.id,
            'nombre': 'Parcela 002',
            'superficie_hectareas': -1,  # Superficie negativa
            'latitud': Decimal('-16.50000000'),
            'longitud': Decimal('-68.10000000'),
            'estado': 'ACTIVA'
        }
        response = self.client.post('/api/parcelas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)