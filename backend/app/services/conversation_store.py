from threading import Lock

# Keep each conversation's messages in chronological order.
_conversations: dict[str, list[dict[str, str]]] = {}
_lock = Lock()


def create_conversation(conversation_id: str) -> None:
    with _lock:
        _conversations[conversation_id] = []


def get_history(conversation_id: str) -> list[dict[str, str]] | None:
    with _lock:
        messages = _conversations.get(conversation_id)
        if messages is None:
            return None

        # Return copies so callers cannot change stored messages.
        return [message.copy() for message in messages]


def save_turn(
    conversation_id: str,
    user_message: str,
    assistant_message: str,
) -> None:
    with _lock:
        # Append both messages after the response finishes successfully.
        _conversations[conversation_id].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message},
        ])