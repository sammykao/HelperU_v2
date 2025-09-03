# Simple AI Agent Chat Test

A simple interactive test script where you can type messages endlessly and get responses from the AI agent.

## Quick Start

1. **Make sure your API server is running:**
   ```bash
   # In your main project directory
   python -m app.main
   ```

2. **Run the simple chat test:**
   ```bash
   # In the tests directory
   python simple_chat_test.py
   ```

3. **Follow the prompts:**
   - Enter your phone number (e.g., `+16108883335`)
   - Check your phone for the OTP code
   - Enter the OTP code
   - Start chatting!

## Features

- **Endless Chat**: Type messages continuously without stopping
- **Conversation Memory**: Maintains conversation context across messages
- **Simple Commands**: Use special commands for different actions
- **Error Handling**: Graceful error handling and recovery
- **Re-authentication**: Re-authenticate if needed during the session

## Available Commands

- **Any message**: Send to AI agent and get response
- **`auth`**: Re-authenticate with new phone/OTP
- **`help`**: Show available commands
- **`quit`, `exit`, `q`**: End the chat session
- **`clear`**: Clear the terminal screen

## Example Usage

```
🤖 Simple AI Agent Chat Test
==================================================
Type 'quit' or 'exit' to end the chat
Type 'auth' to re-authenticate
Type 'help' for available commands
==================================================

🔐 Initial Authentication Required
Enter your phone number (e.g., +16108883335): +16108883335
📱 OTP sent to +16108883335
Enter OTP code: 123456
✅ Authentication successful!
   User ID: 123e4567-e89b-12d3-a456-426614174000

✅ Ready to chat! Type your messages below:
--------------------------------------------------

💬 You: Hello! How can you help me?
🤖 AI: Hello! I'm your AI assistant on HelperU. I can help you with...

💬 You: I want to post a task for moving help
🤖 AI: I'd be happy to help you create a task for moving assistance...

💬 You: What should I include in the task description?
🤖 AI: When creating a moving task, it's helpful to include...

💬 You: quit
👋 Goodbye!
```

## Troubleshooting

### Authentication Issues
- Make sure your phone number is in the correct format (`+1XXXXXXXXXX`)
- Check that you received the OTP code
- If authentication fails, try the `auth` command to re-authenticate

### API Connection Issues
- Ensure your API server is running on `http://localhost:8000`
- Check that the server is accessible
- Verify your environment variables are set correctly

### AI Agent Issues
- If the AI agent doesn't respond, try sending a simple message first
- Check the server logs for any errors
- Restart the chat session if needed

## Environment Variables

The script uses these environment variables:
- `API_BASE_URL`: Base URL for the API (default: `http://localhost:8000`)

You can set them before running:
```bash
export API_BASE_URL="http://localhost:8000"
python simple_chat_test.py
```

## File Structure

```
tests/
├── simple_chat_test.py      # Main chat test script
├── README_SIMPLE_CHAT.md    # This file
└── test_ai_agent_client.py  # Comprehensive test (original)
```

## Differences from Comprehensive Test

The simple chat test is designed for:
- **Quick testing**: No complex setup required
- **Interactive use**: Type messages continuously
- **Debugging**: Easy to test specific scenarios
- **Development**: Fast feedback during development

The comprehensive test (`test_ai_agent_client.py`) is better for:
- **Automated testing**: Pre-defined test scenarios
- **Regression testing**: Consistent test cases
- **Feature validation**: Testing specific features
- **CI/CD**: Automated test runs
