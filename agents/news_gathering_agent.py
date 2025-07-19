"""
News Gathering Agent for the Agentic News Workflow System
Specializes in collecting and analyzing news content
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
from tools.news_tools import NewsScrapingTool, NewsRetrievalTool, NewsStatsTool

class NewsGatheringAgent(BaseNewsAgent):
    """Agent specialized in gathering and analyzing news content"""
    
    def __init__(
        self,
        llm_model: str = "gpt-3.5-turbo",
        memory: Optional[ConversationBufferMemory] = None,
        verbose: bool = False
    ):
        """Initialize the news gathering agent with its specialized tools"""
        # Create the tools for this agent
        tools = [
            NewsScrapingTool(),
            NewsRetrievalTool(),
            NewsStatsTool()
        ]
        
        # Initialize the base agent
        super().__init__(
            name="NewsGatheringAgent",
            description="Specialized agent for gathering and analyzing news content from various sources",
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
    
    def scrape_news(self, category: Optional[str] = None, max_articles: int = 10) -> Dict[str, Any]:
        """
        Scrape news for a specific category
        
        Args:
            category: Optional category to filter sources
            max_articles: Maximum number of articles to scrape per source
            
        Returns:
            Dictionary with scraping results
        """
        prompt = f"Scrape the latest news"
        if category:
            prompt += f" for the category '{category}'"
        prompt += f", with a maximum of {max_articles} articles per source."
        
        return self.run(prompt)
    
    def get_recent_articles(self, category: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get recent articles from the database
        
        Args:
            category: Optional category to filter articles
            days: Number of days to look back
            
        Returns:
            List of article dictionaries
        """
        prompt = f"Retrieve articles from the past {days} days"
        if category:
            prompt += f" in the '{category}' category"
        
        return self.run(prompt)
    
    def analyze_news_trends(self) -> Dict[str, Any]:
        """
        Analyze trends in the news data
        
        Returns:
            Dictionary with analysis results
        """
        prompt = "Analyze the current news trends based on our database statistics."
        
        return self.run(prompt)
