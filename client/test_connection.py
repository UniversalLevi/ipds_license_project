#!/usr/bin/env python3
"""
Test API connection and diagnose issues
"""

import requests
import sys

def test_api_connection(api_url):
    """Test API connection with detailed diagnostics"""
    print(f"🔍 Testing connection to: {api_url}")
    
    # Test 1: Basic connectivity
    try:
        response = requests.get(f"{api_url}/", timeout=5)
        print(f"✅ Root endpoint accessible: {response.status_code}")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return False
    
    # Test 2: Health check
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        print(f"   Response: {response.text}")
        if response.status_code == 200:
            return True
        else:
            print("❌ Health check returned non-200 status")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    api_url = "http://10.10.199.65:8000"
    if len(sys.argv) > 1:
        api_url = sys.argv[1]
    
    success = test_api_connection(api_url)
    if success:
        print("\n🎉 API connection successful!")
    else:
        print("\n❌ API connection failed!")
        print("\n💡 Troubleshooting tips:")
        print("1. Check if agent server is running")
        print("2. Check if database is accessible")
        print("3. Check firewall settings")
        print("4. Check network connectivity") 