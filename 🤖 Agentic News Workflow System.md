# 🤖 Agentic News Workflow System

An intelligent, automated news aggregation and content generation system that scrapes the latest technology and leadership news, generates high-quality articles and social media posts using AI, and provides a streamlined review interface for content approval.

## 🌟 Features

### 📰 Intelligent News Scraping
- **Multi-source aggregation**: RSS feeds, News API, and direct web scraping
- **Smart categorization**: Automatic classification of technology and leadership content
- **Reliable sources**: TechCrunch, Ars Technica, The Verge, Harvard Business Review, and more
- **Duplicate detection**: Prevents redundant content collection

### 🧠 AI-Powered Content Generation
- **Article creation**: Generates comprehensive 800+ word articles from multiple news sources
- **Social media posts**: Creates platform-optimized content for Twitter and LinkedIn
- **Content summarization**: Intelligent extraction of key insights and trends
- **Customizable output**: Configurable word counts and content styles

### 📋 Review & Approval Workflow
- **Web-based interface**: Clean, responsive design for content review
- **Approval system**: Easy approve/reject workflow with feedback options
- **Content editing**: In-browser editing capabilities for fine-tuning
- **Real-time statistics**: Dashboard showing content generation metrics

### 🔄 Automated Scheduling
- **Daily workflows**: Automated scraping and content generation
- **Flexible scheduling**: Configurable timing and frequency
- **Error handling**: Robust error recovery and logging
- **Status monitoring**: Real-time system health checks

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   News Sources  │───▶│  Scraping Engine │───▶│   News Database │
│                 │    │                  │    │                 │
│ • RSS Feeds     │    │ • RSS Parser     │    │ • SQLite        │
│ • News APIs     │    │ • Web Scraper    │    │ • Article Store │
│ • Direct Web    │    │ • Content Filter │    │ • Metadata      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
                                                         ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Review Interface│◀───│  Content Generator│◀───│  AI Processing  │
│                 │    │                  │    │                 │
│ • Web Dashboard │    │ • Article Writer │    │ • OpenAI GPT    │
│ • Approval Flow │    │ • Post Creator   │    │ • LangChain     │
│ • Content Edit  │    │ • Quality Check  │    │ • Summarization │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- OpenAI API key
- Internet connection

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd agentic_news_workflow
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your OpenAI API key
```

4. **Run the system**
```bash
# Start the review interface
cd review_interface
source venv/bin/activate
python src/main.py

# In another terminal, run the workflow
cd ..
python run_workflow.py --mode full
```

5. **Access the interface**
Open your browser to `http://localhost:5000`

## 📖 Usage Guide

### Command Line Interface

The system provides a flexible CLI for different operations:

```bash
# Run complete daily workflow
python run_workflow.py --mode full

# Run only news scraping
python run_workflow.py --mode scrape

# Generate content for specific category
python run_workflow.py --mode generate --category technology

# Check system status
python run_workflow.py --mode status

# Enable verbose logging
python run_workflow.py --mode full --verbose
```

### Web Interface

1. **Dashboard**: View statistics and system status
2. **Scrape News**: Manually trigger news collection
3. **Generate Content**: Create articles and posts from scraped news
4. **Review Content**: Approve, reject, or edit generated content
5. **Monitor Progress**: Track daily content generation metrics

### Automated Scheduling

Set up automated daily workflows using cron:

```bash
# Daily scraping at 6 AM
0 6 * * * cd /path/to/project && python run_workflow.py --mode scrape

# Daily content generation at 8 AM  
0 8 * * * cd /path/to/project && python run_workflow.py --mode generate
```

## ⚙️ Configuration

### News Sources

Configure news sources in `config/config.py`:

```python
NEWS_SOURCES = {
    'technology': [
        'https://techcrunch.com/feed/',
        'https://feeds.arstechnica.com/arstechnica/index',
        'https://www.theverge.com/rss/index.xml'
    ],
    'leadership': [
        'https://feeds.hbr.org/harvardbusiness',
        'https://sloanreview.mit.edu/feed/'
    ]
}
```

### Content Generation

Customize content parameters:

```python
CONTENT_CONFIG = {
    'max_articles_per_day': 5,
    'article_word_count': 800,
    'social_platforms': ['twitter', 'linkedin'],
    'ai_model': 'gpt-4.1-mini'
}
```

### API Configuration

Set up your API keys in `.env`:

```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.manus.im/api/llm-proxy/v1
NEWS_API_KEY=your_news_api_key_here  # Optional
```

