# HelperU AI Agent System

A comprehensive multi-agent LangGraph routing architecture with MCP tools for the HelperU backend platform.

## 🚀 Overview

The HelperU AI Agent System provides an intelligent, scalable architecture for handling complex business workflows through specialized AI agents. Each agent is equipped with MCP (Model Context Protocol) tools that wrap your existing service functions, enabling seamless integration with your backend services.

## 🏗️ Architecture

### Core Components

- **Agent System**: Central coordinator for all AI agents
- **Agent Router**: Intelligent routing system for requests
- **MCP Tools**: Wrappers around your service functions
- **LangGraph Workflows**: Complex multi-step business processes
- **Specialized Agents**: Domain-specific AI assistants

### Agent Types

1. **Task Manager Agent** - Manages task creation, updates, and workflows
2. **User Assistant Agent** - General user support and account management
3. **Application Processor Agent** - Handles helper applications and reviews
4. **Chat Moderator Agent** - Moderates chat interactions and disputes
5. **Payment Processor Agent** - Manages payments and subscriptions
6. **Notification Coordinator Agent** - Coordinates notifications across platforms

## 🛠️ Features

- **Intelligent Routing**: Automatically routes requests to appropriate agents
- **MCP Integration**: All service functions wrapped as MCP tools
- **LangGraph Workflows**: Complex business processes with state management
- **Memory Management**: Conversation history and context preservation
- **Error Handling**: Robust error handling and recovery
- **Monitoring**: Comprehensive system status and health monitoring
- **Async Support**: Full async/await support for high performance

## 📦 Installation

### Prerequisites

- Python 3.11+
- OpenAI API key
- HelperU backend services

### Setup

1. **Install dependencies**:
```bash
pip install -r ai_agent/requirements.txt
```

2. **Set environment variables**:
```bash
export OPENAI_API_KEY="your_openai_api_key"
export SUPABASE_URL="your_supabase_url"
export SUPABASE_SERVICE_ROLE_KEY="your_supabase_key"
```

3. **Configure the system**:
```python
from ai_agent.config import load_config
config = load_config()
```

## 🚀 Quick Start

### Basic Usage

```python
import asyncio
from ai_agent.system import AgentSystem
from ai_agent.router import AgentRouter
from ai_agent.config import load_config

async def main():
    # Initialize the system
    config = load_config()
    agent_system = AgentSystem(config)
    
    # Create router
    router = AgentRouter(agent_system)
    
    # Route a request
    result = await router.route_request(
        user_message="I need help creating a new task",
        user_id="user_123"
    )
    
    print(result)

# Run
asyncio.run(main())
```

### Direct Agent Calls

```python
# Call a specific agent directly
result = await router.execute_direct_agent_call(
    agent_id="task_manager",
    message="Create a task for house cleaning",
    user_id="user_123"
)
```

### Workflow Execution

```python
# Execute a complex workflow
result = await router.route_request(
    user_message="Create a new task",
    user_id="user_123",
    workflow_type="task_creation",
    context={
        "task_data": {
            "title": "House Cleaning",
            "description": "3-bedroom house cleaning",
            "hourly_rate": 25.0,
            "zip_code": "12345"
        }
    }
)
```

## 🔧 MCP Tools

### Available Tool Categories

- **Authentication Tools**: OTP, signup, profile management
- **Task Tools**: Create, update, search, complete tasks
- **Chat Tools**: Chat management, messaging, moderation
- **Profile Tools**: User profile management
- **Application Tools**: Helper application processing
- **Payment Tools**: Subscription and payment management
- **Notification Tools**: SMS, email, and push notifications

### Tool Registration

```python
from ai_agent.tools import register_auth_tools, register_task_tools

# Register tools with your services
register_auth_tools(auth_service)
register_task_tools(task_service)
```

## 🔄 LangGraph Workflows

### Available Workflows

1. **Task Creation Workflow**
   - Input validation
   - Task creation
   - Helper notification
   - Finalization

2. **Application Review Workflow**
   - Application fetching
   - Qualification evaluation
   - Reference checking
   - Decision making
   - Result notification

3. **Dispute Resolution Workflow**
   - Dispute assessment
   - Evidence gathering
   - Mediation
   - Resolution proposal
   - Implementation

### Custom Workflows

