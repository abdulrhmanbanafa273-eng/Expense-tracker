import sqlite3

from werkzeug.security import check_password_hash, generate_password_hash

from app.db import get_db


class UsernameTakenError(Exception):
    """Raised when trying to register a username that's already in use."""


def create_user(username, password):
    """Insert a new user with a hashed password. Raises UsernameTakenError on collision."""
    db = get_db()
    password_hash = generate_password_hash(password)

    try:
        cursor = db.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        db.commit()
    except sqlite3.IntegrityError as error:
        raise UsernameTakenError(f'Username "{username}" is already taken.') from error

    return cursor.lastrowid


def get_user_by_username(username):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()


def get_user_by_id(user_id):
    db = get_db()
    return db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def verify_password(user, password):
    return check_password_hash(user["password_hash"], password)
