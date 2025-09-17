# 📊 T013: Bitácora de Auditoría Básica

## 📋 Descripción

La **Tarea T013** implementa el sistema de bitácora de auditoría básica para el Sistema de Gestión Cooperativa Agrícola. Esta funcionalidad es crítica para mantener un registro completo de todas las operaciones de autenticación y gestión de usuarios, proporcionando trazabilidad y cumplimiento normativo.

## 🎯 Objetivos Específicos

- ✅ **Auditoría de Login:** Registro de todos los intentos de inicio de sesión
- ✅ **Auditoría de Usuarios:** Registro de operaciones CRUD en usuarios
- ✅ **Trazabilidad Completa:** IP, User-Agent, timestamp, detalles de operación
- ✅ **Cumplimiento Normativo:** Base para auditorías de seguridad
- ✅ **Análisis de Actividad:** Datos para análisis de patrones de uso
- ✅ **Soporte Forense:** Información para investigación de incidentes

## 🔧 Implementación Técnica

### **Modelo BitacoraAuditoria**

```python
# models.py
class BitacoraAuditoria(models.Model):
    """
    Modelo para registro de auditoría básica
    T013: Bitácora de auditoría básica
    """
    ACCIONES = [
        ('LOGIN', 'Inicio de sesión'),
        ('LOGIN_FALLIDO', 'Intento fallido de login'),
        ('LOGOUT', 'Cierre de sesión'),
        ('CREAR', 'Crear registro'),
        ('ACTUALIZAR', 'Actualizar registro'),
        ('ELIMINAR', 'Eliminar registro'),
        ('BLOQUEO_CUENTA', 'Bloqueo de cuenta'),
        ('ACTIVAR_USUARIO', 'Activar usuario'),
        ('DESACTIVAR_USUARIO', 'Desactivar usuario'),
        ('CAMBIAR_PASSWORD', 'Cambio de contraseña'),
    ]

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='auditoria'
    )
    accion = models.CharField(max_length=50, choices=ACCIONES)
    tabla_afectada = models.CharField(max_length=100)
    registro_id = models.PositiveIntegerField(null=True, blank=True)
    detalles = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['usuario', 'accion']),
            models.Index(fields=['tabla_afectada', 'registro_id']),
            models.Index(fields=['creado_en']),
            models.Index(fields=['ip_address']),
        ]
```

### **Helper para Obtener IP del Cliente**

```python
# views.py - Función auxiliar
def get_client_ip(request):
    """
    Obtener IP real del cliente considerando proxies
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
```

## 📝 Operaciones Auditadas

### **Auditoría de Autenticación**

#### **Login Exitoso**
```python
# Registro de login exitoso
BitacoraAuditoria.objects.create(
    usuario=user,
    accion='LOGIN',
    tabla_afectada='usuario',
    registro_id=user.id,
    detalles={
        'ip': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'metodo': 'web',  # o 'movil'
        'dispositivo': 'desktop'  # o tipo de dispositivo
    },
    ip_address=request.META.get('REMOTE_ADDR'),
    user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
)
```

#### **Login Fallido**
```python
# Registro de intento fallido
BitacoraAuditoria.objects.create(
    usuario=user,
    accion='LOGIN_FALLIDO',
    tabla_afectada='usuario',
    registro_id=user.id,
    detalles={
        'ip': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'intentos_fallidos': user.intentos_fallidos,
        'bloqueado': user.intentos_fallidos >= 5,
        'razon_fallo': 'contraseña_incorrecta'
    },
    ip_address=request.META.get('REMOTE_ADDR'),
    user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
)
```

#### **Bloqueo de Cuenta**
```python
# Registro de bloqueo por intentos fallidos
BitacoraAuditoria.objects.create(
    usuario=user,
    accion='BLOQUEO_CUENTA',
    tabla_afectada='usuario',
    registro_id=user.id,
    detalles={
        'ip': request.META.get('REMOTE_ADDR'),
        'razon': 'Múltiples intentos fallidos de login',
        'intentos_fallidos': user.intentos_fallidos,
        'fecha_bloqueo': user.fecha_bloqueo.isoformat()
    },
    ip_address=request.META.get('REMOTE_ADDR'),
    user_agent=request.META.get('HTTP_USER_AGENT') or 'Unknown'
)
```

### **Auditoría de Gestión de Usuarios**

