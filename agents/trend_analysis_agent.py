"""
Trend Analysis Agent for the Agentic News Workflow System
Specializes in analyzing news trends and making recommendations
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
from tools.news_tools import NewsRetrievalTool, NewsStatsTool
from tools.content_tools import ContentStatsTool

class TrendAnalysisAgent(BaseNewsAgent):
    """Agent specialized in analyzing news trends and making recommendations"""
    
    def __init__(
        self,
        llm_model: str = "gpt-4",  # Using a more capable model for analysis
        memory: Optional[ConversationBufferMemory] = None,
        verbose: bool = False
    ):
        """Initialize the trend analysis agent with its specialized tools"""
        # Create the tools for this agent
        tools = [
            NewsRetrievalTool(),
            NewsStatsTool(),
            ContentStatsTool()
        ]
        
        # Initialize the base agent
        super().__init__(
            name="TrendAnalysisAgent",
            description="Specialized agent for analyzing news trends and making content recommendations",
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
    
    def analyze_trends(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze news trends from the past days
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        prompt = f"""
        Analyze news trends from the past {days} days.
        First, get news statistics to understand the distribution of articles.
        Then, get a sample of recent articles to identify common topics and themes.
        Identify emerging trends, recurring topics, and patterns in the news coverage.
        Summarize the key trends and provide insights.
        """
        
        return self.run(prompt)
    
    def recommend_content(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Recommend content ideas based on current trends
        
        Args:
            category: Optional category to focus recommendations on
            
        Returns:
            Dictionary with content recommendations
        """
        prompt = "Recommend content ideas based on current news trends"
        if category:
            prompt += f" in the '{category}' category"
        prompt += """
        First, analyze recent news trends.
        Then, identify gaps or opportunities for new content.
        Consider which topics are gaining traction but not yet saturated.
        Suggest specific article ideas, angles, or approaches.
        """
        
        return self.run(prompt)
    
    def compare_performance(self, days: int = 30) -> Dict[str, Any]:
        """
        Compare performance of different content categories
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with performance comparison
        """
        prompt = f"""
        Compare the performance of different content categories over the past {days} days.
        First, get content statistics to understand the distribution and metrics.
        Analyze which categories have the most articles and engagement.
        Identify trends in content production and performance.
        Provide insights and recommendations for content strategy.
        """
        
        return self.run(prompt)
