from threading import Lock
from uuid import uuid4


_conversations: dict[str, list[dict[str, str]]] = {}
_active_conversations: set[str] = set()
_lock = Lock()


class ConversationBusy(Exception):
    pass


def begin_turn(conversation_id: str | None):
    with _lock:
        if conversation_id is None:
            conversation_id = str(uuid4())
            _conversations[conversation_id] = []

        history = _conversations.get(conversation_id)
        if history is None:
            raise KeyError(conversation_id)

        if conversation_id in _active_conversations:
            raise ConversationBusy(conversation_id)

        # Reserve this conversation and take a snapshot of its history.
        _active_conversations.add(conversation_id)
    return conversation_id, [message.copy() for message in history]


def save_turn(conversation_id: str,user_message: str,assistant_message: str) -> None:
    with _lock:
        # Save the user message and the completed assistant response together.
        _conversations[conversation_id].extend([
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message},
        ])


def end_turn(conversation_id: str) -> None:
    with _lock:
        _active_conversations.discard(conversation_id)
