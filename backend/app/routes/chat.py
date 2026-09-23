from flask import Blueprint, jsonify, request
from app.services.chat_service import create_chat_request

chat_bp = Blueprint('chat', __name__)

@chat_bp.get("/health")
def health_check():
    return jsonify({
        "status": "OK",
    })

@chat_bp.post("/chat")
def create_chat():
    data = request.get_json(silent=True) or {}

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "error": "Message is required"
        }),400

    request_id = create_chat_request(message)

    return jsonify({
        "request_id": request_id,
    }), 201
