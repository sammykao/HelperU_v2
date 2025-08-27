"""Base classes for the AI Agent System"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.schema.output import LLMResult
from langchain.callbacks.base import BaseCallbackHandler
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class AgentState(BaseModel):
    """State management for agents"""
    conversation_id: str = Field(description="Unique identifier for the conversation")
    user_id: str = Field(description="User ID initiating the conversation")
    current_agent: str = Field(description="Currently active agent")
    agent_history: List[str] = Field(default_factory=list, description="History of agents used")
    context: Dict[str, Any] = Field(default_factory=dict, description="Context data for the conversation")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class AgentMemory(BaseModel):
    """Memory management for agents"""
    conversation_id: str
    messages: List[BaseMessage] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, description: str, config: Dict[str, Any] = None):
        self.name = name
        self.description = description
        self.config = config or {}
        self.memory: Optional[AgentMemory] = None
        self.state: Optional[AgentState] = None
        self.logger = logging.getLogger(f"agent.{name}")
        
    @abstractmethod
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process incoming message and return response"""
        pass
    
    @abstractmethod
    def can_handle(self, message: str, context: Dict[str, Any] = None) -> bool:
        """Determine if this agent can handle the given message"""
        pass
    
    def add_to_memory(self, message: BaseMessage):
        """Add message to agent memory"""
        if self.memory:
            self.memory.messages.append(message)
            self.memory.last_accessed = datetime.utcnow()
    
    def get_memory_context(self) -> str:
        """Get relevant context from memory"""
        if not self.memory or not self.memory.messages:
            return ""
        
        # Get last few messages for context
        recent_messages = self.memory.messages[-5:]
        context = "\n".join([f"{msg.type}: {msg.content}" for msg in recent_messages])
        return f"Recent conversation context:\n{context}"
    
    def update_state(self, **kwargs):
        """Update agent state"""
        if self.state:
            for key, value in kwargs.items():
                if hasattr(self.state, key):
                    setattr(self.state, key, value)
            self.state.updated_at = datetime.utcnow()

class BaseTool(ABC):
    """Base class for all tools that agents can use"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get tool schema for agent understanding"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self._get_parameters()
        }
    
    @abstractmethod
    def _get_parameters(self) -> Dict[str, Any]:
        """Get parameter schema for the tool"""
        pass

class AgentCallbackHandler(BaseCallbackHandler):
    """Custom callback handler for agent operations"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"callback.{agent_name}")
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs):
        """Called when LLM starts"""
        self.logger.info(f"LLM started for {self.agent_name}")
    
    def on_llm_end(self, response: LLMResult, **kwargs):
        """Called when LLM ends"""
        self.logger.info(f"LLM completed for {self.agent_name}")
    
    def on_llm_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs):
        """Called when LLM errors"""
        self.logger.error(f"LLM error for {self.agent_name}: {error}")
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs):
        """Called when tool starts"""
        self.logger.info(f"Tool started for {self.agent_name}: {input_str}")
    
    def on_tool_end(self, output: str, **kwargs):
        """Called when tool ends"""
        self.logger.info(f"Tool completed for {self.agent_name}")
    
    def on_tool_error(self, error: Union[Exception, KeyboardInterrupt], **kwargs):
        """Called when tool errors"""
        self.logger.error(f"Tool error for {self.agent_name}: {error}")

class AgentRegistry:
    """Registry for managing all available agents"""
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.tools: Dict[str, BaseTool] = {}
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.name] = agent
        logger.info(f"Registered agent: {agent.name}")
    
    def register_tool(self, tool: BaseTool):
        """Register a tool"""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name"""
        return self.agents.get(name)
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get tool by name"""
        return self.tools.get(name)
    
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        return list(self.agents.values())
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def find_best_agent(self, message: str, context: Dict[str, Any] = None) -> Optional[BaseAgent]:
        """Find the best agent to handle a message"""
        best_agent = None
        best_score = 0
        
        for agent in self.agents.values():
            if agent.can_handle(message, context):
                # Simple scoring - can be enhanced with more sophisticated logic
                score = 1
                if context and "preferred_agent" in context:
                    if context["preferred_agent"] == agent.name:
                        score += 2
                
                if score > best_score:
                    best_score = score
                    best_agent = agent
        
        return best_agent
