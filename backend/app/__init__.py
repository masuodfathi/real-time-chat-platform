from flask import Flask, jsonify
from flask_cors import CORS
from app.logging_config import configure_logging
from app.routes.chat import chat_bp


def create_app():
    configure_logging()
    
    app = Flask(__name__)

    CORS(app)

    app.register_blueprint(
        chat_bp,
        url_prefix="/api"
    )

    @app.get("/api/health")
    def health_check():
        return jsonify({
            "status": "ok",
            "service": "real-time-chat-api"
        })

    return app