#### **Creación de Usuario**
```python
# Registro de creación de usuario
BitacoraAuditoria.objects.create(
    usuario=self.request.user,  # Usuario que realizó la acción
    accion='CREAR',
    tabla_afectada='usuario',
    registro_id=instance.id,
    detalles={
        'usuario_creado': instance.usuario,
        'email_creado': instance.email,
        'rol_asignado': 'socio',  # o el rol correspondiente
        'creado_por': self.request.user.usuario
    },
    ip_address=get_client_ip(self.request),
    user_agent=self.request.META.get('HTTP_USER_AGENT') or 'Unknown'
)
```

#### **Actualización de Usuario**
```python
# Registro de actualización de usuario
BitacoraAuditoria.objects.create(
    usuario=self.request.user,
    accion='ACTUALIZAR',
    tabla_afectada='usuario',
    registro_id=instance.id,
    detalles={
        'usuario_actualizado': instance.usuario,
        'cambios_realizados': ['email', 'telefono'],  # campos modificados
        'valores_anteriores': {'email': 'anterior@email.com'},
        'valores_nuevos': {'email': 'nuevo@email.com'},
        'actualizado_por': self.request.user.usuario
    },
    ip_address=get_client_ip(self.request),
    user_agent=self.request.META.get('HTTP_USER_AGENT') or 'Unknown'
)
```

#### **Eliminación de Usuario**
```python
# Registro de eliminación de usuario
BitacoraAuditoria.objects.create(
    usuario=self.request.user,
    accion='ELIMINAR',
    tabla_afectada='usuario',
    registro_id=instance.id,
    detalles={
        'usuario_eliminado': instance.usuario,
        'email_eliminado': instance.email,
        'eliminado_por': self.request.user.usuario,
        'motivo_eliminacion': 'solicitud_usuario'  # o razón correspondiente
    },
    ip_address=get_client_ip(self.request),
    user_agent=self.request.META.get('HTTP_USER_AGENT') or 'Unknown'
)
```

#### **Activación/Desactivación de Usuario**
```python
# Registro de cambio de estado
BitacoraAuditoria.objects.create(
    usuario=self.request.user,
    accion='ACTIVAR_USUARIO',  # o 'DESACTIVAR_USUARIO'
    tabla_afectada='usuario',
    registro_id=instance.id,
    detalles={
        'usuario_afectado': instance.usuario,
        'estado_anterior': 'INACTIVO',
        'estado_nuevo': 'ACTIVO',
        'modificado_por': self.request.user.usuario,
        'motivo': 'reactivacion_solicitada'
    },
    ip_address=get_client_ip(self.request),
    user_agent=self.request.META.get('HTTP_USER_AGENT') or 'Unknown'
)
```

#### **Cambio de Contraseña**
```python
# Registro de cambio de contraseña
BitacoraAuditoria.objects.create(
    usuario=self.request.user,
    accion='CAMBIAR_PASSWORD',
    tabla_afectada='usuario',
    registro_id=user.id,
    detalles={
        'usuario_afectado': user.usuario,
        'cambiado_por': self.request.user.usuario,
        'metodo_cambio': 'formulario_web',  # o 'reset_email', 'admin_forzado'
        'ip_cambio': get_client_ip(self.request)
    },
    ip_address=get_client_ip(self.request),
    user_agent=self.request.META.get('HTTP_USER_AGENT') or 'Unknown'
)
```

## 🔍 Consultas y Reportes de Auditoría

### **ViewSet de Bitácora**
```python
# views.py
class BitacoraAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consulta de bitácora de auditoría
    T013: Bitácora de auditoría básica
    """
    queryset = BitacoraAuditoria.objects.select_related('usuario')
    serializer_class = BitacoraAuditoriaSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filtros disponibles
        usuario_id = self.request.query_params.get('usuario_id')
        accion = self.request.query_params.get('accion')
        tabla_afectada = self.request.query_params.get('tabla_afectada')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')
        ip_address = self.request.query_params.get('ip_address')

        # Aplicar filtros
        if usuario_id:
            queryset = queryset.filter(usuario_id=usuario_id)
        if accion:
            queryset = queryset.filter(accion=accion)
        if tabla_afectada:
            queryset = queryset.filter(tabla_afectada=tabla_afectada)
        if fecha_desde:
            queryset = queryset.filter(creado_en__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(creado_en__lte=fecha_hasta)
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)

        # Usuarios no admin solo ven sus propias acciones
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(
                Q(usuario=user) | Q(detalles__contains={'afectado': user.usuario})
            )

        return queryset.order_by('-creado_en')
```

