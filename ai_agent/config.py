"""
Configuration for AI Agent System
"""
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import os


class AgentConfig(BaseModel):
    """Configuration for individual agents"""
    name: str
    description: str
    model: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 4000
    tools: list[str] = Field(default_factory=list)
    memory_enabled: bool = True
    max_memory_items: int = 10


class LangGraphConfig(BaseModel):
    """Configuration for LangGraph system"""
    max_iterations: int = 25
    interrupt_before: list[str] = Field(default_factory=list)
    interrupt_after: list[str] = Field(default_factory=list)
    debug: bool = False
    stream: bool = True


class MCPConfig(BaseModel):
    """Configuration for MCP tools"""
    tools_dir: str = "tools"
    auto_discover: bool = True
    validate_schemas: bool = True
    timeout: int = 30


class AgentSystemConfig(BaseModel):
    """Main configuration for the agent system"""
    agents: Dict[str, AgentConfig]
    langgraph: LangGraphConfig = Field(default_factory=LangGraphConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    openai_api_key: Optional[str] = None
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None


# Default agent configurations
DEFAULT_AGENTS = {
    "task_manager": AgentConfig(
        name="Task Manager",
        description="Manages task creation, updates, and workflow coordination",
        tools=["task_create", "task_update", "task_search", "task_delete"],
        temperature=0.1
    ),
    "user_assistant": AgentConfig(
        name="User Assistant", 
        description="Helps users with general queries and account management",
        tools=["user_profile", "account_info", "help_search"],
        temperature=0.3
    ),
    "application_processor": AgentConfig(
        name="Application Processor",
        description="Processes and evaluates helper applications",
        tools=["application_review", "application_status", "helper_verify"],
        temperature=0.1
    ),
    "chat_moderator": AgentConfig(
        name="Chat Moderator",
        description="Moderates chat interactions and handles disputes",
        tools=["chat_monitor", "message_filter", "user_warn"],
        temperature=0.2
    ),
    "payment_processor": AgentConfig(
        name="Payment Processor",
        description="Handles payment processing and subscription management",
        tools=["payment_process", "subscription_manage", "refund_handle"],
        temperature=0.1
    ),
    "notification_coordinator": AgentConfig(
        name="Notification Coordinator",
        description="Coordinates and sends notifications across platforms",
        tools=["sms_send", "email_send", "push_notify"],
        temperature=0.2
    )
}


def load_config() -> AgentSystemConfig:
    """Load configuration from environment and defaults"""
    return AgentSystemConfig(
        agents=DEFAULT_AGENTS,
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
        langgraph=LangGraphConfig(
            debug=os.getenv("LANGGRAPH_DEBUG", "false").lower() == "true"
        )
    )
