# Agentic News Workflow System - Deployment Guide

## Overview

This deployment guide provides comprehensive instructions for setting up and deploying the Agentic News Workflow System, an AI-powered solution that automatically scrapes news from technology and leadership sources, generates articles and social media posts, and provides a review interface for content approval.

## System Architecture

The system consists of three main components:

1. **News Scraping Engine** - Automated web scraping using RSS feeds, News API, and direct web scraping
2. **AI Content Generation Pipeline** - OpenAI-powered content creation using LangChain
3. **Review Interface** - Flask-based web application for content review and approval

## Prerequisites

### System Requirements

- Python 3.11 or higher
- Node.js 18+ (for frontend development)
- SQLite (included with Python)
- Internet connection for news scraping and AI API calls

### API Keys Required

- OpenAI API key (for content generation)
- News API key (optional, for additional news sources)

## Installation Instructions

### 1. Clone and Setup Project Structure

```bash
# Create project directory
mkdir agentic_news_workflow
cd agentic_news_workflow

# Create directory structure
mkdir -p {config,scrapers,content_generator,data,logs}
```

### 2. Install Python Dependencies

```bash
# Install core dependencies
pip install flask flask-cors langchain langchain-openai openai
pip install beautifulsoup4 requests feedparser newspaper3k lxml_html_clean
pip install python-dotenv schedule sqlite3
```

### 3. Environment Configuration

Create a `.env` file in the project root:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# News API Configuration (optional)
NEWS_API_KEY=your_news_api_key_here

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/news_workflow.log

# Database Configuration
DATABASE_PATH=data/news_database.db
CONTENT_DATABASE_PATH=data/content_database.db
```

## Configuration

### News Sources Configuration

The system comes pre-configured with reliable news sources:

**Technology Sources:**
- TechCrunch RSS Feed
- Ars Technica RSS Feed
- The Verge RSS Feed

**Leadership Sources:**
- Harvard Business Review RSS Feed
- MIT Sloan Management Review RSS Feed
- McKinsey Insights RSS Feed

You can modify these sources in `config/config.py`.

### Content Generation Settings

Configure content generation parameters:

```python
CONTENT_CONFIG = {
    'max_articles_per_day': 5,
    'article_word_count': 800,
    'social_platforms': ['twitter', 'linkedin'],
    'content_categories': ['technology', 'leadership']
}
```

## Deployment Options

### Option 1: Local Development Setup

1. **Start the Review Interface:**

```bash
cd review_interface
source venv/bin/activate
python src/main.py
```

The interface will be available at `http://localhost:5000`

2. **Run Manual Content Generation:**

```bash
python test_content_generator.py
```

### Option 2: Production Deployment

For production deployment, use a WSGI server like Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Start the application
cd review_interface
gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
```

### Option 3: Automated Scheduling

Set up automated daily content generation using cron:

```bash
# Edit crontab
crontab -e

# Add daily scraping at 6 AM
0 6 * * * cd /path/to/agentic_news_workflow && python -c "from scrapers.news_scraper import NewsAggregator; NewsAggregator().run_daily_scraping()"

# Add daily content generation at 8 AM
0 8 * * * cd /path/to/agentic_news_workflow && python -c "from content_generator.content_generator import ContentGenerator, ContentDatabase; cg = ContentGenerator(); cd = ContentDatabase(); result = cg.generate_daily_content(); cd.save_generated_content(result)"
```

## Testing the System

### 1. Test News Scraping

```bash
python test_scraper.py
```

Expected output:
- Successfully scraped articles from configured sources
- Articles saved to SQLite database
- Log entries showing scraping progress

### 2. Test Content Generation

```bash
python test_content_generator.py
```

Expected output:
- Generated articles based on scraped news
- Created social media posts for each article
- Content saved to content database

### 3. Test Review Interface

1. Open browser to `http://localhost:5000`
2. Click "Scrape News" to populate database
3. Click "Generate Content" to create articles and posts
4. Review and approve/reject generated content

## Monitoring and Maintenance

### Log Files

Monitor system activity through log files:

```bash
# View scraping logs
tail -f logs/news_workflow.log

# View Flask application logs
tail -f review_interface/logs/news_workflow.log
```

### Database Management

The system uses SQLite databases:

- `data/news_database.db` - Stores scraped news articles
- `data/content_database.db` - Stores generated content

### Performance Optimization

1. **Scraping Frequency:** Adjust scraping intervals based on news source update frequency
2. **Content Generation:** Limit daily content generation to avoid API rate limits
3. **Database Cleanup:** Implement periodic cleanup of old articles

## Troubleshooting

### Common Issues

1. **Import Errors:**
   - Ensure all dependencies are installed
   - Check Python path configuration
   - Verify virtual environment activation

2. **API Errors:**
   - Verify OpenAI API key is valid
   - Check API rate limits
   - Ensure internet connectivity

3. **Database Errors:**
   - Check file permissions for database directory
   - Verify SQLite installation
   - Ensure sufficient disk space

### Error Resolution

**"Module not found" errors:**
```bash
pip install -r requirements.txt
```

**"Database locked" errors:**
```bash
# Check for running processes
ps aux | grep python
# Kill any hanging processes
```

**"API rate limit exceeded":**
- Reduce content generation frequency
- Implement exponential backoff
- Consider upgrading OpenAI plan

## Security Considerations

### API Key Management

- Store API keys in environment variables
- Never commit API keys to version control
- Use different keys for development and production

### Access Control

- Implement authentication for the review interface
- Use HTTPS in production
- Restrict database file permissions

### Data Privacy

- Implement data retention policies
- Anonymize user feedback data
- Comply with relevant data protection regulations

## Scaling Considerations

### Horizontal Scaling

- Deploy multiple scraper instances for different news categories
- Use message queues for content generation tasks
- Implement load balancing for the review interface

### Vertical Scaling

- Increase server resources for content generation
- Optimize database queries and indexing
- Implement caching for frequently accessed data

## Maintenance Schedule

### Daily Tasks

- Monitor log files for errors
- Check content generation statistics
- Review and approve pending content

### Weekly Tasks

- Database cleanup and optimization
- Performance monitoring and analysis
- Update news source configurations

### Monthly Tasks

- Security updates and patches
- API usage analysis and optimization
- System backup and disaster recovery testing

## Support and Documentation

For additional support and documentation:

- Review the system architecture document
- Check the API documentation for each component
- Monitor the project repository for updates
- Contact the development team for technical support

This deployment guide provides the foundation for successfully implementing the Agentic News Workflow System in your environment. Regular monitoring and maintenance will ensure optimal performance and reliability.

