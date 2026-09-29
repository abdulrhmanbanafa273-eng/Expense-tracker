from tests.helpers import add_transaction


def test_new_user_dashboard_shows_all_zeros(logged_in_client):
    response = logged_in_client.get("/")
    assert b"$0.00" in response.data
    assert b"No transactions this month" in response.data


def test_dashboard_computes_income_expenses_and_balance_correctly(logged_in_client):
    add_transaction(logged_in_client, type="income", category="Salary", amount="1000", date="2026-09-15")
    add_transaction(logged_in_client, type="expense", category="Food", amount="200", date="2026-09-15")

    response = logged_in_client.get("/?year=2026&month=9")
    body = response.data.decode()
    assert "1000.00" in body
    assert "200.00" in body
    assert "800.00" in body  # balance = income - expenses


def test_dashboard_transaction_count_is_correct(logged_in_client):
    add_transaction(logged_in_client, date="2026-09-01")
    add_transaction(logged_in_client, date="2026-09-02")
    add_transaction(logged_in_client, date="2026-09-03")

    response = logged_in_client.get("/?year=2026&month=9")
    assert b">3<" in response.data


def test_dashboard_only_counts_the_selected_month(logged_in_client):
    add_transaction(logged_in_client, type="expense", amount="500", description="August rent", date="2026-08-15")
    add_transaction(logged_in_client, type="expense", amount="10", description="September snack", date="2026-09-01")

    september = logged_in_client.get("/?year=2026&month=9")
    assert b"August rent" not in september.data
    assert b"10.00" in september.data

    august = logged_in_client.get("/?year=2026&month=8")
    assert b"August rent" in august.data
    assert b"-$500.00" in august.data  # august balance: 0 income - 500 expense


def test_category_breakdown_excludes_income(logged_in_client):
    add_transaction(logged_in_client, type="income", category="Salary", amount="3000", date="2026-09-01")
    add_transaction(logged_in_client, type="expense", category="Food", amount="50", date="2026-09-01")

    response = logged_in_client.get("/?year=2026&month=9")
    body = response.data.decode()

    start = body.index("const categoryData = ") + len("const categoryData = ")
    end = body.index(";", start)
    import json

    breakdown = json.loads(body[start:end])

    categories = [row["category"] for row in breakdown]
    assert "Salary" not in categories
    assert "Food" in categories


def test_category_breakdown_sums_multiple_transactions_in_the_same_category(logged_in_client):
    add_transaction(logged_in_client, type="expense", category="Food", amount="30", date="2026-09-01")
    add_transaction(logged_in_client, type="expense", category="Food", amount="20", date="2026-09-10")

    response = logged_in_client.get("/?year=2026&month=9")
    body = response.data.decode()

    start = body.index("const categoryData = ") + len("const categoryData = ")
    end = body.index(";", start)
    import json

    breakdown = json.loads(body[start:end])

    food_total = next(row["total"] for row in breakdown if row["category"] == "Food")
    assert food_total == 50
