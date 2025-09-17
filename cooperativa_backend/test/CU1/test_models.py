"""
Pruebas unitarias para el Sistema de Gestión Cooperativa
"""
import os
import sys
import django
from django.test import TestCase
from django.contrib.auth import authenticate
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
django.setup()

# Importar modelos después de configurar Django
from cooperativa.models import Usuario, Socio, Comunidad, Parcela


class AuthenticationTestCase(APITestCase):
    """Pruebas para autenticación"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.user_data = {
            'usuario': 'testuser',
            'password': 'testpass123',
            'nombres': 'Usuario',
            'apellidos': 'Test',
            'email': 'test@example.com',
            'ci_nit': '12345678'
        }
        self.user = Usuario.objects.create_user(**self.user_data)

    def test_login_success(self):
        """Prueba login exitoso"""
        url = reverse('login')
        data = {
            'username': self.user_data['usuario'],
            'password': self.user_data['password']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mensaje', response.data)
        self.assertIn('usuario', response.data)

    def test_login_failure(self):
        """Prueba login fallido"""
        url = reverse('login')
        data = {
            'username': self.user_data['usuario'],
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)

    def test_logout(self):
        """Prueba logout"""
        # Primero hacer login
        self.client.force_authenticate(user=self.user)
        url = reverse('logout')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mensaje', response.data)


class SocioModelTestCase(TestCase):
    """Pruebas para el modelo Socio"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.usuario = Usuario.objects.create_user(
            usuario='socio_test',
            password='test123',
            nombres='Juan',
            apellidos='Pérez',
            email='juan@example.com',
            ci_nit='87654321'
        )
        self.comunidad = Comunidad.objects.create(
            nombre='Comunidad Test'
        )

    def test_crear_socio(self):
        """Prueba creación de socio"""
        socio = Socio.objects.create(
            usuario=self.usuario,
            comunidad=self.comunidad,
            estado='ACTIVO'
        )
        self.assertEqual(socio.usuario.nombres, 'Juan')
        self.assertEqual(socio.comunidad.nombre, 'Comunidad Test')

    def test_socio_str(self):
        """Prueba representación string del socio"""
        socio = Socio.objects.create(
            usuario=self.usuario,
            comunidad=self.comunidad
        )
        expected_str = f"{self.usuario.nombres} {self.usuario.apellidos}"
        self.assertEqual(str(socio), expected_str)


class ParcelaModelTestCase(TestCase):
    """Pruebas para el modelo Parcela"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.usuario = Usuario.objects.create_user(
            usuario='parcela_test',
            password='test123',
            nombres='María',
            apellidos='García',
            email='maria@example.com',
            ci_nit='11223344'
        )
        self.comunidad = Comunidad.objects.create(
            nombre='Comunidad Parcela'
        )
        self.socio = Socio.objects.create(
            usuario=self.usuario,
            comunidad=self.comunidad,
            estado='ACTIVO'
        )

    def test_crear_parcela(self):
        """Prueba creación de parcela"""
        from decimal import Decimal
        parcela = Parcela.objects.create(
            socio=self.socio,
            superficie_hectareas=Decimal('10.50'),
            latitud=Decimal('-16.50000000'),
            longitud=Decimal('-68.10000000'),
            estado='ACTIVA'
        )
        self.assertEqual(parcela.superficie_hectareas, Decimal('10.50'))
        self.assertEqual(parcela.latitud, Decimal('-16.50000000'))
        self.assertEqual(parcela.longitud, Decimal('-68.10000000'))

    def test_superficie_validation(self):
        """Prueba validación de superficie mayor a 0"""
        from decimal import Decimal
        with self.assertRaises(Exception):  # Debería fallar por validación
            Parcela.objects.create(
                socio=self.socio,
                superficie_hectareas=0,  # Superficie inválida
                latitud=Decimal('-16.50000000'),
                longitud=Decimal('-68.10000000')
            )


class ComunidadModelTestCase(TestCase):
    """Pruebas para el modelo Comunidad"""

    def test_crear_comunidad(self):
        """Prueba creación de comunidad"""
        comunidad = Comunidad.objects.create(
            nombre='Nueva Comunidad'
        )
        self.assertEqual(comunidad.nombre, 'Nueva Comunidad')

    def test_comunidad_str(self):
        """Prueba representación string de la comunidad"""
        comunidad = Comunidad.objects.create(
            nombre='Comunidad String Test'
        )
        self.assertEqual(str(comunidad), 'Comunidad String Test')


# Pruebas de integración para API
class SocioAPITestCase(APITestCase):
    """Pruebas de API para Socios"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.user = Usuario.objects.create_user(
            usuario='api_test',
            password='test123',
            nombres='API',
            apellidos='Test',
            email='api@example.com',
            ci_nit='55667788'
        )
        self.comunidad = Comunidad.objects.create(
            nombre='API Comunidad'
        )
        self.user.is_staff = True
        self.user.save()
        self.client.force_authenticate(user=self.user)

    def test_listar_socios(self):
        """Prueba listar socios via API"""
        url = reverse('socio-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_crear_socio_api(self):
        """Prueba crear socio via API"""
        url = reverse('crear-socio-completo')
        data = {
            'ci_nit': '33445566',
            'nombres': 'Nuevo',
            'apellidos': 'Socio API',
            'email': 'nuevo_api@example.com',
            'telefono': '77712345',
            'usuario_username': 'nuevo_socio_api',
            'password': 'password123',
            'codigo_interno': 'API-001',
            'fecha_nacimiento': '1990-01-01',
            'sexo': 'M',
            'direccion': 'Dirección de prueba',
            'comunidad': self.comunidad.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


if __name__ == '__main__':
    # Ejecutar pruebas
    import unittest
    unittest.main()