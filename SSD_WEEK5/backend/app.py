from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db
from routes.auth_routes import auth_bp
from routes.intelligence_routes import intelligence_bp
import os
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

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(intelligence_bp, url_prefix="/api")

    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")

    @app.route('/')
    def index():
        return {"message": "API is working"}

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    logger.info(f"Starting server on port {port}")
    # Convert Flask app to ASGI
    asgi_app = WsgiToAsgi(app)
    import uvicorn
    uvicorn.run(asgi_app, host="0.0.0.0", port=port)
