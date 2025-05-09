from flask import Flask, request, jsonify
from flask_cors import CORS
from config import Config
from routes.intelligence_routes import intelligence_bp
from routes.network_intelligence_routes import network_intelligence_bp
from extensions import db
import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging
import argparse

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    db.init_app(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
        logger.info("Database tables created successfully")

    # Enable CORS for all origins in development
    CORS(app, resources={
        r"/*": {
            "origins": "*",  # Allow all origins in development
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })

    # Configure rate limiter
    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"]
    )

    # Register blueprints
    app.register_blueprint(intelligence_bp, url_prefix="/api")
    app.register_blueprint(network_intelligence_bp)

    @app.route('/')
    def index():
        return {"message": "API is working"}

    return app

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5001)
    args = parser.parse_args()

    app = create_app()
    logger.info(f"Starting server on port {args.port}")
    app.run(host="0.0.0.0", port=args.port, debug=True)
