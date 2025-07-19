# 🤖 Agentic News Workflow System

An intelligent, automated news aggregation and content generation system that scrapes the latest technology and leadership news, generates high-quality articles and social media posts using AI, and provides a streamlined review interface for content approval.

## 🌟 Features

- **Multi-Source Aggregation**: Scrapes from RSS feeds, News APIs, and directly from websites.
- **AI-Powered Content Generation**: Uses Large Language Models (like OpenAI's GPT series) to generate unique articles and social media posts.
- **Configurable & Modular**: Easily add new news sources, change AI prompts, and switch LLM providers through simple configuration files.
- **Review & Approval Workflow**: A simple Flask-based web interface to review, edit, and approve generated content.
- **Informative Console Output**: Uses the `rich` library to provide a beautiful and clear view of the workflow's progress in the terminal.
- **Local-First Storage**: Uses SQLite for local database storage, keeping your data private.

## 🏗️ System Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│   News Sources  │─────▶│  Scraping Engine │─────▶│   News Database │
│ (Configurable)  │      │ (news_scraper.py)│      │ (SQLite)        │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                                                           │
                                                           ▼
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│ Review Interface│◀─────│ Content Database │◀─────│ Content Generator│
│ (Flask app.py)  │      │ (SQLite)         │      │(content_gen.py) │
└─────────────────┘      └──────────────────┘      └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- An OpenAI API key (or another compatible LLM provider key)

### Installation

1.  **Clone the repository**
    ```bash
    git clone <repository_url>
    cd agentic-news-workflow
    ```

2.  **Create and activate a virtual environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure environment**
    *   Create a `.env` file in the root directory.
    *   Add your API key:
        ```
        OPENAI_API_KEY="your-key-here"
        NEWSAPI_ORG_KEY="your-key-here" # Optional
        ```

5.  **Run the workflow**
    ```bash
    python run_workflow.py
    ```
    This will scrape the latest news and generate content.

6.  **Review the content**
    ```bash
    python app.py
    ```
    Open your browser to `http://127.0.0.1:5000` to see the review interface.

## 📖 Usage Guide

### Command Line Interface

The `run_workflow.py` script orchestrates the main tasks.

```bash
# Run the complete daily workflow for all categories
python run_workflow.py

# Run the workflow for specific categories
python run_workflow.py --categories technology leadership
```

### Web Interface

The web interface, launched with `python app.py`, allows you to:
- View all generated articles and social media posts.
- See the status of each piece of content (e.g., "pending", "approved").
- Edit and approve content.

## ⚙️ Configuration

### News Sources (`config/config.py`)

Add or modify news sources in the `NEWS_SOURCES` dictionary. You can specify an RSS feed, a base URL for web scraping, and CSS selectors to find article links.

```python
NEWS_SOURCES = {
    'technology': [
        {
            'name': 'TechCrunch',
            'url': 'https://techcrunch.com/',
            'rss_feed': 'https://techcrunch.com/feed/',
            'selectors': { 'article_link': 'a.post-block__title__link' }
        },
        # ... other sources
    ],
}
```

### AI Prompts (`config/prompts.json`)

Customize the prompts used for content generation by editing this JSON file. This allows you to change the AI's tone, style, and output format without changing the code.

```json
{
  "generate_article": {
    "system_prompt": "You are an expert journalist...",
    "human_prompt": "Based on the following articles, write a comprehensive overview..."
  },
  "generate_linkedin_post": {
    "system_prompt": "You are a social media marketing expert...",
    "human_prompt": "Create a LinkedIn post about the following article..."
  }
}
```

## 📁 Project Structure

```
.
├── config/                 # Configuration files
│   ├── config.py           # Main configuration for sources, APIs
│   └── prompts.json        # AI prompt templates
├── content_generator/      # AI content generation logic
│   └── content_generator.py
├── scrapers/               # News scraping components
│   └── news_scraper.py
├── static/                 # CSS for the web app
├── templates/              # HTML templates for the web app
├── data/                   # SQLite databases are stored here
├── logs/                   # Log files
├── .env                    # For API keys
├── app.py                  # Flask web application for review
├── run_workflow.py         # Main workflow runner script
└── requirements.txt        # Python dependencies
```

## 🛠️ Development & Testing

1.  **Set up the environment** as described in the Quick Start.
2.  **Install development dependencies**:
    ```bash
    pip install pytest black flake8
    ```
3.  **Run tests** to ensure core functionality is working:
    ```bash
    python -m pytest
    ```
    (Note: Test files would need to be created for this).

## 🤝 Contributing

Contributions are welcome! Please fork the repository, create a feature branch, and submit a pull request.

## 📄 License

This project is licensed under the MIT License.

