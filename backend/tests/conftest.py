import pytest

from app import create_app
from app.services.request_store import chat_requests

@pytest.fixture
def app():
    flask_app = create_app()

    flask_app.config.update