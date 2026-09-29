from app.db import get_db
from tests.helpers import add_transaction, get_csrf_token, register_and_login


def get_transaction_id(app, description):
    with app.app_context():
        row = get_db().execute("SELECT id FROM transactions WHERE description = ?", (description,)).fetchone()
        return row["id"]


def test_add_transaction_creates_it(logged_in_client):
    response = add_transaction(logged_in_client, description="Lunch", amount="25")
    assert b"Transaction added" in response.data
    assert b"Lunch" in response.data


def test_add_transaction_rejects_negative_amount(logged_in_client):
    response = add_transaction(logged_in_client, amount="-5")
    assert b"greater than zero" in response.data


def test_add_transaction_rejects_invalid_category(logged_in_client):
    response = add_transaction(logged_in_client, category="NotARealCategory")
    assert b"valid category" in response.data


def test_add_transaction_rejects_missing_date(logged_in_client):
    response = add_transaction(logged_in_client, date="")
    assert b"Date is required" in response.data


def test_edit_transaction_updates_it(logged_in_client, app):
    add_transaction(logged_in_client, description="Groceries", amount="40")
    transaction_id = get_transaction_id(app, "Groceries")

    token = get_csrf_token(logged_in_client, f"/transactions/{transaction_id}/edit")
    response = logged_in_client.post(
        f"/transactions/{transaction_id}/edit",
        data={
            "csrf_token": token,
            "type": "expense",
            "amount": "55",
            "category": "Food",
            "description": "Groceries",
            "date": "2026-09-01",
        },
        follow_redirects=True,
    )
    assert b"Transaction updated" in response.data
    assert b"55.00" in response.data


def test_delete_transaction_removes_it(logged_in_client, app):
    add_transaction(logged_in_client, description="Coffee", amount="5")
    transaction_id = get_transaction_id(app, "Coffee")

    token = get_csrf_token(logged_in_client, "/transactions/")
    response = logged_in_client.post(
        f"/transactions/{transaction_id}/delete", data={"csrf_token": token}, follow_redirects=True
    )
    assert b"Transaction deleted" in response.data
    assert b"Coffee" not in response.data


def test_user_cannot_view_edit_or_delete_another_users_transaction(client, app):
    register_and_login(client, "alice")
    add_transaction(client, description="Alices secret expense", amount="99")
    transaction_id = get_transaction_id(app, "Alices secret expense")

    bob_client = app.test_client()
    register_and_login(bob_client, "bob")

    edit_response = bob_client.get(f"/transactions/{transaction_id}/edit")
    assert edit_response.status_code == 404

    token = get_csrf_token(bob_client, "/transactions/")
    delete_response = bob_client.post(f"/transactions/{transaction_id}/delete", data={"csrf_token": token})
    assert delete_response.status_code == 404

    still_there = client.get("/transactions/")
    assert b"Alices secret expense" in still_there.data


def test_users_transaction_list_only_shows_their_own_transactions(app):
    alice_client = app.test_client()
    bob_client = app.test_client()
    register_and_login(alice_client, "alice")
    register_and_login(bob_client, "bob")

    add_transaction(alice_client, description="Alices item", amount="20")
    add_transaction(bob_client, description="Bobs item", amount="30")

    alice_list = alice_client.get("/transactions/")
    bob_list = bob_client.get("/transactions/")

    assert b"Alices item" in alice_list.data
    assert b"Bobs item" not in alice_list.data
    assert b"Bobs item" in bob_list.data
    assert b"Alices item" not in bob_list.data


def test_filter_by_type_excludes_other_types(logged_in_client):
    add_transaction(logged_in_client, type="expense", category="Food", description="Snack", amount="5")
    add_transaction(logged_in_client, type="income", category="Salary", description="Paycheck", amount="2000")

    response = logged_in_client.get("/transactions/?type=expense")
    assert b"Snack" in response.data
    assert b"Paycheck" not in response.data


def test_search_by_description_is_case_insensitive_substring_match(logged_in_client):
    add_transaction(logged_in_client, description="Morning Coffee", amount="4")
    add_transaction(logged_in_client, description="Bus ticket", amount="3")

    response = logged_in_client.get("/transactions/?q=coffee")
    assert b"Morning Coffee" in response.data
    assert b"Bus ticket" not in response.data


def test_sort_by_amount_ascending_orders_results_correctly(logged_in_client):
    add_transaction(logged_in_client, description="Big", amount="90")
    add_transaction(logged_in_client, description="Small", amount="5")

    response = logged_in_client.get("/transactions/?sort=amount&order=asc")
    body = response.data.decode()
    assert body.find("Small") < body.find("Big")
