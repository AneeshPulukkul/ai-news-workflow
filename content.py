"""
Content routes for the review interface
Handles content retrieval, approval, and rejection
"""

import os
import sys
import json
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

# Add parent directories to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from content_generator.content_generator import ContentDatabase, ContentGenerator
from scrapers.news_scraper import NewsAggregator

content_bp = Blueprint('content', __name__)

# Initialize our components
content_db = ContentDatabase()
news_aggregator = NewsAggregator()
content_generator = ContentGenerator()

@content_bp.route('/pending', methods=['GET'])
@cross_origin()
def get_pending_content():
    """Get all pending content for review"""
    try:
        pending_content = content_db.get_pending_content()
        return jsonify({
            'success': True,
            'data': pending_content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/articles/<int:article_id>/approve', methods=['POST'])
@cross_origin()
def approve_article(article_id):
    """Approve an article"""
    try:
        data = request.get_json() or {}
        feedback = data.get('feedback', '')
        
        # Update article status in database
        import sqlite3
        db_path = content_db.db_path
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE generated_articles 
                SET status = 'approved', user_feedback = ?
                WHERE id = ?
            ''', (feedback, article_id))
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Article approved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/articles/<int:article_id>/reject', methods=['POST'])
@cross_origin()
def reject_article(article_id):
    """Reject an article"""
    try:
        data = request.get_json() or {}
        feedback = data.get('feedback', '')
        
        # Update article status in database
        import sqlite3
        db_path = content_db.db_path
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE generated_articles 
                SET status = 'rejected', user_feedback = ?
                WHERE id = ?
            ''', (feedback, article_id))
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Article rejected successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/articles/<int:article_id>/edit', methods=['POST'])
@cross_origin()
def edit_article(article_id):
    """Edit an article"""
    try:
        data = request.get_json()
        title = data.get('title')
        content = data.get('content')
        
        if not title or not content:
            return jsonify({
                'success': False,
                'error': 'Title and content are required'
            }), 400
        
        # Update article in database
        import sqlite3
        db_path = content_db.db_path
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE generated_articles 
                SET title = ?, content = ?, status = 'edited'
                WHERE id = ?
            ''', (title, content, article_id))
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Article updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/posts/<int:post_id>/approve', methods=['POST'])
@cross_origin()
def approve_post(post_id):
    """Approve a social media post"""
    try:
        data = request.get_json() or {}
        feedback = data.get('feedback', '')
        
        # Update post status in database
        import sqlite3
        db_path = content_db.db_path
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE generated_posts 
                SET status = 'approved', user_feedback = ?
                WHERE id = ?
            ''', (feedback, post_id))
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post approved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/posts/<int:post_id>/reject', methods=['POST'])
@cross_origin()
def reject_post(post_id):
    """Reject a social media post"""
    try:
        data = request.get_json() or {}
        feedback = data.get('feedback', '')
        
        # Update post status in database
        import sqlite3
        db_path = content_db.db_path
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE generated_posts 
                SET status = 'rejected', user_feedback = ?
                WHERE id = ?
            ''', (feedback, post_id))
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post rejected successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/posts/<int:post_id>/edit', methods=['POST'])
@cross_origin()
def edit_post(post_id):
    """Edit a social media post"""
    try:
        data = request.get_json()
        content = data.get('content')
        
        if not content:
            return jsonify({
                'success': False,
                'error': 'Content is required'
            }), 400
        
        # Update post in database
        import sqlite3
        db_path = content_db.db_path
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE generated_posts 
                SET content = ?, character_count = ?, status = 'edited'
                WHERE id = ?
            ''', (content, len(content), post_id))
            conn.commit()
        
        return jsonify({
            'success': True,
            'message': 'Post updated successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/generate', methods=['POST'])
@cross_origin()
def generate_content():
    """Trigger content generation"""
    try:
        data = request.get_json() or {}
        category = data.get('category')  # Optional category filter
        
        # Generate new content
        result = content_generator.generate_daily_content(category)
        
        # Save to database
        if result['articles'] or result['posts']:
            content_db.save_generated_content(result)
        
        return jsonify({
            'success': True,
            'data': result['generation_summary']
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/scrape', methods=['POST'])
@cross_origin()
def trigger_scraping():
    """Trigger news scraping"""
    try:
        # Run news scraping
        result = news_aggregator.run_daily_scraping()
        
        return jsonify({
            'success': True,
            'data': result
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@content_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_stats():
    """Get content statistics"""
    try:
        import sqlite3
        db_path = content_db.db_path
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get article stats
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM generated_articles 
                GROUP BY status
            ''')
            article_stats = dict(cursor.fetchall())
            
            # Get post stats
            cursor.execute('''
                SELECT status, COUNT(*) as count 
                FROM generated_posts 
                GROUP BY status
            ''')
            post_stats = dict(cursor.fetchall())
            
            # Get recent articles count
            cursor.execute('''
                SELECT COUNT(*) FROM generated_articles 
                WHERE date(generated_date) = date('now')
            ''')
            today_articles = cursor.fetchone()[0]
            
            # Get recent posts count
            cursor.execute('''
                SELECT COUNT(*) FROM generated_posts 
                WHERE date(generated_date) = date('now')
            ''')
            today_posts = cursor.fetchone()[0]
        
        return jsonify({
            'success': True,
            'data': {
                'article_stats': article_stats,
                'post_stats': post_stats,
                'today_articles': today_articles,
                'today_posts': today_posts
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

