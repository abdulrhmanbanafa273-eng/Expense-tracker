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


def get_transactions_for_user(user_id, year=None, month=None, limit=None):
    """All of a user's transactions, optionally scoped to one month and/or limited in count."""
    db = get_db()
    query = "SELECT * FROM transactions WHERE user_id = ?"
    params = [user_id]

    if year is not None and month is not None:
        query += " AND strftime('%Y', date) = ? AND strftime('%m', date) = ?"
        params += [f"{year:04d}", f"{month:02d}"]

    query += " ORDER BY date DESC, id DESC"

    if limit is not None:
        query += " LIMIT ?"
        params.append(limit)

    return db.execute(query, params).fetchall()


def get_totals_by_type_for_user(user_id, year=None, month=None):
    """Raw SUM(amount)/COUNT(*) per transaction type, optionally scoped to one month."""
    db = get_db()
    query = "SELECT type, SUM(amount) AS total, COUNT(*) AS count FROM transactions WHERE user_id = ?"
    params = [user_id]

    if year is not None and month is not None:
        query += " AND strftime('%Y', date) = ? AND strftime('%m', date) = ?"
        params += [f"{year:04d}", f"{month:02d}"]

    query += " GROUP BY type"
    return db.execute(query, params).fetchall()


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
