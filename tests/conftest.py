import os
import tempfile

import pytest

from app import create_app
from app.db import init_db


@pytest.fixture
def app():
    """A fresh app backed by a temporary, real SQLite file - one per test."""
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.environ.setdefault("SECRET_KEY", "test-secret")

    flask_app = create_app()
    flask_app.config.update(TESTING=True, DATABASE=path)

    with flask_app.app_context():
        init_db()

    yield flask_app

    os.close(fd)
    os.remove(path)


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def logged_in_client(client):
    """A client that's already registered and logged in as a default user."""
    from tests.helpers import register_and_login

    register_and_login(client, "alice")
    return client
