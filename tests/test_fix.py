#!/usr/bin/env python3
"""
Simple test script to verify the JWT token validation fix
"""
import os
import sys
import requests
import json

# Configure API base URL
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

def test_auth_flow():
    """Test the complete authentication flow with the fix"""
    print("🧪 Testing Authentication Flow Fix")
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
        
        if verify_resp.status_code != 200:
            print("   ❌ Failed to verify OTP")
            return None
            
        # Extract tokens
        verify_data = verify_resp.json()
        access_token = verify_data.get("access_token")
        user_id = verify_data.get("user_id")
        
        if not access_token:
            print("   ❌ No access token received")
            return None
            
        print(f"   ✅ Got tokens:")
        print(f"      User ID: {user_id}")
        print(f"      Access Token: {access_token[:50]}...")
        
        return {"access_token": access_token, "user_id": user_id}
        
    except Exception as e:
        print(f"   ❌ Verify Error: {e}")
        return None

def test_profile_access(tokens):
    """Test if the profile endpoint now works with the token"""
    if not tokens:
        print("❌ No tokens to test")
        return False
    
    print(f"\n🧪 Step 4: Testing Profile Access (This should work now!)")
    print("=" * 50)
    
    access_token = tokens["access_token"]
    user_id = tokens["user_id"]
    
    # Test profile endpoint
    profile_url = f"{API_BASE_URL}/api/v1/profile/"
    profile_headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        profile_resp = requests.get(profile_url, headers=profile_headers, timeout=30)
        print(f"   Profile Status: {profile_resp.status_code}")
        
        if profile_resp.status_code == 200:
            print("   🎉 SUCCESS! Profile endpoint now works!")
            try:
                profile_data = profile_resp.json()
                print(f"   Profile Data: {json.dumps(profile_data, indent=2)}")
            except:
                print(f"   Profile Response: {profile_resp.text}")
            return True
        else:
            print(f"   ❌ Still getting error: {profile_resp.status_code}")
            if profile_resp.content:
                try:
                    error_data = profile_resp.json()
                    print(f"   Error Details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error Text: {profile_resp.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Profile Error: {e}")
        return False

def main():
    print("🚀 Testing the JWT Token Validation Fix")
    print("=" * 50)
    
    # Test the complete flow
    tokens = test_auth_flow()
    
    if tokens:
        # Test if profile access now works
        success = test_profile_access(tokens)
        
        if success:
            print(f"\n🎉 SUCCESS! The fix worked!")
            print(f"   User ID: {tokens['user_id']}")
            print(f"   Profile endpoint is now accessible")
        else:
            print(f"\n❌ The fix didn't work completely")
            print(f"   Profile endpoint still has issues")
    else:
        print(f"\n❌ Authentication flow failed")

if __name__ == "__main__":
    main()
