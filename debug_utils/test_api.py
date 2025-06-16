#!/usr/bin/env python3
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test an API endpoint and return result"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method.upper() == 'GET':
            response = requests.get(url, allow_redirects=False)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, allow_redirects=False)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, allow_redirects=False)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, allow_redirects=False)
        
        success = response.status_code == expected_status
        return {
            'method': method,
            'endpoint': endpoint,
            'status_code': response.status_code,
            'expected': expected_status,
            'success': success,
            'response': response.text[:200] if response.text else ''
        }
    except Exception as e:
        return {
            'method': method,
            'endpoint': endpoint,
            'status_code': 'ERROR',
            'expected': expected_status,
            'success': False,
            'response': str(e)
        }

def main():
    print(f"Testing API endpoints at {BASE_URL}")
    print("=" * 60)
    
    # Test endpoints
    tests = [
        # Basic health check
        ('GET', '/', 200),
        ('GET', '/health', 200),
        
        # User endpoints (require authentication)
        ('GET', '/api/users', 401),  # Should return 401 without auth
        
        # Test endpoints (without authentication first)
        ('GET', '/api/auth/google/login', 302),  # Should redirect to Google
        
        # Test endpoints (should return 401 for auth-required endpoints)
        ('GET', '/api/tasks', 401),  # Should return 401 without auth
        ('GET', '/api/tasks/impact-classification', 200),  # Public endpoint
        
        # Project endpoints (require authentication)
        ('GET', '/api/projects', 401),  # Should return 401 without auth
        ('GET', '/api/projects/public/discover', 200),  # Public endpoint
        
        # Group endpoints (require authentication)
        ('GET', '/api/groups', 401),  # Should return 401 without auth
        
        # Analytics endpoints (require authentication)
        ('GET', '/api/analytics/dashboard', 401),  # Should return 401 without auth
    ]
    
    results = []
    for method, endpoint, *args in tests:
        expected_status = args[0] if len(args) == 1 else args[1]
        data = args[0] if len(args) == 2 else None
        
        result = test_endpoint(method, endpoint, data, expected_status)
        results.append(result)
        
        status = "✓" if result['success'] else "✗"
        print(f"{status} {method:6} {endpoint:20} -> {result['status_code']} (expected {result['expected']})")
        if not result['success'] and result['response']:
            print(f"   Error: {result['response']}")
    
    # Summary
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    # Show failed tests
    failed = [r for r in results if not r['success']]
    if failed:
        print(f"\nFailed tests ({len(failed)}):")
        for test in failed:
            print(f"  {test['method']} {test['endpoint']} -> {test['status_code']} (expected {test['expected']})")
            if test['response']:
                print(f"    {test['response']}")

if __name__ == "__main__":
    main()
