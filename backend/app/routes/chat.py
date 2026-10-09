from email.mime import message
import json
from time import sleep
from uuid import uuid4

from flask import Blueprint, Response, jsonify, request
from app.services.chat_service import create_chat_request, build_ui_component

from app.services.request_store import chat_requests

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

@chat_bp.get("chat/stream/<request_id>")
def stream_chat_response(request_id):
    # Find the original chat request using its unique request ID.
    chat_request = chat_requests.get(request_id)

    # Return 404 if the request ID does not exist.
    if not chat_request:
        return jsonify({
            "error": "Chat request not found"
        }), 404
    
    # Read the user's original message from our temporary in-memory store.
    message = chat_request["message"]

    # This generator produces SSE events one at a time.
    def generate():
        try:
            # Create a temporary mock assistant response.
            response_text = (
                f'I received your message: "{message}". '
                "This response is being streamed from the Flask backend."
            )

            # Split the response into words and stream them one by one.
            for word in response_text.split():
                event = {
                    "type": "message.delta",
                    "data":{
                        "text": word + " ",
                    }
                }

                # Convert the Python dictionary to JSON and send one SSE event.
                yield f"data: {json.dumps(event)}\n\n"

                # Slow the stream slightly so we can see it happening.
                sleep(0.2)

            # Ask the service layer whether this message needs a dynamic UI component.
            ui_component = build_ui_component(message)

            # Send the component only when the service generated one.
            if ui_component:
                ui_event = {
                    "type": "ui.component",
                    "data": ui_component,
                }

            # Stream the UI component as another SSE event.
            yield f"data: {json.dumps(ui_event)}\n\n"

            # Tell the client that the stream has finished successfully.
            done_event ={
                "type": "message.done"
            }

            yield f"data: {json.dumps(done_event)}\n\n"

        except Exception:
            # Create a safe error event without exposing internal details.
            error_event = {
                "type": "error",
                "data": {
                    "message": "Streaming interrupted."
                }
            }

            # Send the error event to the connected client.
            yield f"data: {json.dumps(error_event)}\n\n"

        finally:
            # Remove the finished request from temporary memory.
            chat_requests.pop(request_id, None)

    # Keep the HTTP response open and stream events from the generator.
    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )
