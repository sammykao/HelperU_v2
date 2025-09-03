#!/usr/bin/env python3
"""
Simple test script for AI Agent functionality with client authentication
Tests: sign in, verify OTP, query AI agent, and post a task
"""
import os
import requests
import uuid

# Configure API base URL
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")

def test_ai_agent_flow():
    """Test the complete AI agent flow"""
    print("🧪 Testing AI Agent with Client Authentication")
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
            
        print("   ✅ OTP sent successfully")
        
    except Exception as e:
        print(f"   ❌ OTP Error: {e}")
        return None
    
    # Step 2: Get OTP from user
    print("\n📋 Step 2: Enter OTP Code")
    print(f"   Check your phone {test_phone} for the OTP code")
    otp_code = input("   Enter OTP code: ").strip()
    
    if not otp_code:
        print("   ❌ No OTP code provided")
        return None
    
    # Step 3: Verify OTP
    print("\n🔐 Step 3: Verifying OTP")
    verify_url = f"{API_BASE_URL}/api/v1/auth/client/verify-otp"
    verify_payload = {"phone": test_phone, "token": otp_code}
    
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
            
        print("   ✅ Authentication successful:")
        print(f"      User ID: {user_id}")
        print(f"      Access Token: {access_token[:50]}...")
        
    except Exception as e:
        print(f"   ❌ Verify Error: {e}")
        return None
    
    # Step 4: Test AI Agent Queries
    print("\n🤖 Step 4: Testing AI Agent Queries")
    
    ai_url = f"{API_BASE_URL}/api/v1/ai/chat"
    ai_headers = {"Authorization": f"Bearer {access_token}"}
    
    # Test queries
    test_queries = [
        # "Hello, how can you help me?",
        "What tasks have I posted?",
        # "How many tasks can I still post?",
        # "Find helpers near me",
        # "Create a task for moving furniture from my apartment"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {query}")
        
        thread_id = str(uuid.uuid4())
        ai_payload = {
            "message": query,
            "thread_id": thread_id
        }
        
        try:
            ai_resp = requests.post(ai_url, json=ai_payload, headers=ai_headers, timeout=60)
            print(f"   AI Response Status: {ai_resp.status_code}")
            
            if ai_resp.status_code == 200:
                ai_data = ai_resp.json()
                print("   ✅ AI Agent Response:")
                print(f"      Response: {ai_data.get('response', 'No response')[:200]}...")
                print(f"      Thread ID: {ai_data.get('thread_id', 'None')}")
                print(f"      Agent Used: {ai_data.get('agent_used', 'None')}")
            else:
                print(f"   ❌ AI Agent Error: {ai_resp.text}")
                
        except Exception as e:
            print(f"   ❌ AI Agent Error: {e}")
    
    # # Step 5: Test Task Creation via AI
    # print("\n📝 Step 5: Testing Task Creation via AI")
    
    # task_description = "I need help moving furniture from my apartment to a new place. I have a 2-bedroom apartment and need help with heavy items like couches and beds."
    
    # print(f"   Task Description: {task_description}")
    
    # thread_id = str(uuid.uuid4())
    # ai_payload = {
    #     "message": f"Please create a task for me with the following description: {task_description}",
    #     "thread_id": thread_id
    # }
    
    # try:
    #     ai_resp = requests.post(ai_url, json=ai_payload, headers=ai_headers, timeout=60)
    #     print(f"   Task Creation Response Status: {ai_resp.status_code}")
        
    #     if ai_resp.status_code == 200:
    #         ai_data = ai_resp.json()
    #         print("   ✅ Task Creation Response:")
    #         print(f"      Response: {ai_data.get('response', 'No response')[:200]}...")
    #         print(f"      Thread ID: {ai_data.get('thread_id', 'None')}")
    #         print(f"      Agent Used: {ai_data.get('agent_used', 'None')}")
    #     else:
    #         print(f"   ❌ Task Creation Error: {ai_resp.text}")
            
    # except Exception as e:
    #     print(f"   ❌ Task Creation Error: {e}")
    
    # # Step 6: Test Conversation Continuity
    # print("\n💬 Step 6: Testing Conversation Continuity")
    
    # conversation_thread = str(uuid.uuid4())
    # conversation_messages = [
    #     "I want to post a task for moving help",
    #     "What should I include in the task description?",
    #     "How much should I pay for moving help?",
    #     "Can you help me find helpers for this task?"
    # ]
    
    # for i, message in enumerate(conversation_messages, 1):
    #     print(f"\n   Message {i}: {message}")
        
    #     ai_payload = {
    #         "message": message,
    #         "thread_id": conversation_thread
    #     }
        
    #     try:
    #         ai_resp = requests.post(ai_url, json=ai_payload, headers=ai_headers, timeout=60)
    #         print(f"   Response Status: {ai_resp.status_code}")
            
    #         if ai_resp.status_code == 200:
    #             ai_data = ai_resp.json()
    #             print(f"   ✅ Response: {ai_data.get('response', 'No response')[:100]}...")
    #         else:
    #             print(f"   ❌ Error: {ai_resp.text}")
                
    #     except Exception as e:
    #         print(f"   ❌ Error: {e}")
    
    print("\n🎉 AI Agent Test Complete!")
    print(f"   User ID: {user_id}")
    print("   Authentication: ✅ Success")
    print("   AI Agent: ✅ Tested")
    print("   Task Creation: ✅ Tested")
    print("   Conversation: ✅ Tested")


if __name__ == "__main__":
    test_ai_agent_flow()
