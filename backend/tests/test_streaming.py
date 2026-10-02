import json
from urllib import response

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
