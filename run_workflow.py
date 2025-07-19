#!/usr/bin/env python3
"""
Main workflow runner for the Agentic News Workflow System
This script orchestrates the complete workflow: scraping -> generation -> review
"""

import sys
import os
import logging
import argparse
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.news_scraper import NewsAggregator
from content_generator.content_generator import ContentGenerator, ContentDatabase
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


class WorkflowRunner:
    """Main workflow orchestrator"""
    
    def __init__(self):
        self.news_aggregator = NewsAggregator()
        self.content_generator = ContentGenerator()
        self.content_database = ContentDatabase()
    
    def run_daily_workflow(self, categories=None):
        """Run the complete daily workflow"""
        logger.info("Starting daily agentic news workflow")
        
        try:
            # Step 1: Scrape news
            logger.info("Step 1: Scraping news articles")
            scraping_result = self.news_aggregator.run_daily_scraping()
            logger.info(f"Scraping completed: {scraping_result}")
            
            # Step 2: Generate content
            logger.info("Step 2: Generating content from scraped articles")
            if categories:
                for category in categories:
                    logger.info(f"Generating content for category: {category}")
                    content_result = self.content_generator.generate_daily_content(category)
                    
                    if content_result['articles'] or content_result['posts']:
                        self.content_database.save_generated_content(content_result)
                        logger.info(f"Generated and saved: {len(content_result['articles'])} articles, {len(content_result['posts'])} posts for {category}")
            else:
                content_result = self.content_generator.generate_daily_content()
                
                if content_result['articles'] or content_result['posts']:
                    self.content_database.save_generated_content(content_result)
                    logger.info(f"Generated and saved: {len(content_result['articles'])} articles, {len(content_result['posts'])} posts")
            
            # Step 3: Report status
            pending_content = self.content_database.get_pending_content()
            logger.info(f"Workflow completed. Pending review: {len(pending_content['articles'])} articles, {len(pending_content['posts'])} posts")
            
            return {
                'success': True,
                'scraping_result': scraping_result,
                'pending_articles': len(pending_content['articles']),
                'pending_posts': len(pending_content['posts'])
            }
        
        except Exception as e:
            logger.error(f"Workflow failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def run_scraping_only(self):
        """Run only the news scraping component"""
        logger.info("Running news scraping only")
        try:
            result = self.news_aggregator.run_daily_scraping()
            logger.info(f"Scraping completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def run_generation_only(self, category=None):
        """Run only the content generation component"""
        logger.info(f"Running content generation only for category: {category or 'all'}")
        try:
            content_result = self.content_generator.generate_daily_content(category)
            
            if content_result['articles'] or content_result['posts']:
                self.content_database.save_generated_content(content_result)
                logger.info(f"Generated and saved: {len(content_result['articles'])} articles, {len(content_result['posts'])} posts")
            
            return content_result['generation_summary']
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_status(self):
        """Get current system status"""
        try:
            # Get recent articles count
            recent_articles = self.news_aggregator.get_daily_articles()
            
            # Get pending content
            pending_content = self.content_database.get_pending_content()
            
            return {
                'recent_articles': len(recent_articles),
                'pending_articles': len(pending_content['articles']),
                'pending_posts': len(pending_content['posts']),
                'last_run': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {'error': str(e)}


def main():
    """Main entry point with command line interface"""
    parser = argparse.ArgumentParser(description='Agentic News Workflow System')
    parser.add_argument('--mode', choices=['full', 'scrape', 'generate', 'status'], 
                       default='full', help='Workflow mode to run')
    parser.add_argument('--category', choices=['technology', 'leadership'], 
                       help='Category filter for content generation')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize workflow runner
    runner = WorkflowRunner()
    
    # Execute based on mode
    if args.mode == 'full':
        categories = [args.category] if args.category else None
        result = runner.run_daily_workflow(categories)
        print(f"Daily workflow result: {result}")
    
    elif args.mode == 'scrape':
        result = runner.run_scraping_only()
        print(f"Scraping result: {result}")
    
    elif args.mode == 'generate':
        result = runner.run_generation_only(args.category)
        print(f"Generation result: {result}")
    
    elif args.mode == 'status':
        status = runner.get_status()
        print(f"System status: {status}")
        result = {'success': True}
    
    return 0 if result.get('success', True) else 1


if __name__ == "__main__":
    sys.exit(main())

