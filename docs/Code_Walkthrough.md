# Code Walkthrough: Agentic News Workflow System

This document provides a comprehensive walkthrough of the Agentic News Workflow System's codebase, explaining key modules, classes, and their interactions. It's intended to help developers quickly understand the system's implementation and make modifications or extensions.

## 1. Project Structure Overview

```
agentic_news_workflow/
├── config/                 # Configuration files
│   ├── config.py          # Main configuration
│   └── __init__.py
├── scrapers/              # News scraping components
│   ├── news_scraper.py    # Main scraper classes
│   └── __init__.py
├── content_generator/     # AI content generation
│   ├── content_generator.py
│   └── __init__.py
├── review_interface/      # Web interface
│   ├── app.py             # Flask application
│   ├── routes/            # API endpoints
│   │   ├── __init__.py
│   │   └── content.py
│   ├── static/            # Frontend files
│   └── templates/         # HTML templates
├── data/                  # Database files
│   ├── news_database.db
│   └── content_database.db
├── logs/                  # Log files
├── run_workflow.py        # Main workflow runner
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker image definition
├── docker_utils.py        # Docker utility script
└── requirements.txt       # Python dependencies
```

## 2. Key Modules and Classes

### 2.1 Configuration Module (`config/config.py`)

This module defines all configuration parameters for the system.

Key components:
- `NEWS_SOURCES`: Dictionary mapping categories to news source configurations
- `NEWS_API_CONFIG`: API keys and settings for news APIs
- `SCRAPING_CONFIG`: Web scraping parameters (user agent, timeouts, etc.)
- `DATABASE_CONFIG`: Database paths and connection settings
- `LOGGING_CONFIG`: Logging level, format, and output locations
- `CONTENT_CONFIG`: Content generation parameters
- `REVIEW_CONFIG`: Review interface settings

Example:
```python
NEWS_SOURCES = {
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
        # More sources...
    ],
    'leadership': [
        # Leadership sources...
    ]
}
```

### 2.2 News Scraper Module (`scrapers/news_scraper.py`)

This module handles all aspects of collecting news from various sources.

#### 2.2.1 Class: `NewsDatabase`

Responsible for managing the SQLite database that stores scraped articles.

Key methods:
- `__init__(db_path=None)`: Initializes the database handler
- `init_database()`: Creates necessary database tables if they don't exist
- `save_article(article_data)`: Saves or updates an article in the database
- `get_recent_articles(category=None, days=7)`: Retrieves articles from the past N days

Implementation details:
- Uses SQLite3 for database operations
- Creates a table with fields for article metadata and content
- Handles proper JSON serialization/deserialization for list fields like keywords

#### 2.2.2 Class: `RSSFeedScraper`

Handles scraping news from RSS feeds.

Key methods:
- `scrape_rss_feed(feed_url, category, source_name)`: Extracts articles from an RSS feed
- `_extract_keywords(text, category)`: Identifies relevant keywords in article text

Implementation details:
- Uses feedparser to parse RSS XML
- Uses newspaper3k to extract full article content
- Respects rate limiting with configurable delays

#### 2.2.3 Class: `NewsAPIScraper`

Interfaces with news APIs to retrieve structured news data.

Key methods:
- `scrape_newsapi_org(category)`: Retrieves articles from NewsAPI.org
- `_extract_keywords(text, category)`: Identifies relevant keywords in article text

Implementation details:
- Constructs API requests with category-specific keywords
- Handles API authentication and error responses
- Uses newspaper3k to extract full content from article URLs

#### 2.2.4 Class: `WebScraper`

Directly scrapes news websites for articles.

Key methods:
- `scrape_website(source_config, category)`: Scrapes articles from a website
- `_extract_keywords(text, category)`: Identifies relevant keywords in article text

Implementation details:
- Uses BeautifulSoup to parse HTML
- Extracts article links from landing pages
- Uses newspaper3k to extract full article content
- Handles errors and malformed content gracefully

#### 2.2.5 Class: `NewsAggregator`

Coordinates all scraping methods and manages the overall scraping workflow.

