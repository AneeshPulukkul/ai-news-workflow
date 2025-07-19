"""
Base Guardrail class for responsible AI implementations in the news workflow system.
"""
from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

class BaseGuardrail(ABC):
    """
    Abstract base class for all guardrails in the system.
    
    Guardrails enforce responsible AI principles by monitoring and/or
    modifying content at various stages of the workflow.
    """
    
    def __init__(self, name: str, description: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the guardrail.
        
        Args:
            name: Unique identifier for this guardrail
            description: Human-readable description of what this guardrail does
            config: Configuration parameters for this guardrail
        """
        self.name = name
        self.description = description
        self.config = config or {}
        self.metrics = {
            "invocations": 0,
            "blocks": 0,
            "modifications": 0,
            "passes": 0
        }
        logger.info(f"Initialized guardrail: {name}")
    
    @abstractmethod
    def process(self, content: Any) -> Tuple[Any, Dict[str, Any]]:
        """
        Process content through the guardrail.
        
        Args:
            content: The content to process (text, structured data, etc.)
            
        Returns:
            Tuple containing:
                - The processed content (may be modified from original)
                - A result dictionary with metadata about the processing
        """
        pass
    
    def should_block(self, analysis_result: Dict[str, Any]) -> bool:
        """
        Determine if content should be blocked based on analysis.
        
        Args:
            analysis_result: The result of analyzing the content
            
        Returns:
            True if content should be blocked, False otherwise
        """
        # Default implementation - subclasses should override
        return False
    
    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log an event for monitoring and improvement.
        
        Args:
            event_type: Type of event (block, modify, pass)
            details: Details about the event
        """
        # Update metrics
        self.metrics["invocations"] += 1
        if event_type == "block":
            self.metrics["blocks"] += 1
        elif event_type == "modify":
            self.metrics["modifications"] += 1
        elif event_type == "pass":
            self.metrics["passes"] += 1
        
        # Log the event
        logger.info(f"Guardrail {self.name} - {event_type}: {details}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get metrics about this guardrail's performance.
        
        Returns:
            Dictionary of metrics
        """
        return self.metrics
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"


class GuardrailChain:
    """
    Chain multiple guardrails together in sequence.
    """
    
    def __init__(self, guardrails: List[BaseGuardrail]):
        """
        Initialize with a list of guardrails.
        
        Args:
            guardrails: List of guardrails to apply in sequence
        """
        self.guardrails = guardrails
    
    def process(self, content: Any) -> Tuple[Any, Dict[str, List[Dict[str, Any]]]]:
        """
        Process content through all guardrails in sequence.
        
        Args:
            content: The content to process
            
        Returns:
            Tuple containing:
                - The final processed content
                - Dictionary of results from each guardrail
        """
        current_content = content
        results = {"guardrail_results": []}
        
        for guardrail in self.guardrails:
            processed_content, result = guardrail.process(current_content)
            
            results["guardrail_results"].append({
                "guardrail": guardrail.name,
                "result": result
            })
            
            # If the guardrail blocks content, stop processing
            if result.get("blocked", False):
                results["blocked"] = True
                results["blocking_guardrail"] = guardrail.name
                results["blocking_reason"] = result.get("reason", "Unknown reason")
                break
            
            # Otherwise continue with the potentially modified content
            current_content = processed_content
        
        return current_content, results


class LangChainGuardrailTool:
    """
    Adapter to use guardrails as wrappers around LangChain tools.
    """
    
    def __init__(self, tool, guardrail_chain: GuardrailChain):
        """
        Initialize with a tool and guardrail chain.
        
        Args:
            tool: The LangChain tool to wrap
            guardrail_chain: Chain of guardrails to apply
        """
        self.tool = tool
        self.guardrail_chain = guardrail_chain
        
        # Preserve tool metadata
        self.name = f"guarded_{tool.name}"
        self.description = f"{tool.description} (with responsible AI guardrails)"
    
    def run(self, *args, **kwargs):
        """
        Run the tool with guardrails applied to the output.
        
        Returns:
            Guarded tool output
        """
        # Run the original tool
        original_output = self.tool.run(*args, **kwargs)
        
        # Apply guardrails to the output
        guarded_output, results = self.guardrail_chain.process(original_output)
        
        # If any guardrail blocked the output, handle appropriately
        if results.get("blocked", False):
            logger.warning(f"Tool output blocked by guardrail: {results['blocking_reason']}")
            return {
                "error": f"Output blocked by {results['blocking_guardrail']}: {results['blocking_reason']}",
                "original_request": {"args": args, "kwargs": kwargs}
            }
        
        return guarded_output
