from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import MinValueValidator
from .models import (
    Rol, Usuario, UsuarioRol, Comunidad, Socio,
    Parcela, Cultivo, BitacoraAuditoria,
    CicloCultivo, Cosecha, Tratamiento, AnalisisSuelo, TransferenciaParcela
)


class RolSerializer(serializers.ModelSerializer):
    permisos_legibles = serializers.SerializerMethodField()
    usuarios_count = serializers.SerializerMethodField()

    class Meta:
        model = Rol
        fields = [
            'id', 'nombre', 'descripcion', 'permisos', 'permisos_legibles',
            'es_sistema', 'creado_en', 'actualizado_en', 'usuarios_count'
        ]
        read_only_fields = ['es_sistema'] if not hasattr(serializers, 'context') else []

    def get_permisos_legibles(self, obj):
        """Retorna los permisos en formato legible"""
        return obj.obtener_permisos_completos()

    def get_usuarios_count(self, obj):
        """Retorna el número de usuarios con este rol"""
        return UsuarioRol.objects.filter(rol=obj).count()

    def validate_permisos(self, value):
        """Validar estructura de permisos"""
        if not isinstance(value, dict):
            raise serializers.ValidationError('Los permisos deben ser un objeto JSON válido')

        # Validar que todos los módulos requeridos estén presentes
        modulos_requeridos = [
            'usuarios', 'socios', 'parcelas', 'cultivos',
            'ciclos_cultivo', 'cosechas', 'tratamientos',
            'analisis_suelo', 'transferencias', 'reportes',
            'auditoria', 'configuracion'
        ]

        for modulo in modulos_requeridos:
            if modulo not in value:
                value[modulo] = {
                    'ver': False,
                    'crear': False,
                    'editar': False,
                    'eliminar': False,
                    'aprobar': False
                }

        return value

    def validate(self, data):
        """Validaciones adicionales"""
        nombre = data.get('nombre')
        instance = self.instance

        # Validar nombre único
        if nombre and Rol.objects.filter(nombre__iexact=nombre).exclude(id=instance.id if instance else None).exists():
            raise serializers.ValidationError({'nombre': 'Ya existe un rol con este nombre'})

        # Validar que no se pueda modificar roles del sistema
        if instance and instance.es_sistema:
            # Solo permitir modificar descripción y permisos para roles del sistema
            campos_modificables = {'descripcion', 'permisos'}
            campos_en_data = set(data.keys())
            campos_invalidos = campos_en_data - campos_modificables
            if campos_invalidos:
                raise serializers.ValidationError({
                    field: f'No se puede modificar el campo {field} de un rol del sistema'
                    for field in campos_invalidos
                })

        return data


class UsuarioSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()
    edad = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'ci_nit', 'nombres', 'apellidos', 'email', 'telefono',
            'usuario', 'estado', 'intentos_fallidos', 'ultimo_intento',
            'fecha_bloqueo', 'creado_en', 'actualizado_en', 'roles',
            'nombre_completo', 'edad'
        ]
        extra_kwargs = {
            'contrasena_hash': {'write_only': True},
            'token_actual': {'write_only': True},
        }

    def get_roles(self, obj):
        roles = UsuarioRol.objects.filter(usuario=obj).select_related('rol')
        return [usuario_rol.rol.nombre for usuario_rol in roles]

    def get_nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellidos}"

    def get_edad(self, obj):
        # Calcular edad si hay fecha de nacimiento en socio relacionado
        try:
            socio = Socio.objects.get(usuario=obj)
            if socio.fecha_nacimiento:
                from datetime import date
                today = date.today()
                age = today.year - socio.fecha_nacimiento.year - (
                    (today.month, today.day) < (socio.fecha_nacimiento.month, socio.fecha_nacimiento.day)
                )
                return age
        except Socio.DoesNotExist:
            pass
        return None

    def validate_ci_nit(self, value):
        """T021, T027: Validación de CI/NIT único"""
        # Get the instance from the serializer context if not set on self.instance
        instance_id = None
        if self.instance:
            instance_id = self.instance.id
        elif self.parent and hasattr(self.parent, 'instance') and self.parent.instance:
            # For nested serializers, get instance from parent
            instance_id = getattr(self.parent.instance.usuario, 'id', None) if hasattr(self.parent.instance, 'usuario') else None

        queryset = Usuario.objects.filter(ci_nit=value)
        if instance_id:
            queryset = queryset.exclude(id=instance_id)

        if queryset.exists():
            raise serializers.ValidationError('Ya existe un usuario con este CI/NIT')
        return value

    def validate_email(self, value):
        """T021: Validación de email único"""
        if not value:
            return value

        # Get the instance from the serializer context if not set on self.instance
        instance_id = None
        if self.instance:
            instance_id = self.instance.id
        elif self.parent and hasattr(self.parent, 'instance') and self.parent.instance:
            # For nested serializers, get instance from parent
            instance_id = getattr(self.parent.instance.usuario, 'id', None) if hasattr(self.parent.instance, 'usuario') else None

        queryset = Usuario.objects.filter(email__iexact=value)
        if instance_id:
            queryset = queryset.exclude(id=instance_id)

        if queryset.exists():
            raise serializers.ValidationError('Ya existe un usuario con este email')
        return value

    def validate_usuario(self, value):
        """T021: Validación de usuario único"""
        # Get the instance from the serializer context if not set on self.instance
        instance_id = None
        if self.instance:
            instance_id = self.instance.id
        elif self.parent and hasattr(self.parent, 'instance') and self.parent.instance:
            # For nested serializers, get instance from parent
            instance_id = getattr(self.parent.instance.usuario, 'id', None) if hasattr(self.parent.instance, 'usuario') else None

        queryset = Usuario.objects.filter(usuario__iexact=value)
        if instance_id:
            queryset = queryset.exclude(id=instance_id)

        if queryset.exists():
            raise serializers.ValidationError('Ya existe un usuario con este nombre de usuario')
        return value


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    roles = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Usuario
        fields = [
            'id', 'ci_nit', 'nombres', 'apellidos', 'email', 'telefono',
            'usuario', 'password', 'confirm_password', 'roles'
        ]

    def validate(self, data):
        """T021: Validaciones generales del formulario"""
        # Validar contraseñas coincidan
        if data.get('password') != data.get('confirm_password'):
            raise serializers.ValidationError({'confirm_password': 'Las contraseñas no coinciden'})

        # Validar fortaleza de contraseña
        password = data.get('password', '')
        if not any(char.isdigit() for char in password):
            raise serializers.ValidationError({'password': 'La contraseña debe contener al menos un número'})
        if not any(char.isupper() for char in password):
            raise serializers.ValidationError({'password': 'La contraseña debe contener al menos una mayúscula'})

        return data

    def create(self, validated_data):
        roles_data = validated_data.pop('roles', [])
        validated_data.pop('confirm_password')  # Remover campo de confirmación
        password = validated_data.pop('password')

        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()

        # Assign roles
        for rol_nombre in roles_data:
            try:
                rol = Rol.objects.get(nombre=rol_nombre)
                UsuarioRol.objects.create(usuario=user, rol=rol)
            except Rol.DoesNotExist:
                pass  # Skip invalid roles

        return user


class UsuarioRolSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

    class Meta:
        model = UsuarioRol
        fields = ['id', 'usuario', 'rol', 'usuario_nombre', 'rol_nombre', 'creado_en']


class ComunidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunidad
        fields = '__all__'

    def validate_nombre(self, value):
        """T021: Validación de nombre único"""
        if Comunidad.objects.filter(nombre__iexact=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError('Ya existe una comunidad con este nombre')
        return value


class SocioSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    comunidad = ComunidadSerializer(read_only=True)
    edad = serializers.SerializerMethodField()

    class Meta:
        model = Socio
        fields = [
            'id', 'usuario', 'codigo_interno',
            'fecha_nacimiento', 'sexo', 'direccion', 'comunidad',
            'estado', 'creado_en', 'edad'
        ]

    def get_edad(self, obj):
        """Calcular edad del socio"""
        if obj.fecha_nacimiento:
            from datetime import date
            today = date.today()
            age = today.year - obj.fecha_nacimiento.year - (
                (today.month, today.day) < (obj.fecha_nacimiento.month, obj.fecha_nacimiento.day)
            )
            return age
        return None

    def validate_codigo_interno(self, value):
        """T027: Validación de código interno único"""
        if not value:
            return value

        # Get the instance from the serializer context if not set on self.instance
        instance_id = None
        if self.instance:
            instance_id = self.instance.id
        elif self.parent and hasattr(self.parent, 'instance') and self.parent.instance:
            # For nested serializers, get instance from parent
            instance_id = self.parent.instance.id if self.parent.instance else None

        queryset = Socio.objects.filter(codigo_interno__iexact=value)
        if instance_id:
            queryset = queryset.exclude(id=instance_id)

        if queryset.exists():
            raise serializers.ValidationError('Ya existe un socio con este código interno')
        return value

    def validate_usuario(self, value):
        """T027: Validación de usuario único para socio"""
        if Socio.objects.filter(usuario=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError('Este usuario ya está asociado a otro socio')
        return value


class SocioCreateSerializer(serializers.ModelSerializer):
    """Serializer específico para creación de socios con usuario incluido"""
    # Campos del usuario
    ci_nit = serializers.CharField(max_length=20, write_only=True)
    nombres = serializers.CharField(max_length=100, write_only=True)
    apellidos = serializers.CharField(max_length=100, write_only=True)
    email = serializers.EmailField(required=False, write_only=True)
    telefono = serializers.CharField(max_length=20, required=False, write_only=True)
    usuario_username = serializers.CharField(max_length=50, write_only=True)
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Socio
        fields = [
            'ci_nit', 'nombres', 'apellidos', 'email', 'telefono',
            'usuario_username', 'password', 'codigo_interno',
            'fecha_nacimiento', 'sexo', 'direccion', 'comunidad'
        ]

    def validate_ci_nit(self, value):
        """T027: Validación de CI/NIT único"""
        from .models import validate_ci_nit
        validate_ci_nit(value)
        if Usuario.objects.filter(ci_nit=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este CI/NIT')
        return value

    def validate_usuario_username(self, value):
        """T021: Validación de usuario único"""
        if Usuario.objects.filter(usuario__iexact=value).exists():
            raise serializers.ValidationError('Ya existe un usuario con este nombre de usuario')
        return value

    def create(self, validated_data):
        # Extraer datos del usuario
        user_data = {
            'ci_nit': validated_data.pop('ci_nit'),
            'nombres': validated_data.pop('nombres'),
            'apellidos': validated_data.pop('apellidos'),
            'email': validated_data.pop('email', None),
            'usuario': validated_data.pop('usuario_username'),
            'password': validated_data.pop('password'),
        }

        # Extraer teléfono por separado
        telefono = validated_data.pop('telefono', None)

        # Crear usuario
        user = Usuario.objects.create_user(**user_data)

        # Asignar teléfono si fue proporcionado
        if telefono:
            user.telefono = telefono
            user.save()

        # Crear socio
        socio = Socio.objects.create(usuario=user, **validated_data)

        return socio


class ParcelaSerializer(serializers.ModelSerializer):
    socio_nombre = serializers.CharField(source='socio.usuario.get_full_name', read_only=True)
    # Campos adicionales para compatibilidad con frontend
    superficie = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        write_only=True,
        required=False,
        validators=[MinValueValidator(0.01, message='La superficie debe ser mayor a 0')]
    )
    coordenadas = serializers.CharField(write_only=True, required=False)
    descripcion = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Parcela
        fields = [
            'id', 'socio', 'socio_nombre', 'nombre', 'superficie_hectareas',
            'tipo_suelo', 'ubicacion', 'latitud', 'longitud', 'estado', 'creado_en',
            # Campos adicionales para compatibilidad
            'superficie', 'coordenadas', 'descripcion'
        ]
        extra_kwargs = {
            'superficie_hectareas': {'required': False},
            'latitud': {'required': False},
            'longitud': {'required': False},
        }

    def validate_superficie(self, value):
        """T021: Validación de superficie"""
        if value <= 0:
            raise serializers.ValidationError('La superficie debe ser mayor a 0')
        if value > 10000:
            raise serializers.ValidationError('La superficie no puede exceder 10,000 hectáreas')
        return value

    def validate_coordenadas(self, value):
        """Validar formato de coordenadas"""
        if not value:
            return value

        try:
            # Esperar formato "latitud, longitud"
            parts = value.split(',')
            if len(parts) != 2:
                raise serializers.ValidationError('Formato de coordenadas inválido. Use: latitud,longitud')

            lat = float(parts[0].strip())
            lng = float(parts[1].strip())

            if lat < -90 or lat > 90:
                raise serializers.ValidationError('Latitud debe estar entre -90 y 90 grados')
            if lng < -180 or lng > 180:
                raise serializers.ValidationError('Longitud debe estar entre -180 y 180 grados')

            return value
        except (ValueError, IndexError):
            raise serializers.ValidationError('Formato de coordenadas inválido. Use números decimales separados por coma')

    def to_internal_value(self, data):
        """Convertir campos del frontend a campos del modelo"""
        # Convertir 'superficie' a 'superficie_hectareas'
        if 'superficie' in data and data['superficie'] is not None:
            data = data.copy()
            data['superficie_hectareas'] = data.pop('superficie')

        # Convertir 'coordenadas' a 'latitud' y 'longitud'
        if 'coordenadas' in data and data['coordenadas']:
            try:
                parts = data['coordenadas'].split(',')
                if len(parts) == 2:
                    data = data.copy()
                    data['latitud'] = float(parts[0].strip())
                    data['longitud'] = float(parts[1].strip())
            except (ValueError, AttributeError):
                pass

        # Convertir 'descripcion' a parte de 'ubicacion' o 'nombre'
        if 'descripcion' in data and data['descripcion']:
            if not data.get('ubicacion'):
                data = data.copy()
                data['ubicacion'] = data['descripcion']
            elif not data.get('nombre'):
                data = data.copy()
                data['nombre'] = data['descripcion'][:100]  # Limitar longitud

        # Convertir 'socio_id' a 'socio' si es necesario
        if 'socio_id' in data and data['socio_id']:
            try:
                from .models import Socio
                socio = Socio.objects.get(id=data['socio_id'])
                data = data.copy()
                data['socio'] = socio.id
                data.pop('socio_id')
            except (Socio.DoesNotExist, ValueError):
                pass

        # Remover campos que no existen en el modelo
        campos_invalidos = ['fecha_registro']
        for campo in campos_invalidos:
            if campo in data:
                data = data.copy()
                data.pop(campo)

        return super().to_internal_value(data)

    def to_representation(self, instance):
        """Convertir campos del modelo a formato del frontend"""
        data = super().to_representation(instance)

        # Agregar campo 'superficie' para compatibilidad
        if instance.superficie_hectareas:
            data['superficie'] = instance.superficie_hectareas

        # Agregar campo 'coordenadas' para compatibilidad
        if instance.latitud and instance.longitud:
            data['coordenadas'] = f"{instance.latitud}, {instance.longitud}"

        # Agregar campo 'descripcion' para compatibilidad
        data['descripcion'] = instance.ubicacion or instance.nombre or ''

        return data

    def validate(self, data):
        """T021: Validaciones de coordenadas"""
        latitud = data.get('latitud')
        longitud = data.get('longitud')

        if (latitud and not longitud) or (longitud and not latitud):
            raise serializers.ValidationError('Si se proporciona una coordenada, ambas latitud y longitud son requeridas')

        if latitud and (latitud < -90 or latitud > 90):
            raise serializers.ValidationError('Latitud debe estar entre -90 y 90 grados')

        if longitud and (longitud < -180 or longitud > 180):
            raise serializers.ValidationError('Longitud debe estar entre -180 y 180 grados')

        return data


class CultivoSerializer(serializers.ModelSerializer):
    parcela_nombre = serializers.CharField(source='parcela.nombre', read_only=True)
    socio_nombre = serializers.CharField(source='parcela.socio.usuario.get_full_name', read_only=True)

    class Meta:
        model = Cultivo
        fields = [
            'id', 'parcela', 'parcela_nombre', 'socio_nombre', 'especie',
            'variedad', 'tipo_semilla', 'fecha_estimada_siembra',
            'hectareas_sembradas', 'estado', 'creado_en'
        ]

    def validate_hectareas_sembradas(self, value):
        """T021: Validación de hectáreas sembradas"""
        if value and value <= 0:
            raise serializers.ValidationError('Las hectáreas sembradas deben ser mayor a 0')
        return value

    def validate_fecha_estimada_siembra(self, value):
        """T021: Validación de fecha de siembra"""
        if value:
            from datetime import date
            if value < date.today():
                raise serializers.ValidationError('La fecha estimada de siembra no puede ser en el pasado')
        return value

    def validate(self, data):
        """T021: Validaciones entre campos"""
        hectareas_sembradas = data.get('hectareas_sembradas')
        parcela = data.get('parcela') or (self.instance.parcela if self.instance else None)

        if hectareas_sembradas and parcela:
            if hectareas_sembradas > parcela.superficie_hectareas:
                raise serializers.ValidationError({
                    'hectareas_sembradas': 'Las hectáreas sembradas no pueden exceder la superficie de la parcela'
                })

        return data


class BitacoraAuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)

    class Meta:
        model = BitacoraAuditoria
        fields = [
            'id', 'usuario', 'usuario_nombre', 'accion', 'tabla_afectada',
            'registro_id', 'detalles', 'fecha', 'ip_address', 'user_agent'
        ]


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = '__all__'


class UsuarioSerializer(serializers.ModelSerializer):
    roles = serializers.SerializerMethodField()
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = Usuario
        fields = [
            'id', 'ci_nit', 'nombres', 'apellidos', 'email', 'telefono',
            'usuario', 'estado', 'is_staff', 'intentos_fallidos', 'ultimo_intento',
            'fecha_bloqueo', 'creado_en', 'actualizado_en', 'roles',
            'nombre_completo'
        ]
        extra_kwargs = {
            'contrasena_hash': {'write_only': True},
            'token_actual': {'write_only': True},
        }

    def get_roles(self, obj):
        roles = UsuarioRol.objects.filter(usuario=obj).select_related('rol')
        return [usuario_rol.rol.nombre for usuario_rol in roles]

    def get_nombre_completo(self, obj):
        return f"{obj.nombres} {obj.apellidos}"


class UsuarioCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    roles = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Usuario
        fields = [
            'id', 'ci_nit', 'nombres', 'apellidos', 'email', 'telefono',
            'usuario', 'password', 'roles'
        ]

    def create(self, validated_data):
        roles_data = validated_data.pop('roles', [])
        password = validated_data.pop('password')

        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()

        # Assign roles
        for rol_nombre in roles_data:
            try:
                rol = Rol.objects.get(nombre=rol_nombre)
                UsuarioRol.objects.create(usuario=user, rol=rol)
            except Rol.DoesNotExist:
                pass  # Skip invalid roles

        return user


class UsuarioRolSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre', read_only=True)

    class Meta:
        model = UsuarioRol
        fields = ['id', 'usuario', 'rol', 'usuario_nombre', 'rol_nombre', 'creado_en']


class ComunidadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comunidad
        fields = '__all__'


class SocioSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    comunidad = ComunidadSerializer(read_only=True)

    class Meta:
        model = Socio
        fields = [
            'id', 'usuario', 'codigo_interno',
            'fecha_nacimiento', 'sexo', 'direccion', 'comunidad',
            'estado', 'creado_en'
        ]


class SocioCreateSimpleSerializer(serializers.ModelSerializer):
    """Serializer específico para creación de socios con usuario y comunidad existentes"""
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all())
    comunidad = serializers.PrimaryKeyRelatedField(queryset=Comunidad.objects.all())

    class Meta:
        model = Socio
        fields = [
            'usuario', 'codigo_interno', 'fecha_nacimiento',
            'sexo', 'direccion', 'comunidad'
        ]

    def validate_usuario(self, value):
        """Validar que el usuario no tenga ya un socio"""
        if Socio.objects.filter(usuario=value).exists():
            raise serializers.ValidationError('Este usuario ya tiene un socio registrado')
        return value

    def validate_codigo_interno(self, value):
        """Validar código interno único"""
        if Socio.objects.filter(codigo_interno__iexact=value).exists():
            raise serializers.ValidationError('Ya existe un socio con este código interno')
        return value