Key methods:
- `scrape_all_sources()`: Scrapes articles from all configured sources
- `save_articles_to_database(articles_by_category)`: Saves all scraped articles
- `get_daily_articles(category=None)`: Retrieves articles scraped today
- `run_daily_scraping()`: Runs the complete scraping workflow

Implementation details:
- Prioritizes RSS feeds, falling back to web scraping when needed
- Aggregates articles by category
- Generates a summary of the scraping operation
- Coordinates error handling across all scrapers

### 2.3 Content Generator Module (`content_generator/content_generator.py`)

This module handles AI-based content generation from scraped news articles.

#### 2.3.1 Class: `ContentDatabase`

Manages the SQLite database for storing generated content.

Key methods:
- `__init__(db_path=None)`: Initializes the database handler
- `init_database()`: Creates necessary database tables if they don't exist
- `save_generated_content(content_data)`: Saves generated content to the database
- `get_pending_content(content_type=None)`: Retrieves content pending review
- `update_content_status(content_id, status, feedback=None)`: Updates content approval status

Implementation details:
- Creates tables for articles and social media posts
- Stores approval status and user feedback
- Tracks relationships between generated content and source articles

#### 2.3.2 Class: `ContentGenerator`

Generates articles and social media posts using AI.

Key methods:
- `generate_article(source_articles)`: Generates an article from source articles
- `generate_social_post(article, platform)`: Generates a social media post
- `generate_daily_content(category=None)`: Runs daily content generation workflow
- `_create_article_prompt(sources)`: Creates a prompt for article generation
- `_create_social_prompt(article, platform)`: Creates a prompt for social post generation

Implementation details:
- Uses LangChain for managing AI interactions
- Constructs carefully designed prompts for different content types
- Processes and formats AI responses for consistency
- Implements error handling and retry logic for AI requests

### 2.4 Review Interface (`review_interface/app.py` and `review_interface/routes/`)

This module provides a web interface for reviewing and approving generated content.

#### 2.4.1 Function: `create_app()`

Creates and configures the Flask application.

Implementation details:
- Sets up SQLite database connection
- Configures CORS for cross-origin requests
- Registers blueprints for API routes
- Sets up static file serving

#### 2.4.2 Module: `routes/content.py`

Implements API endpoints for content management.

Key endpoints:
- `GET /api/content/pending`: Retrieves pending content for review
- `POST /api/content/articles/{id}/approve`: Approves an article
- `POST /api/content/articles/{id}/reject`: Rejects an article with feedback
- `POST /api/content/articles/{id}/edit`: Updates article content
- `POST /api/content/generate`: Triggers content generation
- `POST /api/content/scrape`: Triggers news scraping
- `GET /api/content/stats`: Retrieves system statistics

Implementation details:
- Uses Flask blueprints for route organization
- Returns JSON responses for API requests
- Implements proper error handling and status codes
- Interfaces with content and news databases

### 2.5 Workflow Runner (`run_workflow.py`)

This script coordinates the overall workflow of the system.

Key components:
- Command-line argument parsing
- Mode selection (scrape, generate, full, status)
- Category filtering for selective operations
- Error handling and reporting
- Status summarization

Implementation details:
- Uses argparse for command-line argument handling
- Creates instances of NewsAggregator and ContentGenerator
- Coordinates workflow execution based on selected mode
- Provides clear console output for operations

## 3. Key Workflows and Data Flows

### 3.1 News Scraping Workflow

1. `run_workflow.py` calls `NewsAggregator.run_daily_scraping()`
2. `run_daily_scraping()` calls `scrape_all_sources()`
3. `scrape_all_sources()` iterates through categories and sources
4. For each source, the appropriate scraper is called:
   - `RSSFeedScraper.scrape_rss_feed()` for RSS feeds
   - `WebScraper.scrape_website()` for direct web scraping
   - `NewsAPIScraper.scrape_newsapi_org()` for news APIs
5. Articles are collected and aggregated by category
6. `save_articles_to_database()` saves all articles to the database
7. A summary of the operation is returned

