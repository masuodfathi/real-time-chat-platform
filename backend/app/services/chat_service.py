import json

def create_sse_event(event_type: str, **data):
    event = {
        "type": event_type,
        **data
    }

    return f"data: {json.dumps(event)}\n\n"


def stream_chat_response(message: str):
    try:
        yield create_sse_event(
            "message.delta",
            text="You said: "
        )

        yield create_sse_event(
            "message.delta",
            text=message
        )
    
        yield create_sse_event(
            "message.done"
        )

    except Exception:
        yield create_sse_event(
            "error",
            message="Unable to generate response."
        )