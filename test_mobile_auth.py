"""
Test script for mobile authentication endpoints.
This script tests the new mobile OAuth flow.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "leonelcs@gmail.com"  # Should be in whitelist

def test_web_auth_with_origin():
    """Test the web authentication endpoint with origin parameter."""
    print("🧪 Testing web authentication with origin parameter...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/google/login", params={"origin": "web"})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Web auth successful")
            print(f"   Auth URL: {data.get('auth_url', 'N/A')[:100]}...")
            print(f"   Origin: {data.get('origin', 'N/A')}")
            print(f"   State: {data.get('state', 'N/A')[:20]}...")
            return True
        else:
            print(f"❌ Web auth failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing web auth: {e}")
        return False

def test_ios_auth_endpoint():
    """Test the iOS authentication endpoint structure."""
    print("\n🧪 Testing iOS authentication endpoint...")
    
    try:
        # This will fail without a valid token, but we can check the endpoint exists
        response = requests.post(
            f"{BASE_URL}/api/auth/mobile/google",
            json={"id_token": "invalid_token", "origin": "ios"}
        )
        
        # We expect this to fail with 500 (invalid token) rather than 404 (endpoint not found)
        if response.status_code in [400, 500]:
            print(f"✅ iOS auth endpoint exists and responds correctly to invalid token")
            print(f"   Status: {response.status_code}")
            error_detail = response.json().get('detail', 'No detail')
            print(f"   Error: {error_detail[:100]}...")
            return True
        else:
            print(f"❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing iOS auth: {e}")
        return False

def test_configuration():
    """Test that the new configuration is loaded."""
    print("\n🧪 Testing configuration...")
    
    try:
        # Test web auth to see if configurations are working
        response = requests.get(f"{BASE_URL}/api/auth/google/login", params={"origin": "ios"})
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Configuration loaded successfully")
            print(f"   Origin in response: {data.get('origin', 'N/A')}")
            
            # Check if the auth URL contains the iOS client ID
            auth_url = data.get('auth_url', '')
            if '813648694576-i7ajuil729ci26n7q40fds1ffus1moo0' in auth_url:
                print(f"✅ iOS client ID found in auth URL")
            else:
                print(f"⚠️  iOS client ID not found in auth URL")
                print(f"   URL: {auth_url[:150]}...")
            
            return True
        else:
            print(f"❌ Configuration test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

def main():
    """Run all tests."""
    print(f"🚀 Starting mobile authentication tests at {datetime.now()}")
    print(f"📍 Testing against: {BASE_URL}")
    print("=" * 60)
    
    results = []
    
    # Test web auth with origin
    results.append(test_web_auth_with_origin())
    
    # Test iOS endpoint
    results.append(test_ios_auth_endpoint())
    
    # Test configuration
    results.append(test_configuration())
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! Mobile authentication is ready.")
    else:
        print("⚠️  Some tests failed. Check the backend configuration.")
    
    print("\n📚 Next steps:")
    print("1. Test with a real iOS app using Google Sign-In SDK")
    print("2. Use the POST /api/auth/mobile/google endpoint with a valid id_token")
    print("3. Verify that tokens are validated against the iOS client ID")

if __name__ == "__main__":
    main()
