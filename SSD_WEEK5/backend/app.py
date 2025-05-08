from flask import Flask
from flask_cors import CORS
from config import Config
from extensions import db
from routes.auth_routes import auth_bp
from routes.intelligence_routes import intelligence_bp
import os
from asgiref.wsgi import WsgiToAsgi

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:8080"],  # Frontend URL
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(intelligence_bp, url_prefix="/api")

    @app.route('/')
    def index():
        return {"message": "API is working"}

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get('PORT', 5001))
    # Convert Flask app to ASGI
    asgi_app = WsgiToAsgi(app)
    import uvicorn
    uvicorn.run(asgi_app, host="0.0.0.0", port=port)
