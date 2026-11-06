from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config

from app.routes.chat import chat_bp

def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app)

    app.register_blueprint(
        chat_bp,
        url_prefix="/api"
    )
    
    return app
