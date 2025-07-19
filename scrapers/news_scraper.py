"""
News Scraper Module for Agentic News Workflow
Handles web scraping, RSS feed parsing, and news API integration
"""

import requests
import feedparser
import time
import logging
import json
import os
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from newspaper import Article

# Import config using sys.path for relative imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import (
    NEWS_SOURCES, NEWS_API_CONFIG, SEARCH_KEYWORDS, 
    SCRAPING_CONFIG, DATABASE_CONFIG, LOGGING_CONFIG
)

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


def _extract_keywords(text: str, category: str) -> List[str]:
    """Extract relevant keywords from article text"""
    keywords = []
    category_keywords = SEARCH_KEYWORDS.get(category, [])

    if not text:
        return keywords

    text_lower = text.lower()
    for keyword in category_keywords:
        if keyword.lower() in text_lower:
            keywords.append(keyword)

    return keywords


class NewsDatabase:
    """
    Simple SQLite database handler for storing news articles
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the news database
        
        Args:
            db_path: Optional path to database file. If None, uses path from config.
        """
        self.db_path = db_path or DATABASE_CONFIG['sqlite_path']
        self.init_database()
    
    def init_database(self) -> None:
        """Initialize the database with required tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT,
                        url TEXT UNIQUE,
                        source TEXT,
                        category TEXT,
                        published_date TEXT,
                        scraped_date TEXT,
                        keywords TEXT,
                        summary TEXT
                    )
                ''')
                conn.commit()
                logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def save_article(self, article_data: Dict[str, Any]) -> bool:
        """
        Save an article to the database
        
        Args:
            article_data: Dictionary containing article data
            
        Returns:
            bool: True if article was saved successfully, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO articles 
                    (title, content, url, source, category, published_date, scraped_date, keywords, summary)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    article_data.get('title'),
                    article_data.get('content'),
                    article_data.get('url'),
                    article_data.get('source'),
                    article_data.get('category'),
                    article_data.get('published_date'),
                    article_data.get('scraped_date'),
                    json.dumps(article_data.get('keywords', [])),
                    article_data.get('summary')
                ))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error saving article: {e}")
            return False
    
    def get_recent_articles(self, category: Optional[str] = None, days: int = 7) -> List[Dict[str, Any]]:
        """
        Retrieve recent articles from the database
        
        Args:
            category: Optional category to filter by
            days: Number of days to look back
            
        Returns:
            List of article dictionaries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT * FROM articles 
                    WHERE scraped_date >= ? 
                '''
                params = [(datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')]
                
                if category:
                    query += ' AND category = ?'
                    params.append(category)
                
                query += ' ORDER BY scraped_date DESC'
                
                cursor.execute(query, params)
                columns = [description[0] for description in cursor.description]
                articles = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                # Parse keywords back to list
                for article in articles:
                    if article['keywords']:
                        article['keywords'] = json.loads(article['keywords'])
                
                return articles
        except Exception as e:
            logger.error(f"Error retrieving articles: {e}")
            return []

    def get_source_stats(self) -> Dict[str, int]:
        """
        Get statistics on the number of articles per source.
        
        Returns:
            Dictionary with source names as keys and article counts as values.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT source, COUNT(*) as article_count
                    FROM articles
                    WHERE source IS NOT NULL
                    GROUP BY source
                    ORDER BY article_count DESC
                '''
                
                cursor.execute(query)
                stats = {source: count for source, count in cursor.fetchall()}
                return stats
        except Exception as e:
            logger.error(f"Error retrieving source stats: {e}")
            return {}


class RSSFeedScraper:
    """RSS Feed scraper for news sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': SCRAPING_CONFIG['user_agent']})
    
    def scrape_rss_feed(self, feed_url: str, category: str, source_name: str) -> List[Dict[str, Any]]:
        """
        Scrape articles from RSS feed
        
        Args:
            feed_url: URL of the RSS feed
            category: Category for the articles
            source_name: Name of the source
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        try:
            logger.info(f"Scraping RSS feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:SCRAPING_CONFIG['max_articles_per_source']]:
                try:
                    # Extract article content using newspaper3k
                    article = Article(entry.link)
                    article.download()
                    article.parse()
                    
                    article_data = {
                        'title': entry.title,
                        'content': article.text,
                        'url': entry.link,
                        'source': source_name,
                        'category': category,
                        'published_date': getattr(entry, 'published', ''),
                        'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'keywords': _extract_keywords(article.text, category),
                        'summary': entry.get('summary', article.text[:500] + '...' if len(article.text) > 500 else article.text)
                    }
                    
                    articles.append(article_data)
                    logger.info(f"Scraped article: {article_data['title'][:50]}...")
                    
                    # Respect rate limiting
                    time.sleep(SCRAPING_CONFIG['delay_between_requests'])
                    
                except Exception as e:
                    logger.error(f"Error processing RSS entry {entry.link}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping RSS feed {feed_url}: {e}")
        
        return articles


class NewsAPIScraper:
    """News API scraper for structured news data"""
    
    def __init__(self):
        self.newsapi_key = NEWS_API_CONFIG['newsapi_org']['api_key']
        self.newsdata_key = NEWS_API_CONFIG['newsdata_io']['api_key']
    
    def scrape_newsapi_org(self, category: str) -> List[Dict[str, Any]]:
        """
        Scrape articles from NewsAPI.org
        
        Args:
            category: Category to search for
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        if not self.newsapi_key:
            logger.warning("NewsAPI.org key not configured")
            return articles
        
        try:
            keywords = ' OR '.join(SEARCH_KEYWORDS[category][:5])  # Limit keywords for API
            url = f"{NEWS_API_CONFIG['newsapi_org']['base_url']}everything"
            
            params = {
                'q': keywords,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': SCRAPING_CONFIG['max_articles_per_source'],
                'apiKey': self.newsapi_key
            }
            
            response = requests.get(url, params=params, timeout=SCRAPING_CONFIG['timeout'])
            response.raise_for_status()
            
            data = response.json()
            
            for article in data.get('articles', []):
                try:
                    # Get full article content
                    full_article = Article(article['url'])
                    full_article.download()
                    full_article.parse()
                    
                    article_data = {
                        'title': article['title'],
                        'content': full_article.text or article.get('content', ''),
                        'url': article['url'],
                        'source': article['source']['name'],
                        'category': category,
                        'published_date': article['publishedAt'],
                        'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'keywords': _extract_keywords(full_article.text or article.get('content', ''), category),
                        'summary': article.get('description', '')
                    }
                    
                    articles.append(article_data)
                    logger.info(f"Scraped NewsAPI article: {article_data['title'][:50]}...")
                    
                    # Add delay to respect rate limits
                    time.sleep(SCRAPING_CONFIG['delay_between_requests'])
                    
                except Exception as e:
                    logger.error(f"Error processing NewsAPI article {article['url']}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping NewsAPI.org for {category}: {e}")
        
        return articles


class WebScraper:
    """Direct web scraper for news websites"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': SCRAPING_CONFIG['user_agent']})
    
    def scrape_website(self, source_config: Dict[str, Any], category: str) -> List[Dict[str, Any]]:
        """
        Scrape articles from a website using CSS selectors
        
        Args:
            source_config: Configuration for the source
            category: Category for the articles
            
        Returns:
            List of article dictionaries
        """
        articles = []
        
        try:
            logger.info(f"Scraping website: {source_config['name']}")
            response = self.session.get(source_config['url'], timeout=SCRAPING_CONFIG['timeout'])
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find article links using selectors from config if available
            article_links = []
            if 'selectors' in source_config and 'article_link' in source_config['selectors']:
                article_links = soup.select(source_config['selectors']['article_link'])
            else:
                # Fallback to generic link finding
                article_links = soup.find_all('a', href=True)

            article_urls = []
            
            for link in article_links:
                href = link.get('href')
                if href:
                    full_url = urljoin(source_config['url'], href)
                    # Basic filtering to avoid non-article links
                    if urlparse(full_url).path and ('article' in full_url or 'story' in full_url or '/20' in full_url):
                        if full_url not in article_urls:
                            article_urls.append(full_url)
                            if len(article_urls) >= SCRAPING_CONFIG['max_articles_per_source']:
                                break
            
            # Scrape individual articles
            for url in article_urls:
                try:
                    article = Article(url)
                    article.download()
                    article.parse()
                    
                    if len(article.text) < 100:  # Skip very short articles
                        continue
                    
                    article_data = {
                        'title': article.title,
                        'content': article.text,
                        'url': url,
                        'source': source_config['name'],
                        'category': category,
                        'published_date': article.publish_date.strftime('%Y-%m-%d %H:%M:%S') if article.publish_date else None,
                        'scraped_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'keywords': _extract_keywords(article.text, category),
                        'summary': article.summary or (article.text[:500] + '...' if len(article.text) > 500 else article.text)
                    }
                    
                    articles.append(article_data)
                    logger.info(f"Scraped web article: {article_data['title'][:50]}...")
                    
                    # Respect rate limiting
                    time.sleep(SCRAPING_CONFIG['delay_between_requests'])
                    
                except Exception as e:
                    logger.error(f"Error scraping article {url}: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"Error scraping website {source_config['name']}: {e}")
        
        return articles


class NewsAggregator:
    """Main news aggregator that coordinates all scraping methods"""
    
    def __init__(self):
        self.database = NewsDatabase()
        self.rss_scraper = RSSFeedScraper()
        self.api_scraper = NewsAPIScraper()
        self.web_scraper = WebScraper()
    
    def scrape_all_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape all configured news sources
        
        Returns:
            Dictionary of articles by category
        """
        all_articles = {}
        
        # Initialize all_articles with keys from NEWS_SOURCES
        for category in NEWS_SOURCES.keys():
            all_articles[category] = []
        
        for category, sources in NEWS_SOURCES.items():
            logger.info(f"Starting scraping for category: {category}")
            
            for source in sources:
                # Try RSS feed first
                if source.get('rss_feed'):
                    rss_articles = self.rss_scraper.scrape_rss_feed(
                        source['rss_feed'], category, source['name']
                    )
                    all_articles[category].extend(rss_articles)
                
                # Fallback to direct web scraping if RSS fails or yields few results
                if not source.get('rss_feed') or len(all_articles[category]) < 3:
                    web_articles = self.web_scraper.scrape_website(source, category)
                    all_articles[category].extend(web_articles)
            
            # Try News APIs for additional coverage
            api_articles = self.api_scraper.scrape_newsapi_org(category)
            all_articles[category].extend(api_articles)
        
        return all_articles
    
    def save_articles_to_database(self, articles_by_category: Dict[str, List[Dict[str, Any]]]) -> int:
        """
        Save all scraped articles to database
        
        Args:
            articles_by_category: Dictionary of articles by category
            
        Returns:
            Number of articles saved
        """
        total_saved = 0
        
        for category, articles in articles_by_category.items():
            for article in articles:
                if self.database.save_article(article):
                    total_saved += 1
        
        logger.info(f"Saved {total_saved} articles to database")
        return total_saved
    
    def get_daily_articles(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get articles scraped today"""
        return self.database.get_recent_articles(category, days=1)
    
    def run_daily_scraping(self) -> Dict[str, Any]:
        """
        Run the complete daily scraping workflow
        
        Returns:
            Summary dictionary with statistics
        """
        logger.info("Starting daily news scraping workflow")
        start_time = datetime.now()
        
        # Scrape all sources
        articles_by_category = self.scrape_all_sources()
        
        # Save to database
        total_saved = self.save_articles_to_database(articles_by_category)
        
        # Generate summary
        summary = {
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_articles_scraped': sum(len(articles) for articles in articles_by_category.values()),
            'total_articles_saved': total_saved,
            'articles_by_category': {
                category: len(articles) for category, articles in articles_by_category.items()
            }
        }
        
        logger.info(f"Daily scraping completed: {summary}")
        return summary


if __name__ == "__main__":
    # Example usage
    aggregator = NewsAggregator()
    result = aggregator.run_daily_scraping()
    print(f"Scraping completed: {result}")
