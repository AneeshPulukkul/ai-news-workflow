"""
News scraping tools for the Agentic News Workflow System
Adapts existing scrapers to LangChain tool format
"""

import os
import json
import sys
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.base import NewsWorkflowTool
from scrapers.news_scraper import NewsAggregator, NewsDatabase

class NewsScrapeInput(BaseModel):
    """Input schema for news scraping tools"""
    category: Optional[str] = Field(
        None, 
        description="Optional category to filter sources (e.g., 'technology', 'business')"
    )
    max_articles: int = Field(
        10, 
        description="Maximum number of articles to scrape per source"
    )

class NewsScrapingTool(NewsWorkflowTool):
    """Tool for scraping news from configured sources"""
    
    name = "news_scraper"
    description = "Scrapes news articles from configured sources. Optionally filter by category."
    
    def __init__(self):
        """Initialize with the NewsAggregator"""
        super().__init__(name=self.name, description=self.description)
        self.news_aggregator = NewsAggregator()
    
    def _run(self, category: Optional[str] = None, max_articles: int = 10) -> Dict[str, Any]:
        """
        Run the news scraping workflow
        
        Args:
            category: Optional category to filter sources
            max_articles: Maximum number of articles to scrape per source
            
        Returns:
            Dictionary with scraping results
        """
        # Override max articles in config temporarily
        from config.config import SCRAPING_CONFIG
        original_max = SCRAPING_CONFIG['max_articles_per_source']
        SCRAPING_CONFIG['max_articles_per_source'] = max_articles
        
        try:
            # If category provided, only scrape that category
            if category:
                from config.config import NEWS_SOURCES
                if category not in NEWS_SOURCES:
                    return {"error": f"Category '{category}' not found in configuration"}
                
                # Create a new dict with just the requested category
                filtered_sources = {category: NEWS_SOURCES[category]}
                articles_by_category = {}
                
                for cat, sources in filtered_sources.items():
                    articles_by_category[cat] = []
                    for source in sources:
                        if source.get('rss_feed'):
                            rss_articles = self.news_aggregator.rss_scraper.scrape_rss_feed(
                                source['rss_feed'], cat, source['name']
                            )
                            articles_by_category[cat].extend(rss_articles)
                        
                        if not source.get('rss_feed') or len(articles_by_category[cat]) < 3:
                            web_articles = self.news_aggregator.web_scraper.scrape_website(source, cat)
                            articles_by_category[cat].extend(web_articles)
                    
                    api_articles = self.news_aggregator.api_scraper.scrape_newsapi_org(cat)
                    articles_by_category[cat].extend(api_articles)
            else:
                # Scrape all categories
                articles_by_category = self.news_aggregator.scrape_all_sources()
            
            # Save to database
            total_saved = self.news_aggregator.save_articles_to_database(articles_by_category)
            
            # Prepare result
            result = {
                "success": True,
                "total_articles_scraped": sum(len(articles) for articles in articles_by_category.values()),
                "total_articles_saved": total_saved,
                "articles_by_category": {
                    cat: len(articles) for cat, articles in articles_by_category.items()
                }
            }
            
            return result
            
        finally:
            # Restore original config
            SCRAPING_CONFIG['max_articles_per_source'] = original_max

class NewsRetrievalTool(NewsWorkflowTool):
    """Tool for retrieving news articles from the database"""
    
    name = "news_retriever"
    description = "Retrieves news articles from the database. Optionally filter by category and time range."
    
    def __init__(self):
        """Initialize with the NewsDatabase"""
        super().__init__(name=self.name, description=self.description)
        self.news_database = NewsDatabase()
    
    def _run(self, category: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
        """
        Retrieve news articles from the database
        
        Args:
            category: Optional category to filter articles
            days: Number of days to look back
            
        Returns:
            List of article dictionaries
        """
        articles = self.news_database.get_recent_articles(category, days)
        
        # Return a simplified version for better readability
        simplified_articles = []
        for article in articles:
            simplified_articles.append({
                "title": article["title"],
                "source": article["source"],
                "category": article["category"],
                "url": article["url"],
                "published_date": article["published_date"],
                "summary": article["summary"],
                "keywords": article["keywords"]
            })
        
        return simplified_articles

class NewsStatsTool(NewsWorkflowTool):
    """Tool for getting statistics about scraped news articles"""
    
    name = "news_stats"
    description = "Gets statistics about scraped news articles from the database."
    
    def __init__(self):
        """Initialize with the NewsDatabase"""
        super().__init__(name=self.name, description=self.description)
        self.news_database = NewsDatabase()
    
    def _run(self) -> Dict[str, Any]:
        """
        Get statistics about scraped news articles
        
        Returns:
            Dictionary with statistics
        """
        source_stats = self.news_database.get_source_stats()
        
        # Get total articles
        total_articles = sum(source_stats.values())
        
        result = {
            "total_articles": total_articles,
            "sources": source_stats
        }
        
        return result
