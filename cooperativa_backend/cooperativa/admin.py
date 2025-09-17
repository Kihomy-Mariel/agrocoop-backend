from django.contrib import admin
from django import forms
from django.utils import timezone
from .models import Usuario, Rol, Comunidad, Socio, Parcela, Cultivo, BitacoraAuditoria, UsuarioRol

# Register your models here.

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'descripcion', 'es_sistema', 'creado_en')
    list_filter = ('es_sistema', 'creado_en')
    search_fields = ('nombre', 'descripcion')
    readonly_fields = ('creado_en', 'actualizado_en')

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.es_sistema:
            # Si es un rol del sistema, hacer todos los campos readonly excepto permisos
            return ['nombre', 'descripcion', 'es_sistema', 'creado_en', 'actualizado_en']
        return self.readonly_fields

@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'rol', 'creado_en')
    list_filter = ('rol', 'creado_en')
    search_fields = ('usuario__usuario', 'usuario__nombres', 'usuario__apellidos', 'rol__nombre')
    raw_id_fields = ('usuario', 'rol')
    readonly_fields = ('creado_en',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario', 'rol')


class UsuarioRolInline(admin.TabularInline):
    model = UsuarioRol
    extra = 0
    readonly_fields = ('creado_en',)
    fields = ('rol', 'creado_en')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('rol')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "rol":
            # Mostrar solo roles del sistema ordenados por nombre
            kwargs["queryset"] = Rol.objects.filter(es_sistema=True).order_by('nombre')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Validar que no se asignen roles duplicados
        def clean(self):
            super(formset, self).clean()
            if hasattr(self, 'cleaned_data'):
                roles = []
                for form in self:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        rol = form.cleaned_data.get('rol')
                        if rol in roles:
                            raise forms.ValidationError("No se puede asignar el mismo rol múltiples veces.")
                        roles.append(rol)
        formset.clean = clean
        return formset


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'nombres', 'apellidos', 'email', 'is_staff', 'is_superuser', 'estado', 'get_roles', 'creado_en')
    list_filter = ('estado', 'is_staff', 'is_superuser', 'creado_en')
    search_fields = ('usuario', 'nombres', 'apellidos', 'email', 'ci_nit')
    readonly_fields = ('creado_en', 'actualizado_en', 'ultimo_intento', 'fecha_bloqueo', 'date_joined')
    list_editable = ('is_staff', 'is_superuser', 'estado')
    inlines = [UsuarioRolInline]
    actions = ['asignar_rol_administrador', 'asignar_rol_socio', 'asignar_rol_operador', 'quitar_todos_roles']

    fieldsets = (
        ('Información Personal', {
            'fields': ('ci_nit', 'nombres', 'apellidos', 'email', 'telefono')
        }),
        ('Información de Usuario', {
            'fields': ('usuario', 'estado', 'is_staff', 'is_superuser')
        }),
        ('Fechas', {
            'fields': ('creado_en', 'actualizado_en', 'date_joined'),
            'classes': ('collapse',)
        }),
        ('Seguridad', {
            'fields': ('intentos_fallidos', 'ultimo_intento', 'fecha_bloqueo'),
            'classes': ('collapse',)
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('usuariorol_set__rol')

    def get_roles(self, obj):
        roles = obj.usuariorol_set.all()
        if roles:
            return ", ".join([rol.rol.nombre for rol in roles])
        return "Sin roles asignados"
    get_roles.short_description = 'Roles'
    get_roles.admin_order_field = 'usuariorol__rol__nombre'

    def asignar_rol_administrador(self, request, queryset):
        rol_admin = Rol.objects.get_or_create(
            nombre='Administrador',
            defaults={
                'descripcion': 'Rol con permisos completos de administración del sistema',
                'permisos': {
                    'usuarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'socios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'transferencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'reportes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'auditoria': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'configuracion': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True}
                },
                'es_sistema': True,
                'creado_en': timezone.now(),
                'actualizado_en': timezone.now()
            }
        )[0]

        # Actualizar permisos si el rol ya existe
        if not rol_admin.permisos:
            rol_admin.permisos = {
                'usuarios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'socios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'transferencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'reportes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'auditoria': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'configuracion': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True}
            }
            rol_admin.save()

        for usuario in queryset:
            UsuarioRol.objects.get_or_create(
                usuario=usuario,
                rol=rol_admin,
                defaults={'creado_en': timezone.now()}
            )
            usuario.is_staff = True
            usuario.is_superuser = True
            usuario.save()

        self.message_user(request, f'Rol Administrador asignado a {queryset.count()} usuario(s).')
    asignar_rol_administrador.short_description = "Asignar rol Administrador"

    def asignar_rol_socio(self, request, queryset):
        rol_socio = Rol.objects.get_or_create(
            nombre='Socio',
            defaults={
                'descripcion': 'Rol para socios de la cooperativa con acceso limitado a sus propios datos',
                'permisos': {
                    'usuarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                    'socios': {'ver': True, 'crear': False, 'editar': True, 'eliminar': False, 'aprobar': False},
                    'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': False},
                    'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                    'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                    'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                    'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                    'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                    'transferencias': {'ver': True, 'crear': True, 'editar': False, 'eliminar': False, 'aprobar': False},
                    'reportes': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                    'auditoria': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                    'configuracion': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False}
                },
                'es_sistema': True,
                'creado_en': timezone.now(),
                'actualizado_en': timezone.now()
            }
        )[0]

        # Actualizar permisos si el rol ya existe
        if not rol_socio.permisos:
            rol_socio.permisos = {
                'usuarios': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                'socios': {'ver': True, 'crear': False, 'editar': True, 'eliminar': False, 'aprobar': False},
                'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': False},
                'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': False},
                'transferencias': {'ver': True, 'crear': True, 'editar': False, 'eliminar': False, 'aprobar': False},
                'reportes': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                'auditoria': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                'configuracion': {'ver': False, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False}
            }
            rol_socio.save()

        for usuario in queryset:
            UsuarioRol.objects.get_or_create(
                usuario=usuario,
                rol=rol_socio,
                defaults={'creado_en': timezone.now()}
            )

        self.message_user(request, f'Rol Socio asignado a {queryset.count()} usuario(s).')
    asignar_rol_socio.short_description = "Asignar rol Socio"

    def asignar_rol_operador(self, request, queryset):
        rol_operador = Rol.objects.get_or_create(
            nombre='Operador',
            defaults={
                'descripcion': 'Rol para operadores con permisos intermedios de gestión operativa',
                'permisos': {
                    'usuarios': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                    'socios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},
                    'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},
                    'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                    'transferencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},
                    'reportes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': False},
                    'auditoria': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                    'configuracion': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False}
                },
                'es_sistema': True,
                'creado_en': timezone.now(),
                'actualizado_en': timezone.now()
            }
        )[0]

        # Actualizar permisos si el rol ya existe
        if not rol_operador.permisos:
            rol_operador.permisos = {
                'usuarios': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                'socios': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},
                'parcelas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},
                'cultivos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'ciclos_cultivo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'cosechas': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'tratamientos': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'analisis_suelo': {'ver': True, 'crear': True, 'editar': True, 'eliminar': True, 'aprobar': True},
                'transferencias': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': True},
                'reportes': {'ver': True, 'crear': True, 'editar': True, 'eliminar': False, 'aprobar': False},
                'auditoria': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False},
                'configuracion': {'ver': True, 'crear': False, 'editar': False, 'eliminar': False, 'aprobar': False}
            }
            rol_operador.save()

        for usuario in queryset:
            UsuarioRol.objects.get_or_create(
                usuario=usuario,
                rol=rol_operador,
                defaults={'creado_en': timezone.now()}
            )

        self.message_user(request, f'Rol Operador asignado a {queryset.count()} usuario(s).')
    asignar_rol_operador.short_description = "Asignar rol Operador"

    def quitar_todos_roles(self, request, queryset):
        count = 0
        for usuario in queryset:
            count += usuario.usuariorol_set.all().delete()[0]

        self.message_user(request, f'{count} rol(es) removido(s) de {queryset.count()} usuario(s).')
    quitar_todos_roles.short_description = "Quitar todos los roles"

