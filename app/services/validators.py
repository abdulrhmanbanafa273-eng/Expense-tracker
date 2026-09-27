MIN_PASSWORD_LENGTH = 8


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
