"""
Content Generator Module for Agentic News Workflow
Handles AI-based content generation using scraped news articles.
"""

import os
import json
import logging
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any

# Import config using sys.path for relative imports
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.config import (
    DATABASE_CONFIG, CONTENT_CONFIG, LOGGING_CONFIG, PROMPTS_FILE_PATH, LLM_PROVIDER
)
from scrapers.news_scraper import NewsDatabase

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

# Conditional import for the LLM provider
if LLM_PROVIDER == 'openai':
    import openai
    openai.api_key = os.getenv("OPENAI_API_KEY")
else:
    raise ImportError(f"Unsupported LLM provider: {LLM_PROVIDER}")


class PromptManager:
    """Loads and manages prompts from a JSON file."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.prompts = self._load_prompts()

    def _load_prompts(self) -> Dict[str, Any]:
        """Loads prompts from the specified JSON file."""
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Prompts file not found at {self.file_path}")
            return {}
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from {self.file_path}")
            return {}

    def get_prompt(self, name: str, **kwargs) -> Optional[str]:
        """
        Gets a formatted prompt by name.
        
        Args:
            name: The name of the prompt (e.g., "generate_article").
            **kwargs: The values to format the prompt with.
            
        Returns:
            The formatted prompt string, or None if not found.
        """
        prompt_template = self.prompts.get(name, {}).get("prompt")
        if not prompt_template:
            logger.error(f"Prompt '{name}' not found in {self.file_path}")
            return None
        
        try:
            return prompt_template.format(**kwargs)
        except KeyError as e:
            logger.error(f"Missing key in prompt formatting: {e}")
            return None


class LLMService:
    """Service to interact with the language model provider."""
    
    def __init__(self, provider: str):
        self.provider = provider
        if self.provider == 'openai':
            if not openai.api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set.")
        else:
            raise ValueError(f"Unsupported LLM provider: {self.provider}")

    def generate(self, prompt: str, model: str, temperature: float, max_tokens: int) -> Optional[str]:
        """
        Generates content using the configured LLM provider.
        
        Args:
            prompt: The prompt to send to the model.
            model: The model to use for generation.
            temperature: The creativity of the response.
            max_tokens: The maximum number of tokens to generate.
            
        Returns:
            The generated text, or None if an error occurs.
        """
        try:
            if self.provider == 'openai':
                response = openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content.strip()
            else:
                logger.error(f"LLM provider '{self.provider}' not implemented.")
                return None
        except Exception as e:
            logger.error(f"Error during LLM generation: {e}")
            return None


class ContentDatabase:
    """
    Simple SQLite database handler for storing generated content
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or DATABASE_CONFIG['content_db_path']
        self.init_database()

    def init_database(self) -> None:
        """Initialize the database with required tables"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS generated_articles (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT,
                        category TEXT,
                        source_articles TEXT,
                        generated_date TEXT,
                        status TEXT DEFAULT 'pending',
                        feedback TEXT,
                        edited_content TEXT
                    )
                ''')
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS social_posts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        article_id INTEGER,
                        platform TEXT,
                        content TEXT,
                        generated_date TEXT,
                        status TEXT DEFAULT 'pending',
                        feedback TEXT,
                        edited_content TEXT,
                        FOREIGN KEY (article_id) REFERENCES generated_articles(id)
                    )
                ''')
                conn.commit()
                logger.info(f"Content database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Content database initialization error: {e}")
            raise

    def save_generated_content(self, content_data: Dict[str, Any]) -> Optional[int]:
        """Saves a generated article and its social posts."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Save article
                cursor.execute('''
                    INSERT INTO generated_articles 
                    (title, content, category, source_articles, generated_date, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    content_data['title'],
                    content_data['content'],
                    content_data['category'],
                    json.dumps(content_data['source_articles']),
                    content_data['generated_date'],
                    'pending'
                ))
                article_id = cursor.lastrowid
                
                # Save social posts
                for post in content_data.get('social_posts', []):
                    cursor.execute('''
                        INSERT INTO social_posts
                        (article_id, platform, content, generated_date, status)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        article_id,
                        post['platform'],
                        post['content'],
                        post['generated_date'],
                        'pending'
                    ))
                
                conn.commit()
                return article_id
        except Exception as e:
            logger.error(f"Error saving generated content: {e}")
            return None

    def get_pending_content(self, content_type: Optional[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieves all content that is pending review.
        
        Args:
            content_type: Optional filter for 'articles' or 'posts'.
            
        Returns:
            A dictionary containing lists of pending articles and posts.
        """
        result = {'articles': [], 'posts': []}
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get pending articles
                if content_type is None or content_type == 'articles':
                    cursor.execute("SELECT * FROM generated_articles WHERE status = 'pending'")
                    result['articles'] = [dict(row) for row in cursor.fetchall()]

                # Get pending posts
                if content_type is None or content_type == 'posts':
                    cursor.execute("SELECT * FROM social_posts WHERE status = 'pending'")
                    result['posts'] = [dict(row) for row in cursor.fetchall()]
            return result
        except Exception as e:
            logger.error(f"Error getting pending content: {e}")
            return result

    def update_article_status(self, article_id: int, status: str, feedback: str = '') -> bool:
        """Updates the status and feedback for a generated article."""
        return self._update_status('generated_articles', article_id, status, feedback)

    def update_post_status(self, post_id: int, status: str, feedback: str = '') -> bool:
        """Updates the status and feedback for a social post."""
        return self._update_status('social_posts', post_id, status, feedback)

    def _update_status(self, table_name: str, content_id: int, status: str, feedback: str) -> bool:
        """Generic method to update status for any content type."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    f"UPDATE {table_name} SET status = ?, feedback = ? WHERE id = ?",
                    (status, feedback, content_id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error updating status for {table_name} ID {content_id}: {e}")
            return False

    def get_article_stats(self) -> Dict[str, int]:
        """Gets statistics on generated articles by status."""
        return self._get_stats('generated_articles')

    def get_post_stats(self) -> Dict[str, int]:
        """Gets statistics on social posts by status."""
        return self._get_stats('social_posts')

    def _get_stats(self, table_name: str) -> Dict[str, int]:
        """Generic method to get statistics by status for a table."""
        stats = {'pending': 0, 'approved': 0, 'rejected': 0, 'total': 0}
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT status, COUNT(*) FROM {table_name} GROUP BY status")
                rows = cursor.fetchall()
                for status, count in rows:
                    if status in stats:
                        stats[status] = count
                stats['total'] = sum(stats.values())
                return stats
        except Exception as e:
            logger.error(f"Error getting stats for {table_name}: {e}")
            return stats


class ContentGenerator:
    """
    Generates articles and social media posts from scraped news.
    """
    
    def __init__(self, news_db: NewsDatabase, content_db: ContentDatabase, prompt_manager: PromptManager, llm_service: LLMService):
        self.news_db = news_db
        self.content_db = content_db
        self.prompt_manager = prompt_manager
        self.llm_service = llm_service

    def generate_article(self, source_articles: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Generates a single article from a list of source articles.
        
        Args:
            source_articles: A list of article dictionaries from the news database.
            
        Returns:
            A dictionary containing the generated article, or None on failure.
        """
        if not source_articles:
            return None

        sources_text = "\n\n".join([f"Title: {a['title']}\nSummary: {a['summary']}" for a in source_articles])
        
        prompt = self.prompt_manager.get_prompt(
            "generate_article",
            word_count=CONTENT_CONFIG['article_word_count'],
            sources=sources_text
        )
        
        if not prompt:
            return None
            
        generated_content = self.llm_service.generate(
            prompt,
            model=CONTENT_CONFIG['model'],
            temperature=CONTENT_CONFIG['temperature'],
            max_tokens=CONTENT_CONFIG['max_tokens']
        )
        
        if not generated_content:
            return None
            
        # Simple title extraction (can be improved)
        title = generated_content.split('\n')[0].replace("Title:", "").strip()
        
        return {
            "title": title,
            "content": generated_content,
            "category": source_articles[0]['category'],
            "source_articles": [a['id'] for a in source_articles],
            "generated_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def generate_social_post(self, article_content: str, article_title: str, platform: str) -> Optional[str]:
        """
        Generates a social media post for a given article.
        
        Args:
            article_content: The full text of the generated article.
            article_title: The title of the generated article.
            platform: The target social media platform (e.g., "twitter").
            
        Returns:
            The generated social media post text, or None on failure.
        """
        prompt = self.prompt_manager.get_prompt(
            "generate_social_post",
            platform=platform,
            title=article_title,
            content=article_content
        )
        
        if not prompt:
            return None
            
        return self.llm_service.generate(
            prompt,
            model=CONTENT_CONFIG['model'],
            temperature=CONTENT_CONFIG['temperature'],
            max_tokens=280 if platform == 'twitter' else 600
        )

    def generate_daily_content(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs the daily content generation workflow.
        
        Args:
            category: Optional category to generate content for.
            
        Returns:
            A summary of the generation process.
        """
        logger.info("Starting daily content generation workflow")
        start_time = datetime.now()
        
        articles_to_process = self.news_db.get_recent_articles(category=category, days=1)
        
        if not articles_to_process:
            logger.info("No new articles to process.")
            return {"status": "No new articles"}
            
        # Group articles by topic (simple keyword-based grouping)
        # This logic can be significantly improved (e.g., using embeddings)
        topic_groups = {}
        for article in articles_to_process:
            main_keyword = article['keywords'][0] if article['keywords'] else 'general'
            if main_keyword not in topic_groups:
                topic_groups[main_keyword] = []
            topic_groups[main_keyword].append(article)
            
        generated_count = 0
        for topic, group in topic_groups.items():
            if len(group) < 2:  # Need at least 2 articles to synthesize
                continue
                
            generated_article = self.generate_article(group)
            
            if generated_article:
                # Generate social posts
                social_posts = []
                for platform in CONTENT_CONFIG['social_platforms']:
                    post_content = self.generate_social_post(
                        generated_article['content'],
                        generated_article['title'],
                        platform
                    )
                    if post_content:
                        social_posts.append({
                            "platform": platform,
                            "content": post_content,
                            "generated_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        })
                
                generated_article['social_posts'] = social_posts
                
                # Save to database
                if self.content_db.save_generated_content(generated_article):
                    generated_count += 1
                    logger.info(f"Generated and saved content for topic: {topic}")

        summary = {
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'end_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'articles_generated': generated_count,
            'topics_processed': len(topic_groups)
        }
        
        logger.info(f"Content generation completed: {summary}")
        return summary


if __name__ == "__main__":
    # Example usage
    news_db_instance = NewsDatabase()
    content_db_instance = ContentDatabase()
    prompt_manager_instance = PromptManager(PROMPTS_FILE_PATH)
    llm_service_instance = LLMService(LLM_PROVIDER)
    
    generator = ContentGenerator(
        news_db=news_db_instance,
        content_db=content_db_instance,
        prompt_manager=prompt_manager_instance,
        llm_service=llm_service_instance
    )
    
    result = generator.generate_daily_content()
    print(f"Content generation completed: {result}")