## 📁 Project Structure

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
│   ├── src/
│   │   ├── main.py       # Flask application
│   │   ├── routes/       # API endpoints
│   │   └── static/       # Frontend files
│   └── venv/             # Virtual environment
├── data/                  # Database files
│   ├── news_database.db
│   └── content_database.db
├── logs/                  # Log files
├── run_workflow.py        # Main workflow runner
├── deployment_guide.md    # Detailed deployment instructions
└── README.md             # This file
```

## 🔧 API Reference

### Content Management API

- `GET /api/content/pending` - Get pending content for review
- `POST /api/content/articles/{id}/approve` - Approve an article
- `POST /api/content/articles/{id}/reject` - Reject an article
- `POST /api/content/articles/{id}/edit` - Edit an article
- `POST /api/content/posts/{id}/approve` - Approve a social post
- `POST /api/content/generate` - Trigger content generation
- `POST /api/content/scrape` - Trigger news scraping
- `GET /api/content/stats` - Get system statistics

### Workflow API

The `WorkflowRunner` class provides programmatic access:

```python
from run_workflow import WorkflowRunner

runner = WorkflowRunner()

# Run daily workflow
result = runner.run_daily_workflow(['technology'])

# Get system status
status = runner.get_status()

# Run specific components
scraping_result = runner.run_scraping_only()
generation_result = runner.run_generation_only('leadership')
```

## 🛠️ Development

### Setting up Development Environment

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install development dependencies**
```bash
pip install -r requirements.txt
pip install pytest black flake8  # Development tools
```

3. **Run tests**
```bash
python test_scraper.py
python test_content_generator.py
```

### Adding New News Sources

1. Add RSS feed URL to `config/config.py`
2. Test with `python run_workflow.py --mode scrape`
3. Verify articles appear in database

### Customizing Content Generation

1. Modify prompts in `content_generator/content_generator.py`
2. Adjust parameters in `config/config.py`
3. Test with `python run_workflow.py --mode generate`

## 📊 Monitoring & Analytics

### Log Files

- `logs/news_workflow.log` - Main application logs
- `review_interface/logs/news_workflow.log` - Web interface logs

### Database Queries

```sql
-- Check recent articles
SELECT title, source, scraped_date FROM articles 
WHERE date(scraped_date) = date('now') 
ORDER BY scraped_date DESC;

-- View content generation stats
SELECT status, COUNT(*) as count 
FROM generated_articles 
GROUP BY status;

-- Monitor daily performance
SELECT date(generated_date) as date, 
       COUNT(*) as articles_generated
FROM generated_articles 
GROUP BY date(generated_date)
ORDER BY date DESC;
```

### Performance Metrics

- **Scraping Rate**: ~2-3 articles per minute
- **Generation Time**: ~30-60 seconds per article
- **API Usage**: ~1000-2000 tokens per article
- **Storage**: ~1MB per 100 articles

## 🔒 Security & Privacy

### Data Protection
- Local SQLite databases (no cloud storage)
- API keys stored in environment variables
- No personal data collection
- Configurable data retention policies

### Access Control
- Web interface runs on localhost by default
- No authentication required for local use
- HTTPS recommended for production deployment
- Rate limiting on API endpoints

## 🚨 Troubleshooting

### Common Issues

**"Module not found" errors**
```bash
pip install -r requirements.txt
source venv/bin/activate  # Ensure virtual environment is active
```

**"Database locked" errors**
```bash
# Check for running processes
ps aux | grep python
# Kill any hanging processes
pkill -f "python.*workflow"
```

**"API rate limit exceeded"**
- Reduce content generation frequency
- Check OpenAI usage dashboard
- Consider upgrading API plan

**"No articles scraped"**
- Check internet connection
- Verify RSS feed URLs are accessible
- Review logs for specific error messages

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
python run_workflow.py --mode full --verbose
```

### Getting Help

1. Check the logs in `logs/news_workflow.log`
2. Review the deployment guide for detailed setup instructions
3. Test individual components using the test scripts
4. Check API key configuration and permissions

## 🤝 Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions
- Include error handling and logging
- Test with multiple news sources
- Update documentation for new features

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT models
- LangChain for the AI framework
- Flask for the web framework
- Beautiful Soup for web scraping capabilities
- All the news sources for providing RSS feeds

---

**Built with ❤️ by the Manus AI Team**

For more information, visit our [documentation](deployment_guide.md) or contact our support team.

