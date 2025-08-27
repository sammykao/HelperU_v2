#!/usr/bin/env python3
"""
Test script for the AI Agent System with one-agent-per-tool structure
Run this from the project root directory
"""

import asyncio
import sys
import os
import logging

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock services for testing
class MockProfileService:
    pass

class MockTaskService:
    pass

class MockSubscriptionService:
    pass

async def test_basic_structure():
    """Test basic system structure without external dependencies"""
    try:
        logger.info("Testing basic AI Agent System structure...")
        
        # Test imports (without LangChain)
        from app.ai_agent.base import BaseAgent, BaseTool, AgentRegistry, AgentManager
        from app.ai_agent.config import agent_config
        
        logger.info("✅ All base classes imported successfully")
        logger.info(f"✅ Configuration loaded: {agent_config.OPENAI_MODEL}")
        
        # Test registry creation
        registry = AgentRegistry()
        logger.info("✅ Agent registry created successfully")
        
        # Test manager creation
        manager = AgentManager(registry)
        logger.info("✅ Agent manager created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Basic structure test failed: {e}")
        return False

async def test_agent_creation():
    """Test that agents can be created with their tools"""
    try:
        logger.info("Testing agent creation with tools...")
        
        # Test profile agent
        from app.ai_agent.agents.profile_agent import ProfileAgent
        
        profile_agent = ProfileAgent(MockProfileService())
        logger.info("✅ Profile agent created successfully")
        
        # Test task agent
        from app.ai_agent.agents.task_agent import TaskAgent
        
        task_agent = TaskAgent(MockTaskService())
        logger.info("✅ Task agent created successfully")
        
        # Test payment agent
        from app.ai_agent.agents.payment_agent import PaymentAgent
        
        payment_agent = PaymentAgent(MockSubscriptionService())
        logger.info("✅ Payment agent created successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent creation test failed: {e}")
        return False

async def test_router_agent():
    """Test router agent functionality"""
    try:
        logger.info("Testing router agent...")
        
        from app.ai_agent.agents.router_agent import RouterAgent
        
        router = RouterAgent()
        logger.info("✅ Router agent created successfully")
        
        # Test intent analysis
        intent = router._analyze_intent("I need to update my profile")
        if intent == "profile":
            logger.info("✅ Router intent analysis working correctly")
        else:
            logger.error(f"❌ Router intent analysis failed: expected 'profile', got '{intent}'")
            return False
        
        # Test routing decision
        routing = router._make_routing_decision("Update my profile", "profile")
        if routing["target_agent"] == "profile_agent":
            logger.info("✅ Router routing decision working correctly")
        else:
            logger.error(f"❌ Router routing decision failed: expected 'profile_agent', got '{routing['target_agent']}'")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Router agent test failed: {e}")
        return False

async def test_factory_structure():
    """Test factory structure without building the full system"""
    try:
        logger.info("Testing factory structure...")
        
        from app.ai_agent.factory import AgentSystemFactory
        
        # Test factory creation
        factory = AgentSystemFactory()
        logger.info("✅ Agent system factory created successfully")
        
        # Test factory methods exist
        if hasattr(factory, 'build_system'):
            logger.info("✅ Factory has build_system method")
        else:
            logger.error("❌ Factory missing build_system method")
            return False
        
        if hasattr(factory, 'get_system_status'):
            logger.info("✅ Factory has get_system_status method")
        else:
            logger.error("❌ Factory missing get_system_status method")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Factory structure test failed: {e}")
        return False

async def test_agent_capabilities():
    """Test that agents can handle appropriate messages"""
    try:
        logger.info("Testing agent message handling capabilities...")
        
        # Test profile agent
        from app.ai_agent.agents.profile_agent import ProfileAgent
        
        profile_agent = ProfileAgent(MockProfileService())
        
        # Test profile agent can handle profile messages
        if profile_agent.can_handle("Update my profile"):
            logger.info("✅ Profile agent correctly identifies profile messages")
        else:
            logger.error("❌ Profile agent failed to identify profile messages")
            return False
        
        # Test task agent
        from app.ai_agent.agents.task_agent import TaskAgent
        
        task_agent = TaskAgent(MockTaskService())
        
        # Test task agent can handle task messages
        if task_agent.can_handle("Create a new task"):
            logger.info("✅ Task agent correctly identifies task messages")
        else:
            logger.error("❌ Task agent failed to identify task messages")
            return False
        
        # Test payment agent
        from app.ai_agent.agents.payment_agent import PaymentAgent
        
        payment_agent = PaymentAgent(MockSubscriptionService())
        
        # Test payment agent can handle payment messages
        if payment_agent.can_handle("Upgrade my subscription"):
            logger.info("✅ Payment agent correctly identifies payment messages")
        else:
            logger.error("❌ Payment agent failed to identify payment messages")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Agent capabilities test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Starting AI Agent System structure tests...")
    
    tests = [
        ("Basic Structure", test_basic_structure),
        ("Agent Creation", test_agent_creation),
        ("Router Agent", test_router_agent),
        ("Factory Structure", test_factory_structure),
        ("Agent Capabilities", test_agent_capabilities),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running: {test_name}")
        try:
            if await test_func():
                passed += 1
                logger.info(f"✅ {test_name} passed")
            else:
                logger.error(f"❌ {test_name} failed")
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
    
    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All structure tests passed! AI Agent System is properly structured.")
        logger.info("\n📝 Architecture Summary:")
        logger.info("• One agent per tool domain")
        logger.info("• Profile Agent → Profile Tools")
        logger.info("• Task Agent → Task Tools") 
        logger.info("• Payment Agent → Payment Tools")
        logger.info("• Router Agent → Routes to appropriate agents")
        logger.info("\n📝 Next steps:")
        logger.info("1. Install LangChain dependencies: pip install langchain langchain-openai")
        logger.info("2. Set up OpenAI API key in environment")
        logger.info("3. Test the full system with actual LLM integration")
        return True
    else:
        logger.error("💥 Some structure tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Unexpected error: {e}")
        sys.exit(1)
