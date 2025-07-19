# Agentic News Workflow System

A comprehensive system for automatically scraping news from various sources, generating content using AI, and providing a review interface for human oversight.

## Features

- Multi-source news scraping (RSS feeds, web pages, News API)
- AI-powered content generation (articles and social media posts)
- Web-based review interface
- Category-based processing (technology, leadership)
- Docker containerization for easy deployment
- Comprehensive testing suite

## Documentation

- [Technical Design Document](docs/Technical_Design_Document.md) - Detailed architecture and design decisions
- [Code Walkthrough](docs/Code_Walkthrough.md) - Comprehensive explanation of code structure and functionality
- [Database Schema Documentation](docs/Database_Schema_Documentation.md) - Details of database tables and relationships
- [Troubleshooting Guide](docs/Troubleshooting_Guide.md) - Solutions for common issues
- [Deployment Guide](Agentic%20News%20Workflow%20System%20-%20Deployment%20Guide.md) - Instructions for deploying the system

## Project Structure

```
agentic-news-workflow/
├── config/                     # Configuration files
│   ├── __init__.py
│   └── config.py
├── content_generator/          # Content generation module
│   ├── __init__.py
│   └── content_generator.py
├── data/                       # Data storage
│   ├── content.db
│   └── news.db
├── docs/                       # Documentation
│   ├── Technical_Design_Document.md
│   ├── Code_Walkthrough.md
│   ├── Database_Schema_Documentation.md
│   └── Troubleshooting_Guide.md
├── logs/                       # Log files
├── review_interface/           # Web review interface
│   ├── __init__.py
│   ├── app.py
│   ├── routes.py
│   ├── static/
│   └── templates/
├── scrapers/                   # News scraping modules
│   ├── __init__.py
│   └── news_scraper.py
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_content_generator.py
│   └── test_scraper.py
├── .env.example                # Environment variables template
├── docker-compose.yml          # Docker Compose configuration
├── Dockerfile                  # Docker image definition
├── docker_utils.py             # Docker utility script
├── requirements.txt            # Python dependencies
├── run_workflow.py             # Main workflow script
└── README.md                   # Project documentation
```

## Setup and Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/agentic-news-workflow.git
   cd agentic-news-workflow
   ```

2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create environment variables file:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

5. Create data directories:
   ```bash
   mkdir -p data logs
   ```

### Docker Deployment

1. Make sure Docker and Docker Compose are installed on your system.

2. Build and start the containers:
   ```bash
   python docker_utils.py build
   python docker_utils.py start
   ```

3. Check the status of the services:
   ```bash
   python docker_utils.py status
   ```

For detailed deployment instructions, see the [Deployment Guide](Agentic%20News%20Workflow%20System%20-%20Deployment%20Guide.md).
   python docker_utils.py build
   python docker_utils.py start
   ```

3. Check the status of the services:
   ```bash
   python docker_utils.py status
   ```

## Usage

### Running the Workflow

To run the complete workflow:
```bash
python run_workflow.py
```

To run only the scraping step:
```bash
python run_workflow.py --mode scrape
```

To run only the content generation for a specific category:
```bash
python run_workflow.py --mode generate --category technology
```

### Using the Review Interface

Start the review interface:
```bash
python review_interface/app.py
```

Then open your browser at: http://localhost:5000

### Docker Commands

The `docker_utils.py` script provides easy access to common Docker operations:

```bash
# Build containers
python docker_utils.py build

# Start services
python docker_utils.py start

# Stop services
python docker_utils.py stop

# View logs
python docker_utils.py logs
python docker_utils.py logs --service workflow --follow

# Run workflow in container
python docker_utils.py workflow
python docker_utils.py workflow --category technology

# Check status
python docker_utils.py status

# Execute command in a service
python docker_utils.py exec workflow python -c "print('Hello, World!')"
```

## Development

For developers looking to extend or modify the system:

1. Read the [Code Walkthrough](docs/Code_Walkthrough.md) to understand the codebase
2. Review the [Technical Design Document](docs/Technical_Design_Document.md) for architecture details
3. Consult the [Database Schema Documentation](docs/Database_Schema_Documentation.md) for data structure information
4. Use the [Troubleshooting Guide](docs/Troubleshooting_Guide.md) if you encounter issues

### Adding New News Sources

To add a new news source, update the `NEWS_SOURCES` dictionary in `config/config.py`:

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

See the [Code Walkthrough](docs/Code_Walkthrough.md) for more details on extending the system.

## Testing

Run the test suite:
```bash
pytest tests/
```

Run specific test files:
```bash
pytest tests/test_scraper.py
pytest tests/test_content_generator.py
```

## Troubleshooting

If you encounter issues while setting up or running the system, consult the [Troubleshooting Guide](docs/Troubleshooting_Guide.md) for solutions to common problems.

## License

[MIT License](LICENSE)
