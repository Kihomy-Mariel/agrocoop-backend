from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear router para ViewSets
router = DefaultRouter()
router.register(r'roles', views.RolViewSet)
router.register(r'usuarios', views.UsuarioViewSet)
router.register(r'usuario-roles', views.UsuarioRolViewSet)
router.register(r'comunidades', views.ComunidadViewSet)
router.register(r'socios', views.SocioViewSet)
router.register(r'parcelas', views.ParcelaViewSet)
router.register(r'cultivos', views.CultivoViewSet)
router.register(r'bitacora', views.BitacoraAuditoriaViewSet)

# CU4: Nuevos ViewSets para gestión avanzada de parcelas y cultivos
router.register(r'ciclo-cultivos', views.CicloCultivoViewSet)
router.register(r'cosechas', views.CosechaViewSet)
router.register(r'tratamientos', views.TratamientoViewSet)
router.register(r'analisis-suelo', views.AnalisisSueloViewSet)
router.register(r'transferencias-parcela', views.TransferenciaParcelaViewSet)

# URLs de la aplicación
urlpatterns = [
    # Endpoints específicos deben ir ANTES del router para evitar conflictos
    # Vistas de autenticación API - CU2: Cerrar sesión
    path('api/auth/login/', views.login_view, name='login'),
    path('api/auth/test-login/', views.test_login, name='test-login'),
    path('api/auth/logout/', views.logout_view, name='logout'),
    path('api/auth/csrf/', views.csrf_token, name='csrf-token'),
    path('api/auth/status/', views.session_status, name='session-status'),

    # Endpoints adicionales para CU2 - Gestión avanzada de sesiones
    path('api/auth/invalidate-sessions/', views.invalidate_all_sessions, name='invalidate-sessions'),
    path('api/auth/session-info/', views.session_info, name='session-info'),
    path('api/auth/force-logout/<int:user_id>/', views.force_logout_user, name='force-logout-user'),

    # CU3: Gestión de Socios - Endpoints adicionales
    path('api/socios/crear-completo/', views.crear_socio_completo, name='crear-socio-completo'),
    path('api/socios/<int:socio_id>/activar-desactivar/', views.activar_desactivar_socio, name='activar-desactivar-socio'),
    path('api/usuarios/<int:usuario_id>/activar-desactivar/', views.activar_desactivar_usuario, name='activar-desactivar-usuario'),
    path('api/socios/buscar-avanzado/', views.buscar_socios_avanzado, name='buscar-socios-avanzado'),
    path('api/socios/buscar-por-cultivo/', views.buscar_socios_por_cultivo, name='buscar-socios-por-cultivo'),
    path('api/reportes/usuarios-socios/', views.reporte_usuarios_socios, name='reporte-usuarios-socios'),
    path('api/validar/datos-socio/', views.validar_datos_socio, name='validar-datos-socio'),

    # CU4: Endpoints específicos para gestión avanzada de parcelas y cultivos
    path('api/ciclos-cultivo/buscar-avanzado/', views.buscar_ciclos_cultivo_avanzado, name='buscar-ciclos-cultivo-avanzado'),
    path('api/parcelas/buscar-avanzado/', views.buscar_parcelas_avanzado, name='buscar-parcelas-avanzado'),
    path('api/reportes/productividad-parcelas/', views.reporte_productividad_parcelas, name='reporte-productividad-parcelas'),
    path('api/validar/transferencia-parcela/', views.validar_transferencia_parcela, name='validar-transferencia-parcela'),
    path('api/transferencias-parcela/<int:transferencia_id>/procesar/', views.procesar_transferencia_parcela, name='procesar-transferencia-parcela'),

    # Endpoint para tipos de suelo
    path('api/parcelas/tipos-suelo/', views.get_tipos_suelo, name='tipos-suelo'),

    # CU6: Endpoints específicos para gestión de roles y permisos
    path('api/roles/asignar-rol/', views.asignar_rol_usuario, name='asignar-rol-usuario'),
    path('api/roles/quitar-rol/', views.quitar_rol_usuario, name='quitar-rol-usuario'),
    path('api/usuarios/<int:usuario_id>/permisos/', views.permisos_usuario, name='permisos-usuario'),
    path('api/validar/permiso-usuario/', views.validar_permiso_usuario, name='validar-permiso-usuario'),
    path('api/reportes/roles-permisos/', views.reporte_roles_permisos, name='reporte-roles-permisos'),
    path('api/roles/crear-personalizado/', views.crear_rol_personalizado, name='crear-rol-personalizado'),
    path('api/roles/buscar-avanzado/', views.buscar_roles_avanzado, name='buscar-roles-avanzado'),

    # Nueva ruta para el endpoint de sesión de depuración
    path('api/auth/debug-session/', views.debug_session_status, name='debug-session'),
    path('api/socios/<int:socio_id>/debug-update/', views.debug_update_socio, name='debug-update-socio'),

    # Incluir rutas del router DESPUÉS de los endpoints específicos
    path('api/', include(router.urls)),
]