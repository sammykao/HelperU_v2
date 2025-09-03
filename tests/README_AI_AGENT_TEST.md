# AI Agent Test Scripts

This directory contains test scripts for testing the AI Agent functionality with client authentication.

## Test Scripts

### 1. `test_ai_agent_simple.py` (Recommended)
A simple, focused test script that covers the core AI agent functionality:
- Client authentication (sign in + OTP verification)
- Basic AI agent queries
- Task creation via AI agent
- Conversation continuity

### 2. `test_ai_agent_client.py`
A comprehensive test script with extensive testing:
- Full authentication flow
- Profile status verification
- Multiple AI agent query types
- Task management queries
- Helper search queries
- Extended conversation testing

## Prerequisites

1. **Server Running**: Make sure your FastAPI server is running on `http://localhost:8000`
2. **Dependencies**: Install required packages:
   ```bash
   pip install requests
   ```
3. **Phone Number**: The test uses `+16108883335` - make sure this is your client account

## Running the Tests

### Simple Test (Recommended)
```bash
cd tests
python test_ai_agent_simple.py
```

### Comprehensive Test
```bash
cd tests
python test_ai_agent_client.py
```

## Test Flow

### Step 1: Authentication
- Sends OTP to your phone number
- Prompts you to enter the OTP code
- Verifies the OTP and gets access token

### Step 2: AI Agent Testing
- Tests basic queries like "Hello, how can you help me?"
- Tests task-related queries like "What tasks have I posted?"
- Tests helper search queries like "Find helpers near me"

### Step 3: Task Creation
- Tests creating a task via AI agent
- Uses natural language to describe the task
- AI agent should route to task_agent and create the task

### Step 4: Conversation Continuity
- Tests maintaining conversation context
- Uses the same thread_id for multiple messages
- Tests progressive task creation workflow

## Expected Results

### Successful Test Output
```
🧪 Testing AI Agent with Client Authentication
==================================================

📱 Step 1: Sending OTP to +16108883335
   OTP Response Status: 200
   ✅ OTP sent successfully

📋 Step 2: Enter OTP Code
   Check your phone +16108883335 for the OTP code
   Enter OTP code: 123456

🔐 Step 3: Verifying OTP
   Verify Response Status: 200
   ✅ Authentication successful:
      User ID: your-user-id
      Access Token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

🤖 Step 4: Testing AI Agent Queries
   Query 1: Hello, how can you help me?
   AI Response Status: 200
   ✅ AI Agent Response:
      Response: Hello! I'm your HelperU AI assistant...
      Thread ID: thread-uuid
      Agent Used: faq_agent

📝 Step 5: Testing Task Creation via AI
   Task Description: I need help moving furniture...
   Task Creation Response Status: 200
   ✅ Task Creation Response:
      Response: I'll help you create a task for moving furniture...
      Thread ID: thread-uuid
      Agent Used: task_agent

🎉 AI Agent Test Complete!
   User ID: your-user-id
   Authentication: ✅ Success
   AI Agent: ✅ Tested
   Task Creation: ✅ Tested
   Conversation: ✅ Tested
```

### Common Issues

1. **Server Not Running**
   ```
   ❌ OTP Error: Connection refused
   ```
   Solution: Start your FastAPI server

2. **Invalid OTP**
   ```
   ❌ Failed to verify OTP
   ```
   Solution: Check your phone for the correct OTP code

3. **AI Agent Errors**
   ```
   ❌ AI Agent Error: 500 Internal Server Error
   ```
   Solution: Check server logs for AI agent configuration issues

4. **Authentication Issues**
   ```
   ❌ No access token received
   ```
   Solution: Verify your phone number and account status

## Configuration

### Environment Variables
- `API_BASE_URL`: Base URL for the API (default: `http://localhost:8000`)

### Customization
You can modify the test scripts to:
- Use a different phone number
- Test different queries
- Add more comprehensive testing scenarios
- Test helper account functionality

## Troubleshooting

### Server Issues
1. Check if the server is running: `curl http://localhost:8000/health`
2. Check server logs for errors
3. Verify all dependencies are installed

### Authentication Issues
1. Verify the phone number is correct
2. Check if the account exists in the database
3. Verify OTP delivery (check phone/SMS)

### AI Agent Issues
1. Check if all AI agent dependencies are installed
2. Verify OpenAI API key is configured
3. Check LangGraph and LangChain versions
4. Review server logs for AI agent errors

## Next Steps

After successful testing:
1. Test with different user types (helper, dual-role)
2. Test edge cases and error scenarios
3. Test performance with multiple concurrent requests
4. Test conversation memory and persistence
5. Test task creation with various parameters
