# Troubleshooting Guide: Agentic News Workflow System

This guide provides solutions for common issues that may arise when running, deploying, or extending the Agentic News Workflow System. It covers installation problems, runtime errors, and performance issues to help developers quickly resolve problems and get the system running smoothly.

## 1. Installation Issues

### 1.1 Python Environment Setup

#### Issue: Missing Dependencies
**Symptoms:** Error messages about missing modules when running the application.

**Solution:**
1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
2. If specific packages are causing issues, try installing them individually:
   ```bash
   pip install newspaper3k nltk python-dotenv flask flask-cors
   ```
3. For `newspaper3k` specifically, ensure you have system dependencies:
   - On Ubuntu/Debian:
     ```bash
     sudo apt-get install python3-dev libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev libpng-dev
     ```
   - On macOS:
     ```bash
     brew install libxml2 libxslt
     ```
   - On Windows:
     Install Visual C++ Build Tools and ensure you have the required libraries.

#### Issue: NLTK Data Missing
**Symptoms:** Errors about missing NLTK data when running the content generator.

**Solution:**
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

You can add this to a setup script or run it once manually in a Python interpreter.

### 1.2 Database Initialization

#### Issue: Database File Permission Errors
**Symptoms:** Permission denied errors when trying to create or access the database files.

**Solution:**
1. Ensure the `data/` directory exists and has appropriate write permissions:
   ```bash
   mkdir -p data
   chmod 755 data
   ```
2. Check file ownership and permissions:
   ```bash
   ls -la data/
   ```
3. If running in Docker, ensure volume mounts are configured correctly in `docker-compose.yml`.

#### Issue: Database Schema Errors
**Symptoms:** SQL errors about missing tables or columns.

**Solution:**
1. Check if database initialization is being called correctly in your code.
2. For a fresh start, delete the database files and let the application recreate them:
   ```bash
   rm data/news_database.db data/content_database.db
   ```
3. Check for SQL syntax errors in the database initialization code.

### 1.3 API Keys and Configuration

#### Issue: Missing API Keys
**Symptoms:** Authentication errors when trying to access external APIs like News API or OpenAI.

**Solution:**
1. Create a `.env` file in the root directory with your API keys:
   ```
   OPENAI_API_KEY=your_openai_key_here
   NEWSAPI_KEY=your_newsapi_key_here
   FLASK_SECRET_KEY=random_secret_key_here
   ```
2. Ensure the application is loading the `.env` file correctly using `python-dotenv`.
3. Verify API keys are valid by testing them directly with the API providers.

## 2. News Scraping Issues

### 2.1 Connection Problems

#### Issue: Website Access Blocked
**Symptoms:** Consistent failures when scraping specific websites, with HTTP 403 (Forbidden) errors.

**Solution:**
1. Update the user agent string in `config.py`:
   ```python
   SCRAPING_CONFIG = {
       'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
       # Other config...
   }
   ```
2. Implement request rotation to vary request patterns.
3. Add delays between requests to avoid triggering rate limits:
   ```python
   import time
   time.sleep(5)  # 5 second delay between requests
   ```
4. Consider using a proxy service for websites with strict anti-scraping measures.

#### Issue: SSL Certificate Verification Failures
**Symptoms:** SSL errors when connecting to certain websites.

**Solution:**
1. Update your CA certificates:
   ```bash
   pip install --upgrade certifi
   ```
2. As a temporary workaround (not recommended for production), you can disable verification:
   ```python
   import requests
   response = requests.get(url, verify=False)
   ```

### 2.2 Content Extraction Problems

#### Issue: Article Content Not Extracted Correctly
**Symptoms:** Empty or incomplete article content after scraping.

**Solution:**
1. Check if the website's HTML structure has changed and update the selectors in your configuration:
   ```python
   'selectors': {
       'title': 'h1.updated-title-class',
       'content': 'div.updated-content-class',
       'date': 'time.updated-date-class'
   }
   ```
