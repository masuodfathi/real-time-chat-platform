from uuid import uuid4

from app.services.request_store import chat_requests

def create_chat_request(message: str):
    request_id = str(uuid4())

    chat_requests[request_id] = {
        "message": message
    }

    return request_id