def get_csrf_token(client, path):
    client.get(path)
    with client.session_transaction() as session:
        return session["csrf_token"]


def register(client, username, password="password123"):
    token = get_csrf_token(client, "/auth/register")
    return client.post(
        "/auth/register",
        data={"csrf_token": token, "username": username, "password": password, "confirm_password": password},
    )


def login(client, username, password="password123"):
    token = get_csrf_token(client, "/auth/login")
    return client.post("/auth/login", data={"csrf_token": token, "username": username, "password": password})


def register_and_login(client, username, password="password123"):
    register(client, username, password)
    login(client, username, password)


def add_transaction(client, **overrides):
    data = {
        "type": "expense",
        "amount": "10",
        "category": "Food",
        "description": "",
        "date": "2026-09-01",
    }
    data.update(overrides)
    token = get_csrf_token(client, "/transactions/add")
    data["csrf_token"] = token
    return client.post("/transactions/add", data=data, follow_redirects=True)
