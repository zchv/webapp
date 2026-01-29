"""
CLIP Semantic Image Search - Flask Web Application
Complete web UI with text, image, voice, and multimodal search capabilities
"""

import os
import uuid
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import logging

import config
from core.clip_model import CLIPModelWrapper
from core.faiss_index import FAISSIndexManager
from core.feedback import FeedbackManager
from api.search import search_bp, init_search_api

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """Create and configure Flask application."""
    app = Flask(
        __name__,
        template_folder=str(Path(__file__).parent / 'templates'),
        static_folder=str(Path(__file__).parent / 'static')
    )

    # Configuration
    app.config['SECRET_KEY'] = config.SECRET_KEY
    app.config['DEBUG'] = config.DEBUG
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_UPLOAD_SIZE

    # Enable CORS
    CORS(app)

    # Initialize ML components
    logger.info("Initializing ML components...")
    try:
        clip_model = CLIPModelWrapper()
        faiss_index = FAISSIndexManager()
        feedback_manager = FeedbackManager()

        # Load FAISS index and metadata
        logger.info("Loading FAISS index...")
        faiss_index.load_index()

        # Initialize search API with components
        init_search_api(clip_model, faiss_index, feedback_manager)

        logger.info("ML components initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize ML components: {e}")
        raise

    # Register blueprints
    app.register_blueprint(search_bp, url_prefix='/api/search')

    # Template routes
    @app.route('/')
    def index():
        """Main search page."""
        return render_template('index.html')

    @app.route('/settings')
    def settings():
        """Settings page."""
        return render_template('settings.html')

    @app.route('/stats')
    def stats():
        """Statistics page."""
        return render_template('stats.html')

    @app.route('/test-images')
    def test_images():
        """Test images page."""
        return render_template('test_images.html')

    # Serve images from data/images directory
    @app.route('/images/<path:filename>')
    def serve_image(filename):
        """Serve images from the data/images directory."""
        return send_from_directory(str(config.IMAGES_DIR), filename)

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint."""
        try:
            index_stats = faiss_index.get_stats()
            return jsonify({
                'status': 'healthy',
                'index': index_stats,
                'device': config.DEVICE
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

    # Example queries endpoint
    @app.route('/api/examples', methods=['GET'])
    def get_example_queries():
        """Get example queries."""
        examples = {
            'english': [
                'a person smiling happily',
                'red sports car on street',
                'delicious food on white plate',
                'beautiful sunset over mountains',
                'modern office interior',
                'cute dog playing in park'
            ],
            'chinese': [
                '一个开心微笑的人',
                '街道上的红色跑车',
                '白色盘子上的美食',
                '山上的美丽日落',
                '现代办公室内景',
                '公园里玩耍的可爱小狗'
            ]
        }
        return jsonify(examples)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404

    @app.errorhandler(500)
    def server_error(error):
        logger.error(f"Server error: {error}")
        return jsonify({'error': 'Internal server error'}), 500

    # Store components in app context for access in request handlers
    app.clip_model = clip_model
    app.faiss_index = faiss_index
    app.feedback_manager = feedback_manager

    return app

if __name__ == '__main__':
    app = create_app()
    logger.info(f"Starting Flask app on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=config.DEBUG)
