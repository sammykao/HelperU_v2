"""
Base Agent Class
Provides common functionality for all AI agents
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
import logging
from openai import AsyncOpenAI
from ..tools.base import tool_registry, BaseMCPTool


class AgentMemory(BaseModel):
    """Memory storage for agents"""
    conversation_history: List[Dict[str, Any]] = []
    context: Dict[str, Any] = {}
    max_items: int = 10
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """Add a message to conversation history"""
        message = {
            "role": role,
            "content": content,
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
        
        # Keep only the last max_items messages
        if len(self.conversation_history) > self.max_items:
            self.conversation_history = self.conversation_history[-self.max_items:]
    
    def get_context(self) -> str:
        """Get formatted context for LLM"""
        if not self.conversation_history:
            return ""
        
        context_parts = []
        for msg in self.conversation_history[-5:]:  # Last 5 messages
            context_parts.append(f"{msg['role']}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def clear(self):
        """Clear memory"""
        self.conversation_history.clear()
        self.context.clear()


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, name: str, description: str, model: str = "gpt-4", 
                 temperature: float = 0.1, max_tokens: int = 4000):
        self.name = name
        self.description = description
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.memory = AgentMemory()
        self.logger = logging.getLogger(f"agent.{name}")
        self.client: Optional[AsyncOpenAI] = None
        self.available_tools: List[BaseMCPTool] = []
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent"""
        pass
    
    @abstractmethod
    def get_available_tools(self) -> List[str]:
        """Get list of tool names this agent can use"""
        pass
    
    def set_openai_client(self, client: AsyncOpenAI):
        """Set OpenAI client"""
        self.client = client
    
    def load_tools(self):
        """Load available tools for this agent"""
        tool_names = self.get_available_tools()
        self.available_tools = []
        
        for tool_name in tool_names:
            tool = tool_registry.get(tool_name)
            if tool:
                self.available_tools.append(tool)
                self.logger.info(f"Loaded tool: {tool_name}")
            else:
                self.logger.warning(f"Tool not found: {tool_name}")
    
    async def process_message(self, message: str, user_id: Optional[str] = None, 
                           context: Optional[Dict[str, Any]] = None) -> str:
        """Process a user message and return response"""
        if not self.client:
            raise ValueError("OpenAI client not set")
        
        # Add user message to memory
        self.memory.add_message("user", message, {"user_id": user_id})
        
        # Prepare conversation context
        system_prompt = self.get_system_prompt()
        conversation = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add memory context
        if self.memory.get_context():
            conversation.append({
                "role": "system", 
                "content": f"Previous conversation context:\n{self.memory.get_context()}"
            })
        
        # Add current message
        conversation.append({"role": "user", "content": message})
        
        # Add context if provided
        if context:
            conversation.append({
                "role": "system",
                "content": f"Additional context: {context}"
            })
        
        try:
            # Get LLM response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=conversation,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                tools=self._get_tool_schemas() if self.available_tools else None,
                tool_choice="auto" if self.available_tools else None
            )
            
            response_content = response.choices[0].message.content or ""
            
            # Handle tool calls if any
            if response.choices[0].message.tool_calls:
                response_content = await self._handle_tool_calls(
                    response.choices[0].message.tool_calls,
                    response_content
                )
            
            # Add assistant response to memory
            self.memory.add_message("assistant", response_content)
            
            return response_content
            
        except Exception as e:
            self.logger.error(f"Error processing message: {e}")
            error_response = f"I encountered an error while processing your request: {str(e)}"
            self.memory.add_message("assistant", error_response)
            return error_response
    
    def _get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get tool schemas for OpenAI function calling"""
        schemas = []
        for tool in self.available_tools:
            schema = tool.get_schema()
            schemas.append({
                "type": "function",
                "function": {
                    "name": schema.name,
                    "description": schema.description,
                    "parameters": schema.input_schema
                }
            })
        return schemas
    
    async def _handle_tool_calls(self, tool_calls: List[Any], original_response: str) -> str:
        """Handle tool calls from LLM response"""
        tool_results = []
        
        for tool_call in tool_calls:
            try:
                tool_name = tool_call.function.name
                tool_args = tool_call.function.arguments
                
                # Find the tool
                tool = tool_registry.get(tool_name)
                if not tool:
                    tool_results.append(f"Tool {tool_name} not found")
                    continue
                
                # Execute tool
                import json
                args = json.loads(tool_args)
                result = await tool.execute(**args)
                
                tool_results.append(f"Tool {tool_name} executed successfully: {result}")
                
            except Exception as e:
                tool_results.append(f"Error executing tool {tool_call.function.name}: {str(e)}")
        
        # Combine original response with tool results
        if tool_results:
            return f"{original_response}\n\nTool execution results:\n" + "\n".join(tool_results)
        
        return original_response
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of agent memory"""
        return {
            "conversation_count": len(self.memory.conversation_history),
            "context_keys": list(self.memory.context.keys()),
            "recent_messages": self.memory.conversation_history[-3:] if self.memory.conversation_history else []
        }
    
    def clear_memory(self):
        """Clear agent memory"""
        self.memory.clear()
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()