@admin.register(Comunidad)
class ComunidadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'municipio', 'departamento', 'creado_en')
    list_filter = ('departamento', 'creado_en')
    search_fields = ('nombre', 'municipio', 'departamento')

@admin.register(Socio)
class SocioAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'comunidad', 'codigo_interno', 'estado', 'creado_en')
    list_filter = ('estado', 'comunidad', 'creado_en')
    search_fields = ('usuario__usuario', 'usuario__nombres', 'codigo_interno')
    readonly_fields = ('creado_en',)

@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ('id', 'socio', 'nombre', 'superficie_hectareas', 'latitud', 'longitud', 'estado')
    list_filter = ('estado', 'creado_en')
    search_fields = ('nombre', 'socio__usuario__nombres')
    list_editable = ('estado',)

@admin.register(Cultivo)
class CultivoAdmin(admin.ModelAdmin):
    list_display = ('id', 'parcela', 'especie', 'variedad', 'fecha_estimada_siembra', 'estado')
    list_filter = ('estado', 'especie', 'fecha_estimada_siembra')
    search_fields = ('especie', 'variedad', 'parcela__nombre')
    readonly_fields = ('creado_en',)

@admin.register(BitacoraAuditoria)
class BitacoraAuditoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'accion', 'tabla_afectada', 'registro_id', 'fecha', 'ip_address')
    list_filter = ('accion', 'tabla_afectada', 'fecha', 'ip_address')
    search_fields = ('usuario__usuario', 'accion', 'tabla_afectada', 'ip_address')
    readonly_fields = ('fecha', 'ip_address', 'user_agent')
    date_hierarchy = 'fecha'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('usuario')
