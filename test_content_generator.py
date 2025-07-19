#!/usr/bin/env python3
"""
Test script for the content generator functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from content_generator.content_generator import ContentGenerator, ContentDatabase
from scrapers.news_scraper import NewsAggregator
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_content_generation():
    """Test the content generation functionality"""
    logger.info("Testing content generation...")
    
    # First, ensure we have some articles in the database
    aggregator = NewsAggregator()
    
    # Check if we have recent articles
    recent_articles = aggregator.get_daily_articles()
    
    if not recent_articles:
        logger.info("No recent articles found, running scraper first...")
        # Run a quick scraping to get some articles
        from scrapers.news_scraper import RSSFeedScraper
        
        rss_scraper = RSSFeedScraper()
        
        # Get a few articles from TechCrunch
        tech_articles = rss_scraper.scrape_rss_feed(
            'https://techcrunch.com/feed/', 'technology', 'TechCrunch'
        )
        
        if tech_articles:
            # Save to database
            all_articles = {'technology': tech_articles[:3]}  # Limit to 3 for testing
            aggregator.save_articles_to_database(all_articles)
            logger.info(f"Scraped and saved {len(tech_articles[:3])} articles for testing")
        else:
            logger.error("Could not scrape any articles for testing")
            return False
    
    # Now test content generation
    generator = ContentGenerator()
    content_db = ContentDatabase()
    
    logger.info("Generating content from recent articles...")
    
    # Generate content for technology category
    result = generator.generate_daily_content('technology')
    
    if result['articles']:
        logger.info(f"Generated {len(result['articles'])} articles")
        for article in result['articles']:
            logger.info(f"Article: {article['title']}")
            logger.info(f"Word count: {article['word_count']}")
            logger.info(f"Based on {article['source_count']} source articles")
            logger.info("---")
    
    if result['posts']:
        logger.info(f"Generated {len(result['posts'])} social media posts")
        for post in result['posts']:
            logger.info(f"{post['platform'].title()} post ({post['character_count']} chars):")
            logger.info(f"Content: {post['content'][:100]}...")
            logger.info("---")
    
    # Save generated content
    if result['articles'] or result['posts']:
        success = content_db.save_generated_content(result)
        if success:
            logger.info("Successfully saved generated content to database")
        else:
            logger.error("Failed to save generated content")
    
    # Test retrieving pending content
    pending_content = content_db.get_pending_content()
    logger.info(f"Pending content: {len(pending_content['articles'])} articles, {len(pending_content['posts'])} posts")
    
    return True

def test_individual_generation():
    """Test individual content generation functions"""
    logger.info("Testing individual generation functions...")
    
    generator = ContentGenerator()
    
    # Create sample articles for testing
    sample_articles = [
        {
            'title': 'AI Breakthrough in Natural Language Processing',
            'content': 'Researchers at leading tech companies have announced significant breakthroughs in natural language processing, with new models showing unprecedented understanding of context and nuance. The developments could revolutionize how we interact with AI systems.',
            'source': 'TechCrunch',
            'category': 'technology',
            'url': 'https://example.com/ai-breakthrough',
            'keywords': ['artificial intelligence', 'natural language processing', 'machine learning']
        },
        {
            'title': 'Leadership Strategies for Remote Teams',
            'content': 'As remote work becomes the norm, leaders are adapting their management styles to effectively guide distributed teams. New research shows that successful remote leaders focus on clear communication, trust-building, and outcome-based performance metrics.',
            'source': 'Harvard Business Review',
            'category': 'leadership',
            'url': 'https://example.com/remote-leadership',
            'keywords': ['leadership', 'remote work', 'team management']
        }
    ]
    
    # Test article generation
    logger.info("Testing article generation...")
    generated_article = generator.generate_article('technology', [sample_articles[0]])
    
    if generated_article:
        logger.info(f"Generated article title: {generated_article['title']}")
        logger.info(f"Word count: {generated_article['word_count']}")
        logger.info(f"Content preview: {generated_article['content'][:200]}...")
        
        # Test social post generation
        logger.info("Testing social post generation...")
        social_posts = generator.generate_social_posts(generated_article)
        
        for platform, post in social_posts.items():
            logger.info(f"{platform.title()} post: {post['content'][:100]}...")
    
    return True

if __name__ == "__main__":
    logger.info("Starting content generator tests...")
    
    try:
        # Test individual functions first
        test_individual_generation()
        
        # Test full content generation workflow
        test_content_generation()
        
        logger.info("All content generation tests completed successfully!")
    
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

