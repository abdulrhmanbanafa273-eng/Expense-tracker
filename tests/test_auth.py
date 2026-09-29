from app.db import get_db
from tests.helpers import get_csrf_token, login, register, register_and_login


def test_register_creates_account_and_redirects_to_login(client):
    response = register(client, "alice")
    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/login"


def test_register_rejects_duplicate_username(client, app):
    register(client, "alice")
    response = register(client, "alice", password="differentpass1")

    with app.app_context():
        count = get_db().execute("SELECT COUNT(*) AS n FROM users WHERE username = ?", ("alice",)).fetchone()["n"]

    assert count == 1
    assert b"already taken" in response.data


def test_register_rejects_mismatched_passwords(client):
    token = get_csrf_token(client, "/auth/register")
    response = client.post(
        "/auth/register",
        data={"csrf_token": token, "username": "bob", "password": "password123", "confirm_password": "nope"},
    )
    assert b"do not match" in response.data


def test_register_rejects_short_password(client):
    token = get_csrf_token(client, "/auth/register")
    response = client.post(
        "/auth/register",
        data={"csrf_token": token, "username": "carol", "password": "short", "confirm_password": "short"},
    )
    assert b"at least 8" in response.data


def test_password_is_hashed_not_stored_in_plaintext(client, app):
    register(client, "alice", password="mysecretpassword")

    with app.app_context():
        stored = get_db().execute("SELECT password_hash FROM users WHERE username = ?", ("alice",)).fetchone()

    assert "mysecretpassword" not in stored["password_hash"]
    assert stored["password_hash"].startswith(("pbkdf2:", "scrypt:"))


def test_login_with_correct_credentials_succeeds(client):
    register(client, "alice")
    response = login(client, "alice")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_login_with_wrong_password_fails(client):
    register(client, "alice")
    response = login(client, "alice", password="wrongpassword")
    assert b"Incorrect username or password" in response.data

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_logout_clears_the_session(client):
    register_and_login(client, "alice")

    with client.session_transaction() as session:
        assert "user_id" in session

    token = get_csrf_token(client, "/")
    client.post("/auth/logout", data={"csrf_token": token})

    with client.session_transaction() as session:
        assert "user_id" not in session


def test_unauthenticated_user_is_redirected_to_login(client):
    response = client.get("/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/login"

    response = client.get("/transactions/")
    assert response.status_code == 302
    assert response.headers["Location"] == "/auth/login"


def test_post_without_valid_csrf_token_is_rejected(logged_in_client):
    response = logged_in_client.post(
        "/transactions/add",
        data={
            "csrf_token": "forged-token",
            "type": "expense",
            "amount": "10",
            "category": "Food",
            "description": "",
            "date": "2026-09-01",
        },
    )
    assert response.status_code == 400
