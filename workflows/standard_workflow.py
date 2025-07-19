"""
Standard News-to-Content Workflow
Orchestrates the process from scraping news to generating content
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflows.base_workflow import BaseWorkflow
from agents.news_gathering_agent import NewsGatheringAgent
from agents.content_creation_agent import ContentCreationAgent
from agents.fact_checking_agent import FactCheckingAgent

from config.config import LOGGING_CONFIG

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOGGING_CONFIG['level']),
    format=LOGGING_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOGGING_CONFIG['file_path']),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class StandardNewsToContentWorkflow(BaseWorkflow):
    """Standard workflow from news scraping to content generation"""
    
    def __init__(self, verbose: bool = False):
        """Initialize the workflow with its component agents"""
        super().__init__(
            name="StandardNewsToContentWorkflow",
            description="Orchestrates the process from scraping news to generating content"
        )
        
        # Initialize agents
        self.news_agent = NewsGatheringAgent(verbose=verbose)
        self.content_agent = ContentCreationAgent(verbose=verbose)
        self.fact_agent = FactCheckingAgent(verbose=verbose)
        
        self.verbose = verbose
    
    def run(
        self,
        categories: List[str],
        articles_per_category: int = 2,
        generate_social_posts: bool = True,
        verify_facts: bool = True
    ) -> Dict[str, Any]:
        """
        Run the complete workflow
        
        Args:
            categories: List of news categories to process
            articles_per_category: Number of articles to generate per category
            generate_social_posts: Whether to generate social media posts
            verify_facts: Whether to verify facts in generated articles
            
        Returns:
            Dictionary with workflow results
        """
        logger.info(f"Starting {self.name} workflow")
        start_time = datetime.now()
        
        results = {
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "categories": categories,
            "scraping_results": {},
            "article_generation_results": {},
            "fact_checking_results": {},
            "social_post_results": {},
            "total_articles_generated": 0,
            "total_posts_generated": 0
        }
        
        try:
            # Step 1: Scrape news for all requested categories
            for category in categories:
                logger.info(f"Scraping news for category: {category}")
                scrape_result = self.news_agent.scrape_news(category=category)
                results["scraping_results"][category] = scrape_result
            
            # Step 2: Generate articles for each category
            all_generated_article_ids = []
            for category in categories:
                logger.info(f"Generating articles for category: {category}")
                generation_result = self.content_agent.generate_articles(
                    category=category,
                    num_articles=articles_per_category
                )
                results["article_generation_results"][category] = generation_result
                
                # Extract article IDs for later use
                if "articles" in generation_result and isinstance(generation_result["articles"], list):
                    article_ids = [article.get("id") for article in generation_result["articles"] if article.get("id")]
                    all_generated_article_ids.extend(article_ids)
                    results["total_articles_generated"] += len(article_ids)
            
            # Step 3: Verify facts in generated articles (if requested)
            if verify_facts and all_generated_article_ids:
                logger.info(f"Verifying facts in {len(all_generated_article_ids)} articles")
                fact_results = {}
                for article_id in all_generated_article_ids:
                    verification_result = self.fact_agent.verify_article(article_id=article_id)
                    fact_results[article_id] = verification_result
                results["fact_checking_results"] = fact_results
            
            # Step 4: Generate social media posts (if requested)
            if generate_social_posts and all_generated_article_ids:
                logger.info(f"Generating social posts for {len(all_generated_article_ids)} articles")
                post_result = self.content_agent.generate_social_posts(
                    article_ids=all_generated_article_ids
                )
                results["social_post_results"] = post_result
                
                if "posts" in post_result and isinstance(post_result["posts"], list):
                    results["total_posts_generated"] = len(post_result["posts"])
            
            # Complete the results
            results["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results["success"] = True
            
            logger.info(f"Workflow completed successfully in {datetime.now() - start_time}")
            return results
            
        except Exception as e:
            logger.error(f"Error in workflow: {e}")
            results["success"] = False
            results["error"] = str(e)
            results["end_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return results
