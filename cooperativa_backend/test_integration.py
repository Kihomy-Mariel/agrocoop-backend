#!/usr/bin/env python3
"""
Test script to verify parcela edit functionality after backend fixes
"""
import requests
import json

BASE_URL = 'http://127.0.0.1:8000'

def test_parcela_edit():
    """Test editing a parcela to verify HTTP 400 error is resolved"""

    # First, get CSRF token
    session = requests.Session()

    # Get the CSRF token from the login page or API
    try:
        # Try to get CSRF token from a simple endpoint
        response = session.get(f'{BASE_URL}/api/parcelas/')
        csrf_token = response.cookies.get('csrftoken') or response.cookies.get('csrf_token')

        if not csrf_token:
            print("Warning: Could not get CSRF token, proceeding without it")

        headers = {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrf_token or '',
        }

        # Test data for parcela edit (similar to what frontend sends)
        test_data = {
            'id': 1,
            'socio_id': 1,  # This should be mapped to 'socio' field
            'nombre': 'Parcela Test Editada',
            'superficie': 25.5,  # This should be mapped to 'superficie_hectareas'
            'coordenadas': '-16.5, -68.2',  # This should be mapped to lat/lng
            'descripcion': 'Ubicación actualizada para testing',
            'tipo_suelo': 'arcilloso',
            'estado': 'activa'
        }

        print("Testing parcela edit with data:")
        print(json.dumps(test_data, indent=2))

        # Test PUT request to edit parcela
        response = session.put(
            f'{BASE_URL}/api/parcelas/1/',
            json=test_data,
            headers=headers
        )

        print(f"\nResponse Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("✅ SUCCESS: Parcela edit successful!")
            print("Response data:")
            print(json.dumps(response.json(), indent=2))
            return True
        else:
            print("❌ ERROR: Parcela edit failed")
            print("Response content:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Django server. Make sure it's running on http://127.0.0.1:8000/")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_tipos_suelo_endpoint():
    """Test the tipos-suelo endpoint"""
    try:
        response = requests.get(f'{BASE_URL}/api/parcelas/tipos-suelo/')

        print(f"\nTesting tipos-suelo endpoint:")
        print(f"Response Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ SUCCESS: Tipos suelo endpoint working!")
            data = response.json()
            print(f"Data type: {type(data)}")
            if isinstance(data, dict) and 'tipos_suelo' in data:
                tipos = data['tipos_suelo']
                print(f"Found {len(tipos)} tipos de suelo")
                for tipo in tipos[:3]:  # Show first 3
                    print(f"  - {tipo}")
            else:
                print("Unexpected response format")
                print(json.dumps(data, indent=2))
            return True
        else:
            print("❌ ERROR: Tipos suelo endpoint failed")
            print(response.text)
            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Django server")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == '__main__':
    print("🧪 Testing Parcela Edit Integration")
    print("=" * 50)

    # Test tipos suelo endpoint first
    tipos_success = test_tipos_suelo_endpoint()

    # Test parcela edit
    edit_success = test_parcela_edit()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Tipos suelo endpoint: {'✅ PASS' if tipos_success else '❌ FAIL'}")
    print(f"Parcela edit: {'✅ PASS' if edit_success else '❌ FAIL'}")

    if tipos_success and edit_success:
        print("\n🎉 All tests passed! Frontend-backend integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")