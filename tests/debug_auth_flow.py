#!/usr/bin/env python3
"""
Debug script to test the complete authentication flow and identify token/session issues
"""
import os
import sys
import requests
import json
from datetime import datetime

# Configure API base URL
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

def test_auth_flow():
    """Test the complete authentication flow step by step"""
    print("🔍 Debugging Authentication Flow")
    print("=" * 50)
    
    # Test phone number
    test_phone = "+16108883335"
    
    # Step 1: Send OTP
    print(f"\n📱 Step 1: Sending OTP to {test_phone}")
    otp_url = f"{API_BASE_URL}/api/v1/auth/client/signin"
    otp_payload = {"phone": test_phone}
    
    try:
        otp_resp = requests.post(otp_url, json=otp_payload, timeout=30)
        print(f"   OTP Response Status: {otp_resp.status_code}")
        print(f"   OTP Response: {json.dumps(otp_resp.json(), indent=2)}")
        
        if otp_resp.status_code != 200:
            print("   ❌ Failed to send OTP")
            return None
            
    except Exception as e:
        print(f"   ❌ OTP Error: {e}")
        return None
    
    # Step 2: Get OTP from user
    print(f"\n📋 Step 2: Enter OTP Code")
    print(f"   Check your phone {test_phone} for the OTP code")
    otp_token = input("   Enter OTP code: ").strip()
    
    if not otp_token:
        print("   ❌ No OTP token provided")
        return None
    
    # Step 3: Verify OTP
    print(f"\n🔐 Step 3: Verifying OTP")
    verify_url = f"{API_BASE_URL}/api/v1/auth/client/verify-otp"
    verify_payload = {"phone": test_phone, "token": otp_token}
    
    try:
        verify_resp = requests.post(verify_url, json=verify_payload, timeout=30)
        print(f"   Verify Response Status: {verify_resp.status_code}")
        print(f"   Verify Response: {json.dumps(verify_resp.json(), indent=2)}")
        
        if verify_resp.status_code != 200:
            print("   ❌ Failed to verify OTP")
            return None
            
        # Extract tokens
        verify_data = verify_resp.json()
        access_token = verify_data.get("access_token")
        refresh_token = verify_data.get("refresh_token")
        user_id = verify_data.get("user_id")
        
        if not access_token:
            print("   ❌ No access token received")
            return None
            
        print(f"   ✅ Got tokens:")
        print(f"      User ID: {user_id}")
        print(f"      Access Token: {access_token[:50]}...")
        print(f"      Refresh Token: {refresh_token[:20]}...")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user_id
        }
        
    except Exception as e:
        print(f"   ❌ Verify Error: {e}")
        return None

def test_token_validation(tokens):
    """Test the received tokens with different endpoints"""
    if not tokens:
        print("❌ No tokens to test")
        return
    
    print(f"\n🧪 Step 4: Testing Token Validation")
    print("=" * 50)
    
    access_token = tokens["access_token"]
    user_id = tokens["user_id"]
    
    # Test 1: Profile endpoint
    print(f"\n📋 Test 1: Profile Endpoint")
    profile_url = f"{API_BASE_URL}/api/v1/profile/"
    profile_headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        profile_resp = requests.get(profile_url, headers=profile_headers, timeout=30)
        print(f"   Profile Status: {profile_resp.status_code}")
        print(f"   Profile Headers: {dict(profile_resp.headers)}")
        
        if profile_resp.content:
            try:
                profile_data = profile_resp.json()
                print(f"   Profile Response: {json.dumps(profile_data, indent=2)}")
            except:
                print(f"   Profile Response Text: {profile_resp.text}")
        else:
            print(f"   Profile Response Text: {profile_resp.text}")
            
    except Exception as e:
        print(f"   Profile Error: {e}")
    
    # Test 2: Auth me endpoint (if it exists)
    print(f"\n🔐 Test 2: Auth Me Endpoint")
    auth_url = f"{API_BASE_URL}/api/v1/auth/me"
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        auth_resp = requests.get(auth_url, headers=auth_headers, timeout=30)
        print(f"   Auth Status: {auth_resp.status_code}")
        
        if auth_resp.content:
            try:
                auth_data = auth_resp.json()
                print(f"   Auth Response: {json.dumps(auth_data, indent=2)}")
            except:
                print(f"   Auth Response Text: {auth_resp.text}")
        else:
            print(f"   Auth Response Text: {auth_resp.text}")
            
    except Exception as e:
        print(f"   Auth Error: {e}")
    
    # Test 3: Tasks endpoint
    print(f"\n📝 Test 3: Tasks Endpoint")
    tasks_url = f"{API_BASE_URL}/api/v1/tasks/"
    tasks_headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        tasks_resp = requests.get(tasks_url, headers=tasks_headers, timeout=30)
        print(f"   Tasks Status: {tasks_resp.status_code}")
        
        if tasks_resp.content:
            try:
                tasks_data = tasks_resp.json()
                print(f"   Tasks Response: {json.dumps(tasks_data, indent=2)}")
            except:
                print(f"   Tasks Response Text: {tasks_resp.text}")
        else:
            print(f"   Tasks Response Text: {tasks_resp.text}")
            
    except Exception as e:
        print(f"   Tasks Error: {e}")
    
    # Test 4: Raw token inspection
    print(f"\n🔍 Test 4: Token Inspection")
    try:
        # Decode JWT payload without verification
        parts = access_token.split('.')
        if len(parts) == 3:
            import base64
            payload = parts[1]
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.b64decode(payload)
            token_data = json.loads(decoded)
            
            print(f"   Token Payload:")
            print(f"      Issuer: {token_data.get('iss', 'N/A')}")
            print(f"      Subject: {token_data.get('sub', 'N/A')}")
            print(f"      Audience: {token_data.get('aud', 'N/A')}")
            print(f"      Expires: {datetime.fromtimestamp(token_data.get('exp', 0))}")
            print(f"      Issued At: {datetime.fromtimestamp(token_data.get('iat', 0))}")
            print(f"      Role: {token_data.get('role', 'N/A')}")
            print(f"      Phone: {token_data.get('phone', 'N/A')}")
            
            # Check if token is expired
            current_time = datetime.now().timestamp()
            if token_data.get('exp', 0) < current_time:
                print(f"   ❌ Token has expired!")
            else:
                print(f"   ✅ Token is still valid")
        else:
            print(f"   ❌ Invalid JWT format")
            
    except Exception as e:
        print(f"   Token Inspection Error: {e}")

def main():
    print("🚀 Starting Authentication Flow Debug")
    print("=" * 50)
    
    # Test the complete flow
    tokens = test_auth_flow()
    
    if tokens:
        # Test token validation
        test_token_validation(tokens)
        
        print(f"\n🎯 Debug Summary:")
        print(f"   User ID: {tokens['user_id']}")
        print(f"   Access Token: {'✅' if tokens['access_token'] else '❌'}")
        print(f"   Refresh Token: {'✅' if tokens['refresh_token'] else '❌'}")
    else:
        print(f"\n❌ Authentication flow failed")

if __name__ == "__main__":
    main()
