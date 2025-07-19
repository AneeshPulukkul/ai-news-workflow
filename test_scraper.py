#!/usr/bin/env python3
"""
Test script for the news scraper functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.news_scraper import NewsAggregator, RSSFeedScraper
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_rss_scraper():
    """Test RSS feed scraping functionality"""
    logger.info("Testing RSS feed scraper...")
    
    scraper = RSSFeedScraper()
    
    # Test with TechCrunch RSS feed
    articles = scraper.scrape_rss_feed(
        'https://techcrunch.com/feed/',
        'technology',
        'TechCrunch'
    )
    
    logger.info(f"Scraped {len(articles)} articles from TechCrunch RSS")
    
    if articles:
        sample_article = articles[0]
        logger.info(f"Sample article title: {sample_article['title']}")
        logger.info(f"Sample article URL: {sample_article['url']}")
        logger.info(f"Sample article keywords: {sample_article['keywords']}")
        logger.info(f"Content length: {len(sample_article['content'])} characters")
    
    return articles

def test_news_aggregator():
    """Test the complete news aggregator"""
    logger.info("Testing news aggregator...")
    
    aggregator = NewsAggregator()
    
    # Run a limited test scraping (just RSS feeds to avoid overwhelming)
    logger.info("Running test scraping...")
    
    # Test just RSS scraping for now
    rss_scraper = RSSFeedScraper()
    
    # Test technology sources
    tech_articles = []
    tech_articles.extend(rss_scraper.scrape_rss_feed(
        'https://techcrunch.com/feed/', 'technology', 'TechCrunch'
    ))
    
    # Test leadership sources  
    leadership_articles = []
    leadership_articles.extend(rss_scraper.scrape_rss_feed(
        'https://feeds.hbr.org/harvardbusiness', 'leadership', 'Harvard Business Review'
    ))
    
    # Save to database
    all_articles = {'technology': tech_articles, 'leadership': leadership_articles}
    total_saved = aggregator.save_articles_to_database(all_articles)
    
    logger.info(f"Test completed. Saved {total_saved} articles to database")
    
    # Retrieve and display recent articles
    recent_articles = aggregator.get_daily_articles()
    logger.info(f"Retrieved {len(recent_articles)} recent articles from database")
    
    return recent_articles

if __name__ == "__main__":
    logger.info("Starting news scraper tests...")
    
    try:
        # Test RSS scraper
        rss_articles = test_rss_scraper()
        
        # Test full aggregator
        recent_articles = test_news_aggregator()
        
        logger.info("All tests completed successfully!")
        
        # Display summary
        if recent_articles:
            logger.info("\nRecent articles summary:")
            for article in recent_articles[:3]:  # Show first 3
                logger.info(f"- {article['title']} ({article['source']}, {article['category']})")
    
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        sys.exit(1)