### 3.2 Content Generation Workflow

1. `run_workflow.py` calls `ContentGenerator.generate_daily_content()`
2. `generate_daily_content()` retrieves recent articles from `NewsDatabase`
3. Articles are grouped by category and topic
4. For each topic group:
   - `generate_article()` creates an article using AI
   - `generate_social_post()` creates social media posts for the article
5. Generated content is saved to `ContentDatabase`
6. A summary of generated content is returned

### 3.3 Review Workflow

1. User accesses the review interface in a web browser
2. Frontend loads pending content via `GET /api/content/pending`
3. User reviews each piece of content and takes action:
   - Approve: Calls `POST /api/content/articles/{id}/approve`
   - Reject: Calls `POST /api/content/articles/{id}/reject` with feedback
   - Edit: Calls `POST /api/content/articles/{id}/edit` with updated content
4. Backend updates content status in `ContentDatabase`
5. Frontend updates to show next pending content

## 4. Database Schema Details

### 4.1 News Database Schema

Table: `articles`
- `id` (INTEGER): Primary key, auto-incrementing
- `title` (TEXT): Article title, not null
- `content` (TEXT): Full article content
- `url` (TEXT): Original article URL, unique
- `source` (TEXT): Source name
- `category` (TEXT): Article category
- `published_date` (TEXT): Original publication date
- `scraped_date` (TEXT): When the article was scraped
- `keywords` (TEXT): JSON string of keywords
- `summary` (TEXT): Article summary

Indexes:
- Unique index on `url` to prevent duplicates
- Index on `scraped_date` for date-based queries
- Index on `category` for category filtering

### 4.2 Content Database Schema

Table: `generated_articles`
- `id` (INTEGER): Primary key, auto-incrementing
- `title` (TEXT): Generated article title
- `content` (TEXT): Generated article content
- `category` (TEXT): Content category
- `source_articles` (TEXT): JSON string of source article IDs
- `generated_date` (TEXT): Generation timestamp
- `status` (TEXT): Status (pending, approved, rejected)
- `feedback` (TEXT): User feedback if rejected
- `edited_content` (TEXT): User-edited version (if any)

Table: `social_posts`
- `id` (INTEGER): Primary key, auto-incrementing
- `article_id` (INTEGER): ID of related generated article
- `platform` (TEXT): Social media platform (twitter, linkedin)
- `content` (TEXT): Post content
- `generated_date` (TEXT): Generation timestamp
- `status` (TEXT): Status (pending, approved, rejected)
- `feedback` (TEXT): User feedback if rejected
- `edited_content` (TEXT): User-edited version (if any)

Indexes:
- Index on `status` for filtering pending content
- Index on `generated_date` for date-based queries
- Index on `article_id` in `social_posts` for relational queries

## 5. Configuration Parameters

### 5.1 Scraping Configuration

```python
SCRAPING_CONFIG = {
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
    'timeout': 30,  # Request timeout in seconds
    'max_articles_per_source': 5,  # Maximum articles to scrape per source
    'delay_between_requests': 3,  # Delay between requests in seconds
}
```

### 5.2 Content Generation Configuration

```python
CONTENT_CONFIG = {
    'max_articles_per_day': 5,  # Maximum articles to generate per day
    'article_word_count': 800,  # Target word count for articles
    'model': 'gpt-4',  # OpenAI model to use
    'temperature': 0.7,  # Creativity parameter (0-1)
    'max_tokens': 1500,  # Maximum tokens for article generation
    'social_platforms': ['twitter', 'linkedin'],  # Platforms for social posts
}
```

### 5.3 Database Configuration

```python
DATABASE_CONFIG = {
    'sqlite_path': 'data/news_database.db',  # Path to news database
    'content_db_path': 'data/content_database.db',  # Path to content database
}
```

## 6. Error Handling Patterns

### 6.1 Function-Level Error Handling

Most functions implement try-except blocks to catch and handle specific exceptions:

```python
def save_article(self, article_data):
    try:
        # Database operations...
        return True
    except Exception as e:
        logger.error(f"Error saving article: {e}")
        return False
```

