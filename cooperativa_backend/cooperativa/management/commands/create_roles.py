from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import Rol


class Command(BaseCommand):
    help = 'Crea los roles del sistema por defecto'

    def handle(self, *args, **options):
        self.stdout.write('Creando roles del sistema...')

        # Crear rol Administrador
        admin_rol, created = Rol.objects.get_or_create(
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
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Rol Administrador creado'))
        else:
            self.stdout.write(f'✓ Rol Administrador ya existe')

        # Crear rol Socio
        socio_rol, created = Rol.objects.get_or_create(
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
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Rol Socio creado'))
        else:
            self.stdout.write(f'✓ Rol Socio ya existe')

        # Crear rol Operador
        operador_rol, created = Rol.objects.get_or_create(
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
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'✓ Rol Operador creado'))
        else:
            self.stdout.write(f'✓ Rol Operador ya existe')

        self.stdout.write(self.style.SUCCESS('¡Roles del sistema creados exitosamente!'))