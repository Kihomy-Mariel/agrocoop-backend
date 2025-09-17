import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
django.setup()

from cooperativa.models import Usuario

try:
    user = Usuario.objects.get(usuario='admin')
    print(f'User ID: {user.id}')
    print(f'Username: {user.usuario}')
    print(f'is_staff: {user.is_staff}')
    print(f'is_superuser: {user.is_superuser}')
    print(f'is_active: {user.is_active}')
    print(f'estado: {user.estado}')
except Usuario.DoesNotExist:
    print('Admin user not found')