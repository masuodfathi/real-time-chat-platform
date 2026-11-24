import json
import logging

from app.services.groq_service import stream_model_response
from app.services.message_repository import save_turn

# Use a logger named after this module.
logger = logging.getLogger(__name__)

def create_sse_event(event_type: str, **data):
    event = {"type": event_type, **data}
    return f"data: {json.dumps(event, ensure_ascii=False)}\n\n"


def stream_chat_response(message: str, conversation_id: str, history: list[dict[str, str]], api_key: str, model: str):
    
    messages = [*history, {"role": "user", "content": message}]
    
    assistant_chunks = []

    try:
        yield create_sse_event("conversation.started", conversationId=conversation_id)
    
        restaurant = None

        if message.strip().casefold() == "show me an italian restaurant":
            # Build the demo text and card from the same data.
            restaurant = {
                "name": "Demo Trattoria",
                "cuisine": "Italian",
                "description": "Sample restaurant card for the UI demo.",
            }
            assistant_message = (
                f"Here is a sample {restaurant['cuisine']} restaurant: "
                f"{restaurant['name']}."
            )
            yield create_sse_event("message.delta", text=assistant_message)
        else:
            # Stream regular chat responses from Groq.
            for content in stream_model_response(
                messages=messages,
                api_key=api_key,
                model=model,
            ):
                assistant_chunks.append(content)
                yield create_sse_event("message.delta", text=content)

            assistant_message = "".join(assistant_chunks)


        # Reject an empty answer before starting the write transaction.
        if not isinstance(assistant_message, str) or not assistant_message.strip():
            raise ValueError("The assistant response contained no text.")

        # Store the same text that was sent to the client.
        save_turn(conversation_id, message, assistant_message)


        if restaurant is not None:
            yield create_sse_event(
                "ui.component",
                component="restaurant_card",
                props=restaurant,
            )

        yield create_sse_event("message.done")

    except Exception:
        # Record the failure with the conversation ID and traceback.
        logger.exception(
            "Chat streaming failed for conversation_id=%s",
            conversation_id,
        )
        yield create_sse_event(
            "error",
            message="Unable to complete the response. Please try again.",
        )