2. Try using newspaper3k's automatic extraction instead of custom selectors:
   ```python
   from newspaper import Article
   article = Article(url)
   article.download()
   article.parse()
   content = article.text
   ```
3. Implement logging to see exactly what HTML is being returned for troubleshooting.

#### Issue: Article Publication Dates Missing or Incorrect
**Symptoms:** Missing publication dates or dates that are significantly off.

**Solution:**
1. Update date parsing code to handle more formats:
   ```python
   import dateparser
   
   def parse_date(date_string):
       if not date_string:
           return None
       return dateparser.parse(date_string)
   ```
2. Check for timezone issues in date parsing.
3. Implement fallback methods to extract dates from URLs or other metadata.

### 2.3 Rate Limiting and Performance

#### Issue: Scraping Too Slow
**Symptoms:** News scraping takes an excessively long time to complete.

**Solution:**
1. Implement concurrent scraping using `concurrent.futures`:
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   def scrape_sources(sources):
       results = []
       with ThreadPoolExecutor(max_workers=5) as executor:
           future_to_source = {executor.submit(scrape_source, source): source for source in sources}
           for future in as_completed(future_to_source):
               results.append(future.result())
       return results
   ```
2. Prioritize RSS feeds over web scraping when available.
3. Implement caching to avoid re-scraping unchanged content.

#### Issue: API Rate Limits Exceeded
**Symptoms:** HTTP 429 (Too Many Requests) errors from news APIs.

**Solution:**
1. Implement exponential backoff for retries:
   ```python
   def make_api_request_with_backoff(url, params, max_retries=5):
       for attempt in range(max_retries):
           response = requests.get(url, params=params)
           if response.status_code == 200:
               return response.json()
           if response.status_code == 429:
               # Exponential backoff
               sleep_time = 2 ** attempt
               print(f"Rate limit hit. Retrying in {sleep_time} seconds...")
               time.sleep(sleep_time)
           else:
               # Other error
               response.raise_for_status()
       raise Exception("Max retries exceeded")
   ```
2. Track API usage and implement daily/hourly quotas.
3. Distribute requests evenly throughout the day.

## 3. Content Generation Issues

### 3.1 AI Model Problems

#### Issue: OpenAI API Errors
**Symptoms:** Failed API calls when generating content.

**Solution:**
1. Check API key validity and usage limits on the OpenAI dashboard.
2. Handle API errors gracefully with retries:
   ```python
   def generate_with_retry(prompt, max_retries=3):
       for attempt in range(max_retries):
           try:
               response = openai.ChatCompletion.create(
                   model="gpt-4",
                   messages=[{"role": "user", "content": prompt}],
                   temperature=0.7,
                   max_tokens=1500
               )
               return response.choices[0].message.content
           except openai.error.RateLimitError:
               wait_time = 2 ** attempt
               print(f"Rate limit hit. Retrying in {wait_time} seconds...")
               time.sleep(wait_time)
           except openai.error.APIError as e:
               print(f"API error: {e}")
               time.sleep(1)
       raise Exception("Failed to generate content after multiple attempts")
   ```
3. Implement fallback models if primary model is unavailable.

#### Issue: Poor Quality Generated Content
**Symptoms:** Content is irrelevant, repetitive, or doesn't match the source articles well.

**Solution:**
1. Improve prompt engineering:
   ```python
   def create_better_prompt(sources):
       prompt = "Based on the following news articles, write a comprehensive summary that highlights the key points and provides insightful analysis:\n\n"
       for i, source in enumerate(sources, 1):
           prompt += f"Source {i}: {source['title']}\n"
           prompt += f"{source['content'][:500]}...\n\n"
       prompt += "Your article should be well-structured, factually accurate, and provide value beyond what's in the original sources."
       return prompt
   ```
2. Adjust model parameters:
   ```python
   response = openai.ChatCompletion.create(
       model="gpt-4",
       messages=[{"role": "user", "content": prompt}],
       temperature=0.5,  # Lower temperature for more focused output
       max_tokens=1500,
       presence_penalty=0.2,  # Discourage repetition
       frequency_penalty=0.5  # Discourage frequent token usage
   )
   ```
3. Implement a content review pipeline to filter low-quality outputs.

### 3.2 Resource Issues

#### Issue: Token Limit Exceeded
**Symptoms:** AI model returns errors about exceeding token limits or truncated responses.

**Solution:**
1. Limit input content:
   ```python
   def create_prompt_within_limits(sources, max_input_tokens=6000):
       prompt = "Write an article based on these sources:\n\n"
       current_tokens = len(prompt.split())
       
       for source in sources:
           source_content = f"Source: {source['title']}\n{source['content']}\n\n"
           source_tokens = len(source_content.split())
           
           if current_tokens + source_tokens > max_input_tokens:
               # Truncate or summarize instead of adding full content
               truncated = f"Source: {source['title']}\n{source['content'][:200]}...\n\n"
               current_tokens += len(truncated.split())
               prompt += truncated
           else:
               current_tokens += source_tokens
               prompt += source_content
       
       return prompt
   ```
2. Split generation into multiple API calls and stitch results together.
3. Use techniques like recursive summarization for large input datasets.

#### Issue: High API Costs
**Symptoms:** Excessive OpenAI API billing or quota depletion.

**Solution:**
1. Implement token usage tracking:
   ```python
   def track_token_usage(prompt, response):
       prompt_tokens = len(prompt.split())
       response_tokens = len(response.split())
       total_tokens = prompt_tokens + response_tokens
       
       # Log usage
       print(f"Usage: {prompt_tokens} prompt tokens, {response_tokens} response tokens")
       
       # Store in database for monitoring
       with sqlite3.connect('data/usage_stats.db') as conn:
           cursor = conn.cursor()
           cursor.execute('''
               INSERT INTO token_usage (date, prompt_tokens, response_tokens, total_tokens)
               VALUES (?, ?, ?, ?)
           ''', (datetime.now().isoformat(), prompt_tokens, response_tokens, total_tokens))
   ```
2. Use a tiered approach: generate high-quality content only for priority categories/topics.
3. Consider switching to less expensive models for drafts or non-critical content.

## 4. Review Interface Issues

### 4.1 Web Server Problems

#### Issue: Flask Server Not Starting
**Symptoms:** Error messages when trying to start the Flask server.

**Solution:**
1. Check port availability:
   ```bash
   # Check if port 5000 is already in use
   netstat -tuln | grep 5000
   ```
2. Try specifying a different port:
   ```python
   app.run(host='0.0.0.0', port=5001, debug=True)
   ```
3. Ensure you're not calling `app.run()` when importing modules:
   ```python
   if __name__ == '__main__':
       app.run(host='0.0.0.0', port=5000, debug=True)
   ```

#### Issue: CORS Errors
**Symptoms:** Browser console shows CORS policy errors when trying to access the API.

**Solution:**
1. Properly configure CORS in the Flask application:
   ```python
   from flask_cors import CORS
   
   app = Flask(__name__)
   CORS(app, resources={r"/api/*": {"origins": "*"}})
   ```
2. For production, restrict origins to specific domains:
   ```python
   CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
   ```
3. Ensure the client is making proper CORS requests.

### 4.2 Database Access Issues

#### Issue: Database Locked Errors
**Symptoms:** "database is locked" errors when multiple processes try to access the SQLite database.

**Solution:**
1. Implement proper connection handling:
   ```python
   def get_db_connection():
       conn = sqlite3.connect('data/content_database.db', timeout=30)
       conn.row_factory = sqlite3.Row
       return conn
   
   def execute_query(query, params=()):
       conn = get_db_connection()
       try:
           result = conn.execute(query, params)
           conn.commit()
           return result
       finally:
           conn.close()
   ```
2. Use connection pooling for high-concurrency scenarios.
3. Consider migrating to a more robust database like PostgreSQL for production environments.

#### Issue: Data Not Showing Up in Interface
**Symptoms:** The review interface doesn't show newly generated content.

**Solution:**
1. Check database connections and queries for errors.
2. Verify API endpoints are returning the expected data.
3. Implement proper error handling in the frontend:
   ```javascript
   fetch('/api/content/pending')
     .then(response => {
       if (!response.ok) {
         throw new Error(`HTTP error! status: ${response.status}`);
       }
       return response.json();
     })
     .then(data => {
       console.log('Data received:', data);
       // Update UI with data
     })
     .catch(error => {
       console.error('Error fetching content:', error);
       // Show error message in UI
     });
   ```

## 5. Docker Deployment Issues

### 5.1 Container Build Problems

#### Issue: Docker Build Fails
**Symptoms:** Errors during `docker build` process.

**Solution:**
1. Check Dockerfile syntax and dependencies:
   ```Dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       build-essential \
       python3-dev \
       libxml2-dev \
       libxslt1-dev \
       libjpeg-dev \
       zlib1g-dev \
       libpng-dev \
       && rm -rf /var/lib/apt/lists/*
   
   # Install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application code
   COPY . .
   
   # Run application
   CMD ["python", "run_workflow.py"]
   ```
2. Build with verbose output for troubleshooting:
   ```bash
   docker build -t agentic-news-workflow . --progress=plain
   ```
3. Check for network issues during build.

#### Issue: Container Exits Immediately
**Symptoms:** Docker container starts but exits immediately.

**Solution:**
1. Use proper entrypoint and command:
   ```yaml
   # docker-compose.yml
   services:
     app:
       build: .
       command: python run_workflow.py --mode=full
       volumes:
         - ./data:/app/data
       environment:
         - OPENAI_API_KEY=${OPENAI_API_KEY}
   ```
2. Check logs for errors:
   ```bash
   docker logs <container_id>
   ```
3. Try running with an interactive shell for debugging:
   ```bash
   docker run -it --rm agentic-news-workflow /bin/bash
   ```

### 5.2 Volume and Persistence Issues

#### Issue: Data Not Persisting Between Container Restarts
**Symptoms:** Database files or logs disappear when containers are restarted.

**Solution:**
1. Ensure volumes are properly configured:
   ```yaml
   # docker-compose.yml
   services:
     app:
       build: .
       volumes:
         - ./data:/app/data
         - ./logs:/app/logs
   ```
2. Check directory permissions inside and outside the container.
3. Verify the paths used in the application match the volume mount points.

#### Issue: Permission Denied on Volume Mounts
**Symptoms:** Container fails to write to mounted volumes with permission errors.

**Solution:**
1. Set appropriate permissions on host directories:
   ```bash
   mkdir -p data logs
   chmod 777 data logs
   ```
2. Use user mapping in Docker Compose:
   ```yaml
   services:
     app:
       build: .
       user: "${UID}:${GID}"
       volumes:
         - ./data:/app/data
   ```
3. Set the correct user in the Dockerfile:
   ```Dockerfile
   RUN useradd -m appuser
   USER appuser
   ```

## 6. Performance Optimization

### 6.1 Memory Usage Issues

#### Issue: High Memory Consumption
**Symptoms:** Application uses excessive memory or crashes with out-of-memory errors.

**Solution:**
1. Implement batch processing for large datasets:
   ```python
   def process_articles_in_batches(articles, batch_size=100):
       for i in range(0, len(articles), batch_size):
           batch = articles[i:i+batch_size]
           process_batch(batch)
           # Clear memory
           gc.collect()
   ```
2. Close resources properly (file handles, network connections, etc.).
3. Profile memory usage to identify leaks:
   ```python
   import tracemalloc
   
   tracemalloc.start()
   # ... run your code ...
   snapshot = tracemalloc.take_snapshot()
   top_stats = snapshot.statistics('lineno')
   for stat in top_stats[:10]:
       print(stat)
   ```

### 6.2 Slow Processing

#### Issue: Slow Content Generation
**Symptoms:** Content generation takes a very long time to complete.

**Solution:**
1. Implement caching for AI responses:
   ```python
   import hashlib
   import json
   
   def get_cached_or_generate(prompt):
       # Create a hash of the prompt
       prompt_hash = hashlib.md5(prompt.encode()).hexdigest()
       
       # Check if we have a cached response
       cache_file = f"cache/{prompt_hash}.json"
       if os.path.exists(cache_file):
           with open(cache_file, 'r') as f:
               return json.load(f)
       
       # Generate new response
       response = generate_content(prompt)
       
       # Cache the response
       os.makedirs("cache", exist_ok=True)
       with open(cache_file, 'w') as f:
           json.dump(response, f)
       
       return response
   ```
2. Parallelize independent generation tasks:
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   def generate_all_content_types(article):
       with ThreadPoolExecutor(max_workers=3) as executor:
           twitter_future = executor.submit(generate_twitter_post, article)
           linkedin_future = executor.submit(generate_linkedin_post, article)
           summary_future = executor.submit(generate_summary, article)
           
           return {
               'twitter': twitter_future.result(),
               'linkedin': linkedin_future.result(),
               'summary': summary_future.result()
           }
   ```
3. Optimize database queries to reduce I/O overhead.

## 7. Extension and Customization Issues

### 7.1 Adding New News Sources

#### Issue: New Source Not Being Scraped
**Symptoms:** Articles from newly added sources don't appear in the database.

**Solution:**
1. Verify source configuration in `config.py`:
   ```python
   NEWS_SOURCES = {
       'technology': [
           # Existing sources...
           {
               'name': 'New Tech Blog',
               'url': 'https://newtechblog.com/',
               'rss_feed': 'https://newtechblog.com/feed/',
               'selectors': {
                   'title': 'h1.post-title',
                   'content': 'div.post-content',
                   'date': 'time.post-date'
               }
           }
       ]
   }
   ```
2. Test selectors manually with a script:
   ```python
   import requests
   from bs4 import BeautifulSoup
   
   url = "https://newtechblog.com/some-article"
   response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0...'})
   soup = BeautifulSoup(response.text, 'html.parser')
   
   title = soup.select_one('h1.post-title')
   content = soup.select_one('div.post-content')
   date = soup.select_one('time.post-date')
   
   print(f"Title: {title.text if title else 'Not found'}")
   print(f"Content length: {len(content.text) if content else 0}")
   print(f"Date: {date.text if date else 'Not found'}")
   ```
3. Check RSS feed validity with a feed validator.

### 7.2 Customizing Content Generation

#### Issue: Content Format Not Meeting Requirements
**Symptoms:** Generated content doesn't follow the required structure or format.

**Solution:**
1. Update prompt templates with more specific instructions:
   ```python
   def create_article_prompt(sources, format_requirements):
       prompt = f"""
       Based on the following news articles, write a comprehensive article that follows this exact format:
       
       {format_requirements}
       
       Here are the source articles:
       
       """
       
       for i, source in enumerate(sources, 1):
           prompt += f"Source {i}: {source['title']}\n"
           prompt += f"{source['content'][:500]}...\n\n"
       
       return prompt
   ```
2. Implement post-processing to enforce format:
   ```python
   def format_generated_content(content, required_sections):
       formatted = {}
       
       for section in required_sections:
           pattern = f"{section}:(.*?)(?={required_sections[0]}:|$)"
           match = re.search(pattern, content, re.DOTALL)
           if match:
               formatted[section] = match.group(1).strip()
           else:
               formatted[section] = ""
       
       return formatted
   ```
3. Use structured output formats with LangChain or OpenAI functions.

## 8. Logging and Monitoring

### 8.1 Enhancing Logging for Troubleshooting

To improve troubleshooting capabilities, implement comprehensive logging:

```python
import logging
import logging.config
import os
from datetime import datetime

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Configure logging
logging_config = {
    'version': 1,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'standard',
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': f'logs/app_{datetime.now().strftime("%Y%m%d")}.log',
        },
        'error_file': {
            'class': 'logging.FileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': f'logs/error_{datetime.now().strftime("%Y%m%d")}.log',
        }
    },
    'loggers': {
        '': {  # Root logger
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
        },
        'news_scraper': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'content_generator': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'DEBUG',
            'propagate': False
        }
    }
}

logging.config.dictConfig(logging_config)

# Create logger instances
logger = logging.getLogger(__name__)
scraper_logger = logging.getLogger('news_scraper')
generator_logger = logging.getLogger('content_generator')

# Example usage
def example_function():
    logger.debug("Debug message with detailed information")
    logger.info("Informational message about normal operation")
    logger.warning("Warning about potential issues")
    logger.error("Error that prevented an operation", exc_info=True)  # Include traceback
```

### 8.2 Implementing Health Checks

To monitor system health, implement API endpoints for health checks:

```python
@app.route('/api/health', methods=['GET'])
def health_check():
    status = {
        'status': 'healthy',
        'components': {}
    }
    
    # Check database connection
    try:
        with sqlite3.connect('data/news_database.db') as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM articles')
            article_count = cursor.fetchone()[0]
            status['components']['news_database'] = {
                'status': 'healthy',
                'article_count': article_count
            }
    except Exception as e:
        status['status'] = 'degraded'
        status['components']['news_database'] = {
            'status': 'error',
            'message': str(e)
        }
    
    # Check OpenAI API connection
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        status['components']['openai_api'] = {
            'status': 'healthy'
        }
    except Exception as e:
        status['status'] = 'degraded'
        status['components']['openai_api'] = {
            'status': 'error',
            'message': str(e)
        }
    
    # Return appropriate HTTP status code
    http_status = 200 if status['status'] == 'healthy' else 500
    return jsonify(status), http_status
```

## 9. Recovery Procedures

### 9.1 Database Recovery

If the database becomes corrupted or data is lost, follow these recovery steps:

1. Stop the application:
   ```bash
   docker-compose down
   ```

2. Check for database corruption:
   ```bash
   sqlite3 data/news_database.db "PRAGMA integrity_check;"
   ```

3. Restore from backup:
   ```bash
   cp data/backups/news_database_20230815.db data/news_database.db
   cp data/backups/content_database_20230815.db data/content_database.db
   ```

4. If no backup is available, rebuild the database:
   ```bash
   rm data/news_database.db data/content_database.db
   python -c "from news_scraper import NewsDatabase; db = NewsDatabase(); db.init_database()"
   python -c "from content_generator import ContentDatabase; db = ContentDatabase(); db.init_database()"
   ```

5. Restart the application:
   ```bash
   docker-compose up -d
   ```

### 9.2 API Key Rotation

If API keys need to be rotated due to exposure or security issues:

1. Generate new API keys from the provider's dashboard.
2. Update the `.env` file with new keys.
3. Restart the application to load new keys:
   ```bash
   docker-compose down
   docker-compose up -d
   ```
4. Verify the new keys work by checking logs.

## 10. Conclusion

This troubleshooting guide covers the most common issues you might encounter when working with the Agentic News Workflow System. By following these solutions, you can quickly diagnose and resolve problems to keep the system running smoothly.

For issues not covered in this guide, refer to the following resources:

1. Check application logs in the `logs/` directory
2. Review the relevant module documentation
3. Consult the API documentation for external services
4. Search for similar issues in the project's issue tracker

If you discover a new issue and its solution, consider updating this guide to help other developers in the future.
