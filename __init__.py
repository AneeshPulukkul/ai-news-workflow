"""
Scrapers module for the Agentic News Workflow system
"""

from .news_scraper import NewsAggregator, NewsDatabase, RSSFeedScraper, NewsAPIScraper, WebScraper

__all__ = ['NewsAggregator', 'NewsDatabase', 'RSSFeedScraper', 'NewsAPIScraper', 'WebScraper']

