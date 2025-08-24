#!/usr/bin/env python3
"""
Test script for helper signup and verification flow.
Tests the complete helper authentication process.
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

# Test helper credentials
TEST_HELPER_EMAIL = "test.helper@tufts.edu"  # Change this to your test email
TEST_HELPER_PHONE = "+16108883335"  # Change this to your test phone


class HelperSignupTester:
    """Test class for helper signup functionality"""
    
    def __init__(self, api_base_url: str):
        self.api_base_url = api_base_url
        self.access_token = None
        self.refresh_token = None
        self.user_id = None
        
    def test_helper_signup(self, email: str, phone: str) -> Dict[str, Any]:
        """Test helper signup endpoint"""
        url = f"{self.api_base_url}{AUTH_PREFIX}/helper/signup"
        payload = {
            "email": email,
            "phone": phone
        }
        
        print(f"📧 Testing Helper Signup")
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, json=payload)
            print(f"   Response: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Data: {json.dumps(data, indent=2)}")
                
                if data.get("success"):
                    self.user_id = data.get("user_id")
                    print(f"   ✅ Helper signup successful! User ID: {self.user_id}")
                    return data
                else:
                    print(f"   ❌ Helper signup failed: {data.get('message')}")
                    return data
            else:
                print(f"   ❌ Helper signup failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            error_msg = f"Helper signup request failed: {e}"
            print(f"   ❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def test_helper_otp_send(self, phone: str) -> Dict[str, Any]:
        """Test sending OTP to helper phone"""
        url = f"{self.api_base_url}{AUTH_PREFIX}/helper/signin"
        payload = {
            "phone": phone
        }
        
        print(f"📱 Testing Helper OTP Send")
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, json=payload)
            print(f"   Response: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Data: {json.dumps(data, indent=2)}")
                
                if data.get("success"):
                    print(f"   ✅ OTP sent successfully to {phone}")
                    return data
                else:
                    print(f"   ❌ OTP send failed: {data.get('message')}")
                    return data
            else:
                print(f"   ❌ OTP send failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            error_msg = f"Helper OTP send request failed: {e}"
            print(f"   ❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def test_helper_otp_verify(self, phone: str, token: str) -> Dict[str, Any]:
        """Test verifying helper OTP"""
        url = f"{self.api_base_url}{AUTH_PREFIX}/helper/verify-otp"
        payload = {
            "phone": phone,
            "token": token
        }
        
        print(f"🔐 Testing Helper OTP Verification")
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, json=payload)
            print(f"   Response: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Data: {json.dumps(data, indent=2)}")
                
                if data.get("success"):
                    self.user_id = data.get("user_id")
                    self.access_token = data.get("access_token")
                    self.refresh_token = data.get("refresh_token")
                    print(f"   ✅ OTP verification successful! User ID: {self.user_id}")
                    print(f"   🔑 Access token received: {'Yes' if self.access_token else 'No'}")
                    return data
                else:
                    print(f"   ❌ OTP verification failed: {data.get('message')}")
                    return data
            else:
                print(f"   ❌ OTP verification failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            error_msg = f"Helper OTP verification request failed: {e}"
            print(f"   ❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def test_helper_profile_completion(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test completing helper profile (requires authentication)"""
        if not self.access_token:
            print("   ❌ No access token available. Please verify OTP first.")
            return {"success": False, "error": "No access token"}
        
        url = f"{self.api_base_url}{AUTH_PREFIX}/helper/complete-profile"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        
        print(f"👤 Testing Helper Profile Completion")
        print(f"   URL: {url}")
        print(f"   Headers: {json.dumps(headers, indent=2)}")
        print(f"   Payload: {json.dumps(profile_data, indent=2)}")
        
        try:
            response = requests.post(url, json=profile_data, headers=headers)
            print(f"   Response: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Data: {json.dumps(data, indent=2)}")
                
                if data.get("success"):
                    print(f"   ✅ Profile completion successful!")
                    return data
                else:
                    print(f"   ❌ Profile completion failed: {data.get('message')}")
                    return data
            else:
                print(f"   ❌ Profile completion failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            error_msg = f"Helper profile completion request failed: {e}"
            print(f"   ❌ {error_msg}")
            return {"success": False, "error": error_msg}
    
    def test_verify_email_otp(self, email: str, otp_code: str) -> Dict[str, Any]:
        """Test verifying email OTP"""
        url = f"{self.api_base_url}{AUTH_PREFIX}/verify-email-otp"
        payload = {
            "email": email,
            "otp_code": otp_code
        }
        
        print(f"📧 Testing Email OTP Verification")
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, json=payload)
            print(f"   Response: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Data: {json.dumps(data, indent=2)}")
                
                if data.get("success"):
                    print(f"   ✅ Email OTP verification successful!")
                    return data
                else:
                    print(f"   ❌ Email OTP verification failed: {data.get('message')}")
                    return data
            else:
                print(f"   ❌ Email OTP verification failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            error_msg = f"Email OTP verification request failed: {e}"
            print(f"   ❌ {error_msg}")
            return {"success": False, "error": error_msg}

    def test_profile_status(self) -> Dict[str, Any]:
        """Test getting profile status (requires authentication)"""
        if not self.access_token:
            print("   ❌ No access token available. Please verify OTP first.")
            return {"success": False, "error": "No access token"}
        
        url = f"{self.api_base_url}{AUTH_PREFIX}/profile-status"
        headers = {
            "Authorization": f"Bearer {self.access_token}"
        }
        
        print(f"📊 Testing Profile Status")
        print(f"   URL: {url}")
        print(f"   Headers: {json.dumps(headers, indent=2)}")
        
        try:
            response = requests.get(url, headers=headers)
            print(f"   Response: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Data: {json.dumps(data, indent=2)}")
                
                if data.get("profile_completed") is not None:
                    print(f"   ✅ Profile status retrieved successfully!")
                    print(f"   📋 Status: {data.get('user_type')} - Email: {data.get('email_verified')}, Phone: {data.get('phone_verified')}, Profile: {data.get('profile_completed')}")
                    return data
                else:
                    print(f"   ❌ Profile status failed: {data.get('message')}")
                    return data
            else:
                print(f"   ❌ Profile status failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            error_msg = f"Profile status request failed: {e}"
            print(f"   ❌ {error_msg}")
            return {"success": False, "error": error_msg}

    def get_profile_info(self, user_id: str) -> Dict[str, Any]:
        """Get profile information for a user (helper or client)"""
        # Try to get helper profile first
        helper_url = f"{self.api_base_url}/api/v1/helper/profile/{user_id}"
        try:
            response = requests.get(helper_url)
            if response.status_code == 200:
                data = response.json()
                print(f"   📋 Found existing helper profile: {data.get('first_name')} {data.get('last_name')}")
                return {
                    "type": "helper",
                    "data": data
                }
        except:
            pass
        
        # Try to get client profile
        client_url = f"{self.api_base_url}/api/v1/client/profile/{user_id}"
        try:
            response = requests.get(client_url)
            if response.status_code == 200:
                data = response.json()
                print(f"   📋 Found existing client profile: {data.get('first_name')} {data.get('last_name')}")
                return {
                    "type": "client", 
                    "data": data
                }
        except:
            pass
        
        print(f"   📋 No existing profile found for user {user_id}")
        return {"type": "none", "data": {}}
    
    def test_email_resend(self, email: str) -> Dict[str, Any]:
        """Test resending email verification"""
        url = f"{self.api_base_url}{AUTH_PREFIX}/resend-email-verification"
        payload = {
            "email": email
        }
        
        print(f"📧 Testing Email Resend")
        print(f"   URL: {url}")
        print(f"   Payload: {json.dumps(payload, indent=2)}")
        
        try:
            response = requests.post(url, json=payload)
            print(f"   Response: HTTP {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   Data: {json.dumps(data, indent=2)}")
                
                if data.get("success"):
                    print(f"   ✅ Email verification resent successfully to {email}")
                    return data
                else:
                    print(f"   ❌ Email resend failed: {data.get('message')}")
                    return data
            else:
                print(f"   ❌ Email resend failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Error: {response.text}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            error_msg = f"Email resend request failed: {e}"
            print(f"   ❌ {error_msg}")
            return {"success": False, "error": error_msg}

    def test_complete_flow(self, email: str, phone: str) -> bool:
        """Test the complete helper signup flow"""
        print("🚀 Testing Complete Helper Signup Flow")
        print("=" * 50)
        
        # Step 1: Helper Signup
        print("\n📋 Step 1: Helper Signup")
        signup_result = self.test_helper_signup(email, phone)
        if not signup_result.get("success"):
            print("❌ Helper signup failed, stopping flow")
            return False
        
        # Step 2: Get OTP from user (Supabase automatically sent it during signup)
        print("\n📋 Step 2: Enter Phone OTP Code")
        print(f"   Supabase automatically sent OTP to {phone} during signup")
        print(f"   Check your phone for the OTP code")
        phone_token = input("   Enter phone OTP code: ").strip()
        
        if not phone_token:
            print("❌ No phone OTP code entered, stopping flow")
            return False
        
        # Step 3: Verify Phone OTP
        print("\n📋 Step 3: Verify Phone OTP")
        otp_verify_result = self.test_helper_otp_verify(phone, phone_token)
        if not otp_verify_result.get("success"):
            print("❌ Phone OTP verification failed, stopping flow")
            return False
        
        # Step 4: Resend Email Verification (after phone OTP is confirmed)
        print("\n📋 Step 4: Resend Email Verification")
        print(f"   Phone OTP verified! Now resending email verification to {email}")
        email_resend_result = self.test_email_resend(email)
        if not email_resend_result.get("success"):
            print("❌ Email resend failed, stopping flow")
            return False
        
        # Step 5: Get Email OTP Code
        print("\n📋 Step 5: Enter Email OTP Code")
        print(f"   Email verification resent! Check your email {email} for the verification code")
        print(f"   Look for a 6-digit code (not a clickable link)")
        email_otp = input("   Enter email OTP code: ").strip()
        
        if not email_otp:
            print("❌ No email OTP code entered, stopping flow")
            return False
        
        # Step 6: Verify Email OTP
        print("\n📋 Step 6: Verify Email OTP")
        email_verify_result = self.test_verify_email_otp(email, email_otp)
        if not email_verify_result.get("success"):
            print("❌ Email OTP verification failed, stopping flow")
            return False
        
        # Step 7: Check Profile Status
        print("\n📋 Step 7: Check Profile Status")
        profile_status_result = self.test_profile_status()
        if not profile_status_result.get("success"):
            print("❌ Profile status check failed")
            return False
        
        # Step 8: Complete Profile (if not already completed)
        if not profile_status_result.get("profile_completed"):
            print("\n📋 Step 8: Complete Helper Profile")
            
            # Get existing profile info to use in payload
            print(f"   🔍 Querying existing profile information...")
            profile_info = self.get_profile_info(self.user_id)
            
            # Use existing profile data if available, otherwise use defaults
            if profile_info["type"] in ["helper", "client"] and profile_info["data"]:
                existing_data = profile_info["data"]
                profile_data = {
                    "first_name": existing_data.get("first_name", "Test"),
                    "last_name": existing_data.get("last_name", "Helper"),
                    "college": existing_data.get("college", "Tufts University"),
                    "bio": existing_data.get("bio", "This is a test helper account for testing purposes."),
                    "graduation_year": existing_data.get("graduation_year", 2025),
                    "zip_code": existing_data.get("zip_code", "02155"),
                    "pfp_url": existing_data.get("pfp_url")
                }
                print(f"   📋 Using existing profile data: {profile_data['first_name']} {profile_data['last_name']}")
            else:
                # Default profile data
                profile_data = {
                    "first_name": "Test",
                    "last_name": "Helper",
                    "college": "Tufts University",
                    "bio": "This is a test helper account for testing purposes.",
                    "graduation_year": 2025,
                    "zip_code": "02155",
                    "pfp_url": None
                }
                print(f"   📋 Using default profile data")
            
            profile_completion_result = self.test_helper_profile_completion(self.user_id, profile_data)
            if not profile_completion_result.get("success"):
                print("❌ Profile completion failed")
                return False
        else:
            print("\n📋 Step 8: Profile already completed, skipping")
        
        print("\n🎉 Complete helper signup flow test completed successfully!")
        print("   ✅ Phone OTP verified")
        print("   ✅ Email verification resent")
        print("   ✅ Email OTP verified") 
        print("   ✅ Profile completed")
        return True
    
    def test_individual_endpoints(self, email: str, phone: str) -> None:
        """Test individual helper endpoints"""
        print("🧪 Testing Individual Helper Endpoints")
        print("=" * 40)
        
        # Test helper signup
        print("\n📧 Testing Helper Signup Endpoint")
        self.test_helper_signup(email, phone)
        
        # Test Phone OTP verification (OTP was automatically sent during signup)
        print("\n🔐 Testing Helper Phone OTP Verification Endpoint")
        print(f"   Supabase automatically sent OTP to {phone} during signup")
        print(f"   Check your phone for the OTP code")
        phone_token = input("   Enter phone OTP code (or press Enter to skip): ").strip()
        
        if phone_token:
            phone_otp_result = self.test_helper_otp_verify(phone, phone_token)
            if phone_otp_result.get("success"):
                # Test email resend after phone OTP verification
                print("\n📧 Testing Email Resend Endpoint")
                print(f"   Phone OTP verified! Now resending email verification to {email}")
                email_resend_result = self.test_email_resend(email)
                if email_resend_result.get("success"):
                    # Test email OTP verification
                    print("\n📧 Testing Email OTP Verification Endpoint")
                    print(f"   Email verification resent! Check your email {email} for the verification code")
                    print(f"   Look for a 6-digit code (not a clickable link)")
                    email_otp = input("   Enter email OTP code (or press Enter to skip): ").strip()
                    
                    if email_otp:
                        email_otp_result = self.test_verify_email_otp(email, email_otp)
                        if email_otp_result.get("success"):
                            # Test profile status
                            print("\n📊 Testing Profile Status Endpoint")
                            self.test_profile_status()
                            
                            # Test profile completion
                            print("\n👤 Testing Helper Profile Completion Endpoint")
                
                # Get existing profile info to use in payload
                print(f"   🔍 Querying existing profile information...")
                profile_info = self.get_profile_info(self.user_id)
                
                # Use existing profile data if available, otherwise use defaults
                if profile_info["type"] in ["helper", "client"] and profile_info["data"]:
                    existing_data = profile_info["data"]
                    profile_data = {
                        "first_name": existing_data.get("first_name", "Test"),
                        "last_name": existing_data.get("last_name", "Helper"),
                        "college": existing_data.get("college", "Tufts University"),
                        "bio": existing_data.get("bio", "This is a test helper account for testing purposes."),
                        "graduation_year": existing_data.get("graduation_year", 2025),
                        "zip_code": existing_data.get("zip_code", "02155"),
                        "pfp_url": existing_data.get("pfp_url")
                    }
                    print(f"   📋 Using existing profile data: {profile_data['first_name']} {profile_data['last_name']}")
                else:
                    # Default profile data
                    profile_data = {
                        "first_name": "Test",
                        "last_name": "Helper",
                        "college": "Tufts University",
                        "bio": "This is a test helper account for testing purposes.",
                        "graduation_year": 2025,
                        "zip_code": "02155",
                        "pfp_url": None
                    }
                    print(f"   📋 Using default profile data")
                
                self.test_helper_profile_completion(self.user_id, profile_data)
        else:
            print("   ⏭️ Skipping OTP verification and subsequent tests")


def main():
    parser = argparse.ArgumentParser(description="Test helper signup flow")
    parser.add_argument("command", choices=["test-flow", "test-endpoints"], 
                       help="Test command to run")
    parser.add_argument("--email", default=TEST_HELPER_EMAIL,
                       help="Helper email for testing")
    parser.add_argument("--phone", default=TEST_HELPER_PHONE,
                       help="Helper phone for testing")
    
    args = parser.parse_args()
    
    # Create tester instance
    tester = HelperSignupTester(API_BASE_URL)
    
    if args.command == "test-flow":
        # Test complete flow
        success = tester.test_complete_flow(args.email, args.phone)
        if success:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    
    elif args.command == "test-endpoints":
        # Test individual endpoints
        tester.test_individual_endpoints(args.email, args.phone)
    
    print("\n🧪 Helper signup flow testing completed!")


if __name__ == "__main__":
    main()
