"""
Base workflow orchestrator for the Agentic News Workflow System
"""

from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod

class BaseWorkflow(ABC):
    """Base class for all workflow orchestrators"""
    
    def __init__(self, name: str, description: str):
        """Initialize the workflow with name and description"""
        self.name = name
        self.description = description
    
    @abstractmethod
    def run(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Run the workflow
        
        Returns:
            Dictionary with workflow results
        """
        pass
