"""
Tests para T030: Bitácora extendida
Ejecutar con: python manage.py test test.test_cu2_bitacora
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from cooperativa.models import BitacoraAuditoria

User = get_user_model()


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