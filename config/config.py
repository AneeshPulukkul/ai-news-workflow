"""
Configuration file for the Agentic News Workflow system
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# News Sources Configuration
NEWS_SOURCES: Dict[str, List[Dict[str, Any]]] = {
    'technology': [
        {
            'name': 'TechCrunch',
            'url': 'https://techcrunch.com/',
            'rss_feed': 'https://techcrunch.com/feed/',
            'selectors': {
                'title': 'h1.article__title',
                'content': 'div.article-content',
                'date': 'time.article__date'
            }
        },
        {
            'name': 'Ars Technica',
            'url': 'https://arstechnica.com/',
            'rss_feed': 'https://feeds.arstechnica.com/arstechnica/index',
            'selectors': {
                'title': 'h1.heading',
                'content': 'div.article-content',
                'date': 'time.date'
            }
        },
        {
            'name': 'The Verge',
            'url': 'https://www.theverge.com/',
            'rss_feed': 'https://www.theverge.com/rss/index.xml',
            'selectors': {
                'title': 'h1.duet--article--dangerously-set-cms-markup',
                'content': 'div.duet--article--article-body-component',
                'date': 'time.c-byline__item'
            }
        },
        {
            'name': 'Wired',
            'url': 'https://www.wired.com/',
            'rss_feed': 'https://www.wired.com/feed/rss',
            'selectors': {
                'title': 'h1.ContentHeaderHed-NCyCC',
                'content': 'div.ArticleBodyWrapper',
                'date': 'time.BaseWrap-sc-gjQpdd'
            }
        }
    ],
    'leadership': [
        {
            'name': 'Harvard Business Review',
            'url': 'https://hbr.org/',
            'rss_feed': 'https://feeds.hbr.org/harvardbusiness',
            'selectors': {
                'title': 'h1.article-hed',
                'content': 'div.article-body',
                'date': 'time.article-date'
            }
        },
        {
            'name': 'MIT Sloan Management Review',
            'url': 'https://sloanreview.mit.edu/',
            'rss_feed': 'https://sloanreview.mit.edu/feed/',
            'selectors': {
                'title': 'h1.entry-title',
                'content': 'div.entry-content',
                'date': 'time.entry-date'
            }
        },
        {
            'name': 'McKinsey Insights',
            'url': 'https://www.mckinsey.com/insights',
            'rss_feed': 'https://www.mckinsey.com/insights/rss',
            'selectors': {
                'title': 'h1.article-title',
                'content': 'div.article-body',
                'date': 'time.article-date'
            }
        }
    ]
}

# News API Configuration
NEWS_API_CONFIG: Dict[str, Dict[str, Any]] = {
    'newsapi_org': {
        'api_key': os.getenv('NEWSAPI_ORG_KEY', ''),
        'base_url': 'https://newsapi.org/v2/',
        'endpoints': {
            'everything': 'everything',
            'top_headlines': 'top-headlines'
        }
    },
    'newsdata_io': {
        'api_key': os.getenv('NEWSDATA_IO_KEY', ''),
        'base_url': 'https://newsdata.io/api/1/',
        'endpoints': {
            'news': 'news'
        }
    }
}

# Search Keywords for different topics
SEARCH_KEYWORDS: Dict[str, List[str]] = {
    'technology': [
        'artificial intelligence', 'machine learning', 'blockchain', 'cryptocurrency',
        'cloud computing', 'cybersecurity', 'data science', 'software development',
        'tech startup', 'innovation', 'digital transformation', 'automation'
    ],
    'leadership': [
        'leadership', 'management', 'CEO', 'executive', 'business strategy',
        'organizational culture', 'team management', 'corporate governance',
        'business transformation', 'change management', 'decision making'
    ]
}

# Scraping Configuration
SCRAPING_CONFIG: Dict[str, Any] = {
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'delay_between_requests': 2,  # seconds
    'timeout': 30,  # seconds
    'max_articles_per_source': 10,
    'max_retries': 3
}

# Database Configuration
DATABASE_CONFIG: Dict[str, Any] = {
    'type': 'sqlite',  # Can be changed to 'postgresql' or 'mongodb'
    'sqlite_path': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'news_database.db'),
    'postgresql': {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': os.getenv('DB_PORT', '5432'),
        'database': os.getenv('DB_NAME', 'news_workflow'),
        'username': os.getenv('DB_USER', 'postgres'),
        'password': os.getenv('DB_PASSWORD', '')
    }
}

# Content Generation Configuration
CONTENT_CONFIG: Dict[str, Any] = {
    'min_article_length': 500,  # words
    'max_article_length': 1000,  # words
    'min_post_length': 100,  # characters
    'max_post_length': 280,  # characters (Twitter limit)
    'topics_to_generate': ['technology', 'leadership']
}

# Notification Configuration
NOTIFICATION_CONFIG: Dict[str, Dict[str, Any]] = {
    'email': {
        'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
        'smtp_port': int(os.getenv('SMTP_PORT', '587')),
        'username': os.getenv('EMAIL_USERNAME', ''),
        'password': os.getenv('EMAIL_PASSWORD', ''),
        'from_email': os.getenv('FROM_EMAIL', ''),
        'to_email': os.getenv('TO_EMAIL', '')
    },
    'slack': {
        'webhook_url': os.getenv('SLACK_WEBHOOK_URL', ''),
        'channel': os.getenv('SLACK_CHANNEL', '#general')
    }
}

# Logging Configuration
LOGGING_CONFIG: Dict[str, Any] = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_path': os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs', 'news_workflow.log')
}

# Review Interface Configuration
REVIEW_CONFIG: Dict[str, Any] = {
    'secret_key': os.getenv('REVIEW_SECRET_KEY', 'dev-secret-key'),
    'port': int(os.getenv('REVIEW_PORT', '5000')),
    'debug': os.getenv('REVIEW_DEBUG', 'True').lower() == 'true',
    'title': 'Agentic News Workflow - Content Review'
}
