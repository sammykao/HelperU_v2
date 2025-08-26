"""Main User Assistant Agent for general user interactions"""

from typing import Any, Dict, List, Optional
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from langchain.agents import Tool, AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from app.ai_agent.base import BaseAgent, AgentState, AgentMemory
from app.ai_agent.config import AgentConfig
from app.ai_agent.tools import (
    AuthTools, ChatTools, TaskTools, ProfileTools, 
    HelperTools, ApplicationTools, PaymentTools
)
import logging

logger = logging.getLogger(__name__)

class UserAssistant(BaseAgent):
    """Main user assistant agent that handles general user interactions"""
    
    def __init__(self, tools: Dict[str, Any], config: Dict[str, Any] = None):
        super().__init__(
            name="user_assistant",
            description="Main assistant for general user interactions and support",
            config=config or {}
        )
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=AgentConfig.OPENAI_MODEL,
            temperature=0.7,
            max_tokens=AgentConfig.OPENAI_MAX_TOKENS
        )
        
        # Store tools
        self.tools = tools
        
        # Create LangChain tools
        self.langchain_tools = self._create_langchain_tools()
        
        # Create agent
        self.agent = self._create_agent()
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.langchain_tools,
            verbose=AgentConfig.ENABLE_LOGGING,
            max_iterations=AgentConfig.MAX_AGENT_ITERATIONS
        )
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process user message using the agent executor"""
        try:
            # Add context to message if available
            enhanced_message = self._enhance_message_with_context(message, context)
            
            # Process with agent executor
            result = await self.agent_executor.ainvoke({
                "input": enhanced_message,
                "chat_history": self._get_chat_history()
            })
            
            # Add to memory
            self.add_to_memory(HumanMessage(content=message))
            self.add_to_memory(AIMessage(content=result["output"]))
            
            # Update state
            self.update_state(context={"last_response": result["output"]})
            
            return result["output"]
            
        except Exception as e:
            logger.error(f"User assistant error: {e}")
            return f"I encountered an error while processing your request: {str(e)}. Please try again or contact support."
    
    def can_handle(self, message: str, context: Dict[str, Any] = None) -> bool:
        """User assistant can handle general queries and most user interactions"""
        # Can handle most things, but specialized agents might be better for specific tasks
        return True
    
    def _create_langchain_tools(self) -> List[Tool]:
        """Create LangChain tools from our tool classes"""
        tools = []
        
        # Auth tools
        if "auth_tools" in self.tools:
            auth_tool = Tool(
                name="authentication_tools",
                description="Tools for user authentication, signup, and verification",
                func=self._execute_auth_tool
            )
            tools.append(auth_tool)
        
        # Profile tools
        if "profile_tools" in self.tools:
            profile_tool = Tool(
                name="profile_tools", 
                description="Tools for managing user profiles and personal information",
                func=self._execute_profile_tool
            )
            tools.append(profile_tool)
        
        # Task tools
        if "task_tools" in self.tools:
            task_tool = Tool(
                name="task_tools",
                description="Tools for creating, managing, and searching tasks",
                func=self._execute_task_tool
            )
            tools.append(task_tool)
        
        # Chat tools
        if "chat_tools" in self.tools:
            chat_tool = Tool(
                name="chat_tools",
                description="Tools for managing chats and messages between users",
                func=self._execute_chat_tool
            )
            tools.append(chat_tool)
        
        # Helper tools
        if "helper_tools" in self.tools:
            helper_tool = Tool(
                name="helper_tools",
                description="Tools for searching and managing helper profiles",
                func=self._execute_helper_tool
            )
            tools.append(helper_tool)
        
        # Application tools
        if "application_tools" in self.tools:
            app_tool = Tool(
                name="application_tools",
                description="Tools for managing task applications and proposals",
                func=self._execute_application_tool
            )
            tools.append(app_tool)
        
        # Payment tools
        if "payment_tools" in self.tools:
            payment_tool = Tool(
                name="payment_tools",
                description="Tools for managing payments, subscriptions, and billing",
                func=self._execute_payment_tool
            )
            tools.append(payment_tool)
        
        return tools
    
    def _create_agent(self):
        """Create the LangChain agent"""
        system_prompt = """You are a helpful AI assistant for a helper marketplace platform called HelperU. 
        
        Your role is to help users with:
        - General questions about the platform
        - User authentication and account management
        - Profile updates and personal information
        - Task creation and management
        - Chat and messaging features
        - Helper search and profiles
        - Payment and subscription questions
        - Application management
        
        Always be helpful, professional, and guide users to the appropriate tools when needed.
        If you're unsure about something, ask for clarification rather than guessing.
        
        Available tools: {tools}
        
        Use the tools when appropriate to help users accomplish their goals."""
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        return create_openai_functions_agent(self.llm, self.langchain_tools, prompt)
    
    def _enhance_message_with_context(self, message: str, context: Dict[str, Any] = None) -> str:
        """Enhance message with context information"""
        if not context:
            return message
        
        context_parts = []
        if "user_id" in context:
            context_parts.append(f"User ID: {context['user_id']}")
        if "user_type" in context:
            context_parts.append(f"User Type: {context['user_type']}")
        if "session_data" in context:
            context_parts.append(f"Session: {context['session_data']}")
        
        if context_parts:
            enhanced_message = f"Context: {' | '.join(context_parts)}\n\nUser Message: {message}"
            return enhanced_message
        
        return message
    
    def _get_chat_history(self) -> List[Any]:
        """Get chat history from memory"""
        if not self.memory or not self.memory.messages:
            return []
        
        # Convert memory messages to chat history format
        history = []
        for msg in self.memory.messages[-10:]:  # Last 10 messages
            if hasattr(msg, 'type'):
                if msg.type == 'human':
                    history.append(("human", msg.content))
                elif msg.type == 'ai':
                    history.append(("ai", msg.content))
        
        return history
    
    # Tool execution methods
    async def _execute_auth_tool(self, action: str, **kwargs) -> str:
        """Execute authentication tool"""
        try:
            result = await self.tools["auth_tools"].execute(action, **kwargs)
            return str(result)
        except Exception as e:
            return f"Authentication tool error: {str(e)}"
    
    async def _execute_profile_tool(self, action: str, **kwargs) -> str:
        """Execute profile tool"""
        try:
            result = await self.tools["profile_tools"].execute(action, **kwargs)
            return str(result)
        except Exception as e:
            return f"Profile tool error: {str(e)}"
    
    async def _execute_task_tool(self, action: str, **kwargs) -> str:
        """Execute task tool"""
        try:
            result = await self.tools["task_tools"].execute(action, **kwargs)
            return str(result)
        except Exception as e:
            return f"Task tool error: {str(e)}"
    
    async def _execute_chat_tool(self, action: str, **kwargs) -> str:
        """Execute chat tool"""
        try:
            result = await self.tools["chat_tools"].execute(action, **kwargs)
            return str(result)
        except Exception as e:
            return f"Chat tool error: {str(e)}"
    
    async def _execute_helper_tool(self, action: str, **kwargs) -> str:
        """Execute helper tool"""
        try:
            result = await self.tools["helper_tools"].execute(action, **kwargs)
            return str(result)
        except Exception as e:
            return f"Helper tool error: {str(e)}"
    
    async def _execute_application_tool(self, action: str, **kwargs) -> str:
        """Execute application tool"""
        try:
            result = await self.tools["application_tools"].execute(action, **kwargs)
            return str(result)
        except Exception as e:
            return f"Application tool error: {str(e)}"
    
    async def _execute_payment_tool(self, action: str, **kwargs) -> str:
        """Execute payment tool"""
        try:
            result = await self.tools["payment_tools"].execute(action, **kwargs)
            return str(result)
        except Exception as e:
            return f"Payment tool error: {str(e)}"

