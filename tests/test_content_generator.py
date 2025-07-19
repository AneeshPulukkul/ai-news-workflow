#!/usr/bin/env python3
"""
Test script for the content generator functionality
"""

import sys
import os
import unittest
import logging
from unittest.mock import patch, MagicMock
from typing import List, Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from content_generator.content_generator import ContentGenerator, ContentDatabase
from scrapers.news_scraper import NewsAggregator, NewsDatabase

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestContentGenerator(unittest.TestCase):
    """Test cases for the content generator"""
    
    def setUp(self):
        """Set up test environment"""
        # Create a news database with test data
        self.news_db = NewsDatabase(':memory:')
        
        # Create test articles
        self.test_articles = [
            {
                'title': 'Test Technology Article 1',
                'url': 'https://example.com/tech1',
                'content': 'This is test content about AI and machine learning advancements.',
                'source': 'Tech News',
                'category': 'technology',
                'published_date': '2023-06-01',
                'author': 'Tech Author',
                'keywords': ['AI', 'machine learning', 'technology']
            },
            {
                'title': 'Test Technology Article 2',
                'url': 'https://example.com/tech2',
                'content': 'Cloud computing continues to evolve with new serverless architectures.',
                'source': 'Tech Journal',
                'category': 'technology',
                'published_date': '2023-06-02',
                'author': 'Cloud Expert',
                'keywords': ['cloud', 'serverless', 'technology']
            },
            {
                'title': 'Test Leadership Article',
                'url': 'https://example.com/leadership1',
                'content': 'Effective leadership strategies for remote teams in the digital age.',
                'source': 'Leadership Today',
                'category': 'leadership',
                'published_date': '2023-06-03',
                'author': 'Leadership Guru',
                'keywords': ['leadership', 'remote work', 'management']
            }
        ]
        
        # Save test articles to the database
        self.news_db.save_articles(self.test_articles)
        
        # Create a content database for testing
        self.content_db = ContentDatabase(':memory:')
        
        # Initialize the content generator with mocked LLM
        self.generator = ContentGenerator(news_db_path=':memory:', content_db_path=':memory:')
    
    @patch('content_generator.content_generator.OpenAI')
    def test_generate_article(self, mock_openai):
        """Test article generation"""
        # Mock the OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = '''
        {
            "title": "The Future of AI and Machine Learning",
            "content": "Artificial Intelligence and Machine Learning continue to transform industries...",
            "summary": "An overview of recent AI advancements",
            "keywords": ["AI", "machine learning", "future technology"]
        }
        '''
        mock_openai.return_value.chat.completions.create.return_value = mock_completion
        
        # Test article generation
        source_articles = self.news_db.get_articles_by_category('technology')
        generated_article = self.generator.generate_article(source_articles)
        
        # Verify the result
        self.assertIsInstance(generated_article, dict)
        self.assertIn('title', generated_article)
        self.assertIn('content', generated_article)
        self.assertIn('summary', generated_article)
        self.assertIn('keywords', generated_article)
    
    @patch('content_generator.content_generator.OpenAI')
    def test_generate_social_media_post(self, mock_openai):
        """Test social media post generation"""
        # Mock the OpenAI response
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = '''
        {
            "platform": "twitter",
            "content": "Exciting developments in #AI and #MachineLearning are transforming industries. Check out our latest article!",
            "hashtags": ["AI", "MachineLearning", "Technology"]
        }
        '''
        mock_openai.return_value.chat.completions.create.return_value = mock_completion
        
        # Test post generation
        source_article = self.test_articles[0]
        generated_post = self.generator.generate_social_media_post(source_article)
        
        # Verify the result
        self.assertIsInstance(generated_post, dict)
        self.assertIn('platform', generated_post)
        self.assertIn('content', generated_post)
        self.assertIn('hashtags', generated_post)
    
    @patch('content_generator.content_generator.ContentGenerator.generate_article')
    @patch('content_generator.content_generator.ContentGenerator.generate_social_media_post')
    def test_generate_daily_content(self, mock_generate_post, mock_generate_article):
        """Test daily content generation workflow"""
        # Mock the article generation
        mock_generate_article.return_value = {
            'title': 'Test Generated Article',
            'content': 'This is test generated content',
            'summary': 'Test summary',
            'keywords': ['test', 'article']
        }
        
        # Mock the post generation
        mock_generate_post.return_value = {
            'platform': 'twitter',
            'content': 'Test social media post',
            'hashtags': ['test', 'social']
        }
        
        # Test daily content generation for technology category
        result = self.generator.generate_daily_content('technology')
        
        # Verify the result
        self.assertIsInstance(result, dict)
        self.assertIn('articles', result)
        self.assertIn('posts', result)
        self.assertIn('generation_summary', result)
        
        # Check if mocks were called
        self.assertTrue(mock_generate_article.called)
        self.assertTrue(mock_generate_post.called)

class TestContentDatabase(unittest.TestCase):
    """Test cases for the content database"""
    
    def setUp(self):
        """Set up test environment"""
        # Use an in-memory database for testing
        self.db = ContentDatabase(':memory:')
    
    def test_save_and_retrieve_content(self):
        """Test saving and retrieving generated content"""
        # Create test articles and posts
        test_content = {
            'articles': [
                {
                    'title': 'Test Generated Article 1',
                    'content': 'This is test generated content 1',
                    'summary': 'Test summary 1',
                    'keywords': ['test', 'article', '1'],
                    'category': 'technology',
                    'source_articles': [{'url': 'https://example.com/tech1'}]
                },
                {
                    'title': 'Test Generated Article 2',
                    'content': 'This is test generated content 2',
                    'summary': 'Test summary 2',
                    'keywords': ['test', 'article', '2'],
                    'category': 'leadership',
                    'source_articles': [{'url': 'https://example.com/leadership1'}]
                }
            ],
            'posts': [
                {
                    'platform': 'twitter',
                    'content': 'Test social media post 1',
                    'hashtags': ['test', 'social', '1'],
                    'article_title': 'Test Generated Article 1'
                },
                {
                    'platform': 'linkedin',
                    'content': 'Test social media post 2',
                    'hashtags': ['test', 'social', '2'],
                    'article_title': 'Test Generated Article 2'
                }
            ]
        }
        
        # Save content
        self.db.save_generated_content(test_content)
        
        # Retrieve content
        all_content = self.db.get_all_content()
        pending_content = self.db.get_pending_content()
        
        # Assert expectations
        self.assertEqual(len(all_content['articles']), 2)
        self.assertEqual(len(all_content['posts']), 2)
        self.assertEqual(len(pending_content['articles']), 2)
        self.assertEqual(len(pending_content['posts']), 2)
        
        # Test status updates
        self.db.update_article_status(1, 'approved', 'Good article')
        self.db.update_post_status(1, 'approved', 'Good post')
        
        # Check updated content
        updated_pending = self.db.get_pending_content()
        self.assertEqual(len(updated_pending['articles']), 1)
        self.assertEqual(len(updated_pending['posts']), 1)

if __name__ == "__main__":
    unittest.main()
