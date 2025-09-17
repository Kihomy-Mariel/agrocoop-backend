from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db.models import Q, Count, Sum, Avg, F, Case, When, DecimalField
from django.db.models.functions import TruncMonth
from django.contrib.sessions.models import Session
from .models import (
    Rol, Usuario, UsuarioRol, Comunidad, Socio,
    Parcela, Cultivo, BitacoraAuditoria,
    CicloCultivo, Cosecha, Tratamiento, AnalisisSuelo, TransferenciaParcela
)
from .serializers import (
    RolSerializer, UsuarioSerializer, UsuarioCreateSerializer,
    UsuarioRolSerializer, ComunidadSerializer, SocioSerializer,
    SocioCreateSerializer, SocioCreateSimpleSerializer, SocioUpdateSerializer, ParcelaSerializer, CultivoSerializer,
    BitacoraAuditoriaSerializer, CicloCultivoSerializer,
    CosechaSerializer, TratamientoSerializer, AnalisisSueloSerializer,
    TransferenciaParcelaSerializer
)


# Función auxiliar para obtener IP del cliente
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Vistas de Autenticación
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def test_login(request):
    """
    Test endpoint to debug login request
    """
    print("=" * 50)
    print("TEST LOGIN DEBUG - REQUEST RECEIVED")
    print("=" * 50)
    print(f"Content-Type: {request.content_type}")
    print(f"Method: {request.method}")
    print(f"Headers: {dict(request.headers)}")

    # Use DRF's request.data for consistent parsing
    if request.content_type == 'application/json':
        data = request.data
        print(f"Parsed data: {data}")
        print(f"Username from data: {data.get('username')}")
        print(f"Password from data: {data.get('password')}")
    else:
        print("Non-JSON content type, checking POST data")
        if hasattr(request, 'POST') and request.POST:
            print(f"POST data: {dict(request.POST)}")

    print("=" * 50)
    print("END TEST LOGIN DEBUG")
    print("=" * 50)

    return Response({'message': 'Debug info printed to console'})


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def login_view(request):
    """
    CU1: Iniciar sesión (web/móvil)
    T011: Autenticación y gestión de sesiones
    T013: Bitácora de auditoría básica
    """
    try:
        print("=== LOGIN DEBUG ===")
        print(f"Content-Type: {request.content_type}")
        print(f"Method: {request.method}")
        print(f"Headers: {dict(request.headers)}")

        # Use DRF's request.data for consistent parsing
        if request.content_type == 'application/json':
            data = request.data
            username = data.get('username')
            password = data.get('password')
            print(f"Parsed JSON data: {data}")
            print(f"Username: {username}, Password: {'*' * len(password) if password else None}")
        elif hasattr(request, 'POST') and request.POST:
            # Handle form data
            username = request.POST.get('username')
            password = request.POST.get('password')
        else:
            # Fallback to manual parsing if needed
            try:
                import json
                raw_body = request.body.decode('utf-8')
                data = json.loads(raw_body)
                username = data.get('username')
                password = data.get('password')
            except (json.JSONDecodeError, UnicodeDecodeError, AttributeError):
                return Response(
                    {'error': 'Formato de datos no soportado'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not username or not password:
            return Response(
                {'error': 'Usuario y contraseña son requeridos'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Test basic authentication
        user = authenticate(request, username=username, password=password)

        if user:
            # Verificar si el usuario está bloqueado
            if user.estado == 'BLOQUEADO':
                return Response(
                    {'error': 'Cuenta bloqueada. Contacte al administrador'},
                    status=status.HTTP_403_FORBIDDEN
                )

            # Login exitoso
            login(request, user)

            # Reset failed attempts
            user.intentos_fallidos = 0
            user.ultimo_intento = timezone.now()
            user.save()

            # Registrar login en bitácora - T013
            BitacoraAuditoria.objects.create(
                usuario=user,
                accion='LOGIN',
                tabla_afectada='usuario',
                registro_id=user.id,
                detalles={
                    'ip': request.META.get('REMOTE_ADDR'),
                    'user_agent': request.META.get('HTTP_USER_AGENT'),
                    'metodo_autenticacion': 'credenciales',
                    'estado_usuario': user.estado
                },
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
            )

            # Simple response without serializer for now
            return Response({
                'mensaje': 'Login exitoso',
                'usuario': {
                    'id': user.id,
                    'usuario': user.usuario,
                    'nombres': user.nombres,
                    'apellidos': user.apellidos,
                    'email': user.email,
                    'estado': user.estado,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                },
                'csrf_token': get_token(request)
            })

        else:
            return Response(
                {'error': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Exception as e:
        # Catch any unexpected errors
        print(f"Unexpected error in login_view: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Error interno del servidor: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def logout_view(request):
    """
    CU2: Cerrar sesión (web/móvil)
    T023: Implementación de cierre de sesión
    T030: Bitácora extendida - Registro de cierres de sesión
    """
    user = request.user

    # Registrar logout en bitácora extendida - T030
    BitacoraAuditoria.objects.create(
        usuario=user,
        accion='LOGOUT',
        tabla_afectada='usuario',
        registro_id=user.id,
        detalles={
            'ip': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'sesion_duracion': 'calculada'  # Podría calcularse con session start time
        },
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
    )

    logout(request)

    return Response({'mensaje': 'Sesión cerrada exitosamente'})


@api_view(['GET'])
@permission_classes([AllowAny])
@csrf_exempt
def csrf_token(request):
    """
    Obtener token CSRF para el frontend
    """
    return Response({'csrf_token': get_token(request)})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def session_status(request):
    """
    Verificar estado de la sesión
    """
    serializer = UsuarioSerializer(request.user)
    return Response({
        'autenticado': True,
        'usuario': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invalidate_all_sessions(request):
    """
    CU2: Invalidar todas las sesiones del usuario actual
    T011: Gestión de sesiones
    T030: Bitácora extendida
    """
    user = request.user

    # Invalidar todas las sesiones del usuario
    sessions_deleted = 0

    for session in Session.objects.all():
        session_data = session.get_decoded()
        if session_data.get('_auth_user_id') == str(user.id):
            session.delete()
            sessions_deleted += 1

    # Registrar en bitácora - T030
    BitacoraAuditoria.objects.create(
        usuario=user,
        accion='SESION_INVALIDADA',
        tabla_afectada='usuario',
        registro_id=user.id,
        detalles={
            'ip': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'sesiones_invalidada': sessions_deleted,
            'razon': 'Invalidación manual de todas las sesiones'
        },
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT')
    )

    return Response({
        'mensaje': f'Se invalidaron {sessions_deleted} sesiones',
        'sesiones_invalidada': sessions_deleted
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def session_info(request):
    """
    CU2: Información detallada de la sesión actual
    T011: Gestión de sesiones
    """
    user = request.user
    session_key = request.session.session_key

    return Response({
        'usuario': UsuarioSerializer(user).data,
        'session_id': session_key,
        'ip_address': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'session_expiry': request.session.get_expiry_date(),
        'is_secure': request.is_secure(),
        'autenticado': True
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def force_logout_user(request, user_id):
    """
    CU2: Forzar cierre de sesión de otro usuario (solo admin)
    T011: Gestión de sesiones
    T030: Bitácora extendida
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        target_user = Usuario.objects.get(id=user_id)

        # Invalidar sesiones del usuario objetivo
        sessions_deleted = 0

        for session in Session.objects.all():
            session_data = session.get_decoded()
            if session_data.get('_auth_user_id') == str(target_user.id):
                session.delete()
                sessions_deleted += 1

        # Registrar en bitácora - T030
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='SESION_INVALIDADA',
            tabla_afectada='usuario',
            registro_id=target_user.id,
            detalles={
                'ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT'),
                'sesiones_invalidada': sessions_deleted,
                'razon': 'Invalidación forzada por administrador',
                'admin': request.user.usuario
            },
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
        )

        return Response({
            'mensaje': f'Se invalidaron {sessions_deleted} sesiones del usuario {target_user.usuario}',
            'usuario_afectado': target_user.usuario,
            'sesiones_invalidada': sessions_deleted
        })

    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )


class RolViewSet(viewsets.ModelViewSet):
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Solo administradores pueden ver roles del sistema
        if not self.request.user.is_staff:
            queryset = queryset.filter(es_sistema=False)
        return queryset

    def perform_create(self, serializer):
        """T012: Registrar creación de rol en bitácora"""
        instance = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR',
            tabla_afectada='rol',
            registro_id=instance.id,
            detalles={'creado_por': self.request.user.usuario}
        )

    def perform_update(self, serializer):
        """T012: Registrar actualización de rol en bitácora"""
        instance = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR',
            tabla_afectada='rol',
            registro_id=instance.id,
            detalles={'actualizado_por': self.request.user.usuario}
        )

    def perform_destroy(self, instance):
        """T012: Registrar eliminación de rol en bitácora"""
        if instance.es_sistema:
            raise serializers.ValidationError('No se puede eliminar un rol del sistema')

        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ELIMINAR',
            tabla_afectada='rol',
            registro_id=instance.id,
            detalles={'eliminado_por': self.request.user.usuario}
        )
        instance.delete()

    @action(detail=True, methods=['post'])
    def asignar_usuario(self, request, pk=None):
        """CU6: Asignar rol a usuario"""
        rol = self.get_object()
        usuario_id = request.data.get('usuario_id')

        if not usuario_id:
            return Response(
                {'error': 'usuario_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            usuario = Usuario.objects.get(id=usuario_id)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Verificar si ya tiene este rol
        if UsuarioRol.objects.filter(usuario=usuario, rol=rol).exists():
            return Response(
                {'error': 'El usuario ya tiene asignado este rol'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear asignación
        usuario_rol = UsuarioRol.objects.create(usuario=usuario, rol=rol)

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='CREAR',
            tabla_afectada='usuario_rol',
            registro_id=usuario_rol.id,
            detalles={
                'rol_asignado': rol.nombre,
                'usuario_afectado': usuario.usuario,
                'asignado_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
        )

        serializer = UsuarioRolSerializer(usuario_rol)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def quitar_usuario(self, request, pk=None):
        """CU6: Quitar rol a usuario"""
        rol = self.get_object()
        usuario_id = request.data.get('usuario_id')

        if not usuario_id:
            return Response(
                {'error': 'usuario_id es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            usuario = Usuario.objects.get(id=usuario_id)
            usuario_rol = UsuarioRol.objects.get(usuario=usuario, rol=rol)
        except Usuario.DoesNotExist:
            return Response(
                {'error': 'Usuario no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )
        except UsuarioRol.DoesNotExist:
            return Response(
                {'error': 'El usuario no tiene asignado este rol'},
                status=status.HTTP_404_NOT_FOUND
            )

        # No permitir quitar roles del sistema si es el último
        if rol.es_sistema:
            otros_roles_sistema = UsuarioRol.objects.filter(
                usuario=usuario,
                rol__es_sistema=True
            ).exclude(id=usuario_rol.id).count()

            if otros_roles_sistema == 0:
                return Response(
                    {'error': 'No se puede quitar el último rol del sistema del usuario'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        usuario_rol_id = usuario_rol.id
        usuario_rol.delete()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='ELIMINAR',
            tabla_afectada='usuario_rol',
            registro_id=usuario_rol_id,
            detalles={
                'rol_removido': rol.nombre,
                'usuario_afectado': usuario.usuario,
                'removido_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
        )

        return Response({'mensaje': 'Rol removido exitosamente'})

    @action(detail=True, methods=['get'])
    def usuarios(self, request, pk=None):
        """CU6: Obtener usuarios con este rol"""
        rol = self.get_object()
        usuarios_roles = UsuarioRol.objects.filter(rol=rol).select_related('usuario')
        serializer = UsuarioRolSerializer(usuarios_roles, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def duplicar(self, request, pk=None):
        """CU6: Duplicar rol con nuevos permisos"""
        rol_original = self.get_object()
        nuevo_nombre = request.data.get('nuevo_nombre')

        if not nuevo_nombre:
            return Response(
                {'error': 'nuevo_nombre es requerido'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que el nombre no exista
        if Rol.objects.filter(nombre__iexact=nuevo_nombre).exists():
            return Response(
                {'error': 'Ya existe un rol con este nombre'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crear rol duplicado
        nuevo_rol = Rol.objects.create(
            nombre=nuevo_nombre,
            descripcion=request.data.get('descripcion', f'Copia de {rol_original.nombre}'),
            permisos=rol_original.permisos.copy(),
            es_sistema=False
        )

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='CREAR',
            tabla_afectada='rol',
            registro_id=nuevo_rol.id,
            detalles={
                'rol_duplicado': rol_original.nombre,
                'creado_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
        )

        serializer = self.get_serializer(nuevo_rol)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by current user if not admin (users can only see themselves)
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(id=user.id)
        return queryset

    def update(self, request, *args, **kwargs):
        """Override update to check permissions"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permisos insuficientes'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        """T013: Registrar creación de usuario en bitácora"""
        instance = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR',
            tabla_afectada='usuario',
            registro_id=instance.id,
            detalles={'creado_por': self.request.user.usuario}
        )

    def perform_update(self, serializer):
        """T013: Registrar actualización de usuario en bitácora"""
        instance = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR',
            tabla_afectada='usuario',
            registro_id=instance.id,
            detalles={'actualizado_por': self.request.user.usuario}
        )

    def perform_destroy(self, instance):
        """T013: Registrar eliminación de usuario en bitácora"""
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ELIMINAR',
            tabla_afectada='usuario',
            registro_id=instance.id,
            detalles={'eliminado_por': self.request.user.usuario}
        )
        instance.delete()

    @action(detail=False, methods=['post'])
    def login(self, request):
        """CU1: Método de login alternativo (mantener compatibilidad)"""
        return login_view(request)

    @action(detail=True, methods=['post'])
    def cambiar_password(self, request, pk=None):
        user = self.get_object()
        nueva_password = request.data.get('nueva_password')

        if nueva_password:
            user.set_password(nueva_password)
            user.save()

            # Registrar cambio de contraseña en bitácora
            BitacoraAuditoria.objects.create(
                usuario=self.request.user,
                accion='CAMBIAR_PASSWORD',
                tabla_afectada='usuario',
                registro_id=user.id,
                detalles={'cambiado_por': self.request.user.usuario}
            )

            return Response({'mensaje': 'Contraseña cambiada exitosamente'})
        return Response(
            {'error': 'Nueva contraseña requerida'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """CU3: Activar usuario"""
        usuario = self.get_object()
        usuario.estado = 'ACTIVO'
        usuario.save()

        # Si es socio, activar también
        try:
            socio = Socio.objects.get(usuario=usuario)
            socio.estado = 'ACTIVO'
            socio.save()
        except Socio.DoesNotExist:
            pass

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='ACTIVAR_USUARIO',
            tabla_afectada='usuario',
            registro_id=usuario.id,
            detalles={'activado_por': request.user.usuario}
        )

        serializer = self.get_serializer(usuario)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """CU3: Desactivar usuario"""
        usuario = self.get_object()
        usuario.estado = 'INACTIVO'
        usuario.save()

        # Si es socio, desactivar también
        try:
            socio = Socio.objects.get(usuario=usuario)
            socio.estado = 'INACTIVO'
            socio.save()
        except Socio.DoesNotExist:
            pass

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='DESACTIVAR_USUARIO',
            tabla_afectada='usuario',
            registro_id=usuario.id,
            detalles={'desactivado_por': request.user.usuario}
        )

        serializer = self.get_serializer(usuario)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        """CU3: Obtener roles de un usuario"""
        usuario = self.get_object()
        roles = UsuarioRol.objects.filter(usuario=usuario).select_related('rol')
        serializer = UsuarioRolSerializer(roles, many=True)
        return Response(serializer.data)


class UsuarioRolViewSet(viewsets.ModelViewSet):
    queryset = UsuarioRol.objects.select_related('usuario', 'rol')
    serializer_class = UsuarioRolSerializer
    permission_classes = [IsAuthenticated]


class ComunidadViewSet(viewsets.ModelViewSet):
    queryset = Comunidad.objects.all()
    serializer_class = ComunidadSerializer
    permission_classes = [IsAuthenticated]


class SocioViewSet(viewsets.ModelViewSet):
    queryset = Socio.objects.select_related('usuario', 'comunidad')
    serializer_class = SocioSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Usar SocioCreateSimpleSerializer para creación, SocioUpdateSerializer para actualización, SocioSerializer para otras operaciones"""
        if self.action == 'create':
            return SocioCreateSimpleSerializer
        elif self.action == 'update':
            return SocioUpdateSerializer
        return SocioSerializer

    def update(self, request, *args, **kwargs):
        """Override update to check permissions"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permisos insuficientes'},
                status=status.HTTP_403_FORBIDDEN
            )
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by current user's socio if not admin
        user = self.request.user
        if not user.is_staff:
            try:
                socio = Socio.objects.get(usuario=user)
                queryset = queryset.filter(id=socio.id)
            except Socio.DoesNotExist:
                queryset = queryset.none()
        return queryset

    def perform_create(self, serializer):
        """T014: Registrar creación de socio en bitácora"""
        instance = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR',
            tabla_afectada='socio',
            registro_id=instance.id,
            detalles={'creado_por': self.request.user.usuario}
        )

    def perform_update(self, serializer):
        """T014: Registrar actualización de socio en bitácora"""
        instance = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR',
            tabla_afectada='socio',
            registro_id=instance.id,
            detalles={'actualizado_por': self.request.user.usuario}
        )

    def perform_destroy(self, instance):
        """T014: Registrar eliminación de socio en bitácora"""
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ELIMINAR',
            tabla_afectada='socio',
            registro_id=instance.id,
            detalles={'eliminado_por': self.request.user.usuario}
        )
        instance.delete()

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """CU3: Activar socio"""
        socio = self.get_object()
        socio.estado = 'ACTIVO'
        socio.usuario.estado = 'ACTIVO'
        socio.save()
        socio.usuario.save()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='ACTIVAR_SOCIO',
            tabla_afectada='socio',
            registro_id=socio.id,
            detalles={'activado_por': request.user.usuario}
        )

        serializer = self.get_serializer(socio)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """CU3: Desactivar socio"""
        socio = self.get_object()
        socio.estado = 'INACTIVO'
        socio.usuario.estado = 'INACTIVO'
        socio.save()
        socio.usuario.save()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='DESACTIVAR_SOCIO',
            tabla_afectada='socio',
            registro_id=socio.id,
            detalles={'desactivado_por': request.user.usuario}
        )

        serializer = self.get_serializer(socio)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def parcelas(self, request, pk=None):
        """CU3: Obtener parcelas de un socio"""
        socio = self.get_object()
        parcelas = Parcela.objects.filter(socio=socio)
        serializer = ParcelaSerializer(parcelas, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def cultivos(self, request, pk=None):
        """CU3: Obtener cultivos de un socio"""
        socio = self.get_object()
        cultivos = Cultivo.objects.filter(parcela__socio=socio).select_related('parcela')
        serializer = CultivoSerializer(cultivos, many=True)
        return Response(serializer.data)


class ParcelaViewSet(viewsets.ModelViewSet):
    queryset = Parcela.objects.select_related('socio__usuario')
    serializer_class = ParcelaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by current user's parcels if not admin
        user = self.request.user
        if not user.is_staff:
            try:
                socio = Socio.objects.get(usuario=user)
                queryset = queryset.filter(socio=socio)
            except Socio.DoesNotExist:
                queryset = queryset.none()
        return queryset

    def perform_create(self, serializer):
        # Validate superficie
        superficie = serializer.validated_data.get('superficie_hectareas')
        if superficie <= 0:
            raise serializers.ValidationError('La superficie debe ser mayor a 0')
        serializer.save()


class CultivoViewSet(viewsets.ModelViewSet):
    queryset = Cultivo.objects.select_related('parcela__socio__usuario')
    serializer_class = CultivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by current user's crops if not admin
        user = self.request.user
        if not user.is_staff:
            try:
                socio = Socio.objects.get(usuario=user)
                queryset = queryset.filter(parcela__socio=socio)
            except Socio.DoesNotExist:
                queryset = queryset.none()
        return queryset


class BitacoraAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BitacoraAuditoria.objects.select_related('usuario')
    serializer_class = BitacoraAuditoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        # Filter by current user if not admin
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(usuario=user)
        return queryset


# CU3: Gestión de Socios - Endpoints adicionales
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_socio_completo(request):
    """
    CU3: Crear socio completo con usuario
    T012: Gestión de usuarios y roles
    T014: CRUD de socios con validaciones
    T021: Validación de datos en formularios
    T027: Validación de duplicados
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = SocioCreateSerializer(data=request.data)
    if serializer.is_valid():
        socio = serializer.save()

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='CREAR',
            tabla_afectada='socio',
            registro_id=socio.id,
            detalles={
                'usuario_creado': socio.usuario.usuario,
                'creado_por': request.user.usuario
            },
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
        )

        # Serializar respuesta completa
        response_serializer = SocioSerializer(socio)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activar_desactivar_socio(request, socio_id):
    """
    CU3: Activar o desactivar socio
    T012: Gestión de usuarios (inhabilitar/reactivar)
    T014: CRUD de socios con validaciones
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        socio = Socio.objects.select_related('usuario').get(id=socio_id)
    except Socio.DoesNotExist:
        return Response(
            {'error': 'Socio no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    accion = request.data.get('accion')  # 'activar' o 'desactivar'

    if accion not in ['activar', 'desactivar']:
        return Response(
            {'error': 'Acción inválida. Use "activar" o "desactivar"'},
            status=status.HTTP_400_BAD_REQUEST
        )

    nuevo_estado = 'ACTIVO' if accion == 'activar' else 'INACTIVO'
    socio.estado = nuevo_estado
    socio.save()

    # Actualizar estado del usuario también
    socio.usuario.estado = nuevo_estado
    socio.usuario.save()

    # Registrar en bitácora
    BitacoraAuditoria.objects.create(
        usuario=request.user,
        accion='ACTIVAR_SOCIO' if accion == 'activar' else 'DESACTIVAR_SOCIO',
        tabla_afectada='socio',
        registro_id=socio.id,
        detalles={
            'nuevo_estado': nuevo_estado,
            'usuario_afectado': socio.usuario.usuario,
            'modificado_por': request.user.usuario
        },
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
    )

    serializer = SocioSerializer(socio)
    return Response({
        'mensaje': f'Socio {"activado" if accion == "activar" else "desactivado"} exitosamente',
        'socio': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def activar_desactivar_usuario(request, usuario_id):
    """
    CU3: Activar o desactivar usuario
    T012: Gestión de usuarios (inhabilitar/reactivar)
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    accion = request.data.get('accion')  # 'activar' o 'desactivar'

    if accion not in ['activar', 'desactivar']:
        return Response(
            {'error': 'Acción inválida. Use "activar" o "desactivar"'},
            status=status.HTTP_400_BAD_REQUEST
        )

    nuevo_estado = 'ACTIVO' if accion == 'activar' else 'INACTIVO'
    usuario.estado = nuevo_estado
    usuario.save()

    # Si el usuario es socio, actualizar también el estado del socio
    try:
        socio = Socio.objects.get(usuario=usuario)
        socio.estado = nuevo_estado
        socio.save()
    except Socio.DoesNotExist:
        pass

    # Registrar en bitácora
    BitacoraAuditoria.objects.create(
        usuario=request.user,
        accion='ACTIVAR_USUARIO' if accion == 'activar' else 'DESACTIVAR_USUARIO',
        tabla_afectada='usuario',
        registro_id=usuario.id,
        detalles={
            'nuevo_estado': nuevo_estado,
            'usuario_afectado': usuario.usuario,
            'modificado_por': request.user.usuario
        },
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
    )

    serializer = UsuarioSerializer(usuario)
    return Response({
        'mensaje': f'Usuario {"activado" if accion == "activar" else "desactivado"} exitosamente',
        'usuario': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def buscar_socios_avanzado(request):
    """
    CU3: Búsqueda avanzada de socios
    T016: Búsquedas y filtros de socios
    T029: Búsqueda avanzada de socios
    """
    # Verificar autenticación manualmente para devolver 401 en lugar de 403
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticación requerida'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    queryset = Socio.objects.select_related('usuario', 'comunidad')

    # Filtros de búsqueda
    nombre = request.query_params.get('nombre', '').strip()
    apellido = request.query_params.get('apellido', '').strip()
    ci_nit = request.query_params.get('ci_nit', '').strip()
    comunidad_id = request.query_params.get('comunidad', '').strip()
    estado = request.query_params.get('estado', '').strip()
    codigo_interno = request.query_params.get('codigo_interno', '').strip()
    sexo = request.query_params.get('sexo', '').strip()

    # Aplicar filtros
    if nombre:
        queryset = queryset.filter(usuario__nombres__icontains=nombre)
    if apellido:
        queryset = queryset.filter(usuario__apellidos__icontains=apellido)
    if ci_nit:
        queryset = queryset.filter(usuario__ci_nit__icontains=ci_nit)
    if comunidad_id:
        queryset = queryset.filter(comunidad_id=comunidad_id)
    if estado:
        queryset = queryset.filter(estado=estado)
    if codigo_interno:
        queryset = queryset.filter(codigo_interno__icontains=codigo_interno)
    if sexo:
        queryset = queryset.filter(sexo=sexo)

    # Paginación básica
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    socios = queryset[start:end]

    serializer = SocioSerializer(socios, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def buscar_socios_por_cultivo(request):
    """
    CU3: Búsqueda de socios por cultivo
    T016: Búsquedas y filtros de socios (Comunidad/cultivo)
    """
    # Verificar autenticación manualmente para devolver 401 en lugar de 403
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticación requerida'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    cultivo_especie = request.query_params.get('especie', '').strip()
    cultivo_estado = request.query_params.get('estado', '').strip()

    if not cultivo_especie:
        return Response(
            {'error': 'Debe especificar la especie del cultivo'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Buscar socios que tienen parcelas con cultivos de la especie especificada
    socios_ids = Cultivo.objects.filter(
        especie__icontains=cultivo_especie
    ).select_related('parcela__socio').values_list('parcela__socio', flat=True).distinct()

    if cultivo_estado:
        socios_ids = Cultivo.objects.filter(
            especie__icontains=cultivo_especie,
            estado=cultivo_estado
        ).select_related('parcela__socio').values_list('parcela__socio', flat=True).distinct()

    queryset = Socio.objects.filter(id__in=socios_ids).select_related('usuario', 'comunidad')

    # Paginación
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    socios = queryset[start:end]

    serializer = SocioSerializer(socios, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'filtros': {
            'especie_cultivo': cultivo_especie,
            'estado_cultivo': cultivo_estado
        },
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def reporte_usuarios_socios(request):
    """
    CU3: Reporte inicial de usuarios activos/inactivos y socios registrados
    T031: Reporte inicial de usuarios activos/inactivos y socios registrados
    """
    # Verificar autenticación manualmente para devolver 401 en lugar de 403
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Autenticación requerida'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Estadísticas de usuarios
    usuarios_total = Usuario.objects.count()
    usuarios_activos = Usuario.objects.filter(estado='ACTIVO').count()
    usuarios_inactivos = Usuario.objects.filter(estado='INACTIVO').count()
    usuarios_bloqueados = Usuario.objects.filter(estado='BLOQUEADO').count()

    # Estadísticas de socios
    socios_total = Socio.objects.count()
    socios_activos = Socio.objects.filter(estado='ACTIVO').count()
    socios_inactivos = Socio.objects.filter(estado='INACTIVO').count()

    # Socios por comunidad
    socios_por_comunidad = Comunidad.objects.annotate(
        num_socios=Count('socio')
    ).values('nombre', 'num_socios').order_by('-num_socios')

    # Usuarios por rol
    usuarios_por_rol = Rol.objects.annotate(
        num_usuarios=Count('usuariorol')
    ).values('nombre', 'num_usuarios').order_by('-num_usuarios')

    # Socios registrados por mes (últimos 12 meses)
    socios_por_mes = Socio.objects.annotate(
        mes=TruncMonth('creado_en')
    ).values('mes').annotate(
        count=Count('id')
    ).order_by('mes')[:12]

    return Response({
        'resumen_general': {
            'usuarios_total': usuarios_total,
            'usuarios_activos': usuarios_activos,
            'usuarios_inactivos': usuarios_inactivos,
            'usuarios_bloqueados': usuarios_bloqueados,
            'socios_total': socios_total,
            'socios_activos': socios_activos,
            'socios_inactivos': socios_inactivos
        },
        'socios_por_comunidad': list(socios_por_comunidad),
        'usuarios_por_rol': list(usuarios_por_rol),
        'socios_por_mes': list(socios_por_mes),
        'porcentajes': {
            'usuarios_activos_pct': round((usuarios_activos / usuarios_total * 100), 2) if usuarios_total > 0 else 0,
            'socios_activos_pct': round((socios_activos / socios_total * 100), 2) if socios_total > 0 else 0
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validar_datos_socio(request):
    """
    CU3: Validar datos de socio antes de crear/editar
    T021: Validación de datos en formularios
    T027: Validación de duplicados
    """
    ci_nit = request.query_params.get('ci_nit', '').strip()
    email = request.query_params.get('email', '').strip()
    usuario = request.query_params.get('usuario', '').strip()
    codigo_interno = request.query_params.get('codigo_interno', '').strip()

    errores = {}

    # Validar CI/NIT
    if ci_nit:
        if Usuario.objects.filter(ci_nit=ci_nit).exists():
            errores['ci_nit'] = 'Ya existe un usuario con este CI/NIT'

    # Validar email
    if email:
        if Usuario.objects.filter(email__iexact=email).exists():
            errores['email'] = 'Ya existe un usuario con este email'

    # Validar usuario
    if usuario:
        if Usuario.objects.filter(usuario__iexact=usuario).exists():
            errores['usuario'] = 'Ya existe un usuario con este nombre de usuario'

    # Validar código interno
    if codigo_interno:
        if Socio.objects.filter(codigo_interno__iexact=codigo_interno).exists():
            errores['codigo_interno'] = 'Ya existe un socio con este código interno'

    if errores:
        return Response({
            'valido': False,
            'errores': errores
        }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'valido': True,
            'mensaje': 'Todos los datos son válidos'
        })


# CU4: Gestión Avanzada de Parcelas y Cultivos
# ============================================

class CicloCultivoViewSet(viewsets.ModelViewSet):
    """
    CU4: Gestión de Ciclos de Cultivo
    T041: Gestión de ciclos de cultivo
    """
    queryset = CicloCultivo.objects.all().select_related('cultivo__parcela')
    serializer_class = CicloCultivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        parcela_id = self.request.query_params.get('parcela_id')
        cultivo_id = self.request.query_params.get('cultivo_id')
        estado = self.request.query_params.get('estado')
        fecha_inicio_desde = self.request.query_params.get('fecha_inicio_desde')
        fecha_inicio_hasta = self.request.query_params.get('fecha_inicio_hasta')

        if parcela_id:
            queryset = queryset.filter(cultivo__parcela_id=parcela_id)
        if cultivo_id:
            queryset = queryset.filter(cultivo_id=cultivo_id)
        if estado:
            queryset = queryset.filter(estado=estado)
        if fecha_inicio_desde:
            queryset = queryset.filter(fecha_inicio__gte=fecha_inicio_desde)
        if fecha_inicio_hasta:
            queryset = queryset.filter(fecha_inicio__lte=fecha_inicio_hasta)

        return queryset.order_by('-fecha_inicio')

    def perform_create(self, serializer):
        # Registrar en bitácora
        ciclo = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_CICLO_CULTIVO',
            tabla_afectada='CicloCultivo',
            registro_id=ciclo.id,
            detalles=f'Ciclo de cultivo creado para parcela {ciclo.cultivo.parcela.nombre}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        # Registrar en bitácora
        ciclo = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_CICLO_CULTIVO',
            tabla_afectada='CicloCultivo',
            registro_id=ciclo.id,
            detalles=f'Ciclo de cultivo actualizado para parcela {ciclo.cultivo.parcela.nombre}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class CosechaViewSet(viewsets.ModelViewSet):
    """
    CU4: Gestión de Cosechas
    T042: Gestión de cosechas
    """
    queryset = Cosecha.objects.all().select_related('ciclo_cultivo__cultivo__parcela', 'ciclo_cultivo__cultivo')
    serializer_class = CosechaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        ciclo_cultivo_id = self.request.query_params.get('ciclo_cultivo_id')
        parcela_id = self.request.query_params.get('parcela_id')
        fecha_cosecha_desde = self.request.query_params.get('fecha_cosecha_desde')
        fecha_cosecha_hasta = self.request.query_params.get('fecha_cosecha_hasta')
        estado = self.request.query_params.get('estado')

        if ciclo_cultivo_id:
            queryset = queryset.filter(ciclo_cultivo_id=ciclo_cultivo_id)
        if parcela_id:
            queryset = queryset.filter(ciclo_cultivo__parcela_id=parcela_id)
        if fecha_cosecha_desde:
            queryset = queryset.filter(fecha_cosecha__gte=fecha_cosecha_desde)
        if fecha_cosecha_hasta:
            queryset = queryset.filter(fecha_cosecha__lte=fecha_cosecha_hasta)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset.order_by('-fecha_cosecha')

    def perform_create(self, serializer):
        # Registrar en bitácora
        cosecha = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_COSECHA',
            tabla_afectada='Cosecha',
            registro_id=cosecha.id,
            detalles=f'Cosecha registrada para ciclo {cosecha.ciclo_cultivo.id}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        # Registrar en bitácora
        cosecha = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_COSECHA',
            tabla_afectada='Cosecha',
            registro_id=cosecha.id,
            detalles=f'Cosecha actualizada para ciclo {cosecha.ciclo_cultivo.id}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class TratamientoViewSet(viewsets.ModelViewSet):
    """
    CU4: Gestión de Tratamientos
    T043: Gestión de tratamientos
    """
    queryset = Tratamiento.objects.all().select_related('ciclo_cultivo__cultivo__parcela', 'ciclo_cultivo__cultivo')
    serializer_class = TratamientoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        ciclo_cultivo_id = self.request.query_params.get('ciclo_cultivo_id')
        parcela_id = self.request.query_params.get('parcela_id')
        tipo_tratamiento = self.request.query_params.get('tipo_tratamiento')
        fecha_aplicacion_desde = self.request.query_params.get('fecha_aplicacion_desde')
        fecha_aplicacion_hasta = self.request.query_params.get('fecha_aplicacion_hasta')

        if ciclo_cultivo_id:
            queryset = queryset.filter(ciclo_cultivo_id=ciclo_cultivo_id)
        if parcela_id:
            queryset = queryset.filter(ciclo_cultivo__parcela_id=parcela_id)
        if tipo_tratamiento:
            queryset = queryset.filter(tipo_tratamiento=tipo_tratamiento)
        if fecha_aplicacion_desde:
            queryset = queryset.filter(fecha_aplicacion__gte=fecha_aplicacion_desde)
        if fecha_aplicacion_hasta:
            queryset = queryset.filter(fecha_aplicacion__lte=fecha_aplicacion_hasta)

        return queryset.order_by('-fecha_aplicacion')

    def perform_create(self, serializer):
        # Registrar en bitácora
        tratamiento = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_TRATAMIENTO',
            tabla_afectada='Tratamiento',
            registro_id=tratamiento.id,
            detalles=f'Tratamiento aplicado a ciclo {tratamiento.ciclo_cultivo.id}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        # Registrar en bitácora
        tratamiento = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_TRATAMIENTO',
            tabla_afectada='Tratamiento',
            registro_id=tratamiento.id,
            detalles=f'Tratamiento actualizado para ciclo {tratamiento.ciclo_cultivo.id}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class AnalisisSueloViewSet(viewsets.ModelViewSet):
    """
    CU4: Gestión de Análisis de Suelo
    T044: Gestión de análisis de suelo
    """
    queryset = AnalisisSuelo.objects.all().select_related('parcela')
    serializer_class = AnalisisSueloSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        parcela_id = self.request.query_params.get('parcela_id')
        fecha_analisis_desde = self.request.query_params.get('fecha_analisis_desde')
        fecha_analisis_hasta = self.request.query_params.get('fecha_analisis_hasta')
        tipo_analisis = self.request.query_params.get('tipo_analisis')

        if parcela_id:
            queryset = queryset.filter(parcela_id=parcela_id)
        if fecha_analisis_desde:
            queryset = queryset.filter(fecha_analisis__gte=fecha_analisis_desde)
        if fecha_analisis_hasta:
            queryset = queryset.filter(fecha_analisis__lte=fecha_analisis_hasta)
        if tipo_analisis:
            queryset = queryset.filter(tipo_analisis=tipo_analisis)

        return queryset.order_by('-fecha_analisis')

    def perform_create(self, serializer):
        # Registrar en bitácora
        analisis = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_ANALISIS_SUELO',
            tabla_afectada='AnalisisSuelo',
            registro_id=analisis.id,
            detalles=f'Análisis de suelo realizado para parcela {analisis.parcela.nombre}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        # Registrar en bitácora
        analisis = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_ANALISIS_SUELO',
            tabla_afectada='AnalisisSuelo',
            registro_id=analisis.id,
            detalles=f'Análisis de suelo actualizado para parcela {analisis.parcela.nombre}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


class TransferenciaParcelaViewSet(viewsets.ModelViewSet):
    """
    CU4: Gestión de Transferencias de Parcelas
    T045: Gestión de transferencias de parcelas
    """
    queryset = TransferenciaParcela.objects.all().select_related(
        'parcela', 'socio_anterior__usuario', 'socio_nuevo__usuario', 'autorizado_por'
    )
    serializer_class = TransferenciaParcelaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        parcela_id = self.request.query_params.get('parcela_id')
        socio_anterior_id = self.request.query_params.get('socio_anterior_id')
        socio_nuevo_id = self.request.query_params.get('socio_nuevo_id')
        fecha_transferencia_desde = self.request.query_params.get('fecha_transferencia_desde')
        fecha_transferencia_hasta = self.request.query_params.get('fecha_transferencia_hasta')
        estado = self.request.query_params.get('estado')

        if parcela_id:
            queryset = queryset.filter(parcela_id=parcela_id)
        if socio_anterior_id:
            queryset = queryset.filter(socio_anterior_id=socio_anterior_id)
        if socio_nuevo_id:
            queryset = queryset.filter(socio_nuevo_id=socio_nuevo_id)
        if fecha_transferencia_desde:
            queryset = queryset.filter(fecha_transferencia__gte=fecha_transferencia_desde)
        if fecha_transferencia_hasta:
            queryset = queryset.filter(fecha_transferencia__lte=fecha_transferencia_hasta)
        if estado:
            queryset = queryset.filter(estado=estado)

        return queryset.order_by('-fecha_transferencia')

    def perform_create(self, serializer):
        # Registrar en bitácora
        transferencia = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='CREAR_TRANSFERENCIA_PARCELA',
            tabla_afectada='TransferenciaParcela',
            registro_id=transferencia.id,
            detalles=f'Transferencia de parcela {transferencia.parcela.nombre} de socio {transferencia.socio_anterior.usuario.ci_nit} a socio {transferencia.socio_nuevo.usuario.ci_nit}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )

    def perform_update(self, serializer):
        # Registrar en bitácora
        transferencia = serializer.save()
        BitacoraAuditoria.objects.create(
            usuario=self.request.user,
            accion='ACTUALIZAR_TRANSFERENCIA_PARCELA',
            tabla_afectada='TransferenciaParcela',
            registro_id=transferencia.id,
            detalles=f'Transferencia actualizada para parcela {transferencia.parcela.nombre}',
            ip_address=get_client_ip(self.request),
            user_agent=self.request.META.get('HTTP_USER_AGENT', '')
        )


# Endpoints específicos para CU4
# ==============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_ciclos_cultivo_avanzado(request):
    """
    CU4: Búsqueda avanzada de ciclos de cultivo
    T041: Gestión de ciclos de cultivo - Búsqueda avanzada
    """
    especie = request.query_params.get('especie', '').strip()
    estado_ciclo = request.query_params.get('estado_ciclo', '').strip()
    comunidad_id = request.query_params.get('comunidad_id')
    fecha_inicio_desde = request.query_params.get('fecha_inicio_desde')
    fecha_inicio_hasta = request.query_params.get('fecha_inicio_hasta')

    queryset = CicloCultivo.objects.select_related(
        'cultivo__parcela__socio__comunidad', 'cultivo'
    ).filter(cultivo__parcela__socio__estado='ACTIVO')

    if especie:
        queryset = queryset.filter(cultivo__especie__icontains=especie)
    if estado_ciclo:
        queryset = queryset.filter(estado=estado_ciclo)
    if comunidad_id:
        queryset = queryset.filter(cultivo__parcela__socio__comunidad_id=comunidad_id)
    if fecha_inicio_desde:
        queryset = queryset.filter(fecha_inicio__gte=fecha_inicio_desde)
    if fecha_inicio_hasta:
        queryset = queryset.filter(fecha_inicio__lte=fecha_inicio_hasta)

    # Paginación
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    ciclos = queryset[start:end]

    serializer = CicloCultivoSerializer(ciclos, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'filtros': {
            'especie': especie,
            'estado_ciclo': estado_ciclo,
            'comunidad_id': comunidad_id,
            'fecha_inicio_desde': fecha_inicio_desde,
            'fecha_inicio_hasta': fecha_inicio_hasta
        },
        'results': serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_productividad_parcelas(request):
    """
    CU4: Reporte de productividad de parcelas
    T046: Reportes de productividad
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Estadísticas generales de cosechas
    cosechas_total = Cosecha.objects.count()
    cosechas_completadas = Cosecha.objects.filter(estado='COMPLETADA').count()
    cosechas_pendientes = Cosecha.objects.filter(estado='PENDIENTE').count()

    # Productividad por especie
    productividad_por_especie = Cultivo.objects.annotate(
        total_cosechado=Sum('ciclocultivo__cosecha__cantidad_cosechada'),
        num_ciclos=Count('ciclocultivo', distinct=True),
        num_cosechas=Count('ciclocultivo__cosecha', distinct=True)
    ).values('especie', 'total_cosechado', 'num_ciclos', 'num_cosechas').order_by('-total_cosechado')

    # Rendimiento promedio por parcela
    rendimiento_parcelas = Parcela.objects.annotate(
        total_cosechado=Sum('cultivo__ciclocultivo__cosecha__cantidad_cosechada'),
        superficie_total=F('superficie_hectareas')
    ).filter(total_cosechado__isnull=False).values(
        'nombre', 'superficie_total', 'total_cosechado'
    ).annotate(
        rendimiento_promedio=Case(
            When(superficie_total__gt=0, then=F('total_cosechado') / F('superficie_total')),
            default=0,
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
    ).order_by('-rendimiento_promedio')[:20]

    # Tratamientos aplicados por mes
    tratamientos_por_mes = Tratamiento.objects.annotate(
        mes=TruncMonth('fecha_aplicacion')
    ).values('mes', 'tipo_tratamiento').annotate(
        count=Count('id')
    ).order_by('mes', 'tipo_tratamiento')[:24]

    # Análisis de suelo por tipo
    analisis_por_tipo = AnalisisSuelo.objects.values('tipo_analisis').annotate(
        count=Count('id'),
        promedio_ph=Avg('ph'),
        promedio_materia_organica=Avg('materia_organica')
    ).order_by('-count')

    return Response({
        'estadisticas_generales': {
            'cosechas_total': cosechas_total,
            'cosechas_completadas': cosechas_completadas,
            'cosechas_pendientes': cosechas_pendientes,
            'porcentaje_completadas': round((cosechas_completadas / cosechas_total * 100), 2) if cosechas_total > 0 else 0
        },
        'productividad_por_especie': list(productividad_por_especie),
        'rendimiento_parcelas_top20': list(rendimiento_parcelas),
        'tratamientos_por_mes': list(tratamientos_por_mes),
        'analisis_suelo_por_tipo': list(analisis_por_tipo)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_tipos_suelo(request):
    """
    CU4: Obtener tipos de suelo disponibles
    """
    tipos_suelo = [
        'ARCILLOSO',
        'ARENAL',
        'LIMOSO',
        'FRANCO',
        'FRANCO-ARCILLOSO',
        'FRANCO-ARENAL',
        'FRANCO-LIMOSO',
        'ARCILLO-LIMOSO',
        'ARENAL-LIMOSO',
        'TURBA',
        'CALCAREO',
        'SALINO',
        'PEDREGOSO'
    ]

    return Response({
        'tipos_suelo': tipos_suelo
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validar_transferencia_parcela(request):
    """
    CU4: Validar transferencia de parcela
    T045: Validación de transferencias de parcelas
    """
    parcela_id = request.query_params.get('parcela_id')
    socio_nuevo_id = request.query_params.get('socio_nuevo_id')

    if not parcela_id or not socio_nuevo_id:
        return Response(
            {'error': 'Debe especificar parcela_id y socio_nuevo_id'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        parcela = Parcela.objects.get(id=parcela_id)
        socio_nuevo = Socio.objects.get(id=socio_nuevo_id)
    except (Parcela.DoesNotExist, Socio.DoesNotExist):
        return Response(
            {'error': 'Parcela o socio no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    errores = []

    # Validar que el socio nuevo esté activo
    if socio_nuevo.estado != 'ACTIVO':
        errores.append('El socio nuevo debe estar activo')

    # Validar que la parcela esté activa
    if parcela.estado != 'ACTIVA':
        errores.append('La parcela debe estar activa')

    # Validar que no haya transferencias pendientes para esta parcela
    transferencias_pendientes = TransferenciaParcela.objects.filter(
        parcela=parcela,
        estado='PENDIENTE'
    ).exists()

    if transferencias_pendientes:
        errores.append('Ya existe una transferencia pendiente para esta parcela')

    # Validar que el socio nuevo no sea el mismo que el actual
    if parcela.socio_id == socio_nuevo.id:
        errores.append('El socio nuevo debe ser diferente al socio actual')

    if errores:
        return Response({
            'valido': False,
            'errores': errores
        }, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({
            'valido': True,
            'mensaje': 'La transferencia puede proceder',
            'detalles': {
                'parcela': parcela.nombre,
                'socio_actual': f"{parcela.socio.usuario.ci_nit} - {parcela.socio.usuario.nombres} {parcela.socio.usuario.apellidos}",
                'socio_nuevo': f"{socio_nuevo.usuario.ci_nit} - {socio_nuevo.usuario.nombres} {socio_nuevo.usuario.apellidos}"
            }
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def procesar_transferencia_parcela(request, transferencia_id):
    """
    CU4: Procesar transferencia de parcela (aprobar/rechazar)
    T045: Gestión de transferencias de parcelas
    """
    try:
        transferencia = TransferenciaParcela.objects.get(id=transferencia_id)
    except TransferenciaParcela.DoesNotExist:
        return Response(
            {'error': 'Transferencia no encontrada'},
            status=status.HTTP_404_NOT_FOUND
        )

    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    accion = request.data.get('accion')
    observaciones = request.data.get('observaciones', '')

    if accion not in ['APROBAR', 'RECHAZAR']:
        return Response(
            {'error': 'Acción debe ser APROBAR o RECHAZAR'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if accion == 'APROBAR':
        # Actualizar la parcela con el nuevo socio
        transferencia.parcela.socio = transferencia.socio_nuevo
        transferencia.parcela.save()

        transferencia.estado = 'APROBADA'
        transferencia.fecha_aprobacion = timezone.now()
        transferencia.aprobado_por = request.user
    else:
        transferencia.estado = 'RECHAZADA'

    transferencia.observaciones = observaciones
    transferencia.save()

    # Registrar en bitácora
    BitacoraAuditoria.objects.create(
        usuario=request.user,
        accion='PROCESAR_TRANSFERENCIA_APROBAR' if accion == 'APROBAR' else 'PROCESAR_TRANSFERENCIA_RECHAZAR',
        tabla_afectada='TransferenciaParcela',
        registro_id=transferencia.id,
        detalles=f'Transferencia {transferencia.id} procesada: {accion}',
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )

    return Response({
        'mensaje': f'Transferencia {accion.lower()} exitosamente',
        'transferencia': TransferenciaParcelaSerializer(transferencia).data
    })


# CU6: Gestión de Roles y Permisos - Endpoints adicionales
# ========================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def asignar_rol_usuario(request):
    """
    CU6: Asignar rol a usuario
    T012: Gestión de usuarios y roles
    T022: Gestión de permisos
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    usuario_id = request.data.get('usuario_id')
    rol_id = request.data.get('rol_id')

    if not usuario_id or not rol_id:
        return Response(
            {'error': 'usuario_id y rol_id son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Rol.DoesNotExist:
        return Response(
            {'error': 'Rol no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verificar si ya tiene este rol
    if UsuarioRol.objects.filter(usuario=usuario, rol=rol).exists():
        return Response(
            {'error': 'El usuario ya tiene asignado este rol'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Crear asignación
    usuario_rol = UsuarioRol.objects.create(usuario=usuario, rol=rol)

    # Registrar en bitácora
    BitacoraAuditoria.objects.create(
        usuario=request.user,
        accion='CREAR',
        tabla_afectada='usuario_rol',
        registro_id=usuario_rol.id,
        detalles={
            'rol_asignado': rol.nombre,
            'usuario_afectado': usuario.usuario,
            'asignado_por': request.user.usuario
        },
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
    )

    serializer = UsuarioRolSerializer(usuario_rol)
    return Response({
        'mensaje': 'Rol asignado exitosamente',
        'usuario_rol': serializer.data
    }, status=status.HTTP_201_CREATED)
    """
    Debug endpoint para asignar rol a usuario
    """
    print("=" * 80)
    print("DEBUG ASIGNAR ROL - REQUEST RECEIVED")
    print("=" * 80)
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"User: {request.user}")
    print(f"User ID: {request.user.id if request.user.is_authenticated else 'N/A'}")
    print(f"Username: {request.user.usuario if request.user.is_authenticated else 'N/A'}")
    print(f"Is staff: {request.user.is_staff if request.user.is_authenticated else 'N/A'}")
    print(f"Is superuser: {request.user.is_superuser if request.user.is_authenticated else 'N/A'}")
    print(f"Request data: {request.data}")
    print(f"Content-Type: {request.content_type}")
    print(f"Method: {request.method}")

    # Check if user is authenticated
    if not request.user.is_authenticated:
        print("ERROR: User not authenticated")
        return Response(
            {'error': 'Usuario no autenticado'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Check if user is staff
    if not request.user.is_staff:
        print("ERROR: User is not staff")
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    usuario_id = request.data.get('usuario_id')
    rol_id = request.data.get('rol_id')

    print(f"usuario_id: {usuario_id} (type: {type(usuario_id)})")
    print(f"rol_id: {rol_id} (type: {type(rol_id)})")

    if not usuario_id or not rol_id:
        print("ERROR: Missing usuario_id or rol_id")
        return Response(
            {'error': 'usuario_id y rol_id son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        print(f"Usuario found: {usuario.usuario}")
    except Usuario.DoesNotExist:
        print(f"ERROR: Usuario with ID {usuario_id} not found")
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"ERROR getting usuario: {e}")
        return Response(
            {'error': f'Error al buscar usuario: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        rol = Rol.objects.get(id=rol_id)
        print(f"Rol found: {rol.nombre}")
    except Rol.DoesNotExist:
        print(f"ERROR: Rol with ID {rol_id} not found")
        return Response(
            {'error': 'Rol no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        print(f"ERROR getting rol: {e}")
        return Response(
            {'error': f'Error al buscar rol: {str(e)}'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verificar si ya tiene este rol
    if UsuarioRol.objects.filter(usuario=usuario, rol=rol).exists():
        print("ERROR: Usuario already has this rol")
        return Response(
            {'error': 'El usuario ya tiene asignado este rol'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Crear asignación
        usuario_rol = UsuarioRol.objects.create(usuario=usuario, rol=rol)
        print(f"SUCCESS: Rol asignado - UsuarioRol ID: {usuario_rol.id}")

        # Registrar en bitácora
        BitacoraAuditoria.objects.create(
            usuario=request.user,
            accion='CREAR',
            tabla_afectada='usuario_rol',
            registro_id=usuario_rol.id,
            detalles={
                'rol_asignado': rol.nombre,
                'usuario_afectado': usuario.usuario,
                'asignado_por': request.user.usuario
            },
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
        )

        serializer = UsuarioRolSerializer(usuario_rol)
        return Response({
            'mensaje': 'Rol asignado exitosamente',
            'usuario_rol': serializer.data
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        print(f"ERROR creating UsuarioRol: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Error al asignar rol: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def quitar_rol_usuario(request):
    """
    CU6: Quitar rol a usuario
    T012: Gestión de usuarios y roles
    T022: Gestión de permisos
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    usuario_id = request.data.get('usuario_id')
    rol_id = request.data.get('rol_id')

    if not usuario_id or not rol_id:
        return Response(
            {'error': 'usuario_id y rol_id son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(id=usuario_id)
        rol = Rol.objects.get(id=rol_id)
        usuario_rol = UsuarioRol.objects.get(usuario=usuario, rol=rol)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Rol.DoesNotExist:
        return Response(
            {'error': 'Rol no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )
    except UsuarioRol.DoesNotExist:
        return Response(
            {'error': 'El usuario no tiene asignado este rol'},
            status=status.HTTP_404_NOT_FOUND
        )

    # No permitir quitar roles del sistema si es el último rol del usuario
    if rol.es_sistema:
        otros_roles_usuario = UsuarioRol.objects.filter(
            usuario=usuario
        ).exclude(id=usuario_rol.id).count()

        if otros_roles_usuario == 0:
            return Response(
                {'error': 'No se puede quitar el último rol del usuario'},
                status=status.HTTP_400_BAD_REQUEST
            )

    usuario_rol_id = usuario_rol.id
    usuario_rol.delete()

    # Registrar en bitácora
    BitacoraAuditoria.objects.create(
        usuario=request.user,
        accion='ELIMINAR',
        tabla_afectada='usuario_rol',
        registro_id=usuario_rol_id,
        detalles={
            'rol_removido': rol.nombre,
            'usuario_afectado': usuario.usuario,
            'removido_por': request.user.usuario
        },
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
    )

    return Response({'mensaje': 'Rol removido exitosamente'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def permisos_usuario(request, usuario_id):
    """
    CU6: Obtener permisos consolidados de un usuario
    T022: Gestión de permisos
    T034: Validación de permisos
    """
    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verificar permisos (solo admin o el propio usuario)
    if not request.user.is_staff and request.user.id != usuario_id:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    roles_usuario = UsuarioRol.objects.filter(usuario=usuario).select_related('rol')

    # Consolidar permisos de todos los roles del usuario
    permisos_consolidados = {}
    modulos = [
        'usuarios', 'socios', 'parcelas', 'cultivos',
        'ciclos_cultivo', 'cosechas', 'tratamientos',
        'analisis_suelo', 'transferencias', 'reportes',
        'auditoria', 'configuracion'
    ]

    for modulo in modulos:
        permisos_modulo = {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False}

        # Si el usuario es admin, tiene todos los permisos
        if usuario.is_staff or usuario.is_superuser:
            permisos_modulo = {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True}
        else:
            # Consolidar permisos de todos los roles
            for usuario_rol in roles_usuario:
                rol_permisos = usuario_rol.rol.permisos
                if modulo in rol_permisos:
                    for accion, permitido in rol_permisos[modulo].items():
                        if permitido:
                            permisos_modulo[accion] = True

        permisos_consolidados[modulo] = permisos_modulo

    return Response({
        'usuario_id': usuario.id,
        'usuario': usuario.usuario,
        'nombre_completo': usuario.get_full_name(),
        'roles': [ur.rol.nombre for ur in roles_usuario],
        'permisos': permisos_consolidados
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def validar_permiso_usuario(request):
    """
    CU6: Validar si un usuario tiene un permiso específico
    T022: Gestión de permisos
    T034: Validación de permisos
    """
    usuario_id = request.query_params.get('usuario_id')
    modulo = request.query_params.get('modulo')
    accion = request.query_params.get('accion')

    if not usuario_id or not modulo or not accion:
        return Response(
            {'error': 'usuario_id, modulo y accion son requeridos'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        usuario = Usuario.objects.get(id=usuario_id)
    except Usuario.DoesNotExist:
        return Response(
            {'error': 'Usuario no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verificar permisos (solo admin o el propio usuario)
    if not request.user.is_staff and request.user.id != int(usuario_id):
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Verificar si el usuario tiene el permiso
    tiene_permiso = False

    if usuario.is_staff or usuario.is_superuser:
        tiene_permiso = True
    else:
        roles_usuario = UsuarioRol.objects.filter(usuario=usuario).select_related('rol')
        for usuario_rol in roles_usuario:
            if usuario_rol.rol.tiene_permiso(modulo, accion):
                tiene_permiso = True
                break

    return Response({
        'usuario_id': usuario.id,
        'usuario': usuario.usuario,
        'modulo': modulo,
        'accion': accion,
        'tiene_permiso': tiene_permiso
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reporte_roles_permisos(request):
    """
    CU6: Reporte de roles y permisos
    T012: Gestión de usuarios y roles
    T022: Gestión de permisos
    T034: Validación de permisos
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Estadísticas de roles
    total_roles = Rol.objects.count()
    roles_sistema = Rol.objects.filter(es_sistema=True).count()
    roles_personalizados = Rol.objects.filter(es_sistema=False).count()

    # Usuarios por rol
    usuarios_por_rol = Rol.objects.annotate(
        num_usuarios=Count('usuariorol')
    ).values('id', 'nombre', 'es_sistema', 'num_usuarios').order_by('-num_usuarios')

    # Roles más utilizados
    roles_mas_utilizados = list(usuarios_por_rol[:10])

    # Permisos más comunes
    permisos_comunes = {}
    modulos = [
        'usuarios', 'socios', 'parcelas', 'cultivos',
        'ciclos_cultivo', 'cosechas', 'tratamientos',
        'analisis_suelo', 'transferencias', 'reportes',
        'auditoria', 'configuracion'
    ]

    for modulo in modulos:
        permisos_modulo = {'ver': 0, 'crear': 0, 'editar': 0, 'eliminar': 0, 'aprobar': 0}
        roles_con_modulo = Rol.objects.filter(permisos__has_key=modulo)

        for rol in roles_con_modulo:
            if modulo in rol.permisos:
                for accion, permitido in rol.permisos[modulo].items():
                    if permitido:
                        permisos_modulo[accion] += 1

        permisos_comunes[modulo] = permisos_modulo

    # Usuarios sin roles asignados
    usuarios_sin_roles = Usuario.objects.exclude(
        id__in=UsuarioRol.objects.values_list('usuario_id', flat=True)
    ).count()

    return Response({
        'estadisticas_generales': {
            'total_roles': total_roles,
            'roles_sistema': roles_sistema,
            'roles_personalizados': roles_personalizados,
            'usuarios_sin_roles': usuarios_sin_roles
        },
        'usuarios_por_rol': list(usuarios_por_rol),
        'roles_mas_utilizados': roles_mas_utilizados,
        'permisos_comunes': permisos_comunes
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_rol_personalizado(request):
    """
    CU6: Crear rol personalizado con permisos específicos
    T012: Gestión de usuarios y roles
    T022: Gestión de permisos
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    nombre = request.data.get('nombre')
    descripcion = request.data.get('descripcion', '')
    permisos = request.data.get('permisos', {})

    if not nombre:
        return Response(
            {'error': 'El nombre del rol es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verificar que el nombre no exista
    if Rol.objects.filter(nombre__iexact=nombre).exists():
        return Response(
            {'error': 'Ya existe un rol con este nombre'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Crear rol personalizado
    rol = Rol.objects.create(
        nombre=nombre,
        descripcion=descripcion,
        permisos=permisos,
        es_sistema=False
    )

    # Registrar en bitácora
    BitacoraAuditoria.objects.create(
        usuario=request.user,
        accion='CREAR',
        tabla_afectada='rol',
        registro_id=rol.id,
        detalles={
            'tipo_rol': 'personalizado',
            'creado_por': request.user.usuario
        },
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
    )

    serializer = RolSerializer(rol)
    return Response({
        'mensaje': 'Rol personalizado creado exitosamente',
        'rol': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_roles_avanzado(request):
    """
    CU6: Búsqueda avanzada de roles
    T012: Gestión de usuarios y roles
    """
    nombre = request.query_params.get('nombre', '').strip()
    es_sistema = request.query_params.get('es_sistema')
    modulo_permiso = request.query_params.get('modulo_permiso')
    accion_permiso = request.query_params.get('accion_permiso')

    queryset = Rol.objects.all()

    if nombre:
        queryset = queryset.filter(nombre__icontains=nombre)

    if es_sistema is not None:
        es_sistema_bool = es_sistema.lower() == 'true'
        queryset = queryset.filter(es_sistema=es_sistema_bool)

    if modulo_permiso and accion_permiso:
        # Filtrar roles que tienen un permiso específico
        queryset = queryset.filter(
            permisos__has_key=modulo_permiso
        ).filter(
            **{f'permisos__{modulo_permiso}__{accion_permiso}': True}
        )

    # Paginación
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    roles = queryset[start:end]

    serializer = RolSerializer(roles, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'filtros': {
            'nombre': nombre,
            'es_sistema': es_sistema,
            'modulo_permiso': modulo_permiso,
            'accion_permiso': accion_permiso
        },
        'results': serializer.data
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
@csrf_exempt
def debug_update_socio(request, socio_id):
    """
    Debug endpoint to check permissions and session for socio update
    """
    print("=" * 80)
    print("DEBUG UPDATE SOCIO - REQUEST RECEIVED")
    print("=" * 80)
    print(f"Socio ID: {socio_id}")
    print(f"Method: {request.method}")
    print(f"User authenticated: {request.user.is_authenticated}")
    print(f"User: {request.user}")
    print(f"User ID: {request.user.id if request.user.is_authenticated else 'N/A'}")
    print(f"Username: {request.user.usuario if request.user.is_authenticated else 'N/A'}")
    print(f"Is staff: {request.user.is_staff if request.user.is_authenticated else 'N/A'}")
    print(f"Is superuser: {request.user.is_superuser if request.user.is_authenticated else 'N/A'}")
    print(f"Session key: {request.session.session_key}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Content-Type: {request.content_type}")

    # Check if user is authenticated
    if not request.user.is_authenticated:
        print("ERROR: User not authenticated")
        return Response(
            {'error': 'Usuario no autenticado'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Check if user is staff
    if not request.user.is_staff:
        print("ERROR: User is not staff")
        return Response(
            {'error': 'Permisos insuficientes - no es staff'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Check if socio exists
    try:
        socio = Socio.objects.select_related('usuario').get(id=socio_id)
        print(f"Socio found: {socio.usuario.ci_nit} - {socio.usuario.nombres} {socio.usuario.apellidos}")
    except Socio.DoesNotExist:
        print(f"ERROR: Socio with ID {socio_id} not found")
        return Response(
            {'error': 'Socio no encontrado'},
            status=status.HTTP_404_NOT_FOUND
        )

    # Check CSRF token
    csrf_token = request.META.get('HTTP_X_CSRFTOKEN', 'Not found')
    print(f"CSRF token from header: {csrf_token}")

    # Check session data
    session_data = request.session._session_cache if hasattr(request.session, '_session_cache') else 'No cache'
    print(f"Session data: {session_data}")

    # Try to update the socio (similar to the real update)
    try:
        if request.content_type == 'application/json':
            data = request.data
            print(f"Request data: {data}")

            # Update socio fields
            socio_fields = ['telefono', 'direccion', 'fecha_nacimiento', 'sexo', 'estado_civil', 'fecha_ingreso', 'estado']
            for field in socio_fields:
                if field in data:
                    setattr(socio, field, data[field])

            # Update usuario fields if provided
            if 'usuario' in data:
                usuario_data = data['usuario']
                usuario_fields = ['usuario', 'nombres', 'apellidos', 'ci_nit', 'email', 'telefono', 'estado']
                for field in usuario_fields:
                    if field in usuario_data:
                        setattr(socio.usuario, field, usuario_data[field])

            socio.save()
            socio.usuario.save()

            print("SUCCESS: Socio updated successfully")
            serializer = SocioSerializer(socio)
            return Response(serializer.data)

        else:
            print("ERROR: Content type is not JSON")
            return Response(
                {'error': 'Content type debe ser application/json'},
                status=status.HTTP_400_BAD_REQUEST
            )

    except Exception as e:
        print(f"ERROR during update: {e}")
        import traceback
        traceback.print_exc()
        return Response(
            {'error': f'Error interno: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_session_status(request):
    """
    Debug endpoint for detailed session information
    """
    user = request.user
    session_key = request.session.session_key

    # Get all active sessions for debugging
    user_sessions = []
    total_sessions = 0

    for session in Session.objects.all():
        session_data = session.get_decoded()
        if session_data.get('_auth_user_id') == str(user.id):
            total_sessions += 1
            user_sessions.append({
                'session_key': session.session_key,
                'expire_date': session.expire_date,
                'is_current': session.session_key == session_key
            })

    return Response({
        'debug_info': {
            'timestamp': timezone.now(),
            'request_method': request.method,
            'request_path': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT'),
            'remote_addr': request.META.get('REMOTE_ADDR'),
            'is_secure': request.is_secure(),
            'session_engine': request.session.__class__.__name__,
        },
        'session_info': {
            'session_key': session_key,
            'session_expiry': request.session.get_expiry_date(),
            'session_age': (timezone.now() - request.session.get('created_at', timezone.now())).total_seconds() if request.session.get('created_at') else None,
            'total_user_sessions': total_sessions,
            'user_sessions': user_sessions[:5]  # Limit to first 5 for brevity
        },
        'user_info': {
            'id': user.id,
            'username': user.usuario,
            'email': user.email,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'is_active': user.is_active,
            'last_login': user.last_login,
            'date_joined': user.date_joined
        },
        'authentication_status': {
            'is_authenticated': True,
            'backend': getattr(user, 'backend', None),
            'auth_time': getattr(request.session, '_auth_user_time', None)
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def buscar_parcelas_avanzado(request):
    """
    CU4: Búsqueda avanzada de parcelas
    T016: Búsquedas y filtros de parcelas
    """
    queryset = Parcela.objects.select_related('socio__usuario')

    # Filtros de búsqueda
    nombre = request.query_params.get('nombre', '').strip()
    socio_id = request.query_params.get('socio_id', '').strip()
    socio_nombre = request.query_params.get('socio_nombre', '').strip()
    tipo_suelo = request.query_params.get('tipo_suelo', '').strip()
    estado = request.query_params.get('estado', '').strip()
    ubicacion = request.query_params.get('ubicacion', '').strip()
    superficie_min = request.query_params.get('superficie_min', '').strip()
    superficie_max = request.query_params.get('superficie_max', '').strip()
    fecha_desde = request.query_params.get('fecha_desde', '').strip()
    fecha_hasta = request.query_params.get('fecha_hasta', '').strip()

    # Aplicar filtros
    if nombre:
        queryset = queryset.filter(nombre__icontains=nombre)
    if socio_id:
        queryset = queryset.filter(socio_id=socio_id)
    if socio_nombre:
        queryset = queryset.filter(
            Q(socio__usuario__nombres__icontains=socio_nombre) |
            Q(socio__usuario__apellidos__icontains=socio_nombre)
        )
    if tipo_suelo:
        queryset = queryset.filter(tipo_suelo__icontains=tipo_suelo)
    if estado:
        queryset = queryset.filter(estado=estado)
    if ubicacion:
        queryset = queryset.filter(ubicacion__icontains=ubicacion)
    if superficie_min:
        try:
            superficie_min_val = float(superficie_min)
            queryset = queryset.filter(superficie_hectareas__gte=superficie_min_val)
        except ValueError:
            pass
    if superficie_max:
        try:
            superficie_max_val = float(superficie_max)
            queryset = queryset.filter(superficie_hectareas__lte=superficie_max_val)
        except ValueError:
            pass
    if fecha_desde:
        queryset = queryset.filter(creado_en__gte=fecha_desde)
    if fecha_hasta:
        queryset = queryset.filter(creado_en__lte=fecha_hasta)

    # Paginación básica
    page = int(request.query_params.get('page', 1))
    page_size = int(request.query_params.get('page_size', 20))
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    parcelas = queryset[start:end]

    serializer = ParcelaSerializer(parcelas, many=True)

    return Response({
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'results': serializer.data
    })
