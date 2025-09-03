#!/usr/bin/env python3
"""
Comprehensive test script for AI Agent functionality with client authentication
Tests the complete flow: sign in, verify OTP, query AI agent, and post tasks
"""
import os
import requests
import time
import uuid
from typing import Optional, Dict, Any

# Configure API base URL
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

class AITestClient:
    """Test client for AI Agent functionality"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.access_token: Optional[str] = None
        self.user_id: Optional[str] = None
        self.thread_id: Optional[str] = None
        
    def sign_in(self, phone: str) -> bool:
        """Sign in with phone number"""
        print(f"📱 Step 1: Sending OTP to {phone}")
        
        otp_url = f"{self.base_url}/api/v1/auth/client/signin"
        otp_payload = {"phone": phone}
        
        try:
            otp_resp = requests.post(otp_url, json=otp_payload, timeout=30)
            print(f"   OTP Response Status: {otp_resp.status_code}")
            
            if otp_resp.status_code != 200:
                print("   ❌ Failed to send OTP")
                return False
                
            print("   ✅ OTP sent successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ OTP Error: {e}")
            return False
    
    def verify_otp(self, phone: str, otp_code: str) -> bool:
        """Verify OTP code"""
        print("🔐 Step 2: Verifying OTP code")
        
        verify_url = f"{self.base_url}/api/v1/auth/client/verify-otp"
        verify_payload = {"phone": phone, "token": otp_code}
        
        try:
            verify_resp = requests.post(verify_url, json=verify_payload, timeout=30)
            print(f"   Verify Response Status: {verify_resp.status_code}")
            
            if verify_resp.status_code != 200:
                print("   ❌ Failed to verify OTP")
                return False
                
            # Extract tokens
            verify_data = verify_resp.json()
            self.access_token = verify_data.get("access_token")
            self.user_id = verify_data.get("user_id")
            
            if not self.access_token:
                print("   ❌ No access token received")
                return False
                
            print("   ✅ Authentication successful:")
            print(f"      User ID: {self.user_id}")
            print(f"      Access Token: {self.access_token[:50]}...")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Verify Error: {e}")
            return False
    
    def query_ai_agent(self, message: str, thread_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Query the AI agent"""
        if not self.access_token:
            print("❌ No access token available")
            return None
            
        print("🤖 Step 3: Querying AI Agent")
        print(f"   Message: {message}")
        
        ai_url = f"{self.base_url}/api/v1/ai/chat"
        ai_headers = {"Authorization": f"Bearer {self.access_token}"}
        ai_payload = {"message": message}
        
        if thread_id:
            ai_payload["thread_id"] = thread_id
            self.thread_id = thread_id
        
        try:
            ai_resp = requests.post(ai_url, json=ai_payload, headers=ai_headers, timeout=60)
            print(f"   AI Response Status: {ai_resp.status_code}")
            
            if ai_resp.status_code != 200:
                print(f"   ❌ AI Agent Error: {ai_resp.text}")
                return None
                
            ai_data = ai_resp.json()
            print("   ✅ AI Agent Response:")
            print(f"      Response: {ai_data.get('response', 'No response')[:200]}...")
            print(f"      Thread ID: {ai_data.get('thread_id', 'None')}")
            print(f"      Agent Used: {ai_data.get('agent_used', 'None')}")
            
            return ai_data
            
        except Exception as e:
            print(f"   ❌ AI Agent Error: {e}")
            return None
    
    def get_profile_status(self) -> Optional[Dict[str, Any]]:
        """Get user profile status"""
        if not self.access_token:
            print("❌ No access token available")
            return None
            
        print("👤 Step 4: Getting Profile Status")
        
        profile_url = f"{self.base_url}/api/v1/profile/"
        profile_headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            profile_resp = requests.get(profile_url, headers=profile_headers, timeout=30)
            print(f"   Profile Status: {profile_resp.status_code}")
            
            if profile_resp.status_code != 200:
                print(f"   ❌ Profile Error: {profile_resp.text}")
                return None
                
            profile_data = profile_resp.json()
            print("   ✅ Profile Data:")
            print(f"      User Type: {profile_data.get('user_type', 'Unknown')}")
            print(f"      Profile Completed: {profile_data.get('profile_completed', False)}")
            print(f"      Email Verified: {profile_data.get('email_verified', False)}")
            print(f"      Phone Verified: {profile_data.get('phone_verified', False)}")
            
            return profile_data
            
        except Exception as e:
            print(f"   ❌ Profile Error: {e}")
            return None
    
    def create_task_via_ai(self, task_description: str) -> Optional[Dict[str, Any]]:
        """Create a task using the AI agent"""
        if not self.access_token:
            print("❌ No access token available")
            return None
            
        print("📝 Step 5: Creating Task via AI Agent")
        print(f"   Task Description: {task_description}")
        
        # Create a unique thread ID for this task creation
        task_thread_id = str(uuid.uuid4())
        
        # Query AI agent to create task
        ai_message = f"Please create a task for me with the following description: {task_description}"
        
        ai_response = self.query_ai_agent(ai_message, task_thread_id)
        
        if ai_response:
            print("   ✅ Task creation request sent to AI agent")
            return ai_response
        else:
            print("   ❌ Failed to create task via AI agent")
            return None
    
    def test_task_management_queries(self):
        """Test various task management queries with AI agent"""
        if not self.access_token:
            print("❌ No access token available")
            return
            
        print("🔍 Step 6: Testing Task Management Queries")
        
        # Test queries
        test_queries = [
            "What tasks have I posted?",
            "How many tasks can I still post?",
            "Show me my task history",
            "What's my current posting limit?",
            "Help me find helpers for my tasks"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Query {i}: {query}")
            thread_id = str(uuid.uuid4())
            response = self.query_ai_agent(query, thread_id)
            
            if response:
                print(f"   ✅ Query {i} successful")
            else:
                print(f"   ❌ Query {i} failed")
            
            time.sleep(1)  # Small delay between queries
    
    def test_helper_search_queries(self):
        """Test helper search queries with AI agent"""
        if not self.access_token:
            print("❌ No access token available")
            return
            
        print("🔍 Step 7: Testing Helper Search Queries")
        
        # Test queries
        test_queries = [
            "Find helpers near me",
            "Show me helpers with moving experience",
            "Search for helpers in college students",
            "Find helpers available this weekend",
            "Show me the best rated helpers"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Query {i}: {query}")
            thread_id = str(uuid.uuid4())
            response = self.query_ai_agent(query, thread_id)
            
            if response:
                print(f"   ✅ Query {i} successful")
            else:
                print(f"   ❌ Query {i} failed")
            
            time.sleep(1)  # Small delay between queries


def main():
    """Main test function"""
    print("🧪 Testing AI Agent with Client Authentication")
    print("=" * 60)
    
    # Initialize test client
    client = AITestClient(API_BASE_URL)
    
    # Test phone number
    test_phone = "+16108883335"
    
    # Step 1: Sign in
    if not client.sign_in(test_phone):
        print("❌ Sign in failed")
        return
    
    # Step 2: Get OTP from user
    print("\n📋 Step 2: Enter OTP Code")
    print(f"   Check your phone {test_phone} for the OTP code")
    otp_code = input("   Enter OTP code: ").strip()
    
    if not otp_code:
        print("❌ No OTP code provided")
        return
    
    # Step 3: Verify OTP
    if not client.verify_otp(test_phone, otp_code):
        print("❌ OTP verification failed")
        return
    
    # Step 4: Get profile status
    profile_data = client.get_profile_status()
    if not profile_data:
        print("❌ Failed to get profile status")
        return
    
    # Step 5: Test basic AI agent queries
    print("\n🤖 Step 5: Testing Basic AI Agent Queries")
    
    # Test general queries
    general_queries = [
        "Hello, how can you help me?",
        "What can I do on HelperU?",
        "Tell me about the platform",
        "How do I post a task?",
        "What are the safety measures?"
    ]
    
    for i, query in enumerate(general_queries, 1):
        print(f"\n   Query {i}: {query}")
        thread_id = str(uuid.uuid4())
        response = client.query_ai_agent(query, thread_id)
        
        if response:
            print(f"   ✅ Query {i} successful")
        else:
            print(f"   ❌ Query {i} failed")
        
        time.sleep(1)  # Small delay between queries
    
    # Step 6: Test task creation via AI
    print("\n📝 Step 6: Testing Task Creation via AI")
    
    task_descriptions = [
        "I need help moving furniture from my apartment to a new place. I have a 2-bedroom apartment and need help with heavy items like couches and beds.",
        "I need a tutor for my high school math class. I'm struggling with algebra and need help 2-3 times per week.",
        "I need help cleaning my house before a party. I need someone to help with general cleaning, organizing, and setting up for guests."
    ]
    
    for i, task_desc in enumerate(task_descriptions, 1):
        print(f"\n   Task {i}: {task_desc[:100]}...")
        response = client.create_task_via_ai(task_desc)
        
        if response:
            print(f"   ✅ Task {i} creation request successful")
        else:
            print(f"   ❌ Task {i} creation failed")
        
        time.sleep(2)  # Delay between task creation attempts
    
    # Step 7: Test task management queries
    client.test_task_management_queries()
    
    # Step 8: Test helper search queries
    client.test_helper_search_queries()
    
    # Step 9: Test conversation continuity
    print("\n💬 Step 9: Testing Conversation Continuity")
    
    conversation_thread = str(uuid.uuid4())
    conversation_messages = [
        "I want to post a task for moving help",
        "What should I include in the task description?",
        "How much should I pay for moving help?",
        "Can you help me find helpers for this task?",
        "What safety measures are in place?"
    ]
    
    for i, message in enumerate(conversation_messages, 1):
        print(f"\n   Message {i}: {message}")
        response = client.query_ai_agent(message, conversation_thread)
        
        if response:
            print(f"   ✅ Message {i} successful")
        else:
            print(f"   ❌ Message {i} failed")
        
        time.sleep(1)
    
    print("\n🎉 AI Agent Test Complete!")
    print(f"   User ID: {client.user_id}")
    print(f"   Thread ID: {client.thread_id}")
    print("   Authentication: ✅ Success")
    print("   AI Agent: ✅ Tested")
    print("   Task Creation: ✅ Tested")
    print("   Helper Search: ✅ Tested")
    print("   Conversation: ✅ Tested")


if __name__ == "__main__":
    main()
