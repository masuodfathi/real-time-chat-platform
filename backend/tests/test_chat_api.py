import json

def test_chat_post_starts_conversation(client, monkeypatch):
    def fake_stream_model_response(*, messages, api_key, model):
        # Return one predictable chunk without contacting Groq.
        yield "Hello from the test"

    monkeypatch.setattr(
        "app.services.chat_service.stream_model_response",
        fake_stream_model_response,
    )

    response = client.post(
        "/api/chat",
        json={"message": "Hello"},
        buffered=True,
    )

    assert response.status_code == 200
    assert response.mimetype == "text/event-stream"

    # Decode only the first event to verify how the chat starts.
    first_line = response.get_data(as_text=True).splitlines()[0]
    assert first_line.startswith("data: ")
    first_event = json.loads(first_line.removeprefix("data: "))

    assert first_event["type"] == "conversation.started"
    assert first_event["conversationId"]

def test_empty_message_returns_400(client):
    response = client.post(
        "/api/chat",
        json={
            "message": ""
        },
    )

    data = response.get_json()

    assert response.status_code == 400
    assert data == {
        "error": "Message cannot be empty."
}

def test_whitespace_message_returns_400(client):
    response = client.post(
        "/api/chat",
        json={
            "message": "     "
        },
    )

    assert response.status_code == 400