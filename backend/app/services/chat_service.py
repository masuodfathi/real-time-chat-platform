import json
import traceback

from app.services.conversation_store import save_turn
from app.services.groq_service import stream_model_response


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
        traceback.print_exc()
        yield create_sse_event(
            "error",
            message="Unable to generate response.",
        )