```python
from ai_agent.workflows.base import BaseWorkflow
from langgraph.graph import StateGraph, END

class CustomWorkflow(BaseWorkflow):
    def build_graph(self) -> StateGraph:
        workflow = StateGraph(WorkflowState)
        
        # Add your workflow nodes and edges
        workflow.add_node("step1", self._step1)
        workflow.add_node("step2", self._step2)
        workflow.add_edge("step1", "step2")
        workflow.add_edge("step2", END)
        
        return workflow
```

## 🎯 Agent Configuration

### Agent Settings

```python
from ai_agent.config import AgentConfig

custom_agent = AgentConfig(
    name="Custom Agent",
    description="Custom agent for specific tasks",
    model="gpt-4",
    temperature=0.1,
    max_tokens=4000,
    tools=["tool1", "tool2"],
    memory_enabled=True
)
```

### System Configuration

```python
from ai_agent.config import AgentSystemConfig

config = AgentSystemConfig(
    agents=DEFAULT_AGENTS,
    openai_api_key="your_key",
    langgraph=LangGraphConfig(
        max_iterations=25,
        debug=True,
        stream=True
    )
)
```

## 📊 Monitoring & Status

### System Status

```python
# Get comprehensive system status
status = router.get_system_status()

print(f"System: {status['agent_system']['system']}")
print(f"Agents: {len(status['agent_system']['agents'])}")
print(f"Tools: {status['agent_system']['tools']['total_registered']}")
print(f"Workflows: {len(status['workflows'])}")
```

### Agent Status

```python
# Get specific agent status
agent = agent_system.get_agent("task_manager")
memory_summary = agent.get_memory_summary()
print(f"Conversations: {memory_summary['conversation_count']}")
```

## 🔒 Security & Best Practices

### Security Features

- **Input Validation**: All inputs validated through Pydantic schemas
- **Error Handling**: Comprehensive error handling and logging
- **Memory Management**: Configurable memory limits and cleanup
- **Service Injection**: Secure service dependency injection

### Best Practices

1. **Always validate user input** before processing
2. **Use appropriate agent temperatures** for different use cases
3. **Implement proper error handling** in custom workflows
4. **Monitor system performance** and agent memory usage
5. **Regularly update agent prompts** based on user feedback

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest ai_agent/tests/

# Run specific test categories
pytest ai_agent/tests/test_agents.py
pytest ai_agent/tests/test_workflows.py
```

### Example Test

```python
import pytest
from ai_agent.system import AgentSystem

@pytest.mark.asyncio
async def test_agent_system_initialization():
    config = load_config()
    system = AgentSystem(config)
    
    assert len(system.agents) > 0
    assert system.openai_client is not None
```

## 🚀 Performance & Scaling

### Performance Tips

- **Use appropriate model sizes** for different tasks
- **Implement caching** for frequently accessed data
- **Monitor token usage** and optimize prompts
- **Use async operations** for I/O-bound tasks

### Scaling Considerations

- **Horizontal scaling** through multiple agent instances
- **Load balancing** for high-traffic scenarios
- **Database connection pooling** for service tools
- **Redis caching** for workflow state management

## 🔧 Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Check API key validity
   - Verify rate limits
   - Check API endpoint configuration

2. **Tool Registration Errors**
   - Ensure services are properly injected
   - Check tool schema definitions
   - Verify service method signatures

3. **Workflow Execution Errors**
   - Check workflow state definitions
   - Verify node implementations
   - Review error handling logic

### Debug Mode

```python
# Enable debug mode
config = AgentSystemConfig(
    langgraph=LangGraphConfig(debug=True)
)
```

## 📚 API Reference

### Core Classes

- `AgentSystem`: Main system coordinator
- `AgentRouter`: Request routing and workflow management
- `BaseAgent`: Base class for all agents
- `BaseWorkflow`: Base class for all workflows
- `BaseMCPTool`: Base class for all MCP tools

### Key Methods

- `route_request()`: Route requests to appropriate agents
- `execute_direct_agent_call()`: Direct agent communication
- `run()`: Execute LangGraph workflows
- `process_message()`: Process messages with agents

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints throughout
- Add comprehensive docstrings
- Include error handling

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Getting Help

- Check the documentation
- Review example code
- Open an issue on GitHub
- Contact the development team

### Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [MCP Protocol](https://modelcontextprotocol.io/)
- [HelperU Backend](https://github.com/your-org/helperu-backend)

---

**Built with ❤️ for the HelperU platform**
