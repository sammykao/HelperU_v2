#!/usr/bin/env python3
"""
Debug script to test JWT token validation
"""
import os
import sys
import requests
import json
import jwt
from datetime import datetime

# Configure API base URL
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

def decode_jwt_payload(token: str) -> dict:
    """Decode JWT payload without verification to inspect contents"""
    try:
        # Split the token and decode the payload part
        parts = token.split('.')
        if len(parts) != 3:
            return {"error": "Invalid JWT format"}
        
        # Decode the payload (second part)
        import base64
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        return {"error": f"Failed to decode payload: {str(e)}"}

def test_jwt_validation(token: str):
    """Test JWT validation with different approaches"""
    print("🔍 JWT Token Analysis")
    print("=" * 50)
    
    # 1. Decode and inspect JWT payload
    print("\n📋 JWT Payload (unverified):")
    payload = decode_jwt_payload(token)
    print(json.dumps(payload, indent=2))
    
    # 2. Check token expiration
    if 'exp' in payload:
        exp_timestamp = payload['exp']
        exp_date = datetime.fromtimestamp(exp_timestamp)
        current_date = datetime.now()
        time_diff = exp_date - current_date
        
        print(f"\n⏰ Token Expiration:")
        print(f"   Expires at: {exp_date}")
        print(f"   Current time: {current_date}")
        print(f"   Time until expiry: {time_diff}")
        
        if time_diff.total_seconds() < 0:
            print("   ❌ Token has expired!")
        else:
            print("   ✅ Token is still valid")
    
    # 3. Test token with profile endpoint
    print(f"\n🧪 Testing Token with Profile Endpoint:")
    url = f"{API_BASE_URL}/api/v1/profile/"
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"   URL: {url}")
    print(f"   Headers: {json.dumps(headers, indent=2)}")
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        print(f"   Response Status: {resp.status_code}")
        print(f"   Response Headers: {dict(resp.headers)}")
        
        if resp.content:
            try:
                data = resp.json()
                print(f"   Response Data: {json.dumps(data, indent=2)}")
            except:
                print(f"   Response Text: {resp.text}")
        else:
            print(f"   Response Text: {resp.text}")
            
    except Exception as e:
        print(f"   Error: {e}")
    
    # 4. Test token with different endpoints
    print(f"\n🧪 Testing Token with Auth Endpoint:")
    auth_url = f"{API_BASE_URL}/api/v1/auth/me"
    try:
        resp = requests.get(auth_url, headers=headers, timeout=30)
        print(f"   Auth Endpoint Status: {resp.status_code}")
        if resp.content:
            try:
                data = resp.json()
                print(f"   Auth Response: {json.dumps(data, indent=2)}")
            except:
                print(f"   Auth Response Text: {resp.text}")
    except Exception as e:
        print(f"   Auth Endpoint Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python debug_jwt.py <jwt_token>")
        print("Example: python debug_jwt.py eyJhbGciOiJIUzI1NiIs...")
        sys.exit(1)
    
    token = sys.argv[1]
    
    if not token or token == "None":
        print("❌ No valid token provided")
        sys.exit(1)
    
    test_jwt_validation(token)

if __name__ == "__main__":
    main()
