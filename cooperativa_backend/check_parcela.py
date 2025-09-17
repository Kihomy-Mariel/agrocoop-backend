#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')

# Setup Django
django.setup()

from cooperativa.models import Parcela

def check_parcela():
    try:
        parcela = Parcela.objects.get(id=1)
        print("Parcela found:", parcela.nombre)
        print("Current data:")
        print(f"  ID: {parcela.id}")
        print(f"  Socio ID: {parcela.socio_id}")
        print(f"  Superficie: {parcela.superficie_hectareas}")
        print(f"  Tipo suelo: {parcela.tipo_suelo}")
        print(f"  Ubicacion: {parcela.ubicacion}")
        print(f"  Latitud: {parcela.latitud}")
        print(f"  Longitud: {parcela.longitud}")
        print(f"  Estado: {parcela.estado}")
        return True
    except Parcela.DoesNotExist:
        print("Parcela with ID 1 does not exist")
        return False
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    check_parcela()