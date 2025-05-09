from flask import Flask
from flask_cors import CORS
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from SSD_WEEK5.backend.config import Config
from routes.intelligence_routes import intelligence_bp
from asgiref.wsgi import WsgiToAsgi
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app, resources={
        r"/*": {  # Allow all routes
            "origins": ["http://localhost:5173"],  # Vite's default port
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

    @app.route('/')
    def index():
        return {"message": "API is working"}

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=True)
