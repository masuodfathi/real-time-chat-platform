from flask import Blueprint, Response, jsonify, request, current_app

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
        stream_chat_response(
            message=message,
            api_key=current_app.config["GROQ_API_KEY"],
            model=current_app.config["GROQ_MODEL"]
        ),
        mimetype="text/event-stream"
    )