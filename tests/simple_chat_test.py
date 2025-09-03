#!/usr/bin/env python3
"""
Simple interactive chat test for AI Agent
Type messages endlessly and get responses from the AI agent
"""
import os
import requests
from typing import Optional

# Configure API base URL
API_BASE_URL = "http://localhost:8000"
DEBUG_MODE = os.environ.get("DEBUG_MODE", "false").lower() == "true"

class SimpleChatClient:
    """Simple chat client for endless message testing"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.thread_id: Optional[str] = None
        
    def send_otp(self, phone: str) -> bool:
        """Send OTP to phone number"""
        print(f"📱 Sending OTP to {phone}")
        
        otp_url = f"{self.base_url}/api/v1/auth/client/signin"
        otp_payload = {"phone": phone}
        
        if DEBUG_MODE:
            print(f"   Debug: URL: {otp_url}")
            print(f"   Debug: Payload: {otp_payload}")
        
        try:
            otp_resp = requests.post(otp_url, json=otp_payload, timeout=30)
            print(f"   OTP Response Status: {otp_resp.status_code}")
            
            if DEBUG_MODE:
                print(f"   Debug: Response Headers: {dict(otp_resp.headers)}")
                print(f"   Debug: Response Body: {otp_resp.text}")
            
            if otp_resp.status_code != 200:
                print(f"   ❌ Failed to send OTP: {otp_resp.text}")
                return False
                
            print("   ✅ OTP sent successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ OTP Error: {e}")
            if DEBUG_MODE:
                import traceback
                print(f"   Debug: Full traceback: {traceback.format_exc()}")
            return False
    
    def verify_otp(self, phone: str, otp_code: str) -> bool:
        """Verify OTP code"""
        print("🔐 Verifying OTP code")
        
        verify_url = f"{self.base_url}/api/v1/auth/client/verify-otp"
        verify_payload = {"phone": phone, "token": otp_code}
        
        try:
            verify_resp = requests.post(verify_url, json=verify_payload, timeout=30)
            print(f"   Verify Response Status: {verify_resp.status_code}")
            
            if verify_resp.status_code != 200:
                print(f"   ❌ Failed to verify OTP: {verify_resp.text}")
                return False
                
            verify_data = verify_resp.json()
            self.access_token = verify_data.get("access_token")
            self.user_id = verify_data.get("user_id")
            
            if not self.access_token:
                print("   ❌ No access token received")
                return False
                
            print("   ✅ Authentication successful!")
            print(f"      User ID: {self.user_id}")
            return True
            
        except Exception as e:
            print(f"   ❌ Verify Error: {e}")
            return False
    
    def authenticate(self, phone: str, otp_code: str) -> bool:
        """Authenticate with phone and OTP"""
        print(f"🔐 Authenticating with phone: {phone}")
        
        # Step 1: Send OTP
        if not self.send_otp(phone):
            return False
        
        # Step 2: Verify OTP
        return self.verify_otp(phone, otp_code)
    
    def send_message(self, message: str) -> Optional[str]:
        """Send a message to the AI agent and get response"""
        if not self.access_token:
            print("❌ Not authenticated. Please authenticate first.")
            return None
            
        ai_url = f"{self.base_url}/api/v1/ai/chat"
        ai_headers = {"Authorization": f"Bearer {self.access_token}"}
        ai_payload = {"message": message}
        
        if self.thread_id:
            ai_payload["thread_id"] = self.thread_id
        
        try:
            ai_resp = requests.post(ai_url, json=ai_payload, headers=ai_headers, timeout=60)
            
            if ai_resp.status_code != 200:
                print(f"❌ AI Agent Error: {ai_resp.text}")
                return None
                
            ai_data = ai_resp.json()
            response = ai_data.get('response', 'No response')
            self.thread_id = ai_data.get('thread_id', self.thread_id)
            
            return response
            
        except Exception as e:
            print(f"❌ AI Agent Error: {e}")
            return None

def main():
    """Main interactive chat function"""
    print("🤖 Simple AI Agent Chat Test")
    print("=" * 50)
    print("Type 'quit' or 'exit' to end the chat")
    print("Type 'auth' to re-authenticate")
    print("Type 'help' for available commands")
    print("=" * 50)
    
    client = SimpleChatClient(API_BASE_URL)
    
    # Initial authentication
    print("\n🔐 Initial Authentication Required")
    phone = input("Enter your phone number (e.g., +16108883335): ").strip()
    
    if not phone:
        print("❌ No phone number provided")
        return
    
    # Send OTP
    if not client.send_otp(phone):
        print("❌ Failed to send OTP")
        return
    
    # Get OTP code from user
    otp_code = input("Enter OTP code from your phone: ").strip()
    
    if not otp_code:
        print("❌ No OTP code provided")
        return
    
    # Verify OTP
    if not client.verify_otp(phone, otp_code):
        print("❌ Authentication failed")
        return
    
    print("\n✅ Ready to chat! Type your messages below:")
    print("-" * 50)
    
    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            # Handle special commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'auth':
                print("\n🔐 Re-authenticating...")
                phone = input("Enter your phone number: ").strip()
                
                if not phone:
                    print("❌ No phone number provided")
                    continue
                
                # Send OTP
                if not client.send_otp(phone):
                    print("❌ Failed to send OTP")
                    continue
                
                # Get OTP code from user
                otp_code = input("Enter OTP code from your phone: ").strip()
                
                if not otp_code:
                    print("❌ No OTP code provided")
                    continue
                
                # Verify OTP
                if client.verify_otp(phone, otp_code):
                    print("✅ Re-authentication successful!")
                else:
                    print("❌ Re-authentication failed")
                continue
            elif user_input.lower() == 'help':
                print("\n📋 Available Commands:")
                print("  - Type any message to chat with AI")
                print("  - 'auth' - Re-authenticate")
                print("  - 'help' - Show this help")
                print("  - 'quit', 'exit', 'q' - End chat")
                print("  - 'clear' - Clear screen")
                continue
            elif user_input.lower() == 'clear':
                os.system('cls' if os.name == 'nt' else 'clear')
                continue
            elif not user_input:
                continue
            
            # Send message to AI agent
            print("🤖 AI: ", end="", flush=True)
            response = client.send_message(user_input)
            
            if response:
                print(response)
            else:
                print("❌ Failed to get response from AI agent")
                
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Type 'quit' to exit or continue chatting...")

if __name__ == "__main__":
    main()
