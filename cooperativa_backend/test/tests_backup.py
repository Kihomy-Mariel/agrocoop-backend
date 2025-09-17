"""
Tests para verificar el funcionamiento de la API
Ejecutar con: python manage.py test
"""

import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from cooperativa.models import Rol, Comunidad, Socio, Parcela, Cultivo

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
            'latitud': -16.5,
            'longitud': -68.1,
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
            'latitud': -16.5,
            'longitud': -68.1,
            'estado': 'ACTIVA'
        }
        response = self.client.post('/api/parcelas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


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
            estado='ACTIVA'
        )

    def test_create_cultivo(self):
        """Test crear cultivo"""
        data = {
            'parcela': self.parcela.id,
            'especie': 'Maíz',
            'variedad': 'Variedad A',
            'tipo_semilla': 'Híbrida',
            'fecha_estimada_siembra': '2030-03-01',
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


class CU2LogoutTests(APITestCase):
    """Tests para CU2: Cerrar sesión y gestión avanzada de sesiones"""

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
        self.admin_user = User.objects.create_user(
            ci_nit='987654321',
            nombres='Admin',
            apellidos='Sistema',
            email='admin@cooperativa.com',
            usuario='admin',
            password='admin123'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()

    def test_logout_success(self):
        """CU2: Test logout exitoso"""
        # Login primero
        self.client.force_authenticate(user=self.user)

        # Logout
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mensaje', response.data)
        self.assertEqual(response.data['mensaje'], 'Sesión cerrada exitosamente')

    def test_logout_without_authentication(self):
        """CU2: Test logout sin autenticación"""
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_session_status_authenticated(self):
        """CU2: Test verificar estado de sesión autenticado"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/status/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['autenticado'])
        self.assertIn('usuario', response.data)

    def test_session_status_not_authenticated(self):
        """CU2: Test verificar estado de sesión no autenticado"""
        response = self.client.get('/api/auth/status/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_session_info_authenticated(self):
        """CU2: Test información detallada de sesión"""
        self.client.force_authenticate(user=self.user)
        response = self.client.get('/api/auth/session-info/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('usuario', response.data)
        self.assertIn('session_id', response.data)
        self.assertIn('ip_address', response.data)
        self.assertIn('user_agent', response.data)
        self.assertTrue(response.data['autenticado'])

    def test_invalidate_all_sessions(self):
        """CU2: Test invalidar todas las sesiones del usuario"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/auth/invalidate-sessions/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mensaje', response.data)
        self.assertIn('sesiones_invalidada', response.data)

    def test_force_logout_user_by_admin(self):
        """CU2: Test forzar logout de usuario por admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(f'/api/auth/force-logout/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('mensaje', response.data)
        self.assertIn('usuario_afectado', response.data)

    def test_force_logout_user_by_non_admin(self):
        """CU2: Test forzar logout por usuario no admin (debe fallar)"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/api/auth/force-logout/{self.admin_user.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)

    def test_force_logout_nonexistent_user(self):
        """CU2: Test forzar logout de usuario inexistente"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post('/api/auth/force-logout/99999/')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)


class CU2BitacoraExtendidaTests(APITestCase):
    """Tests para T030: Bitácora extendida"""

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

    def test_login_creates_audit_log(self):
        """T030: Test que login crea registro en bitácora extendida"""
        from cooperativa.models import BitacoraAuditoria

        # Login
        data = {'username': 'testuser', 'password': 'testpass123'}
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar registro en bitácora
        audit_log = BitacoraAuditoria.objects.filter(
            usuario=self.user,
            accion='LOGIN'
        ).first()
        self.assertIsNotNone(audit_log)
        self.assertIsNotNone(audit_log.ip_address)
        self.assertIsNotNone(audit_log.user_agent)

    def test_logout_creates_audit_log(self):
        """T030: Test que logout crea registro en bitácora extendida"""
        from cooperativa.models import BitacoraAuditoria

        # Login y logout
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/auth/logout/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar registro en bitácora
        audit_log = BitacoraAuditoria.objects.filter(
            usuario=self.user,
            accion='LOGOUT'
        ).first()
        self.assertIsNotNone(audit_log)
        self.assertIsNotNone(audit_log.ip_address)
        self.assertIsNotNone(audit_log.user_agent)

    def test_failed_login_creates_audit_log(self):
        """T030: Test que login fallido crea registro en bitácora extendida"""
        from cooperativa.models import BitacoraAuditoria

        # Intentar login con contraseña incorrecta
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post('/api/auth/login/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Verificar registro en bitácora
        audit_log = BitacoraAuditoria.objects.filter(
            usuario=self.user,
            accion='LOGIN_FALLIDO'
        ).first()
        self.assertIsNotNone(audit_log)
        self.assertIsNotNone(audit_log.ip_address)
        self.assertIsNotNone(audit_log.user_agent)

    def test_account_block_audit_log(self):
        """T030: Test que bloqueo de cuenta crea registro en bitácora"""
        from cooperativa.models import BitacoraAuditoria

        # Simular múltiples intentos fallidos
        self.user.intentos_fallidos = 5
        self.user.save()

        # Intentar login (debería bloquear)
        data = {'username': 'testuser', 'password': 'wrongpassword'}
        response = self.client.post('/api/auth/login/', data, format='json')

        # Verificar registro de bloqueo en bitácora
        audit_log = BitacoraAuditoria.objects.filter(
            usuario=self.user,
            accion='BLOQUEO_CUENTA'
        ).first()
        self.assertIsNotNone(audit_log)

    def test_audit_log_fields(self):
        """T030: Test que bitácora extendida incluye todos los campos"""
        from cooperativa.models import BitacoraAuditoria

        # Crear una acción que genere auditoría
        self.client.force_authenticate(user=self.user)
        self.client.post('/api/auth/logout/')

        # Verificar campos extendidos
        audit_log = BitacoraAuditoria.objects.filter(
            usuario=self.user,
            accion='LOGOUT'
        ).first()

        self.assertIsNotNone(audit_log.fecha)
        self.assertIsNotNone(audit_log.ip_address)
        self.assertIsNotNone(audit_log.user_agent)
        self.assertEqual(audit_log.tabla_afectada, 'usuario')
        self.assertEqual(audit_log.registro_id, self.user.id)