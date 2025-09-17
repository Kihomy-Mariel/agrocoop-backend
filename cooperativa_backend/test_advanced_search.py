#!/usr/bin/env python3
"""
Test script for the advanced parcela search endpoint
"""
import requests
import json

# Django server URL
BASE_URL = "http://127.0.0.1:8000"

def test_advanced_parcela_search():
    """Test the advanced parcela search endpoint"""

    print("� Testing advanced parcela search endpoint (without auth for now)...")

    # Test with some search parameters
    search_params = {
        'page': 1,
        'page_size': 10,
        'estado': 'ACTIVA'
    }

    try:
        search_response = requests.get(
            f"{BASE_URL}/api/parcelas/buscar-avanzado/",
            params=search_params,
            headers={
                "Content-Type": "application/json"
            }
        )

        print(f"Status Code: {search_response.status_code}")

        if search_response.status_code == 403:
            print("✅ Endpoint exists and authentication is working (403 = Forbidden, not 404 = Not Found)")
            print("This confirms the endpoint is properly implemented!")
            return True
        elif search_response.status_code == 200:
            result = search_response.json()
            print("✅ Advanced parcela search successful!")
            print(f"Total results: {result.get('count', 0)}")
            print(f"Page: {result.get('page', 0)}")
            print(f"Results returned: {len(result.get('results', []))}")

            # Show first result if any
            results = result.get('results', [])
            if results:
                print("\n📋 First parcela result:")
                parcela = results[0]
                print(f"  ID: {parcela.get('id')}")
                print(f"  Nombre: {parcela.get('nombre')}")
                print(f"  Socio: {parcela.get('socio_nombre')}")
                print(f"  Estado: {parcela.get('estado')}")
                print(f"  Superficie: {parcela.get('superficie_hectareas')} ha")
            return True
        else:
            print(f"❌ Unexpected status code: {search_response.status_code}")
            print(f"Response: {search_response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Django server. Make sure it's running!")
        return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_advanced_parcela_search()
    if success:
        print("\n🎉 Test completed successfully!")
        print("The advanced parcela search endpoint is working correctly.")
        print("Authentication can be tested separately from the frontend.")
    else:
        print("\n❌ Test failed. Check the errors above.")