"""
Content Safety Guardrail for detecting and filtering harmful content.
"""
from typing import Any, Dict, List, Optional, Tuple, Union
import logging
import re
from .base_guardrail import BaseGuardrail

logger = logging.getLogger(__name__)

class ContentSafetyGuardrail(BaseGuardrail):
    """
    Guardrail to detect and filter potentially harmful content.
    
    This guardrail can use various methods to assess content safety:
    1. Basic keyword/pattern matching
    2. External content moderation APIs (e.g. Perspective API)
    3. LLM-based content evaluation
    
    Based on the assessment, it can block, modify, or pass through content.
    """
    
    def __init__(
        self, 
        categories: List[str] = None, 
        threshold: float = 0.8,
        use_external_api: bool = False,
        llm_service = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the content safety guardrail.
        
        Args:
            categories: Categories of harmful content to check for
            threshold: Confidence threshold for blocking content (0.0 to 1.0)
            use_external_api: Whether to use external content moderation APIs
            llm_service: LLM service for content evaluation (if using LLM approach)
            config: Additional configuration
        """
        super().__init__(
            name="content_safety",
            description="Detects and filters harmful or inappropriate content",
            config=config or {}
        )
        self.categories = categories or ["hate", "harassment", "self-harm", "sexual", "violence", "misleading"]
        self.threshold = threshold
        self.use_external_api = use_external_api
        self.llm_service = llm_service
        
        # Load dictionaries of harmful patterns (simplified example)
        self.harmful_patterns = self._load_harmful_patterns()
    
    def _load_harmful_patterns(self) -> Dict[str, List[str]]:
        """Load patterns of harmful content by category."""
        # In a real implementation, these would be more extensive and nuanced
        return {
            "hate": [
                r'\b(hate|hateful|hating)\b.*\b(group|race|gender|religion|orientation)\b',
                # More patterns would be defined here
            ],
            "harassment": [
                r'\b(harass|bully|intimidate|threaten|attack)\b.*\b(person|individual|you)\b',
                # More patterns would be defined here
            ],
            "self-harm": [
                r'\b(suicide|self-harm|hurt (yourself|myself|themselves))\b',
                # More patterns would be defined here
            ],
            "sexual": [
                r'\b(explicit|graphic)\b.*\b(sexual|content)\b',
                # More patterns would be defined here
            ],
            "violence": [
                r'\b(kill|murder|attack|hurt|harm)\b.*\b(people|person|group)\b',
                # More patterns would be defined here
            ],
            "misleading": [
                r'\b(fake news|propaganda|conspiracy|hoax)\b',
                # More patterns would be defined here
            ]
        }
    
    def process(self, content: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process content through the safety guardrail.
        
        Args:
            content: The text content to check
            
        Returns:
            Tuple containing:
                - The processed content (may be filtered/modified)
                - A result dictionary with metadata about the processing
        """
        self.metrics["invocations"] += 1
        
        # Analyze the content
        if isinstance(content, str):
            analysis_result = self._analyze_text_content(content)
        else:
            # Handle structured content
            analysis_result = self._analyze_structured_content(content)
        
        # Determine if content should be blocked
        if self.should_block(analysis_result):
            self.metrics["blocks"] += 1
            self.log_event("block", {
                "categories": analysis_result["flagged_categories"],
                "scores": analysis_result["category_scores"]
            })
            return content, {
                "blocked": True,
                "reason": f"Content flagged for: {', '.join(analysis_result['flagged_categories'])}",
                "analysis": analysis_result
            }
        
        # If content needs modification
        if analysis_result["needs_modification"]:
            modified_content = self._modify_content(content, analysis_result)
            self.metrics["modifications"] += 1
            self.log_event("modify", {
                "categories": analysis_result["flagged_categories"],
                "scores": analysis_result["category_scores"]
            })
            return modified_content, {
                "modified": True,
                "reason": f"Content modified for: {', '.join(analysis_result['flagged_categories'])}",
                "analysis": analysis_result
            }
        
        # Content passes the guardrail
        self.metrics["passes"] += 1
        self.log_event("pass", {
            "scores": analysis_result["category_scores"]
        })
        return content, {
            "passed": True,
            "analysis": analysis_result
        }
    
    def _analyze_text_content(self, text: str) -> Dict[str, Any]:
        """
        Analyze text content for safety concerns.
        
        This implementation uses a multi-layered approach:
        1. Pattern matching (fast initial check)
        2. External API (if configured)
        3. LLM-based analysis (if configured)
        
        Returns:
            Analysis result with scores and flags
        """
        result = {
            "category_scores": {},
            "flagged_categories": [],
            "needs_modification": False,
            "overall_safety_score": 1.0  # Start with perfect score
        }
        
        # 1. Basic pattern matching
        for category, patterns in self.harmful_patterns.items():
            if category not in self.categories:
                continue
                
            category_score = 0.0
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    # Simple scoring based on number of matches
                    pattern_score = min(1.0, len(matches) * 0.2)  
                    category_score = max(category_score, pattern_score)
            
            result["category_scores"][category] = category_score
            if category_score >= self.threshold:
                result["flagged_categories"].append(category)
                result["needs_modification"] = True
        
        # 2. External API (if configured)
        if self.use_external_api and not result["flagged_categories"]:
            api_results = self._check_external_api(text)
            # Merge results
            for category, score in api_results["category_scores"].items():
                if category in self.categories:
                    current_score = result["category_scores"].get(category, 0.0)
                    result["category_scores"][category] = max(current_score, score)
                    if score >= self.threshold and category not in result["flagged_categories"]:
                        result["flagged_categories"].append(category)
                        result["needs_modification"] = True
        
        # 3. LLM-based analysis (if configured)
        if self.llm_service and not result["flagged_categories"]:
            llm_results = self._analyze_with_llm(text)
            # Merge results
            for category, score in llm_results["category_scores"].items():
                if category in self.categories:
                    current_score = result["category_scores"].get(category, 0.0)
                    result["category_scores"][category] = max(current_score, score)
                    if score >= self.threshold and category not in result["flagged_categories"]:
                        result["flagged_categories"].append(category)
                        result["needs_modification"] = True
        
        # Calculate overall safety score (lower is less safe)
        if result["category_scores"]:
            max_unsafe_score = max(result["category_scores"].values())
            result["overall_safety_score"] = 1.0 - max_unsafe_score
        
        return result
    
    def _analyze_structured_content(self, content: Any) -> Dict[str, Any]:
        """Analyze structured content (like JSON objects)."""
        # For demonstration, we'll convert to string and use text analysis
        # In a real implementation, this would be more sophisticated
        if hasattr(content, '__str__'):
            return self._analyze_text_content(str(content))
        return {"category_scores": {}, "flagged_categories": [], "needs_modification": False, "overall_safety_score": 1.0}
    
    def _check_external_api(self, text: str) -> Dict[str, Any]:
        """Check content using external content moderation API."""
        # This would call an external API like Perspective API
        # Simplified mock implementation for demonstration
        logger.info("Calling external content moderation API (mock)")
        return {
            "category_scores": {
                # Mock scores - would come from the API in reality
                "hate": 0.1,
                "harassment": 0.05,
                "self-harm": 0.01,
                "sexual": 0.02,
                "violence": 0.03,
                "misleading": 0.2
            }
        }
    
    def _analyze_with_llm(self, text: str) -> Dict[str, Any]:
        """Use LLM to analyze content for safety concerns."""
        # This would prompt the LLM to evaluate the safety of the content
        # Simplified mock implementation for demonstration
        logger.info("Using LLM for content safety analysis (mock)")
        return {
            "category_scores": {
                # Mock scores - would come from LLM analysis in reality
                "hate": 0.05,
                "harassment": 0.03,
                "self-harm": 0.01,
                "sexual": 0.02,
                "violence": 0.04,
                "misleading": 0.15
            }
        }
    
    def should_block(self, analysis_result: Dict[str, Any]) -> bool:
        """
        Determine if content should be blocked based on analysis.
        
        Args:
            analysis_result: The result of analyzing the content
            
        Returns:
            True if content should be blocked, False otherwise
        """
        # Block if any category exceeds the extreme threshold (0.9 by default)
        extreme_threshold = self.config.get("extreme_threshold", 0.9)
        for category, score in analysis_result.get("category_scores", {}).items():
            if score >= extreme_threshold:
                return True
        
        # Also block if multiple categories are flagged above the regular threshold
        if len(analysis_result.get("flagged_categories", [])) >= 2:
            return True
        
        return False
    
    def _modify_content(self, content: str, analysis_result: Dict[str, Any]) -> str:
        """
        Modify content to address safety concerns.
        
        This could involve:
        - Redacting specific harmful phrases
        - Adding warning labels
        - Rephrasing using an LLM
        
        Args:
            content: Original content
            analysis_result: Analysis results with flagged categories
            
        Returns:
            Modified content
        """
        # For simplicity, we'll just add a warning label
        # In a real implementation, this would be more sophisticated
        warning = "\n\n[CONTENT WARNING: This content may contain "
        warning += ", ".join(analysis_result["flagged_categories"])
        warning += ". Proceed with caution.]\n\n"
        
        # If we have an LLM service, we could use it to rewrite problematic sections
        if self.llm_service:
            # This would be implemented with actual LLM calls
            pass
        
        return warning + content
