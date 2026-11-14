from flask import Blueprint, Response, current_app, jsonify, request

from app.services.chat_service import stream_chat_response
from app.services.conversation_store import (
    ConversationBusy,
    begin_turn,
    end_turn,
)


chat_bp = Blueprint("chat", __name__)


@chat_bp.post("/chat")
def chat():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    message = data.get("message")
    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Message cannot be empty."}), 400

    conversation_id = data.get("conversationId")

    if conversation_id is not None:
        if not isinstance(conversation_id, str) or not conversation_id.strip():
            return jsonify({"error": "Invalid conversation ID."}), 400
        
        conversation_id = conversation_id.strip()

    api_key = current_app.config["GROQ_API_KEY"]
    model = current_app.config["GROQ_MODEL"]

    try:
        conversation_id, history = begin_turn(conversation_id)
    except KeyError:
        return jsonify({"error": "Conversation not found."}), 404
    except ConversationBusy:
        return jsonify({"error": "This conversation is already generating."}), 409

    response = Response(
        stream_chat_response(
            message=message.strip(),
            conversation_id=conversation_id,
            history=history,
            api_key=api_key,
            model=model,
        ),
        mimetype="text/event-stream",
    )

    # Release the conversation when the response is closed.
    response.call_on_close(lambda: end_turn(conversation_id))
    return response