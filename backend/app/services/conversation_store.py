from threading import Lock

from app.services.conversation_repository import (
    conversation_exists,
    create_conversation,
)
from app.services.message_repository import load_conversation_history


_active_conversations: set[str] = set()
_lock = Lock()


class ConversationBusy(Exception):
    pass


def begin_turn(conversation_id: str | None):
    if conversation_id is None:
        conversation_id = create_conversation()
    elif not conversation_exists(conversation_id):
        raise KeyError(conversation_id)

    # Check and reserve the conversation under the same lock.
    with _lock:
        if conversation_id in _active_conversations:
            raise ConversationBusy(conversation_id)

        _active_conversations.add(conversation_id)

    # Release the reservation if loading history fails before streaming starts.
    try:
        history = load_conversation_history(conversation_id)
    except Exception:
        end_turn(conversation_id)
        raise

    return conversation_id, history


def end_turn(conversation_id: str) -> None:
    with _lock:
        _active_conversations.discard(conversation_id)