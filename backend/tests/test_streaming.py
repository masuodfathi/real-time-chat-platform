import json

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