"""
Tests para CU2: Cerrar sesión y gestión avanzada de sesiones
Ejecutar con: python manage.py test test.test_cu2_logout
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


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