"""Router Agent for directing messages to appropriate specialized agents"""

from typing import Any, Dict, List, Optional
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from app.ai_agent.base import BaseAgent, AgentState, AgentMemory
from app.ai_agent.config import AgentConfig
import logging

logger = logging.getLogger(__name__)

class RouterAgent(BaseAgent):
    """Router agent that determines which specialized agent should handle a message"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(
            name="router_agent",
            description="Routes messages to appropriate specialized agents based on content analysis",
            config=config or {}
        )
        
        # Initialize LLM for routing decisions
        self.llm = ChatOpenAI(
            model=AgentConfig.OPENAI_MODEL,
            temperature=0.1,  # Low temperature for consistent routing
            max_tokens=100
        )
        
        # Routing rules and agent mappings
        self.routing_rules = {
            "authentication": ["auth_tools"],
            "profile": ["profile_tools"],
            "task": ["task_tools", "application_tools"],
            "chat": ["chat_tools"],
            "payment": ["payment_tools"],
            "helper": ["helper_tools"],
            "general": ["all_tools"]
        }
        
        self.agent_mappings = {
            "user_assistant": "general",
            "task_manager": "task", 
            "chat_moderator": "chat",
            "payment_processor": "payment",
            "application_processor": "task"
        }
    
    async def process_message(self, message: str, context: Dict[str, Any] = None) -> str:
        """Process message and route to appropriate agent"""
        try:
            # Analyze message to determine intent
            intent = await self._analyze_intent(message, context)
            
            # Route to appropriate agent
            routing_decision = await self._make_routing_decision(message, intent, context)
            
            # Update state with routing decision
            self.update_state(
                current_agent=routing_decision["target_agent"],
                context={"routing_intent": intent, "routing_reason": routing_decision["reason"]}
            )
            
            return f"Message routed to {routing_decision['target_agent']} agent. Intent: {intent}. Reason: {routing_decision['reason']}"
            
        except Exception as e:
            logger.error(f"Router agent error: {e}")
            return f"Routing error: {str(e)}"
    
    def can_handle(self, message: str, context: Dict[str, Any] = None) -> bool:
        """Router can handle any message - it's the entry point"""
        return True
    
    async def _analyze_intent(self, message: str, context: Dict[str, Any] = None) -> str:
        """Analyze message to determine primary intent"""
        try:
            system_prompt = """You are an intent classifier for a helper marketplace platform. 
            Analyze the user message and classify it into one of these categories:
            
            - authentication: login, signup, verification, password reset
            - profile: profile updates, personal information changes
            - task: creating tasks, searching tasks, task management, applications
            - chat: messaging, conversations, communication
            - payment: billing, subscriptions, payment methods
            - helper: helper search, helper profiles, helper management
            - general: general questions, help, support
            
            Respond with only the category name."""
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Classify this message: {message}")
            ]
            
            response = await self.llm.agenerate([messages])
            intent = response.generations[0][0].text.strip().lower()
            
            # Validate intent
            valid_intents = list(self.routing_rules.keys())
            if intent not in valid_intents:
                intent = "general"  # Default to general if unclear
                
            return intent
            
        except Exception as e:
            logger.error(f"Intent analysis error: {e}")
            return "general"
    
    async def _make_routing_decision(self, message: str, intent: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make routing decision based on intent and context"""
        try:
            # Get available tools for this intent
            available_tools = self.routing_rules.get(intent, ["all_tools"])
            
            # Consider context preferences
            preferred_agent = context.get("preferred_agent") if context else None
            
            # Determine target agent
            if preferred_agent and preferred_agent in self.agent_mappings:
                target_agent = preferred_agent
                reason = f"User preferred agent: {preferred_agent}"
            else:
                target_agent = self._get_default_agent_for_intent(intent)
                reason = f"Intent-based routing: {intent}"
            
            return {
                "target_agent": target_agent,
                "intent": intent,
                "available_tools": available_tools,
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"Routing decision error: {e}")
            return {
                "target_agent": "user_assistant",
                "intent": intent,
                "available_tools": ["all_tools"],
                "reason": "Fallback to general assistant due to error"
            }
    
    def _get_default_agent_for_intent(self, intent: str) -> str:
        """Get default agent for a given intent"""
        intent_to_agent = {
            "authentication": "user_assistant",
            "profile": "user_assistant", 
            "task": "task_manager",
            "chat": "chat_moderator",
            "payment": "payment_processor",
            "helper": "user_assistant",
            "general": "user_assistant"
        }
        
        return intent_to_agent.get(intent, "user_assistant")
    
    def get_routing_summary(self) -> Dict[str, Any]:
        """Get summary of routing decisions"""
        if not self.state:
            return {"error": "No routing state available"}
        
        return {
            "current_agent": self.state.current_agent,
            "agent_history": self.state.agent_history,
            "routing_context": self.state.context.get("routing_intent"),
            "routing_reason": self.state.context.get("routing_reason")
        }

