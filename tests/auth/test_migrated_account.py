#!/usr/bin/env python3
"""
Test script for migrated account authentication and profile endpoints.
Tests the migrated account with phone number 16108883335.
"""

import os
import sys
import argparse
import requests
import json
from typing import Optional, Dict, Any

# Configure API base URL (override with API_BASE_URL env var)
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
AUTH_PREFIX = "/api/v1/auth"
PROFILE_PREFIX = "/api/v1/profile"

# Test phone number (migrated account) - E.164 format required
TEST_PHONE = "+16108883335"


class MigratedAccountTester:
    """Test class for migrated account functionality"""
    
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        
    def send_signin_otp(self, phone: str) -> Dict[str, Any]:
        """Send signin OTP to phone number"""
        url = f"{self.api_base_url}{AUTH_PREFIX}/client/signin"
        payload = {"phone": phone}
        
        print(f"📱 Sending signin OTP to {phone}...")
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        try:
            resp = requests.post(url, json=payload, timeout=30)
            data = resp.json() if resp.content else {"text": resp.text}
            
            result = {
                "status": resp.status_code,
                "data": data,
                "headers": dict(resp.headers)
            }
            
            print(f"   Response: HTTP {resp.status_code}")
            print(f"   Data: {json.dumps(data, indent=2)}")
            
            return result
            
        except Exception as e:
            error_result = {
                "status": 0,
                "data": {"error": str(e)},
                "headers": {}
            }
            print(f"   Error: {e}")
            return error_result
    
    def verify_otp(self, phone: str, token: str) -> Dict[str, Any]:
        """Verify OTP token and get authentication tokens"""
        url = f"{self.api_base_url}{AUTH_PREFIX}/client/verify-otp"
        payload = {"phone": phone, "token": token}
        
        print(f"🔐 Verifying OTP token {token} for {phone}...")
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        try:
            resp = requests.post(url, json=payload, timeout=30)
            data = resp.json() if resp.content else {"text": resp.text}
            
            result = {
                "status": resp.status_code,
                "data": data,
                "headers": dict(resp.headers)
            }
            
            print(f"   Response: HTTP {resp.status_code}")
            print(f"   Data: {json.dumps(data, indent=2)}")
            
            # Store tokens if successful
            if resp.status_code == 200 and data.get("success"):
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self.user_id = data.get("user_id")
                print(f"   ✅ Stored tokens - User ID: {self.user_id}")
            
            return result
            
        except Exception as e:
            error_result = {
                "status": 0,
                "data": {"error": str(e)},
                "headers": {}
            }
            print(f"   Error: {e}")
            return error_result
    
    def get_profile(self) -> Dict[str, Any]:
        """Get user profile using stored access token"""
        if not self.access_token:
            print("❌ No access token available. Please sign in first.")
            return {"status": 0, "data": {"error": "No access token"}}
        
        url = f"{self.api_base_url}{PROFILE_PREFIX}/"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        print(f"👤 Getting profile for user {self.user_id}...")
        print(f"   URL: {url}")
        print(f"   Headers: {json.dumps(headers, indent=2)}")
        
        try:
            resp = requests.get(url, headers=headers, timeout=30)
            data = resp.json() if resp.content else {"text": resp.text}
            
            result = {
                "status": resp.status_code,
                "data": data,
                "headers": dict(resp.headers)
            }
            
            print(f"   Response: HTTP {resp.status_code}")
            print(f"   Data: {json.dumps(data, indent=2)}")
            
            return result
            
        except Exception as e:
            error_result = {
                "status": 0,
                "data": {"error": str(e)},
                "headers": {}
            }
            print(f"   Error: {e}")
            return error_result
    
    def test_complete_flow(self) -> bool:
        """Test the complete authentication and profile flow"""
        print("🚀 Testing Complete Migrated Account Flow")
        print("=" * 50)
        
        # Step 1: Send signin OTP
        print("\n📋 Step 1: Send Signin OTP")
        otp_result = self.send_signin_otp(TEST_PHONE)
        if otp_result["status"] != 200:
            print(f"❌ Failed to send OTP: {otp_result['status']}")
            return False
        
        # Step 2: Get OTP from user input
        print(f"\n📋 Step 2: Enter OTP Code")
        print(f"   Check your phone {TEST_PHONE} for the OTP code")
        otp_token = input("   Enter OTP code: ").strip()
        
        if not otp_token:
            print("❌ No OTP token provided")
            return False
        
        # Step 3: Verify OTP
        print(f"\n📋 Step 3: Verify OTP")
        verify_result = self.verify_otp(TEST_PHONE, otp_token)
        if verify_result["status"] != 200:
            print(f"❌ Failed to verify OTP: {verify_result['status']}")
            return False
        
        # Step 4: Get profile
        print(f"\n📋 Step 4: Get User Profile")
        profile_result = self.get_profile()
        if profile_result["status"] != 200:
            print(f"❌ Failed to get profile: {profile_result['status']}")
            return False
        
        print(f"\n🎉 Complete flow test successful!")
        print(f"   User ID: {self.user_id}")
        print(f"   Access Token: {'✅' if self.access_token else '❌'}")
        print(f"   Refresh Token: {'✅' if self.refresh_token else '❌'}")
        
        return True
    
    def test_individual_endpoints(self) -> None:
        """Test individual endpoints separately"""
        print("\n🔧 Testing Individual Endpoints")
        print("=" * 30)
        
        # Test signin endpoint
        print(f"\n📱 Testing Signin Endpoint")
        signin_result = self.send_signin_otp(TEST_PHONE)
        print(f"   Signin Status: {signin_result['status']}")
        
        # Test profile endpoint (should fail without auth)
        print(f"\n👤 Testing Profile Endpoint (Unauthenticated)")
        profile_result = self.get_profile()
        print(f"   Profile Status: {profile_result['status']}")
        if profile_result["status"] == 401:
            print("   ✅ Correctly rejected unauthenticated request")
        else:
            print("   ⚠️ Unexpected response for unauthenticated request")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Test migrated account authentication and profile endpoints")
    parser.add_argument("--api-url", default=API_BASE_URL, help=f"API base URL (default: {API_BASE_URL})")
    parser.add_argument("--phone", default=TEST_PHONE, help=f"Phone number to test (default: {TEST_PHONE})")
    
    sub = parser.add_subparsers(dest="command", required=True)
    
    # Complete flow test
    flow_parser = sub.add_parser("test-flow", help="Test complete authentication and profile flow")
    
    # Individual endpoint tests
    endpoints_parser = sub.add_parser("test-endpoints", help="Test individual endpoints separately")
    
    # Manual OTP verification
    verify_parser = sub.add_parser("verify-otp", help="Manually verify OTP with token")
    verify_parser.add_argument("token", help="OTP token to verify")
    
    # Get profile (requires previous authentication)
    profile_parser = sub.add_parser("get-profile", help="Get user profile (requires previous authentication)")
    
    args = parser.parse_args(argv)
    
    # Create tester instance
    tester = MigratedAccountTester(args.api_url)
    
    try:
        if args.command == "test-flow":
            success = tester.test_complete_flow()
            return 0 if success else 1
            
        elif args.command == "test-endpoints":
            tester.test_individual_endpoints()
            return 0
            
        elif args.command == "verify-otp":
            print(f"🔐 Verifying OTP for {args.phone}...")
            result = tester.verify_otp(args.phone, args.token)
            return 0 if result["status"] == 200 else 1
            
        elif args.command == "get-profile":
            if not tester.access_token:
                print("❌ No access token available. Please run 'test-flow' or 'verify-otp' first.")
                return 1
            result = tester.get_profile()
            return 0 if result["status"] == 200 else 1
            
        else:
            print(f"❌ Unknown command: {args.command}")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
