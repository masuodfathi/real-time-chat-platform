from uuid import uuid4

from app.services.request_store import chat_requests

def create_chat_request(message: str):
    request_id = str(uuid4())

    chat_requests[request_id] = {
        "message": message
    }

    return request_id

def build_ui_component(message: str):
    # Normalize the message so keyword checks are case-insensitive.
    lower_message = message.lower()

    # Return an information card when the user asks about a restaurant.
    if "restaurant" in lower_message:
        return {
            "type": "info_card",
            "props": {
                "title": "Bella Italia",
                "description": "Italian restaurant in Vancouver",
                "rating": 4.7,
            },
        }

    # Return no UI component when no rule matches.
    return None