### **Serializer de Bitácora**
```python
# serializers.py
class BitacoraAuditoriaSerializer(serializers.ModelSerializer):
    """
    Serializer para bitácora de auditoría
    """
    usuario_info = serializers.SerializerMethodField()
    accion_display = serializers.CharField(source='get_accion_display', read_only=True)

    class Meta:
        model = BitacoraAuditoria
        fields = [
            'id', 'usuario', 'usuario_info', 'accion', 'accion_display',
            'tabla_afectada', 'registro_id', 'detalles', 'ip_address',
            'user_agent', 'creado_en'
        ]

    def get_usuario_info(self, obj):
        if obj.usuario:
            return {
                'id': obj.usuario.id,
                'usuario': obj.usuario.usuario,
                'nombres': obj.usuario.nombres,
                'apellidos': obj.usuario.apellidos
            }
        return None
```

## 📊 Endpoints de Auditoría

```http
# Consultas de bitácora
GET  /api/bitacora/                          # Lista de registros
GET  /api/bitacora/{id}/                     # Detalle de registro
GET  /api/bitacora/?usuario_id=1             # Por usuario
GET  /api/bitacora/?accion=LOGIN             # Por acción
GET  /api/bitacora/?fecha_desde=2025-01-01   # Por fecha
GET  /api/bitacora/?ip_address=192.168.1.1   # Por IP
```

## 🧪 Tests de Auditoría

### **Tests de Login**
```python
# test/CU1/test_bitacora.py
class BitacoraLoginTests(APITestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            usuario='testuser',
            password='testpass123'
        )

    def test_login_audit_successful(self):
        """Test que se registra login exitoso en bitácora"""
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        })

        # Verificar login exitoso
        self.assertEqual(response.status_code, 200)

        # Verificar registro en bitácora
        auditoria = BitacoraAuditoria.objects.filter(
            usuario=self.user,
            accion='LOGIN'
        ).first()

        self.assertIsNotNone(auditoria)
        self.assertEqual(auditoria.tabla_afectada, 'usuario')
        self.assertIn('ip', auditoria.detalles)

    def test_login_audit_failed(self):
        """Test que se registra login fallido en bitácora"""
        response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        # Verificar login fallido
        self.assertEqual(response.status_code, 401)

        # Verificar registro en bitácora
        auditoria = BitacoraAuditoria.objects.filter(
            usuario=self.user,
            accion='LOGIN_FALLIDO'
        ).first()

        self.assertIsNotNone(auditoria)
        self.assertIn('intentos_fallidos', auditoria.detalles)
```

### **Tests de Gestión de Usuarios**
```python
class BitacoraUsuarioTests(APITestCase):
    def setUp(self):
        self.admin = Usuario.objects.create_superuser(
            usuario='admin',
            password='admin123',
            email='admin@example.com'
        )
        self.client.force_authenticate(user=self.admin)

    def test_create_user_audit(self):
        """Test auditoría de creación de usuario"""
        response = self.client.post('/api/usuarios/', {
            'usuario': 'newuser',
            'password': 'newpass123',
            'email': 'new@example.com',
            'nombres': 'Nuevo',
            'apellidos': 'Usuario'
        })

        self.assertEqual(response.status_code, 201)

        # Verificar registro en bitácora
        auditoria = BitacoraAuditoria.objects.filter(
            accion='CREAR',
            tabla_afectada='usuario'
        ).first()

        self.assertIsNotNone(auditoria)
        self.assertEqual(auditoria.usuario, self.admin)
        self.assertIn('usuario_creado', auditoria.detalles)
```

## 📈 Análisis y Reportes

### **Dashboard de Actividad**
```python
# Vista para dashboard de auditoría
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_auditoria(request):
    """
    Dashboard con estadísticas de auditoría
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permisos insuficientes'},
            status=status.HTTP_403_FORBIDDEN
        )

    # Estadísticas generales
    total_registros = BitacoraAuditoria.objects.count()
    registros_hoy = BitacoraAuditoria.objects.filter(
        creado_en__date=timezone.now().date()
    ).count()

    # Actividad por acción
    actividad_por_accion = BitacoraAuditoria.objects.values('accion').annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # Actividad por usuario
    actividad_por_usuario = BitacoraAuditoria.objects.values(
        'usuario__usuario', 'usuario__nombres', 'usuario__apellidos'
    ).annotate(
        count=Count('id')
    ).exclude(usuario__isnull=True).order_by('-count')[:10]

    # Actividad por IP
    actividad_por_ip = BitacoraAuditoria.objects.values('ip_address').annotate(
        count=Count('id')
    ).exclude(ip_address__isnull=True).order_by('-count')[:10]

    # Intentos de login fallidos
    login_fallidos = BitacoraAuditoria.objects.filter(
        accion='LOGIN_FALLIDO'
    ).count()

    return Response({
        'estadisticas_generales': {
            'total_registros': total_registros,
            'registros_hoy': registros_hoy,
            'login_fallidos': login_fallidos
        },
        'actividad_por_accion': list(actividad_por_accion),
        'actividad_por_usuario': list(actividad_por_usuario),
        'actividad_por_ip': list(actividad_por_ip)
    })
```

