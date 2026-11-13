import json
import traceback

from app.services.groq_service import stream_model_response


def create_sse_event(event_type: str, **data):
    event = {
        "type": event_type,
        **data
    }

    return f"data: {json.dumps(
        event,
        ensure_ascii=False
        )}\n\n"


def stream_chat_response(
    message: str,
    api_key: str,
    model: str
):
    try:
        for content in stream_model_response(
            message=message,
            api_key=api_key,
            model=model
        ):
            yield create_sse_event(
                "message.delta",
                text=content
            )

        yield create_sse_event(
            "message.done"
        )

    except Exception as error:
        print("Chat streaming error:", repr(error))
        traceback.print_exc()

        yield create_sse_event(
            "error",
            message="Unable to generate response."
        )