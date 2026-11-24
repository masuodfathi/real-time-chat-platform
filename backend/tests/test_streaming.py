import json
from psycopg.errors import NotNullViolation

from app.db import connect_db
from app.services.conversation_repository import create_conversation
from app.services.message_repository import load_conversation_history, save_turn

def parse_sse_events(response):
    body = response.get_data(as_text=True)

    events = []

    for block in body.split("\n\n"):
        if not block.strip():
            continue

        for line in block.splitlines():
            if line.startswith("data: "):
                json_data = line.removeprefix("data: ")

                events.append(
                    json.loads(json_data)
                )

    return events

def test_unknown_conversation_returns_404(client):
    # Send a message with a conversation ID that does not exist.
    response = client.post(
        "/api/chat",
        json={"conversationId": "not-real", "message": "Hello"},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Conversation not found."}


def test_stream_without_ui_component(client, monkeypatch):
    def fake_stream_model_response(*, messages, api_key, model):
        # Return one predictable chunk for a regular chat message.
        yield "Hello from the test"

    monkeypatch.setattr(
        "app.services.chat_service.stream_model_response",
        fake_stream_model_response,
    )

    response = client.post(
        "/api/chat",
        json={"message": "Hello, how are you?"},
        buffered=True,
    )

    assert response.status_code == 200
    assert response.mimetype == "text/event-stream"

    events = parse_sse_events(response)
    event_types = [event["type"] for event in events]

    assert event_types == [
        "conversation.started",
        "message.delta",
        "message.done",
    ]
    assert events[1]["text"] == "Hello from the test"


def test_chat_stream_reports_provider_failure(client, monkeypatch):
    def fake_stream_model_response(*, messages, api_key, model):
        # Send one chunk before simulating a provider failure.
        yield "Partial answer"
        raise RuntimeError("Simulated Groq stream failure")

    # Replace the function used by the chat service for this test.
    monkeypatch.setattr(
        "app.services.chat_service.stream_model_response",
        fake_stream_model_response,
    )

    # Send a request through Flask and read the stream to completion.
    response = client.post(
        "/api/chat",
        json={"message": "Hello"},
        buffered=True,
    )

    assert response.status_code == 200
    assert response.mimetype == "text/event-stream"
    events = parse_sse_events(response)

    # Verify the exact event order and the partial text.
    event_types = [event["type"] for event in events]
    assert event_types == ["conversation.started", "message.delta", "error"]
    assert events[1]["text"] == "Partial answer"


def test_chat_stream_rolls_back_when_saving_answer_fails(client, monkeypatch):
    conversation_id = create_conversation()
    storage_errors = []

    def fake_stream_model_response(*, messages, api_key, model):
        # Produce one complete answer without calling Groq.
        yield "Answer generated successfully"

    def save_with_invalid_answer(conversation_id, user_message, assistant_message):
        # Run the real inserts, but give the second insert a SQL NULL.
        try:
            save_turn(conversation_id, user_message, None)
        except NotNullViolation as error:
            storage_errors.append(error.diag.column_name)
            raise

    monkeypatch.setattr(
        "app.services.chat_service.stream_model_response",
        fake_stream_model_response,
    )
    monkeypatch.setattr(
        "app.services.chat_service.save_turn",
        save_with_invalid_answer,
    )

    try:
        response = client.post(
            "/api/chat",
            json={"conversationId": conversation_id, "message": "Hello"},
            buffered=True,
        )

        assert response.status_code == 200

        events = parse_sse_events(response)

        assert [event["type"] for event in events] == [
            "conversation.started",
            "message.delta",
            "error",
        ]
        assert events[1]["text"] == "Answer generated successfully"
        assert storage_errors == ["content"]
        assert load_conversation_history(conversation_id) == []
    finally:
        # Remove only the conversation created by this test.
        with connect_db() as conn:
            conn.execute(
                "DELETE FROM messages WHERE conversation_id = %s",
                (conversation_id,),
            )
            conn.execute(
                "DELETE FROM conversations WHERE id = %s",
                (conversation_id,),
            )



def test_empty_assistant_response_is_not_saved(monkeypatch):
    from app.services import chat_service

    save_calls = []

    def empty_model_response(*, messages, api_key, model):
        # Return a generator that produces no text chunks.
        yield from ()

    def record_save(*args):
        # Record any unexpected attempt to save the turn.
        save_calls.append(args)

    monkeypatch.setattr(chat_service, "stream_model_response", empty_model_response)
    monkeypatch.setattr(chat_service, "save_turn", record_save)

    stream = chat_service.stream_chat_response(
        message="Hello",
        conversation_id="test-conversation",
        history=[],
        api_key="test-key",
        model="test-model",
    )

    events = [
        json.loads(event.removeprefix("data: "))
        for event in stream
    ]

    assert [event["type"] for event in events] == [
        "conversation.started",
        "error",
    ]
    assert events[-1]["message"] == "Unable to complete the response. Please try again."
    assert save_calls == []