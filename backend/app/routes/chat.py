from flask import Blueprint, Response, jsonify, request

from app.services.chat_service import stream_chat_response


chat_bp = Blueprint("chat", __name__)


@chat_bp.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "error": "Message cannot be empty."
        }), 400

    return Response(
        stream_chat_response(message),
        mimetype="text/event-stream"
    )