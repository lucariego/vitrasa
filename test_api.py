#!/usr/bin/env python3
"""
Test script for the Vitrasa API
"""

import requests
import json
import sys

def test_api():
    """Test the Vitrasa API"""
    base_url = "http://localhost:5000"
    
    print("Testing Vitrasa Bus Stop API...")
    print("=" * 40)
    
    # Test health endpoint
    try:
        print("1. Testing health endpoint...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.json()}")
        print()
    except Exception as e:
        print(f"   Error: {e}")
        print()
    
    # Test API documentation
    try:
        print("2. Testing API documentation...")
        response = requests.get(f"{base_url}/", timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            doc = response.json()
            print(f"   API Name: {doc.get('name')}")
            print(f"   Version: {doc.get('version')}")
        print()
    except Exception as e:
        print(f"   Error: {e}")
        print()
    
    # Test bus stop endpoint
    stop_ids = ["20195", "12345", "invalid"]
    
    for stop_id in stop_ids:
        try:
            print(f"3. Testing stop ID: {stop_id}")
            response = requests.get(f"{base_url}/api/stop/{stop_id}", timeout=10)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Stop Name: {data.get('stop_name')}")
                print(f"   Routes Found: {data.get('total_routes')}")
                if data.get('routes'):
                    print("   Sample Route:")
                    route = data['routes'][0]
                    print(f"     Line: {route.get('line')}")
                    print(f"     Route: {route.get('route')}")
                    print(f"     Minutes: {route.get('minutes')}")
            else:
                error_data = response.json()
                print(f"   Error: {error_data.get('error')}")
                print(f"   Message: {error_data.get('message')}")
            print()
            
        except Exception as e:
            print(f"   Error: {e}")
            print()

if __name__ == "__main__":
    test_api()
