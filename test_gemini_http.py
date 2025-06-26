#!/usr/bin/env python3
"""
Test HTTP Gemini Server
"""
import requests
import json

def test_gemini_http_server():
    # Test health check
    print("Testing health check...")
    response = requests.get("http://localhost:8016/health")
    print(f"Health Status: {response.status_code}")
    print(f"Health Response: {json.dumps(response.json(), indent=2)}")
    
    # Test generation
    print("\nTesting generation...")
    response = requests.post("http://localhost:8016/generate", json={
        "prompt": "Hello! Are you working correctly? Please respond with a short confirmation.",
        "model": "gemini-2.5-pro",
        "temperature": 0.7,
        "max_tokens": 100
    })
    print(f"Generation Status: {response.status_code}")
    print(f"Generation Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    test_gemini_http_server()
