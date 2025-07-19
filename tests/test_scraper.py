#!/usr/bin/env python3
"""
Test script for the news scraper functionality
"""

import sys
import os
import unittest
import logging
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scrapers.news_scraper import NewsAggregator, RSSFeedScraper, NewsAPIScraper, WebScraper, NewsDatabase

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestRSSFeedScraper(unittest.TestCase):
    """Test cases for the RSS feed scraper"""
    
    def setUp(self):
        """Set up test environment"""
        self.scraper = RSSFeedScraper()
    
    def test_scrape_rss_feed(self):
        """Test RSS feed scraping functionality"""
        # Test with TechCrunch RSS feed
        articles = self.scraper.scrape_rss_feed(
            'https://techcrunch.com/feed/',
            'technology',
            'TechCrunch'
        )
        
        # Log some information
        logger.info(f"Scraped {len(articles)} articles from TechCrunch RSS")
        
        # Assert some basic expectations
        self.assertIsInstance(articles, list)
        if articles:
            sample_article = articles[0]
            self.assertIn('title', sample_article)
            self.assertIn('url', sample_article)
            self.assertIn('content', sample_article)
            self.assertIn('source', sample_article)
            self.assertEqual(sample_article['source'], 'TechCrunch')
            
            # Log some details for manual verification
            logger.info(f"Sample article title: {sample_article['title']}")
            logger.info(f"Sample article URL: {sample_article['url']}")
            logger.info(f"Content length: {len(sample_article['content'])} characters")

class TestNewsAggregator(unittest.TestCase):
    """Test cases for the news aggregator"""
    
    def setUp(self):
        """Set up test environment"""
        self.aggregator = NewsAggregator()
    
    def test_scrape_rss_feeds(self):
        """Test the RSS feed scraping functionality of the aggregator"""
        # Run the RSS scraping
        results = self.aggregator.scrape_rss_feeds()
        
        # Log the results
        logger.info(f"RSS scraping results: {results}")
        
        # Assert some basic expectations
        self.assertIsInstance(results, dict)
        self.assertIn('total_articles', results)
        self.assertIn('sources', results)
        self.assertIsInstance(results['sources'], dict)
    
    def test_scrape_web_pages(self):
        """Test the web scraping functionality of the aggregator"""
        # Run the web scraping (with a small limit)
        results = self.aggregator.scrape_web_pages(limit=1)
        
        # Log the results
        logger.info(f"Web scraping results: {results}")
        
        # Assert some basic expectations
        self.assertIsInstance(results, dict)
        self.assertIn('total_articles', results)
        self.assertIn('sources', results)
        self.assertIsInstance(results['sources'], dict)

class TestNewsDatabase(unittest.TestCase):
    """Test cases for the news database"""
    
    def setUp(self):
        """Set up test environment"""
        # Use an in-memory database for testing
        self.db = NewsDatabase(':memory:')
    
    def test_save_and_retrieve_articles(self):
        """Test saving and retrieving articles"""
        # Create test articles
        test_articles = [
            {
                'title': 'Test Article 1',
                'url': 'https://example.com/1',
                'content': 'This is test content 1',
                'source': 'Test Source',
                'category': 'technology',
                'published_date': '2023-06-01',
                'author': 'Test Author',
                'keywords': ['test', 'technology']
            },
            {
                'title': 'Test Article 2',
                'url': 'https://example.com/2',
                'content': 'This is test content 2',
                'source': 'Test Source',
                'category': 'leadership',
                'published_date': '2023-06-02',
                'author': 'Test Author',
                'keywords': ['test', 'leadership']
            }
        ]
        
        # Save articles
        self.db.save_articles(test_articles)
        
        # Retrieve articles
        all_articles = self.db.get_all_articles()
        recent_articles = self.db.get_recent_articles(days=30)
        tech_articles = self.db.get_articles_by_category('technology')
        
        # Assert expectations
        self.assertEqual(len(all_articles), 2)
        self.assertEqual(len(recent_articles), 2)
        self.assertEqual(len(tech_articles), 1)
        self.assertEqual(tech_articles[0]['title'], 'Test Article 1')
        
        # Test article exists
        exists = self.db.article_exists('https://example.com/1')
        self.assertTrue(exists)
        
        # Test article doesn't exist
        exists = self.db.article_exists('https://example.com/nonexistent')
        self.assertFalse(exists)

if __name__ == "__main__":
    unittest.main()
