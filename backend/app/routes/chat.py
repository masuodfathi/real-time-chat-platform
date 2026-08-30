from uuid import uuid4

from flask import Blueprint, jsonify, request

from app.services.request_store import chat_requests


chat_bp = Blueprint("chat", __name__)


@chat_bp.post("/chat")
def create_chat_request():
    data = request.get_json(silent=True) or {}

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "error": "Message cannot be empty."
        }), 400

    request_id = str(uuid4())

    chat_requests[request_id] = {
        "message": message
    }

    return jsonify({
        "requestId": request_id
    }), 201