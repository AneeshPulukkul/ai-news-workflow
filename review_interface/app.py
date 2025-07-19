"""
Review Interface for Agentic News Workflow System
This module provides a Flask web application for reviewing generated content
"""

import os
import sys
import logging
from flask import Flask, send_from_directory
from flask_cors import CORS

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project config
from config.config import REVIEW_CONFIG

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('review_interface.log')
    ]
)
logger = logging.getLogger('review_interface')

# Import routes
from review_interface.routes import content_bp

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__, 
                static_folder=os.path.join(os.path.dirname(__file__), 'static'),
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
    
    # Configure app
    app.config['SECRET_KEY'] = REVIEW_CONFIG.get('secret_key', 'dev-secret-key')
    
    # Enable CORS for all routes
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(content_bp, url_prefix='/api/content')
    
    # Serve static files
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        static_folder_path = app.static_folder
        if static_folder_path is None:
            return "Static folder not configured", 404

        if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
            return send_from_directory(static_folder_path, path)
        else:
            index_path = os.path.join(static_folder_path, 'index.html')
            if os.path.exists(index_path):
                return send_from_directory(static_folder_path, 'index.html')
            else:
                return "index.html not found", 404
    
    logger.info("Review interface app created")
    return app

if __name__ == '__main__':
    app = create_app()
    port = REVIEW_CONFIG.get('port', 5000)
    debug = REVIEW_CONFIG.get('debug', True)
    
    logger.info(f"Starting review interface on port {port} (debug={debug})")
    app.run(host='0.0.0.0', port=port, debug=debug)
