"""
AI Content Generator Module for Agentic News Workflow
Handles content generation using OpenAI and LangChain
"""

import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
import json
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai

from config.config import CONTENT_CONFIG, LOGGING_CONFIG
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


class ContentGenerator:
    """AI-powered content generator using OpenAI and LangChain"""
    
    def __init__(self, model_name: str = "gpt-4.1-mini"):
        """Initialize the content generator with OpenAI model"""
        self.model_name = model_name
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            max_tokens=2000
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=200
        )
        self.database = NewsDatabase()
    
    def summarize_articles(self, articles: List[Dict]) -> List[Dict]:
        """Summarize multiple articles into key insights"""
        summaries = []
        
        for article in articles:
            try:
                summary = self._summarize_single_article(article)
                if summary:
                    summaries.append({
                        'original_article': article,
                        'summary': summary,
                        'key_points': self._extract_key_points(article['content'])
                    })
            except Exception as e:
                logger.error(f"Error summarizing article {article.get('title', 'Unknown')}: {e}")
                continue
        
        return summaries
    
    def _summarize_single_article(self, article: Dict) -> str:
        """Summarize a single article"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert content summarizer. Create a concise, informative summary 
            of the given news article. Focus on the key facts, implications, and relevance to the topic.
            Keep the summary between 100-200 words."""),
            ("human", """Article Title: {title}
            Article Content: {content}
            
            Please provide a clear, concise summary of this article.""")
        ])
        
        try:
            # Truncate content if too long
            content = article['content'][:3000] if len(article['content']) > 3000 else article['content']
            
            chain = prompt | self.llm
            response = chain.invoke({
                "title": article['title'],
                "content": content
            })
            
            return response.content.strip()
        
        except Exception as e:
            logger.error(f"Error in LLM summarization: {e}")
            return ""
    
    def _extract_key_points(self, content: str) -> List[str]:
        """Extract key points from article content"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract 3-5 key points from the given article content. 
            Each point should be a concise bullet point highlighting important information.
            Return the points as a JSON list of strings."""),
            ("human", "Article Content: {content}")
        ])
        
        try:
            content = content[:2000] if len(content) > 2000 else content
            
            chain = prompt | self.llm
            response = chain.invoke({"content": content})
            
            # Try to parse as JSON, fallback to simple list
            try:
                key_points = json.loads(response.content)
                if isinstance(key_points, list):
                    return key_points
            except:
                # Fallback: split by lines and clean up
                lines = response.content.strip().split('\n')
                return [line.strip('- •').strip() for line in lines if line.strip()]
        
        except Exception as e:
            logger.error(f"Error extracting key points: {e}")
            return []
    
    def generate_article(self, topic: str, source_articles: List[Dict], target_length: int = 800) -> Dict:
        """Generate a comprehensive article based on multiple source articles"""
        
        # First, summarize the source articles
        summaries = self.summarize_articles(source_articles)
        
        if not summaries:
            logger.warning("No summaries generated from source articles")
            return {}
        
        # Create context from summaries
        context = self._create_article_context(summaries, topic)
        
        # Generate the article
        article_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert technology and leadership writer. Create an engaging, 
            informative article based on the provided context and summaries. The article should:
            
            1. Have a compelling headline
            2. Include an engaging introduction
            3. Present information in a logical flow
            4. Include insights and analysis, not just facts
            5. Have a strong conclusion
            6. Be approximately {target_length} words
            7. Use a professional but accessible tone
            8. Include relevant quotes or data points when available
            
            Focus on providing value to readers interested in {topic}."""),
            ("human", """Topic: {topic}
            
            Context and Source Information:
            {context}
            
            Please write a comprehensive article based on this information.""")
        ])
        
        try:
            chain = article_prompt | self.llm
            response = chain.invoke({
                "topic": topic,
                "context": context,
                "target_length": target_length
            })
            
            article_content = response.content.strip()
            
            # Extract title (assume first line is the title)
            lines = article_content.split('\n')
            title = lines[0].strip('# ').strip()
            content = '\n'.join(lines[1:]).strip()
            
            return {
                'title': title,
                'content': content,
                'topic': topic,
                'source_count': len(source_articles),
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'word_count': len(content.split()),
                'source_articles': [article['url'] for article in source_articles]
            }
        
        except Exception as e:
            logger.error(f"Error generating article: {e}")
            return {}
    
    def generate_social_posts(self, article: Dict, platforms: List[str] = ['twitter', 'linkedin']) -> Dict:
        """Generate social media posts based on an article"""
        posts = {}
        
        for platform in platforms:
            try:
                post = self._generate_platform_post(article, platform)
                if post:
                    posts[platform] = post
            except Exception as e:
                logger.error(f"Error generating {platform} post: {e}")
                continue
        
        return posts
    
    def _generate_platform_post(self, article: Dict, platform: str) -> Dict:
        """Generate a post for a specific social media platform"""
        
        platform_configs = {
            'twitter': {
                'max_length': 280,
                'style': 'concise, engaging, with relevant hashtags',
                'format': 'Tweet format with hashtags'
            },
            'linkedin': {
                'max_length': 1300,
                'style': 'professional, insightful, thought-provoking',
                'format': 'LinkedIn post format with professional tone'
            }
        }
        
        config = platform_configs.get(platform, platform_configs['twitter'])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Create a {platform} post based on the given article. The post should:
            
            1. Be engaging and {config['style']}
            2. Stay within {config['max_length']} characters
            3. Use {config['format']}
            4. Include a call-to-action when appropriate
            5. Capture the key insight from the article
            
            For Twitter: Include 2-3 relevant hashtags
            For LinkedIn: Focus on professional insights and industry implications"""),
            ("human", """Article Title: {title}
            Article Content: {content}
            
            Create an engaging {platform} post based on this article.""")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "title": article['title'],
                "content": article['content'][:1000],  # Truncate for context
                "platform": platform
            })
            
            post_content = response.content.strip()
            
            return {
                'platform': platform,
                'content': post_content,
                'character_count': len(post_content),
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'source_article': article.get('title', 'Unknown')
            }
        
        except Exception as e:
            logger.error(f"Error generating {platform} post: {e}")
            return {}
    
    def _create_article_context(self, summaries: List[Dict], topic: str) -> str:
        """Create context string from article summaries"""
        context_parts = []
        
        for i, summary_data in enumerate(summaries, 1):
            article = summary_data['original_article']
            summary = summary_data['summary']
            key_points = summary_data['key_points']
            
            context_part = f"""
Source {i}: {article['title']} ({article['source']})
Summary: {summary}
Key Points: {', '.join(key_points[:3])}  # Limit to top 3 points
URL: {article['url']}
"""
            context_parts.append(context_part)
        
        return '\n'.join(context_parts)
    
    def generate_daily_content(self, category: str = None) -> Dict:
        """Generate daily content based on recent articles"""
        logger.info(f"Starting daily content generation for category: {category or 'all'}")
        
        # Get recent articles from database
        recent_articles = self.database.get_recent_articles(category, days=1)
        
        if not recent_articles:
            logger.warning("No recent articles found for content generation")
            return {'articles': [], 'posts': []}
        
        logger.info(f"Found {len(recent_articles)} recent articles")
        
        generated_content = {
            'articles': [],
            'posts': [],
            'generation_summary': {
                'total_source_articles': len(recent_articles),
                'generated_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'category': category or 'all'
            }
        }
        
        # Group articles by category for better content generation
        articles_by_category = {}
        for article in recent_articles:
            cat = article['category']
            if cat not in articles_by_category:
                articles_by_category[cat] = []
            articles_by_category[cat].append(article)
        
        # Generate articles for each category
        for cat, articles in articles_by_category.items():
            if len(articles) >= 2:  # Need at least 2 articles to generate content
                logger.info(f"Generating article for category: {cat}")
                
                # Take top articles (by relevance/keywords)
                top_articles = self._select_top_articles(articles, max_count=5)
                
                generated_article = self.generate_article(cat, top_articles)
                if generated_article:
                    generated_content['articles'].append(generated_article)
                    
                    # Generate social posts for the article
                    social_posts = self.generate_social_posts(generated_article)
                    for platform, post in social_posts.items():
                        post['source_article_title'] = generated_article['title']
                        generated_content['posts'].append(post)
        
        # Update generation summary
        generated_content['generation_summary'].update({
            'articles_generated': len(generated_content['articles']),
            'posts_generated': len(generated_content['posts'])
        })
        
        logger.info(f"Content generation completed: {generated_content['generation_summary']}")
        return generated_content
    
    def _select_top_articles(self, articles: List[Dict], max_count: int = 5) -> List[Dict]:
        """Select top articles based on relevance and keywords"""
        # Simple scoring based on keyword count and content length
        scored_articles = []
        
        for article in articles:
            score = 0
            
            # Score based on keyword count
            keywords = article.get('keywords', [])
            score += len(keywords) * 2
            
            # Score based on content length (prefer substantial articles)
            content_length = len(article.get('content', ''))
            if 500 <= content_length <= 3000:
                score += 3
            elif content_length > 3000:
                score += 2
            elif content_length > 200:
                score += 1
            
            # Score based on source reliability (simple heuristic)
            reliable_sources = ['TechCrunch', 'Harvard Business Review', 'MIT Sloan', 'McKinsey']
            if article.get('source') in reliable_sources:
                score += 2
            
            scored_articles.append((score, article))
        
        # Sort by score and return top articles
        scored_articles.sort(key=lambda x: x[0], reverse=True)
        return [article for score, article in scored_articles[:max_count]]


