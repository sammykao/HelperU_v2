"""
Example Usage of HelperU AI Agent System
Demonstrates how to use the multi-agent system with MCP tools and LangGraph workflows
"""
import asyncio
import logging
from typing import Dict, Any
from .system import AgentSystem
from .router import AgentRouter
from .config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Main example function"""
    logger.info("Starting HelperU AI Agent System Example")
    
    try:
        # 1. Initialize the system
        logger.info("Initializing AI Agent System...")
        config = load_config()
        agent_system = AgentSystem(config)
        
        # 2. Create the router
        logger.info("Creating Agent Router...")
        router = AgentRouter(agent_system)
        
        # 3. Example 1: Simple agent routing
        logger.info("\n=== Example 1: Simple Agent Routing ===")
        await example_simple_routing(router)
        
        # 4. Example 2: Direct agent calls
        logger.info("\n=== Example 2: Direct Agent Calls ===")
        await example_direct_agent_calls(router)
        
        # 5. Example 3: Workflow execution
        logger.info("\n=== Example 3: Workflow Execution ===")
        await example_workflow_execution(router)
        
        # 6. Example 4: System status and monitoring
        logger.info("\n=== Example 4: System Status ===")
        await example_system_status(router)
        
        # 7. Cleanup
        logger.info("\nCleaning up...")
        await router.shutdown()
        
        logger.info("Example completed successfully!")
        
    except Exception as e:
        logger.error(f"Error in main example: {e}")
        raise


async def example_simple_routing(router: AgentRouter):
    """Example of simple request routing"""
    logger.info("Testing simple request routing...")
    
    # Test different types of requests
    test_requests = [
        {
            "message": "I need help creating a new task for house cleaning",
            "expected_agent": "task_manager"
        },
        {
            "message": "How do I update my profile information?",
            "expected_agent": "user_assistant"
        },
        {
            "message": "I want to apply for a helper position",
            "expected_agent": "application_processor"
        },
        {
            "message": "I have a payment issue with my subscription",
            "expected_agent": "payment_processor"
        }
    ]
    
    for i, test in enumerate(test_requests, 1):
        logger.info(f"Test {i}: {test['message']}")
        
        try:
            result = await router.route_request(
                user_message=test["message"],
                user_id="example_user_123"
            )
            
            if result["success"]:
                logger.info(f"✓ Routed successfully to agent")
            else:
                logger.warning(f"✗ Routing failed: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"✗ Error in routing: {e}")


async def example_direct_agent_calls(router: AgentRouter):
    """Example of direct agent calls"""
    logger.info("Testing direct agent calls...")
    
    # Test direct call to task manager
    try:
        result = await router.execute_direct_agent_call(
            agent_id="task_manager",
            message="Create a task for lawn mowing at 123 Main St, hourly rate $25",
            user_id="client_user_456"
        )
        
        if result["success"]:
            logger.info(f"✓ Direct call successful: {result['agent_id']}")
        else:
            logger.warning(f"✗ Direct call failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"✗ Error in direct agent call: {e}")


async def example_workflow_execution(router: AgentRouter):
    """Example of workflow execution"""
    logger.info("Testing workflow execution...")
    
    # Test task creation workflow
    try:
        task_data = {
            "title": "House Cleaning Service",
            "description": "Need help cleaning a 3-bedroom house",
            "hourly_rate": 30.0,
            "zip_code": "12345",
            "dates": ["2024-01-15", "2024-01-16"],
            "location_type": "onsite",
            "tools_info": "Basic cleaning supplies provided"
        }
        
        result = await router.route_request(
            user_message="I want to create a new task",
            user_id="client_user_789",
            workflow_type="task_creation",
            context={"task_data": task_data}
        )
        
        if result["success"]:
            logger.info(f"✓ Workflow executed successfully: {result['workflow_type']}")
            logger.info(f"  Summary: {result.get('workflow_summary', 'No summary')}")
            logger.info(f"  Data: {result.get('workflow_data', {})}")
        else:
            logger.warning(f"✗ Workflow failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"✗ Error in workflow execution: {e}")


async def example_system_status(router: AgentRouter):
    """Example of system status monitoring"""
    logger.info("Getting system status...")
    
    try:
        status = router.get_system_status()
        
        logger.info("=== System Status ===")
        logger.info(f"Agent System: {status['agent_system']['system']}")
        logger.info(f"OpenAI Client: {status['agent_system']['openai_client']}")
        
        logger.info("\n=== Available Agents ===")
        for agent_id, agent_status in status['agent_system']['agents'].items():
            logger.info(f"  {agent_id}: {agent_status['status']} "
                       f"(Tools: {agent_status['tools_loaded']}, "
                       f"Memory: {agent_status['memory_items']})")
        
        logger.info(f"\n=== Available Workflows ===")
        for workflow_type in status['workflows']:
            workflow_info = status['workflows'][workflow_type]
            logger.info(f"  {workflow_type}: {workflow_info['description']} "
                       f"(Steps: {len(workflow_info['steps'])})")
        
        logger.info(f"\n=== Tools ===")
        logger.info(f"  Total Registered: {status['agent_system']['tools']['total_registered']}")
        
    except Exception as e:
        logger.error(f"✗ Error getting system status: {e}")


async def example_advanced_usage():
    """Example of more advanced usage patterns"""
    logger.info("=== Advanced Usage Examples ===")
    
    # This would show more complex scenarios like:
    # - Multi-agent conversations
    # - Complex workflow chains
    # - Integration with external systems
    # - Custom agent development
    # - Performance monitoring and optimization
    
    logger.info("Advanced usage examples would be implemented here")
    logger.info("Including multi-agent conversations, complex workflows, etc.")


if __name__ == "__main__":
    # Run the example
    asyncio.run(main())
