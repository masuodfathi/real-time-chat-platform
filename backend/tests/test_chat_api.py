def test_create_chat_request(client):
    response = client.post(
        "/api/chat",
        json={
            "message": "Hello"
        },
    )

    data = response.get_json()

    assert response.status_code == 201
    assert "requestId" in data
    assert isinstance(data["requestId"], str)

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