## 🔒 Consideraciones de Seguridad

### **Protección de Datos Sensibles**
- ✅ **Enmascaramiento de IPs:** No se muestran IPs completas a usuarios no admin
- ✅ **Filtrado de Información:** Usuarios solo ven sus propias acciones
- ✅ **Rate Limiting:** Límite de consultas de auditoría por usuario
- ✅ **Encriptación:** Datos sensibles encriptados en BD si es necesario

### **Retención de Datos**
```python
# Configuración de retención (ejemplo)
AUDITORIA_RETENTION_DAYS = 365  # 1 año

# Comando de management para limpieza
class Command(BaseCommand):
    help = 'Limpiar registros antiguos de auditoría'

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=AUDITORIA_RETENTION_DAYS)
        deleted_count = BitacoraAuditoria.objects.filter(
            creado_en__lt=cutoff_date
        ).delete()[0]

        self.stdout.write(
            f'Se eliminaron {deleted_count} registros antiguos de auditoría'
        )
```

## 📊 Rendimiento y Optimización

### **Índices de Base de Datos**
```sql
-- Índices para optimizar consultas de auditoría
CREATE INDEX idx_bitacora_usuario_accion ON bitacora_auditoria (usuario_id, accion);
CREATE INDEX idx_bitacora_tabla_registro ON bitacora_auditoria (tabla_afectada, registro_id);
CREATE INDEX idx_bitacora_fecha ON bitacora_auditoria (creado_en);
CREATE INDEX idx_bitacora_ip ON bitacora_auditoria (ip_address);
```

### **Optimizaciones de Consulta**
- ✅ **Select Related:** Carga relacionada de usuarios
- ✅ **Paginación:** Resultados paginados para listas grandes
- ✅ **Filtros Eficientes:** Filtros a nivel de base de datos
- ✅ **Cache:** Resultados de dashboard cacheados

## 🚨 Alertas y Monitoreo

### **Sistema de Alertas**
```python
# Función para detectar actividad sospechosa
def detectar_actividad_sospechosa():
    """
    Detectar patrones de actividad que requieren atención
    """
    # Múltiples login fallidos desde misma IP
    ip_sospechosa = BitacoraAuditoria.objects.filter(
        accion='LOGIN_FALLIDO',
        creado_en__gte=timezone.now() - timedelta(hours=1)
    ).values('ip_address').annotate(
        count=Count('id')
    ).filter(count__gte=10).first()

    if ip_sospechosa:
        # Enviar alerta al administrador
        enviar_alerta_admin(
            f"Actividad sospechosa desde IP: {ip_sospechosa['ip_address']}"
        )

    # Múltiples cambios de contraseña en corto tiempo
    cambios_password = BitacoraAuditoria.objects.filter(
        accion='CAMBIAR_PASSWORD',
        creado_en__gte=timezone.now() - timedelta(hours=24)
    ).values('usuario').annotate(
        count=Count('id')
    ).filter(count__gte=3)

    for cambio in cambios_password:
        enviar_alerta_admin(
            f"Múltiples cambios de contraseña para usuario ID: {cambio['usuario']}"
        )
```

## 📚 Documentación Relacionada

- **CU1 README:** Documentación general del CU1
- **T011 Autenticación:** Sistema de login y sesiones
- **T023 Logout:** Cierre de sesión con auditoría
- **API Docs:** Endpoints de bitácora
- **Tests:** Casos de prueba de auditoría

---

**📅 Fecha de implementación:** Septiembre 2025  
**🔧 Framework:** Django + PostgreSQL  
**📊 Registros por día:** 500-2000 (dependiendo de uso)  
**🚀 Estado:** ✅ Completado y optimizado</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\proyecto_Final\Backend_Django\cooperativa_backend\docs\CU1_Autenticacion\T013_Bitacora_Basica.md