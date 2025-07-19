"""
Fact Checking Agent for the Agentic News Workflow System
Specializes in verifying facts in generated content
"""

import os
import json
import sys
from typing import Dict, List, Any, Optional, Union
from langchain.agents import AgentType, initialize_agent, Tool
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseNewsAgent
from tools.content_tools import ContentRetrievalTool
from tools.news_tools import NewsRetrievalTool

class FactCheckInput(BaseNewsAgent):
    """Input for the fact checking process"""
    article_id: int
    source_confidence_threshold: float = 0.7

class FactCheckingAgent(BaseNewsAgent):
    """Agent specialized in fact checking generated content"""
    
    def __init__(
        self,
        llm_model: str = "gpt-4", # Using a more capable model for fact checking
        memory: Optional[ConversationBufferMemory] = None,
        verbose: bool = False
    ):
        """Initialize the fact checking agent with its specialized tools"""
        # Create the tools for this agent
        tools = [
            ContentRetrievalTool(),
            NewsRetrievalTool()
        ]
        
        # Initialize the base agent
        super().__init__(
            name="FactCheckingAgent",
            description="Specialized agent for verifying facts in generated content",
            tools=tools,
            llm_model=llm_model,
            memory=memory,
            verbose=verbose
        )
        
        # Initialize the agent
        self.initialize_agent()
    
    def initialize_agent(self):
        """Initialize the LangChain agent with the tools"""
        # Convert our custom tools to LangChain Tool format
        langchain_tools = [
            Tool(
                name=tool.name,
                description=tool.description,
                func=tool._run
            ) for tool in self.tools
        ]
        
        # Create the agent
        self.agent_executor = initialize_agent(
            tools=langchain_tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=self.verbose,
            memory=self.memory
        )
    
    def verify_article(self, article_id: int, confidence_threshold: float = 0.7) -> Dict[str, Any]:
        """
        Verify facts in a generated article
        
        Args:
            article_id: ID of the article to check
            confidence_threshold: Threshold for fact confidence (0.0 to 1.0)
            
        Returns:
            Dictionary with verification results
        """
        prompt = f"""
        Verify the facts in the article with ID {article_id}. 
        Use a confidence threshold of {confidence_threshold}. 
        First, retrieve the article content. 
        Then, retrieve the source articles it was based on.
        Check if statements in the generated article are supported by the source articles.
        Identify any unsupported claims or potential inaccuracies.
        """
        
        return self.run(prompt)
    
    def verify_claim(self, claim: str, category: str) -> Dict[str, Any]:
        """
        Verify a specific claim against news sources
        
        Args:
            claim: The claim to verify
            category: The news category to check against
            
        Returns:
            Dictionary with verification results
        """
        prompt = f"""
        Verify this claim: "{claim}"
        Look for relevant articles in the '{category}' category.
        Check if the claim is supported by the articles.
        Determine if the claim is accurate, misleading, or false.
        """
        
        return self.run(prompt)
