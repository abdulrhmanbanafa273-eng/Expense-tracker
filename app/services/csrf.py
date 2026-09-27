import secrets

from flask import abort, session


def generate_csrf_token():
    """Return this session's CSRF token, creating one if it doesn't exist yet."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_hex(32)
    return session["csrf_token"]


def validate_csrf_token(submitted_token):
    """Abort the request with 400 if the submitted token doesn't match the session's."""
    expected_token = session.get("csrf_token")
    if not expected_token or submitted_token != expected_token:
        abort(400, description="Invalid or missing CSRF token.")
