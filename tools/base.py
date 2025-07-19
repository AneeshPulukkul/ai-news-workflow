"""
Base tools for the Agentic News Workflow System
Defines base classes and utilities for LangChain tools
"""

from typing import Dict, List, Any, Optional, Union
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class NewsWorkflowTool(BaseTool):
    """Base class for all News Workflow tools"""
    
    def __init__(self, name: str, description: str, **kwargs):
        """Initialize the tool with name and description"""
        self.name = name
        self.description = description
        super().__init__(**kwargs)
    
    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """Run the tool - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _run method")
    
    def _arun(self, *args: Any, **kwargs: Any) -> Any:
        """Async run - default to sync implementation unless overridden"""
        return self._run(*args, **kwargs)