class ContentDatabase:
    """Database handler for generated content"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or 'data/content_database.db'
        self.init_database()
    
    def init_database(self):
        """Initialize the content database"""
        import sqlite3
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Generated articles table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generated_articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    topic TEXT,
                    source_count INTEGER,
                    generated_date TEXT,
                    word_count INTEGER,
                    source_articles TEXT,
                    status TEXT DEFAULT 'pending',
                    user_feedback TEXT
                )
            ''')
            
            # Generated posts table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS generated_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    platform TEXT NOT NULL,
                    content TEXT NOT NULL,
                    character_count INTEGER,
                    generated_date TEXT,
                    source_article_title TEXT,
                    status TEXT DEFAULT 'pending',
                    user_feedback TEXT
                )
            ''')
            
            conn.commit()
    
    def save_generated_content(self, content_data: Dict) -> bool:
        """Save generated content to database"""
        import sqlite3
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Save articles
                for article in content_data.get('articles', []):
                    cursor.execute('''
                        INSERT INTO generated_articles 
                        (title, content, topic, source_count, generated_date, word_count, source_articles)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        article['title'],
                        article['content'],
                        article['topic'],
                        article['source_count'],
                        article['generated_date'],
                        article['word_count'],
                        json.dumps(article['source_articles'])
                    ))
                
                # Save posts
                for post in content_data.get('posts', []):
                    cursor.execute('''
                        INSERT INTO generated_posts 
                        (platform, content, character_count, generated_date, source_article_title)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        post['platform'],
                        post['content'],
                        post['character_count'],
                        post['generated_date'],
                        post.get('source_article_title', '')
                    ))
                
                conn.commit()
                return True
        
        except Exception as e:
            logger.error(f"Error saving generated content: {e}")
            return False
    
    def get_pending_content(self) -> Dict:
        """Get content pending review"""
        import sqlite3
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get pending articles
                cursor.execute('''
                    SELECT * FROM generated_articles WHERE status = 'pending'
                    ORDER BY generated_date DESC
                ''')
                article_columns = [description[0] for description in cursor.description]
                articles = [dict(zip(article_columns, row)) for row in cursor.fetchall()]
                
                # Get pending posts
                cursor.execute('''
                    SELECT * FROM generated_posts WHERE status = 'pending'
                    ORDER BY generated_date DESC
                ''')
                post_columns = [description[0] for description in cursor.description]
                posts = [dict(zip(post_columns, row)) for row in cursor.fetchall()]
                
                return {'articles': articles, 'posts': posts}
        
        except Exception as e:
            logger.error(f"Error retrieving pending content: {e}")
            return {'articles': [], 'posts': []}


if __name__ == "__main__":
    # Example usage
    generator = ContentGenerator()
    content_db = ContentDatabase()
    
    # Generate daily content
    result = generator.generate_daily_content()
    
    # Save to database
    if result['articles'] or result['posts']:
        content_db.save_generated_content(result)
        print(f"Generated and saved: {len(result['articles'])} articles, {len(result['posts'])} posts")
    else:
        print("No content generated")

