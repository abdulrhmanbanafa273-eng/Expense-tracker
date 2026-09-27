from app.db import get_db

CATEGORIES = (
    "Food",
    "Transport",
    "Shopping",
    "Entertainment",
    "Bills",
    "Health",
    "Education",
    "Salary",
    "Other",
)


def create_transaction(user_id, type_, amount, category, description, date):
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO transactions (user_id, type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (user_id, type_, amount, category, description, date),
    )
    db.commit()
    return cursor.lastrowid


def get_transactions_for_user(user_id):
    db = get_db()
    return db.execute(
        "SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC, id DESC",
        (user_id,),
    ).fetchall()


def get_transaction_for_user(transaction_id, user_id):
    """Look up a transaction, scoped to this user. Returns None if it's missing or not theirs."""
    db = get_db()
    return db.execute(
        "SELECT * FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, user_id),
    ).fetchone()


def update_transaction(transaction_id, user_id, type_, amount, category, description, date):
    db = get_db()
    db.execute(
        """
        UPDATE transactions
        SET type = ?, amount = ?, category = ?, description = ?, date = ?
        WHERE id = ? AND user_id = ?
        """,
        (type_, amount, category, description, date, transaction_id, user_id),
    )
    db.commit()


def delete_transaction(transaction_id, user_id):
    db = get_db()
    db.execute(
        "DELETE FROM transactions WHERE id = ? AND user_id = ?",
        (transaction_id, user_id),
    )
    db.commit()
