"""
Content Creation Agent for the Agentic News Workflow System
Specializes in generating articles and social media posts from news content
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
from tools.content_tools import ContentGenerationTool, SocialPostGenerationTool, ContentRetrievalTool, ContentStatsTool
from tools.news_tools import NewsRetrievalTool

class ContentCreationAgent(BaseNewsAgent):
    """Agent specialized in generating content from news articles"""
    
    def __init__(
        self,
        llm_model: str = "gpt-3.5-turbo",
        memory: Optional[ConversationBufferMemory] = None,
        verbose: bool = False
    ):
        """Initialize the content creation agent with its specialized tools"""
        # Create the tools for this agent
        tools = [
            ContentGenerationTool(),
            SocialPostGenerationTool(),
            ContentRetrievalTool(),
            ContentStatsTool(),
            NewsRetrievalTool()  # Include this to get source articles
        ]
        
        # Initialize the base agent
        super().__init__(
            name="ContentCreationAgent",
            description="Specialized agent for generating articles and social media posts from news content",
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
    
    def generate_articles(
        self,
        category: str,
        num_articles: int = 1,
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate articles from news in a specific category
        
        Args:
            category: Category of news to generate content for
            num_articles: Number of articles to generate
            sources: Optional list of source names to focus on
            
        Returns:
            Dictionary with generation results
        """
        prompt = f"Generate {num_articles} articles for the '{category}' category"
        if sources:
            prompt += f" focusing on these sources: {', '.join(sources)}"
        
        return self.run(prompt)
    
    def generate_social_posts(
        self,
        article_ids: List[int],
        platforms: List[str] = ["twitter", "linkedin"]
    ) -> Dict[str, Any]:
        """
        Generate social media posts from articles
        
        Args:
            article_ids: IDs of articles to generate social posts for
            platforms: Social media platforms to generate posts for
            
        Returns:
            Dictionary with generation results
        """
        prompt = f"Generate social media posts for articles with IDs {article_ids} "
        prompt += f"for these platforms: {', '.join(platforms)}"
        
        return self.run(prompt)
    
    def get_content_stats(self) -> Dict[str, Any]:
        """
        Get statistics about generated content
        
        Returns:
            Dictionary with statistics
        """
        prompt = "Get statistics about our generated content"
        
        return self.run(prompt)
