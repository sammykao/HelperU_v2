"""
Main Agent System
Coordinates all agents and manages the multi-agent architecture
"""
from typing import Dict, List, Optional, Any
import logging
from openai import AsyncOpenAI
from .config import AgentSystemConfig, load_config
from .tools import (
    register_auth_tools, register_task_tools, register_chat_tools,
    register_profile_tools, register_application_tools, 
    register_payment_tools, register_notification_tools
)
from .agents import (
    TaskManagerAgent, UserAssistantAgent, ApplicationProcessorAgent,
    ChatModeratorAgent, PaymentProcessorAgent, NotificationCoordinatorAgent
)
from app.services import (
    AuthService, TaskService, ChatService, ProfileService,
    ApplicationService, StripeService, OpenPhoneService
)


class AgentSystem:
    """Main system for coordinating all AI agents"""
    
    def __init__(self, config: Optional[AgentSystemConfig] = None):
        self.config = config or load_config()
        self.logger = logging.getLogger("agent_system")
        
        # Initialize OpenAI client
        if self.config.openai_api_key:
            self.openai_client = AsyncOpenAI(api_key=self.config.openai_api_key)
        else:
            self.openai_client = None
            self.logger.warning("No OpenAI API key provided")
        
        # Initialize services
        self.services = self._initialize_services()
        
        # Initialize agents
        self.agents = self._initialize_agents()
        
        # Register tools
        self._register_all_tools()
        
        # Load tools for each agent
        self._load_agent_tools()
    
    def _initialize_services(self) -> Dict[str, Any]:
        """Initialize all service instances"""
        # Note: In a real implementation, you'd inject these services
        # For now, creating placeholder instances
        services = {
            "auth_service": None,  # Would be injected
            "task_service": None,  # Would be injected
            "chat_service": None,  # Would be injected
            "profile_service": None,  # Would be injected
            "application_service": None,  # Would be injected
            "stripe_service": None,  # Would be injected
            "openphone_service": None,  # Would be injected
        }
        return services
    
    def _initialize_agents(self) -> Dict[str, Any]:
        """Initialize all agent instances"""
        agents = {}
        
        # Create agents based on config
        for agent_id, agent_config in self.config.agents.items():
            if agent_id == "task_manager":
                agent = TaskManagerAgent(
                    model=agent_config.model,
                    temperature=agent_config.temperature
                )
            elif agent_id == "user_assistant":
                agent = UserAssistantAgent(
                    model=agent_config.model,
                    temperature=agent_config.temperature
                )
            elif agent_id == "application_processor":
                agent = ApplicationProcessorAgent(
                    model=agent_config.model,
                    temperature=agent_config.temperature
                )
            elif agent_id == "chat_moderator":
                agent = ChatModeratorAgent(
                    model=agent_config.model,
                    temperature=agent_config.temperature
                )
            elif agent_id == "payment_processor":
                agent = PaymentProcessorAgent(
                    model=agent_config.model,
                    temperature=agent_config.temperature
                )
            elif agent_id == "notification_coordinator":
                agent = NotificationCoordinatorAgent(
                    model=agent_config.model,
                    temperature=agent_config.temperature
                )
            else:
                self.logger.warning(f"Unknown agent type: {agent_id}")
                continue
            
            # Set OpenAI client
            if self.openai_client:
                agent.set_openai_client(self.openai_client)
            
            agents[agent_id] = agent
            self.logger.info(f"Initialized agent: {agent_id}")
        
        return agents
    
    def _register_all_tools(self):
        """Register all MCP tools"""
        try:
            # Register tools for each service
            if self.services["auth_service"]:
                register_auth_tools(self.services["auth_service"])
            
            if self.services["task_service"]:
                register_task_tools(self.services["task_service"])
            
            if self.services["chat_service"]:
                register_chat_tools(self.services["chat_service"])
            
            if self.services["profile_service"]:
                register_profile_tools(self.services["profile_service"])
            
            if self.services["application_service"]:
                register_application_tools(self.services["application_service"])
            
            if self.services["stripe_service"]:
                register_payment_tools(self.services["stripe_service"])
            
            if self.services["openphone_service"]:
                register_notification_tools(self.services["openphone_service"])
            
            self.logger.info("All tools registered successfully")
            
        except Exception as e:
            self.logger.error(f"Error registering tools: {e}")
    
    def _load_agent_tools(self):
        """Load tools for each agent"""
        for agent_id, agent in self.agents.items():
            try:
                agent.load_tools()
                self.logger.info(f"Tools loaded for agent: {agent_id}")
            except Exception as e:
                self.logger.error(f"Error loading tools for agent {agent_id}: {e}")
    
    def get_agent(self, agent_id: str) -> Optional[Any]:
        """Get a specific agent by ID"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> List[str]:
        """List all available agent IDs"""
        return list(self.agents.keys())
    
    async def route_request(self, user_message: str, user_id: Optional[str] = None,
                           context: Optional[Dict[str, Any]] = None,
                           preferred_agent: Optional[str] = None) -> str:
        """Route a user request to the appropriate agent"""
        
        # If preferred agent is specified and exists, use it
        if preferred_agent and preferred_agent in self.agents:
            agent = self.agents[preferred_agent]
            return await agent.process_message(user_message, user_id, context)
        
        # Otherwise, use routing logic to determine the best agent
        agent_id = self._determine_agent(user_message, context)
        
        if agent_id and agent_id in self.agents:
            agent = self.agents[agent_id]
            return await agent.process_message(user_message, user_id, context)
        else:
            # Fallback to user assistant
            agent = self.agents.get("user_assistant")
            if agent:
                return await agent.process_message(user_message, user_id, context)
            else:
                return "I'm sorry, but I'm unable to process your request at the moment."
    
    def _determine_agent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """Determine which agent should handle the request"""
        message_lower = message.lower()
        
        # Task-related keywords
        task_keywords = ["task", "create", "post", "job", "work", "help needed", "assistance"]
        if any(keyword in message_lower for keyword in task_keywords):
            return "task_manager"
        
        # Application-related keywords
        app_keywords = ["apply", "application", "helper", "qualification", "experience"]
        if any(keyword in message_lower for keyword in app_keywords):
            return "application_processor"
        
        # Payment/subscription keywords
        payment_keywords = ["payment", "subscription", "billing", "charge", "refund", "cancel"]
        if any(keyword in message_lower for keyword in payment_keywords):
            return "payment_processor"
        
        # Chat/messaging keywords
        chat_keywords = ["message", "chat", "conversation", "dispute", "moderate"]
        if any(keyword in message_lower for keyword in chat_keywords):
            return "chat_moderator"
        
        # Notification keywords
        notification_keywords = ["notify", "alert", "reminder", "sms", "email"]
        if any(keyword in message_lower for keyword in notification_keywords):
            return "notification_coordinator"
        
        # Default to user assistant for general queries
        return "user_assistant"
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get system status and health information"""
        status = {
            "system": "operational",
            "agents": {},
            "tools": {},
            "openai_client": "connected" if self.openai_client else "not_configured"
        }
        
        # Agent status
        for agent_id, agent in self.agents.items():
            status["agents"][agent_id] = {
                "status": "active",
                "tools_loaded": len(agent.available_tools),
                "memory_items": len(agent.memory.conversation_history)
            }
        
        # Tool status
        from .tools.base import tool_registry
        status["tools"]["total_registered"] = len(tool_registry.list_tools())
        status["tools"]["available_tools"] = tool_registry.list_tools()
        
        return status
    
    def inject_services(self, **services):
        """Inject service instances (for testing/dependency injection)"""
        for service_name, service_instance in services.items():
            if service_name in self.services:
                self.services[service_name] = service_instance
                self.logger.info(f"Injected service: {service_name}")
        
        # Re-register tools with new services
        self._register_all_tools()
        self._load_agent_tools()
    
    async def shutdown(self):
        """Shutdown the agent system"""
        self.logger.info("Shutting down agent system...")
        
        # Clear agent memories
        for agent in self.agents.values():
            agent.clear_memory()
        
        # Close OpenAI client if exists
        if self.openai_client:
            await self.openai_client.close()
        
        self.logger.info("Agent system shutdown complete")
