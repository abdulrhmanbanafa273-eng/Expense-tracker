from datetime import datetime

from app.models.transaction import CATEGORIES

MIN_PASSWORD_LENGTH = 8
VALID_TRANSACTION_TYPES = ("income", "expense")


def validate_registration(username, password, confirm_password):
    """Return a list of human-readable error messages; empty means the input is valid."""
    errors = []

    if not username:
        errors.append("Username is required.")

    if not password:
        errors.append("Password is required.")
    elif len(password) < MIN_PASSWORD_LENGTH:
        errors.append(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")

    if password and password != confirm_password:
        errors.append("Passwords do not match.")

    return errors


def validate_transaction(type_, amount_raw, category, date_str):
    """Return (errors, parsed_amount). parsed_amount is None if it couldn't be parsed."""
    errors = []

    if type_ not in VALID_TRANSACTION_TYPES:
        errors.append("Please choose a valid transaction type.")

    amount = None
    try:
        amount = float(amount_raw)
        if amount <= 0:
            errors.append("Amount must be greater than zero.")
    except (TypeError, ValueError):
        errors.append("Amount must be a valid number.")

    if category not in CATEGORIES:
        errors.append("Please choose a valid category.")

    if not date_str:
        errors.append("Date is required.")
    else:
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            errors.append("Date must be a valid date.")

    return errors, amount
