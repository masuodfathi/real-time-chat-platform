import json

def parse_sse_events(response):
    body = response.get_data(as_text=True)

    events = []

    for block in body.split("\n\n"):
        if not block.strip():
            continue

        for line in block.splitlines():
            if line.startswith("data: "):
                json_data = line.remove_prefix("data: ")

                events.append(
                    json.loads(json_data)
                )

    return events

def test_unknown_request_404(client):
    response =client.get(
        "/api/chat/stream/not-real"
    )

    assert response.status_code == 404
