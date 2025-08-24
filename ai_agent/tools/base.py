"""
Base MCP Tool Class
Provides common functionality for all MCP tools
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
from pydantic import BaseModel, Field
import asyncio
import logging


class ToolSchema(BaseModel):
    """Schema for MCP tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    required: bool = True


class BaseMCPTool(ABC):
    """Base class for all MCP tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"mcp_tool.{name}")
        
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with given parameters"""
        pass
    
    @abstractmethod
    def get_schema(self) -> ToolSchema:
        """Get the tool's schema definition"""
        pass
    
    async def execute_with_retry(self, max_retries: int = 3, **kwargs) -> Any:
        """Execute tool with retry logic"""
        for attempt in range(max_retries):
            try:
                return await self.execute(**kwargs)
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters against schema"""
        try:
            schema = self.get_schema()
            # Basic validation - could be enhanced with JSON Schema validation
            return True
        except Exception as e:
            self.logger.error(f"Input validation failed: {e}")
            return False
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
    
    def __repr__(self) -> str:
        return self.__str__()


class ToolRegistry:
    """Registry for managing all MCP tools"""
    
    def __init__(self):
        self._tools: Dict[str, BaseMCPTool] = {}
    
    def register(self, tool: BaseMCPTool):
        """Register a tool"""
        self._tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")
    
    def get(self, name: str) -> Optional[BaseMCPTool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all registered tool names"""
        return list(self._tools.keys())
    
    def get_all_tools(self) -> Dict[str, BaseMCPTool]:
        """Get all registered tools"""
        return self._tools.copy()
    
    def unregister(self, name: str):
        """Unregister a tool"""
        if name in self._tools:
            del self._tools[name]
            self.logger.info(f"Unregistered tool: {name}")


# Global tool registry
tool_registry = ToolRegistry()
