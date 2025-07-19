"""
Content generation tools for the Agentic News Workflow System
Adapts existing content generator to LangChain tool format
"""

import os
import json
import sys
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.base import NewsWorkflowTool
from content_generator.content_generator import ContentGenerator, ContentDatabase, PromptManager, LLMService

class ArticleGenerationInput(BaseModel):
    """Input schema for article generation tool"""
    category: str = Field(
        ..., 
        description="Category of news to generate content for (e.g., 'technology', 'business')"
    )
    num_articles: int = Field(
        1, 
        description="Number of articles to generate"
    )
    sources: Optional[List[str]] = Field(
        None, 
        description="Optional list of source names to focus on"
    )

class SocialPostGenerationInput(BaseModel):
    """Input schema for social post generation tool"""
    article_ids: List[int] = Field(
        ..., 
        description="IDs of articles to generate social posts for"
    )
    platforms: List[str] = Field(
        ["twitter", "linkedin"], 
        description="Social media platforms to generate posts for"
    )

class ContentGenerationTool(NewsWorkflowTool):
    """Tool for generating articles from scraped news"""
    
    name = "article_generator"
    description = "Generates articles from scraped news. Specify category and number of articles to generate."
    
    def __init__(self):
        """Initialize with the ContentGenerator"""
        super().__init__(name=self.name, description=self.description)
        self.content_generator = ContentGenerator()
    
    def _run(
        self, 
        category: str, 
        num_articles: int = 1, 
        sources: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate articles from scraped news
        
        Args:
            category: Category of news to generate content for
            num_articles: Number of articles to generate
            sources: Optional list of source names to focus on
            
        Returns:
            Dictionary with generation results
        """
        result = self.content_generator.generate_articles(
            category=category,
            count=num_articles,
            sources=sources
        )
        
        return {
            "success": bool(result),
            "articles_generated": len(result),
            "articles": result
        }

class SocialPostGenerationTool(NewsWorkflowTool):
    """Tool for generating social media posts from articles"""
    
    name = "social_post_generator"
    description = "Generates social media posts from existing articles. Specify article IDs and platforms."
    
    def __init__(self):
        """Initialize with the ContentGenerator"""
        super().__init__(name=self.name, description=self.description)
        self.content_generator = ContentGenerator()
    
    def _run(
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
        all_posts = []
        for article_id in article_ids:
            posts = self.content_generator.generate_social_posts(
                article_id=article_id,
                platforms=platforms
            )
            all_posts.extend(posts)
        
        return {
            "success": bool(all_posts),
            "posts_generated": len(all_posts),
            "posts": all_posts
        }

class ContentRetrievalTool(NewsWorkflowTool):
    """Tool for retrieving generated content from the database"""
    
    name = "content_retriever"
    description = "Retrieves generated articles and social posts from the database."
    
    def __init__(self):
        """Initialize with the ContentDatabase"""
        super().__init__(name=self.name, description=self.description)
        self.content_database = ContentDatabase()
    
    def _run(
        self, 
        content_type: str = "articles", 
        days: int = 7,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve generated content from the database
        
        Args:
            content_type: Type of content to retrieve ('articles' or 'posts')
            days: Number of days to look back
            status: Optional status filter ('pending', 'published', 'rejected')
            
        Returns:
            List of content dictionaries
        """
        if content_type == "articles":
            return self.content_database.get_recent_articles(days=days, status=status)
        elif content_type == "posts":
            return self.content_database.get_recent_posts(days=days, status=status)
        else:
            return {"error": f"Invalid content type: {content_type}. Use 'articles' or 'posts'."}

class ContentStatsTool(NewsWorkflowTool):
    """Tool for getting statistics about generated content"""
    
    name = "content_stats"
    description = "Gets statistics about generated content from the database."
    
    def __init__(self):
        """Initialize with the ContentDatabase"""
        super().__init__(name=self.name, description=self.description)
        self.content_database = ContentDatabase()
    
    def _run(self) -> Dict[str, Any]:
        """
        Get statistics about generated content
        
        Returns:
            Dictionary with statistics
        """
        article_stats = self.content_database.get_article_stats()
        post_stats = self.content_database.get_post_stats()
        
        result = {
            "article_stats": article_stats,
            "post_stats": post_stats
        }
        
        return result