class SocioUpdateSerializer(serializers.ModelSerializer):
    """Serializer específico para actualización de socios con usuario incluido"""
    usuario = UsuarioSerializer()

    class Meta:
        model = Socio
        fields = [
            'id', 'usuario', 'codigo_interno',
            'fecha_nacimiento', 'sexo', 'direccion', 'comunidad',
            'estado', 'creado_en'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the instance for the nested usuario serializer
        if self.instance and hasattr(self.instance, 'usuario'):
            usuario_serializer = self.fields['usuario']
            usuario_serializer.instance = self.instance.usuario

    def to_internal_value(self, data):
        """Handle nested usuario data properly"""
        usuario_data = data.get('usuario', {})
        if self.instance and hasattr(self.instance, 'usuario'):
            # Create a UsuarioSerializer with the correct instance
            usuario_serializer = UsuarioSerializer(instance=self.instance.usuario, data=usuario_data, partial=True)
            usuario_validated = usuario_serializer.to_internal_value(usuario_data)
            data = data.copy()
            data['usuario'] = usuario_validated
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        """Actualizar socio y usuario anidado"""
        usuario_data = validated_data.pop('usuario', {})

        # Actualizar campos del socio
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Actualizar campos del usuario
        if usuario_data:
            usuario = instance.usuario
            for attr, value in usuario_data.items():
                setattr(usuario, attr, value)
            usuario.save()

        return instance


class CicloCultivoSerializer(serializers.ModelSerializer):
    """CU4: Serializer para ciclos de cultivo"""
    cultivo_especie = serializers.CharField(source='cultivo.especie', read_only=True)
    cultivo_variedad = serializers.CharField(source='cultivo.variedad', read_only=True)
    parcela_nombre = serializers.CharField(source='cultivo.parcela.nombre', read_only=True)
    socio_nombre = serializers.CharField(source='cultivo.parcela.socio.usuario.get_full_name', read_only=True)
    dias_transcurridos = serializers.SerializerMethodField()
    progreso_estimado = serializers.SerializerMethodField()

    class Meta:
        model = CicloCultivo
        fields = [
            'id', 'cultivo', 'cultivo_especie', 'cultivo_variedad',
            'parcela_nombre', 'socio_nombre', 'fecha_inicio',
            'fecha_estimada_fin', 'fecha_fin_real', 'estado',
            'observaciones', 'costo_estimado', 'costo_real',
            'rendimiento_esperado', 'rendimiento_real', 'unidad_rendimiento',
            'dias_transcurridos', 'progreso_estimado', 'creado_en', 'actualizado_en'
        ]

    def get_dias_transcurridos(self, obj):
        return obj.dias_transcurridos()

    def get_progreso_estimado(self, obj):
        return round(obj.progreso_estimado(), 2)

    def validate(self, data):
        """Validaciones del ciclo de cultivo"""
        fecha_inicio = data.get('fecha_inicio')
        fecha_estimada_fin = data.get('fecha_estimada_fin')
        fecha_fin_real = data.get('fecha_fin_real')

        if fecha_estimada_fin and fecha_inicio and fecha_estimada_fin < fecha_inicio:
            raise serializers.ValidationError({
                'fecha_estimada_fin': 'La fecha estimada de fin no puede ser anterior a la fecha de inicio'
            })

        if fecha_fin_real and fecha_inicio and fecha_fin_real < fecha_inicio:
            raise serializers.ValidationError({
                'fecha_fin_real': 'La fecha de fin real no puede ser anterior a la fecha de inicio'
            })

        return data


class CosechaSerializer(serializers.ModelSerializer):
    """CU4: Serializer para cosechas"""
    ciclo_info = CicloCultivoSerializer(source='ciclo_cultivo', read_only=True)
    valor_total = serializers.SerializerMethodField()

    class Meta:
        model = Cosecha
        fields = [
            'id', 'ciclo_cultivo', 'ciclo_info', 'fecha_cosecha',
            'cantidad_cosechada', 'unidad_medida', 'calidad', 'estado',
            'precio_venta', 'valor_total', 'observaciones', 'creado_en'
        ]

    def get_valor_total(self, obj):
        return obj.valor_total()

    def validate(self, data):
        """Validaciones de cosecha"""
        fecha_cosecha = data.get('fecha_cosecha')
        ciclo_cultivo = data.get('ciclo_cultivo') or (self.instance.ciclo_cultivo if self.instance else None)

        if fecha_cosecha and ciclo_cultivo and fecha_cosecha < ciclo_cultivo.fecha_inicio:
            raise serializers.ValidationError({
                'fecha_cosecha': 'La fecha de cosecha no puede ser anterior al inicio del ciclo'
            })

        return data


class TratamientoSerializer(serializers.ModelSerializer):
    """CU4: Serializer para tratamientos"""
    ciclo_info = CicloCultivoSerializer(source='ciclo_cultivo', read_only=True)

    class Meta:
        model = Tratamiento
        fields = [
            'id', 'ciclo_cultivo', 'ciclo_info', 'tipo_tratamiento',
            'nombre_producto', 'dosis', 'unidad_dosis', 'fecha_aplicacion',
            'costo', 'observaciones', 'aplicado_por', 'creado_en'
        ]

    def validate(self, data):
        """Validaciones de tratamiento"""
        fecha_aplicacion = data.get('fecha_aplicacion')
        ciclo_cultivo = data.get('ciclo_cultivo') or (self.instance.ciclo_cultivo if self.instance else None)

        if fecha_aplicacion and ciclo_cultivo:
            if fecha_aplicacion < ciclo_cultivo.fecha_inicio:
                raise serializers.ValidationError({
                    'fecha_aplicacion': 'La fecha de aplicación no puede ser anterior al inicio del ciclo'
                })

            if ciclo_cultivo.fecha_fin_real and fecha_aplicacion > ciclo_cultivo.fecha_fin_real:
                raise serializers.ValidationError({
                    'fecha_aplicacion': 'La fecha de aplicación no puede ser posterior al fin del ciclo'
                })

        return data


class AnalisisSueloSerializer(serializers.ModelSerializer):
    """CU4: Serializer para análisis de suelo"""
    parcela_info = ParcelaSerializer(source='parcela', read_only=True)
    recomendaciones_basicas = serializers.SerializerMethodField()

    class Meta:
        model = AnalisisSuelo
        fields = [
            'id', 'parcela', 'parcela_info', 'fecha_analisis', 'tipo_analisis', 'ph',
            'materia_organica', 'nitrogeno', 'fosforo', 'potasio',
            'laboratorio', 'recomendaciones', 'recomendaciones_basicas',
            'costo_analisis', 'creado_en'
        ]

    def get_recomendaciones_basicas(self, obj):
        return obj.get_recomendaciones_basicas()

    def validate_ph(self, value):
        """Validación específica del pH"""
        if value is not None and not (4 <= value <= 10):
            raise serializers.ValidationError('El pH del suelo debe estar entre 4 y 10 para ser óptimo para cultivos')
        return value


class TransferenciaParcelaSerializer(serializers.ModelSerializer):
    """CU4: Serializer para transferencias de parcelas"""
    parcela_info = ParcelaSerializer(source='parcela', read_only=True)
    socio_anterior_info = SocioSerializer(source='socio_anterior', read_only=True)
    socio_nuevo_info = SocioSerializer(source='socio_nuevo', read_only=True)
    autorizado_por_info = UsuarioSerializer(source='autorizado_por', read_only=True)

    class Meta:
        model = TransferenciaParcela
        fields = [
            'id', 'parcela', 'parcela_info', 'socio_anterior',
            'socio_anterior_info', 'socio_nuevo', 'socio_nuevo_info',
            'fecha_transferencia', 'motivo', 'documento_legal',
            'costo_transferencia', 'estado', 'autorizado_por', 'autorizado_por_info',
            'fecha_aprobacion', 'observaciones', 'creado_en'
        ]

    def validate(self, data):
        """Validaciones de transferencia"""
        socio_anterior = data.get('socio_anterior')
        socio_nuevo = data.get('socio_nuevo')
        parcela = data.get('parcela') or (self.instance.parcela if self.instance else None)

        if socio_anterior and socio_nuevo and socio_anterior == socio_nuevo:
            raise serializers.ValidationError('El socio anterior y nuevo no pueden ser el mismo')

        if parcela and socio_anterior and parcela.socio != socio_anterior:
            raise serializers.ValidationError('El socio anterior no es el propietario actual de la parcela')

        return data


class CultivoSerializer(serializers.ModelSerializer):
    parcela_nombre = serializers.CharField(source='parcela.nombre', read_only=True)
    socio_nombre = serializers.CharField(source='parcela.socio.usuario.get_full_name', read_only=True)

    class Meta:
        model = Cultivo
        fields = [
            'id', 'parcela', 'parcela_nombre', 'socio_nombre', 'especie',
            'variedad', 'tipo_semilla', 'fecha_estimada_siembra',
            'hectareas_sembradas', 'estado', 'creado_en'
        ]


class BitacoraAuditoriaSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)

    class Meta:
        model = BitacoraAuditoria
        fields = [
            'id', 'usuario', 'usuario_nombre', 'accion', 'tabla_afectada',
            'registro_id', 'detalles', 'fecha', 'ip_address', 'user_agent'
        ]