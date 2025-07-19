"""
Content routes for the review interface
Handles content retrieval, approval, and rejection
"""

import os
import sys
import json
import logging
from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from typing import Dict, List, Any, Optional, Union, Tuple

# Initialize logger
logger = logging.getLogger('review_interface.routes')

# Create blueprint
content_bp = Blueprint('content', __name__)

# Import database components
from content_generator.content_generator import ContentDatabase
from scrapers.news_scraper import NewsDatabase

# Initialize our components
content_db = ContentDatabase()
news_db = NewsDatabase()

@content_bp.route('/pending', methods=['GET'])
@cross_origin()
def get_pending_content() -> Tuple[Dict[str, Any], int]:
    """
    Get all pending content for review
    
    Returns:
        JSON response with pending content and status code
    """
    try:
        pending_content = content_db.get_pending_content()
        logger.info(f"Retrieved {len(pending_content.get('articles', []))} pending articles and {len(pending_content.get('posts', []))} pending posts")
        return jsonify({
            'success': True,
            'data': pending_content
        }), 200
    except Exception as e:
        logger.error(f"Failed to get pending content: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@content_bp.route('/articles/<int:article_id>/approve', methods=['POST'])
@cross_origin()
def approve_article(article_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Approve an article
    
    Args:
        article_id: ID of the article to approve
        
    Returns:
        JSON response with success message and status code
    """
    try:
        data = request.get_json() or {}
        feedback = data.get('feedback', '')
        
        # Update article status in database
        content_db.update_article_status(article_id, 'approved', feedback)
        
        logger.info(f"Article {article_id} approved with feedback: {feedback[:50]}...")
        return jsonify({
            'success': True,
            'message': 'Article approved successfully',
            'article_id': article_id
        }), 200
    except Exception as e:
        logger.error(f"Failed to approve article {article_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@content_bp.route('/articles/<int:article_id>/reject', methods=['POST'])
@cross_origin()
def reject_article(article_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Reject an article
    
    Args:
        article_id: ID of the article to reject
        
    Returns:
        JSON response with success message and status code
    """
    try:
        data = request.get_json() or {}
        feedback = data.get('feedback', '')
        
        # Update article status in database
        content_db.update_article_status(article_id, 'rejected', feedback)
        
        logger.info(f"Article {article_id} rejected with feedback: {feedback[:50]}...")
        return jsonify({
            'success': True,
            'message': 'Article rejected successfully',
            'article_id': article_id
        }), 200
    except Exception as e:
        logger.error(f"Failed to reject article {article_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@content_bp.route('/posts/<int:post_id>/approve', methods=['POST'])
@cross_origin()
def approve_post(post_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Approve a social media post
    
    Args:
        post_id: ID of the post to approve
        
    Returns:
        JSON response with success message and status code
    """
    try:
        data = request.get_json() or {}
        feedback = data.get('feedback', '')
        
        # Update post status in database
        content_db.update_post_status(post_id, 'approved', feedback)
        
        logger.info(f"Post {post_id} approved with feedback: {feedback[:50]}...")
        return jsonify({
            'success': True,
            'message': 'Post approved successfully',
            'post_id': post_id
        }), 200
    except Exception as e:
        logger.error(f"Failed to approve post {post_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@content_bp.route('/posts/<int:post_id>/reject', methods=['POST'])
@cross_origin()
def reject_post(post_id: int) -> Tuple[Dict[str, Any], int]:
    """
    Reject a social media post
    
    Args:
        post_id: ID of the post to reject
        
    Returns:
        JSON response with success message and status code
    """
    try:
        data = request.get_json() or {}
        feedback = data.get('feedback', '')
        
        # Update post status in database
        content_db.update_post_status(post_id, 'rejected', feedback)
        
        logger.info(f"Post {post_id} rejected with feedback: {feedback[:50]}...")
        return jsonify({
            'success': True,
            'message': 'Post rejected successfully',
            'post_id': post_id
        }), 200
    except Exception as e:
        logger.error(f"Failed to reject post {post_id}: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@content_bp.route('/stats', methods=['GET'])
@cross_origin()
def get_statistics() -> Tuple[Dict[str, Any], int]:
    """
    Get content statistics
    
    Returns:
        JSON response with content statistics and status code
    """
    try:
        # Get content statistics
        article_stats = content_db.get_article_stats()
        post_stats = content_db.get_post_stats()
        source_stats = news_db.get_source_stats()
        
        return jsonify({
            'success': True,
            'data': {
                'articles': article_stats,
                'posts': post_stats,
                'sources': source_stats
            }
        }), 200
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500
