from langchain.tools.base import BaseTool
from langchain_openai import ChatOpenAI
from app.core.config import settings

MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.4

def collect_tools(module) -> list[BaseTool]:
    """Collect all @tool-decorated functions from a module."""
    tools = []
    
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, BaseTool):  # @tool wraps into StructuredTool (subclass of BaseTool)
            tools.append(attr)
    return tools


def create_llm() -> ChatOpenAI:
    """Create a LangChain OpenAI model"""
    return ChatOpenAI(model=MODEL_NAME, temperature=TEMPERATURE, api_key=settings.OPENAI_API_KEY)