### 6.2 API Endpoint Error Handling

API endpoints use try-except with appropriate HTTP status codes:

```python
@content_bp.route('/articles/<int:article_id>/approve', methods=['POST'])
def approve_article(article_id):
    try:
        # Approve article in database
        database.update_content_status(article_id, 'approved')
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

### 6.3 Workflow-Level Error Handling

The main workflow runner implements higher-level error handling:

```python
def run_workflow(mode, category=None):
    try:
        if mode == 'scrape':
            result = run_scraping()
        elif mode == 'generate':
            result = run_generation(category)
        # ...
        return result
    except Exception as e:
        logger.critical(f"Workflow failed: {e}")
        print(f"Error: {e}")
        return None
```

## 7. Extension Points

The system provides several extension points for adding new functionality:

### 7.1 Adding New News Sources

To add a new news source:
1. Update `NEWS_SOURCES` in `config.py` with the new source information
2. If it's a special API, consider adding a new scraper class in `news_scraper.py`
3. For standard RSS or web sources, the existing scrapers will handle it

### 7.2 Adding New Content Types

To add a new type of generated content:
1. Add methods to `ContentGenerator` for the new content type
2. Create appropriate prompt templates
3. Update the database schema to store the new content type
4. Add API endpoints in the review interface
5. Update the frontend to display and manage the new content type

### 7.3 Customizing AI Models

To use different AI models:
1. Update `CONTENT_CONFIG` in `config.py` with new model settings
2. Modify `ContentGenerator` prompt templates if needed for the new model
3. Adjust token limits and other model-specific parameters

## 8. Common Coding Patterns

### 8.1 Configuration Loading

```python
# Import configuration from module
from config.config import SOME_CONFIG

# Access configuration values
max_items = SOME_CONFIG['max_items']
```

### 8.2 Database Operations

```python
# Connect to database
with sqlite3.connect(self.db_path) as conn:
    cursor = conn.cursor()
    
    # Execute query
    cursor.execute('''
        SELECT * FROM table
        WHERE condition = ?
    ''', (value,))
    
    # Process results
    results = cursor.fetchall()
```

### 8.3 API Calls

```python
# Make API request
response = requests.get(
    url,
    params={'key': 'value'},
    headers={'User-Agent': user_agent},
    timeout=timeout
)
response.raise_for_status()  # Raise exception for HTTP errors

# Process JSON response
data = response.json()
```

### 8.4 Logging

```python
# Import logger
logger = logging.getLogger(__name__)

# Log at different levels
logger.debug("Debug message with detailed information")
logger.info("Informational message about normal operation")
logger.warning("Warning about potential issues")
logger.error("Error that prevented an operation")
logger.critical("Critical error that affects system operation")
```

## 9. Testing Approach

The system includes tests for key components:

### 9.1 Scraper Tests (`test_scraper.py`)

Tests for the news scraping components, including:
- RSS feed parsing
- Web scraping
- News API integration
- Database operations

### 9.2 Content Generator Tests (`test_content_generator.py`)

Tests for the content generation components, including:
- Article generation
- Social post generation
- Prompt construction
- Database operations

## 10. Performance Considerations

### 10.1 Database Optimization

- Use transactions for batch operations
- Create appropriate indexes for common queries
- Keep database connections open only when needed

### 10.2 Network Request Optimization

- Use session objects for persistent connections
- Implement appropriate timeouts to avoid hanging
- Add delays between requests to respect rate limits
- Consider using asynchronous requests for parallel operations

### 10.3 Content Generation Optimization

- Optimize prompts to reduce token usage
- Use appropriate model parameters (temperature, top_p)
- Implement caching for repeated operations
- Consider batching similar requests

## 11. Conclusion

This code walkthrough provides a comprehensive overview of the Agentic News Workflow System's implementation. By understanding the key modules, classes, workflows, and patterns, developers can efficiently navigate, modify, and extend the codebase to meet evolving requirements.

For further details on specific components, refer to the inline documentation in the code and the technical design document.
