#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de prueba
"""
import os
import sys
import django
from django.utils import timezone

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
django.setup()

from cooperativa.models import Rol, Usuario, Comunidad, Socio, Parcela, Cultivo

def crear_datos_prueba():
    print("Verificando y creando datos de prueba...")

    # Verificar y crear roles usando los métodos del modelo
    print("Verificando roles...")
    admin_rol = Rol.crear_rol_administrador()
    print("✓ Rol Administrador configurado")

    socio_rol = Rol.crear_rol_socio()
    print("✓ Rol Socio configurado")

    operador_rol = Rol.crear_rol_operador()
    print("✓ Rol Operador configurado")

    # Verificar y crear comunidades
    print("Verificando comunidades...")
    if not Comunidad.objects.filter(nombre='Comunidad San Pedro').exists():
        comunidad1 = Comunidad.objects.create(
            nombre='Comunidad San Pedro',
            municipio='Cochabamba',
            departamento='Cochabamba'
        )
        print("✓ Comunidad San Pedro creada")
    else:
        comunidad1 = Comunidad.objects.get(nombre='Comunidad San Pedro')
        print("✓ Comunidad San Pedro ya existe")

    if not Comunidad.objects.filter(nombre='Comunidad Villa Tunari').exists():
        comunidad2 = Comunidad.objects.create(
            nombre='Comunidad Villa Tunari',
            municipio='Villa Tunari',
            departamento='Cochabamba'
        )
        print("✓ Comunidad Villa Tunari creada")
    else:
        comunidad2 = Comunidad.objects.get(nombre='Comunidad Villa Tunari')
        print("✓ Comunidad Villa Tunari ya existe")

    # Verificar y crear usuarios adicionales
    print("Verificando usuarios...")
    if not Usuario.objects.filter(usuario='operador1').exists():
        operador_user = Usuario.objects.create_user(
            ci_nit='123456789',
            nombres='Juan Carlos',
            apellidos='Rodriguez Silva',
            email='operador@cooperativa.com',
            usuario='operador1',
            password='operador123'
        )
        print("✓ Usuario operador1 creado")
    else:
        operador_user = Usuario.objects.get(usuario='operador1')
        print("✓ Usuario operador1 ya existe")

    if not Usuario.objects.filter(usuario='socio1').exists():
        socio1_user = Usuario.objects.create_user(
            ci_nit='987654321',
            nombres='Maria Elena',
            apellidos='Perez Lopez',
            email='maria@cooperativa.com',
            usuario='socio1',
            password='socio123'
        )
        print("✓ Usuario socio1 creado")
    else:
        socio1_user = Usuario.objects.get(usuario='socio1')
        print("✓ Usuario socio1 ya existe")

    if not Usuario.objects.filter(usuario='socio2').exists():
        socio2_user = Usuario.objects.create_user(
            ci_nit='456789123',
            nombres='Carlos Alberto',
            apellidos='Gomez Martinez',
            email='carlos@cooperativa.com',
            usuario='socio2',
            password='socio123'
        )
        print("✓ Usuario socio2 creado")
    else:
        socio2_user = Usuario.objects.get(usuario='socio2')
        print("✓ Usuario socio2 ya existe")

    # Verificar y crear socios
    print("Verificando socios...")
    if not Socio.objects.filter(usuario__usuario='socio1').exists():
        socio1 = Socio.objects.create(
            usuario=socio1_user,
            codigo_interno='SOC001',
            fecha_nacimiento='1985-05-15',
            sexo='F',
            direccion='Zona Norte, Calle Principal 123',
            comunidad=comunidad1
        )
        print("✓ Socio SOC001 creado")
    else:
        socio1 = Socio.objects.get(usuario__usuario='socio1')
        print("✓ Socio SOC001 ya existe")

    if not Socio.objects.filter(usuario__usuario='socio2').exists():
        socio2 = Socio.objects.create(
            usuario=socio2_user,
            codigo_interno='SOC002',
            fecha_nacimiento='1978-12-03',
            sexo='M',
            direccion='Zona Sur, Avenida Central 456',
            comunidad=comunidad2
        )
        print("✓ Socio SOC002 creado")
    else:
        socio2 = Socio.objects.get(usuario__usuario='socio2')
        print("✓ Socio SOC002 ya existe")

    # Verificar y crear parcelas
    print("Verificando parcelas...")
    if not Parcela.objects.filter(socio=socio1, nombre='Parcela Norte').exists():
        parcela1 = Parcela.objects.create(
            socio=socio1,
            nombre='Parcela Norte',
            superficie_hectareas=5.5,
            tipo_suelo='Arcilloso',
            ubicacion='Sector Norte de la comunidad',
            latitud=-17.3895,
            longitud=-66.1568,
            estado='ACTIVA'
        )
        print("✓ Parcela Norte creada")
    else:
        parcela1 = Parcela.objects.get(socio=socio1, nombre='Parcela Norte')
        print("✓ Parcela Norte ya existe")

    if not Parcela.objects.filter(socio=socio1, nombre='Parcela Sur').exists():
        parcela2 = Parcela.objects.create(
            socio=socio1,
            nombre='Parcela Sur',
            superficie_hectareas=3.2,
            tipo_suelo='Arenoso',
            ubicacion='Sector Sur de la comunidad',
            latitud=-17.3912,
            longitud=-66.1589,
            estado='ACTIVA'
        )
        print("✓ Parcela Sur creada")
    else:
        parcela2 = Parcela.objects.get(socio=socio1, nombre='Parcela Sur')
        print("✓ Parcela Sur ya existe")

    if not Parcela.objects.filter(socio=socio2, nombre='Parcela Principal').exists():
        parcela3 = Parcela.objects.create(
            socio=socio2,
            nombre='Parcela Principal',
            superficie_hectareas=8.0,
            tipo_suelo='Franco',
            ubicacion='Centro de la comunidad',
            latitud=-17.3856,
            longitud=-66.1543,
            estado='ACTIVA'
        )
        print("✓ Parcela Principal creada")
    else:
        parcela3 = Parcela.objects.get(socio=socio2, nombre='Parcela Principal')
        print("✓ Parcela Principal ya existe")

    # Verificar y crear cultivos
    print("Verificando cultivos...")
    if not Cultivo.objects.filter(parcela=parcela1, especie='Maíz').exists():
        cultivo1 = Cultivo.objects.create(
            parcela=parcela1,
            especie='Maíz',
            variedad='Maíz duro',
            tipo_semilla='Híbrido',
            fecha_estimada_siembra='2025-10-15',
            hectareas_sembradas=3.0,
            estado='ACTIVO'
        )
        print("✓ Cultivo Maíz creado")
    else:
        print("✓ Cultivo Maíz ya existe")

    if not Cultivo.objects.filter(parcela=parcela2, especie='Papa').exists():
        cultivo2 = Cultivo.objects.create(
            parcela=parcela2,
            especie='Papa',
            variedad='Papa blanca',
            tipo_semilla='Nativa',
            fecha_estimada_siembra='2025-09-20',
            hectareas_sembradas=2.5,
            estado='ACTIVO'
        )
        print("✓ Cultivo Papa creado")
    else:
        print("✓ Cultivo Papa ya existe")

    if not Cultivo.objects.filter(parcela=parcela3, especie='Trigo').exists():
        cultivo3 = Cultivo.objects.create(
            parcela=parcela3,
            especie='Trigo',
            variedad='Trigo panadero',
            tipo_semilla='Mejorada',
            fecha_estimada_siembra='2025-11-01',
            hectareas_sembradas=6.0,
            estado='ACTIVO'
        )
        print("✓ Cultivo Trigo creado")
    else:
        print("✓ Cultivo Trigo ya existe")

    print("\n✅ Verificación completada!")
    print(f"Total Roles: {Rol.objects.count()}")
    print(f"Total Usuarios: {Usuario.objects.count()}")
    print(f"Total Comunidades: {Comunidad.objects.count()}")
    print(f"Total Socios: {Socio.objects.count()}")
    print(f"Total Parcelas: {Parcela.objects.count()}")
    print(f"Total Cultivos: {Cultivo.objects.count()}")

    print("\nCredenciales de acceso:")
    print("Admin: usuario='admin', password='admin123'")
    print("Operador: usuario='operador1', password='operador123'")
    print("Socio1: usuario='socio1', password='socio123'")
    print("Socio2: usuario='socio2', password='socio123'")

    # Asignar roles a usuarios
    print("Asignando roles a usuarios...")
    from cooperativa.models import UsuarioRol

    # Asignar rol Operador al usuario operador1
    if not UsuarioRol.objects.filter(usuario=operador_user, rol=operador_rol).exists():
        UsuarioRol.objects.create(usuario=operador_user, rol=operador_rol)
        print("✓ Rol Operador asignado a operador1")

    # Asignar rol Socio a socio1 y socio2
    if not UsuarioRol.objects.filter(usuario=socio1_user, rol=socio_rol).exists():
        UsuarioRol.objects.create(usuario=socio1_user, rol=socio_rol)
        print("✓ Rol Socio asignado a socio1")

    if not UsuarioRol.objects.filter(usuario=socio2_user, rol=socio_rol).exists():
        UsuarioRol.objects.create(usuario=socio2_user, rol=socio_rol)
        print("✓ Rol Socio asignado a socio2")

if __name__ == '__main__':
    crear_datos_prueba()