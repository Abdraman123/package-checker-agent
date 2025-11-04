#!/usr/bin/env python3
"""
Local testing script for Package Checker Agent
Usage: python test_local.py
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"

def test_health():
    """Test health endpoint"""
    print("\n1️⃣ Testing Health Endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_root():
    """Test root endpoint"""
    print("\n2️⃣ Testing Root Endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_a2a_package(query: str, test_name: str):
    """Test A2A endpoint with a package query"""
    print(f"\n{test_name}")
    
    payload = {
        "jsonrpc": "2.0",
        "id": f"test-{datetime.now().timestamp()}",
        "method": "message/send",
        "params": {
            "message": {
                "kind": "message",
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": query
                    }
                ],
                "messageId": f"msg-{datetime.now().timestamp()}"
            }
        }
    }
    
    print(f"Query: '{query}'")
    response = requests.post(
        f"{BASE_URL}/a2a/package",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        if "result" in result and "status" in result["result"]:
            message = result["result"]["status"].get("message", {})
            if "parts" in message and len(message["parts"]) > 0:
                text = message["parts"][0].get("text", "")
                print(f"Response:\n{text}")
                return True
    else:
        print(f"Error Response: {json.dumps(response.json(), indent=2)}")
    
    return False

def main():
    """Run all tests"""
    print("🧪 Testing Package Checker Agent")
    print("=" * 60)
    
    results = []
    
    # Test 1: Health
    results.append(("Health Check", test_health()))
    
    # Test 2: Root
    results.append(("Root Endpoint", test_root()))
    
    # Test 3: PyPI package
    results.append(("PyPI Package (fastapi)", test_a2a_package("Check fastapi", "3️⃣ Testing PyPI Package")))
    
    # Test 4: npm package
    results.append(("npm Package (express)", test_a2a_package("npm package express", "4️⃣ Testing npm Package")))
    
    # Test 5: Python keyword
    results.append(("Python Package (django)", test_a2a_package("python package django", "5️⃣ Testing with Python Keyword")))
    
    # Test 6: Package not found
    results.append(("Package Not Found", test_a2a_package("nonexistentpackage12345xyz", "6️⃣ Testing Package Not Found")))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your agent is working correctly!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the output above.")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure the server is running on http://localhost:8080")
        print("Run: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")