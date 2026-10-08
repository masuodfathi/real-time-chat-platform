import json
from urllib import response
# Import the in-memory request store to verify cleanup.
from app.services.request_store import chat_requests

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

def test_unknown_request_404(client):
    response =client.get(
        "/api/chat/stream/not-real"
    )

    assert response.status_code == 404


def test_chat_stream(client, monkeypatch):
    monkeypatch.setattr(
        "app.routes.chat.sleep",
        lambda _: None,
    )

    create_response = client.post(
        "/api/chat",
        json={
            "message": "Show me an Italian restaurant"
        },
    )

    request_id = create_response.get_json()["request_id"]

    response = client.get(
        f"/api/chat/stream/{request_id}",
    )

    assert response.status_code == 200
    # Verify that the response uses the SSE MIME type.
    assert response.mimetype == "text/event-stream"

    events = parse_sse_events(response)

    event_types = [
        event["type"]
        for event in events
    ]

    assert "message.delta" in event_types
    #assert "ui.component" in event_types
    assert event_types[-1] == "message.done"

    # Find the first UI component event in the stream.
    ui_event = next(
        event
        for event in events
        if event["type"] == "ui.component"
    )

    # Verify that the server generated an information card.
    assert ui_event["data"]["type"] == "info_card"

    # Verify that the information card contains the expected title.
    assert ui_event["data"]["props"]["title"] == "Bella Italia"

    # Verify that the completed request was removed from memory.
    assert request_id not in chat_requests
