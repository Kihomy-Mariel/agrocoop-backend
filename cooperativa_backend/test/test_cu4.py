"""
Tests para CU4: Gestión Avanzada de Parcelas y Cultivos
"""
import json
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import date, timedelta

from cooperativa.models import (
    Comunidad, Socio, Parcela, Cultivo, CicloCultivo,
    Cosecha, Tratamiento, AnalisisSuelo, TransferenciaParcela,
    BitacoraAuditoria
)

Usuario = get_user_model()


class CicloCultivoTests(APITestCase):
    """Tests para CicloCultivo"""

    def setUp(self):
        # Crear usuario admin
        self.admin_user = Usuario.objects.create_user(
            ci_nit='123456789',
            nombres='Admin',
            apellidos='Sistema',
            email='admin@test.com',
            usuario='admin',
            password='admin123'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()

        # Crear comunidad
        self.comunidad = Comunidad.objects.create(
            nombre='Comunidad Test',
            municipio='Municipio Test',
            departamento='Departamento Test'
        )

        # Crear socio
        self.socio_user = Usuario.objects.create_user(
            ci_nit='987654321',
            nombres='Juan',
            apellidos='Pérez',
            email='juan@test.com',
            usuario='jperez',
            password='password123'
        )
        self.socio = Socio.objects.create(
            usuario=self.socio_user,
            comunidad=self.comunidad,
            codigo_interno='SOC-987654321'
        )

        # Crear parcela
        self.parcela = Parcela.objects.create(
            socio=self.socio,
            nombre='Parcela Test',
            superficie_hectareas=10.5,
            tipo_suelo='Arcilloso',
            latitud=-16.5,
            longitud=-68.0,  # Cambiar a menos decimales
            estado='ACTIVA'
        )

        # Crear cultivo
        self.cultivo = Cultivo.objects.create(
            parcela=self.parcela,
            especie='Maíz',
            variedad='Variedad Test',
            hectareas_sembradas=8.0
        )

    def test_crear_ciclo_cultivo(self):
        """Test crear ciclo de cultivo"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'cultivo': self.cultivo.id,
            'fecha_inicio': '2024-01-15',
            'fecha_estimada_fin': '2024-05-15',
            'estado': 'PLANIFICADO',
            'costo_estimado': 5000.00,
            'rendimiento_esperado': 8000.00,
            'unidad_rendimiento': 'kg/ha'
        }

        response = self.client.post('/api/ciclo-cultivos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que se creó
        ciclo = CicloCultivo.objects.get(cultivo=self.cultivo)
        self.assertEqual(ciclo.estado, 'PLANIFICADO')
        self.assertEqual(ciclo.costo_estimado, 5000.00)

        # Verificar bitácora
        bitacora = BitacoraAuditoria.objects.filter(
            usuario=self.admin_user,
            accion='CREAR_CICLO_CULTIVO'
        ).first()
        self.assertIsNotNone(bitacora)

    def test_listar_ciclos_cultivo(self):
        """Test listar ciclos de cultivo"""
        self.client.force_authenticate(user=self.admin_user)

        # Crear ciclo
        ciclo = CicloCultivo.objects.create(
            cultivo=self.cultivo,
            fecha_inicio=date(2024, 1, 15),
            fecha_estimada_fin=date(2024, 5, 15)
        )

        response = self.client.get('/api/ciclo-cultivos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class CosechaTests(APITestCase):
    """Tests para Cosecha"""

    def setUp(self):
        # Crear datos similares al test anterior
        self.admin_user = Usuario.objects.create_user(
            ci_nit='123456789',
            nombres='Admin',
            apellidos='Sistema',
            email='admin@test.com',
            usuario='admin',
            password='admin123'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.comunidad = Comunidad.objects.create(nombre='Comunidad Test')
        self.socio_user = Usuario.objects.create_user(
            ci_nit='987654321',
            nombres='Juan',
            apellidos='Pérez',
            email='juan@test.com',
            usuario='jperez',
            password='password123'
        )
        self.socio = Socio.objects.create(
            usuario=self.socio_user,
            comunidad=self.comunidad
        )
        self.parcela = Parcela.objects.create(
            socio=self.socio,
            nombre='Parcela Test',
            superficie_hectareas=10.0,
            latitud=-16.5,
            longitud=-68.0
        )
        self.cultivo = Cultivo.objects.create(
            parcela=self.parcela,
            especie='Maíz',
            hectareas_sembradas=8.0
        )
        self.ciclo = CicloCultivo.objects.create(
            cultivo=self.cultivo,
            fecha_inicio=date(2024, 1, 15),
            fecha_estimada_fin=date(2024, 5, 15)
        )

    def test_crear_cosecha(self):
        """Test crear cosecha"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'ciclo_cultivo': self.ciclo.id,
            'fecha_cosecha': '2024-05-10',
            'cantidad_cosechada': 6500.00,
            'unidad_medida': 'kg',
            'calidad': 'BUENA',
            'precio_venta': 2.50
        }

        response = self.client.post('/api/cosechas/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar cálculo de valor total
        cosecha = Cosecha.objects.get(ciclo_cultivo=self.ciclo)
        self.assertEqual(cosecha.valor_total(), 16250.00)  # 6500 * 2.50

    def test_listar_cosechas(self):
        """Test listar cosechas"""
        self.client.force_authenticate(user=self.admin_user)

        # Crear cosecha
        Cosecha.objects.create(
            ciclo_cultivo=self.ciclo,
            fecha_cosecha=date(2024, 5, 10),
            cantidad_cosechada=6500.00
        )

        response = self.client.get('/api/cosechas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)


class TratamientoTests(APITestCase):
    """Tests para Tratamiento"""

    def setUp(self):
        # Configuración similar
        self.admin_user = Usuario.objects.create_user(
            ci_nit='123456789',
            nombres='Admin',
            apellidos='Sistema',
            email='admin@test.com',
            usuario='admin',
            password='admin123'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.comunidad = Comunidad.objects.create(nombre='Comunidad Test')
        self.socio_user = Usuario.objects.create_user(
            ci_nit='987654321',
            nombres='Juan',
            apellidos='Pérez',
            email='juan@test.com',
            usuario='jperez',
            password='password123'
        )
        self.socio = Socio.objects.create(
            usuario=self.socio_user,
            comunidad=self.comunidad
        )
        self.parcela = Parcela.objects.create(
            socio=self.socio,
            nombre='Parcela Test',
            superficie_hectareas=10.0,
            latitud=-16.5,
            longitud=-68.0
        )
        self.cultivo = Cultivo.objects.create(
            parcela=self.parcela,
            especie='Maíz',
            hectareas_sembradas=8.0
        )
        self.ciclo = CicloCultivo.objects.create(
            cultivo=self.cultivo,
            fecha_inicio=date(2024, 1, 15),
            fecha_estimada_fin=date(2024, 5, 15)
        )

    def test_crear_tratamiento(self):
        """Test crear tratamiento"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'ciclo_cultivo': self.ciclo.id,
            'tipo_tratamiento': 'FERTILIZANTE',
            'nombre_producto': 'Urea 46-0-0',
            'dosis': 200.00,
            'unidad_dosis': 'kg/ha',
            'fecha_aplicacion': '2024-02-15',
            'costo': 1500.00,
            'aplicado_por': 'Juan Pérez'
        }

        response = self.client.post('/api/tratamientos/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        tratamiento = Tratamiento.objects.get(ciclo_cultivo=self.ciclo)
        self.assertEqual(tratamiento.tipo_tratamiento, 'FERTILIZANTE')
        self.assertEqual(tratamiento.costo, 1500.00)


class AnalisisSueloTests(APITestCase):
    """Tests para AnalisisSuelo"""

    def setUp(self):
        self.admin_user = Usuario.objects.create_user(
            ci_nit='123456789',
            nombres='Admin',
            apellidos='Sistema',
            email='admin@test.com',
            usuario='admin',
            password='admin123'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.comunidad = Comunidad.objects.create(nombre='Comunidad Test')
        self.socio_user = Usuario.objects.create_user(
            ci_nit='987654321',
            nombres='Juan',
            apellidos='Pérez',
            email='juan@test.com',
            usuario='jperez',
            password='password123'
        )
        self.socio = Socio.objects.create(
            usuario=self.socio_user,
            comunidad=self.comunidad
        )
        self.parcela = Parcela.objects.create(
            socio=self.socio,
            nombre='Parcela Test',
            superficie_hectareas=10.0,
            latitud=-16.5,
            longitud=-68.0
        )

    def test_crear_analisis_suelo(self):
        """Test crear análisis de suelo"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'parcela': self.parcela.id,
            'fecha_analisis': '2024-01-10',
            'ph': 6.5,
            'materia_organica': 3.2,
            'nitrogeno': 0.15,
            'fosforo': 25.0,
            'potasio': 180.0,
            'laboratorio': 'Laboratorio ABC',
            'costo_analisis': 500.00
        }

        response = self.client.post('/api/analisis-suelo/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        analisis = AnalisisSuelo.objects.get(parcela=self.parcela)
        self.assertEqual(analisis.ph, 6.5)
        self.assertEqual(len(analisis.get_recomendaciones_basicas()), 1)  # pH óptimo

    def test_analisis_ph_invalido(self):
        """Test validación de pH inválido"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'parcela': self.parcela.id,
            'fecha_analisis': '2024-01-10',
            'ph': 15.0,  # pH inválido
        }

        response = self.client.post('/api/analisis-suelo/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TransferenciaParcelaTests(APITestCase):
    """Tests para TransferenciaParcela"""

    def setUp(self):
        self.admin_user = Usuario.objects.create_user(
            ci_nit='123456789',
            nombres='Admin',
            apellidos='Sistema',
            email='admin@test.com',
            usuario='admin',
            password='admin123'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()

        self.comunidad = Comunidad.objects.create(nombre='Comunidad Test')

        # Socio anterior
        self.socio_anterior_user = Usuario.objects.create_user(
            ci_nit='111111111',
            nombres='Pedro',
            apellidos='Gómez',
            email='pedro@test.com',
            usuario='pgomez',
            password='password123'
        )
        self.socio_anterior = Socio.objects.create(
            usuario=self.socio_anterior_user,
            comunidad=self.comunidad
        )

        # Socio nuevo
        self.socio_nuevo_user = Usuario.objects.create_user(
            ci_nit='222222222',
            nombres='María',
            apellidos='López',
            email='maria@test.com',
            usuario='mlopez',
            password='password123'
        )
        self.socio_nuevo = Socio.objects.create(
            usuario=self.socio_nuevo_user,
            comunidad=self.comunidad
        )

        # Parcela del socio anterior
        self.parcela = Parcela.objects.create(
            socio=self.socio_anterior,
            nombre='Parcela Transferible',
            superficie_hectareas=5.0,
            latitud=-16.5,
            longitud=-68.0
        )

    def test_crear_transferencia_parcela(self):
        """Test crear transferencia de parcela"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'parcela': self.parcela.id,
            'socio_anterior': self.socio_anterior.id,
            'socio_nuevo': self.socio_nuevo.id,
            'fecha_transferencia': '2024-03-15',
            'motivo': 'Venta de parcela',
            'costo_transferencia': 1000.00,
            'autorizado_por': self.admin_user.id
        }

        response = self.client.post('/api/transferencias-parcela/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar que la parcela cambió de propietario
        self.parcela.refresh_from_db()
        self.assertEqual(self.parcela.socio, self.socio_nuevo)

    def test_validar_transferencia(self):
        """Test validar transferencia"""
        self.client.force_authenticate(user=self.admin_user)

        url = f'/api/validar/transferencia-parcela/?parcela_id={self.parcela.id}&socio_nuevo_id={self.socio_nuevo.id}'

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['valido'])

    def test_procesar_transferencia_aprobar(self):
        """Test procesar transferencia - aprobar"""
        self.client.force_authenticate(user=self.admin_user)

        # Crear transferencia
        transferencia = TransferenciaParcela.objects.create(
            parcela=self.parcela,
            socio_anterior=self.socio_anterior,
            socio_nuevo=self.socio_nuevo,
            fecha_transferencia=date(2024, 3, 15),
            motivo='Transferencia test'
        )

        data = {
            'accion': 'APROBAR',
            'observaciones': 'Aprobada por administrador'
        }

        response = self.client.post(
            f'/api/transferencias-parcela/{transferencia.id}/procesar/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar estado
        transferencia.refresh_from_db()
        self.assertEqual(transferencia.estado, 'APROBADA')


class ReportesCU4Tests(APITestCase):
    """Tests para reportes de CU4"""

    def setUp(self):
        self.admin_user = Usuario.objects.create_user(
            ci_nit='123456789',
            nombres='Admin',
            apellidos='Sistema',
            email='admin@test.com',
            usuario='admin',
            password='admin123'
        )
        self.admin_user.is_staff = True
        self.admin_user.save()

        # Crear datos de prueba
        self.comunidad = Comunidad.objects.create(nombre='Comunidad Test')
        self.socio_user = Usuario.objects.create_user(
            ci_nit='987654321',
            nombres='Juan',
            apellidos='Pérez',
            email='juan@test.com',
            usuario='jperez',
            password='password123'
        )
        self.socio = Socio.objects.create(
            usuario=self.socio_user,
            comunidad=self.comunidad
        )
        self.parcela = Parcela.objects.create(
            socio=self.socio,
            nombre='Parcela Test',
            superficie_hectareas=10.0,
            latitud=-16.5,
            longitud=-68.0
        )
        self.cultivo = Cultivo.objects.create(
            parcela=self.parcela,
            especie='Maíz',
            hectareas_sembradas=8.0
        )
        self.ciclo = CicloCultivo.objects.create(
            cultivo=self.cultivo,
            fecha_inicio=date(2024, 1, 15),
            fecha_estimada_fin=date(2024, 5, 15)
        )

    def test_reporte_productividad_parcelas(self):
        """Test reporte de productividad"""
        self.client.force_authenticate(user=self.admin_user)

        # Crear cosecha
        Cosecha.objects.create(
            ciclo_cultivo=self.ciclo,
            fecha_cosecha=date(2024, 5, 10),
            cantidad_cosechada=6400.00
        )

        # Crear tratamiento
        Tratamiento.objects.create(
            ciclo_cultivo=self.ciclo,
            tipo_tratamiento='FERTILIZANTE',
            nombre_producto='Urea',
            dosis=200.00,
            fecha_aplicacion=date(2024, 2, 15)
        )

        # Crear análisis
        AnalisisSuelo.objects.create(
            parcela=self.parcela,
            fecha_analisis=date(2024, 1, 10),
            ph=6.5,
            materia_organica=3.0
        )

        response = self.client.get('/api/reportes/productividad-parcelas/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar estructura del reporte
        self.assertIn('estadisticas_generales', response.data)
        self.assertIn('productividad_por_especie', response.data)
        self.assertIn('rendimiento_parcelas_top20', response.data)
        self.assertIn('tratamientos_por_mes', response.data)
        self.assertIn('analisis_suelo_por_tipo', response.data)
