from datetime import date

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.auth import login_required
from app.models.transaction import (
    CATEGORIES,
    create_transaction,
    delete_transaction,
    get_transaction_for_user,
    get_transactions_for_user,
    update_transaction,
)
from app.services.csrf import validate_csrf_token
from app.services.validators import validate_transaction

transactions = Blueprint("transactions", __name__, url_prefix="/transactions")


@transactions.route("/")
@login_required
def index():
    all_transactions = get_transactions_for_user(g.user["id"])
    return render_template("transactions/list.html", transactions=all_transactions)


@transactions.route("/add", methods=("GET", "POST"))
@login_required
def add():
    if request.method == "POST":
        validate_csrf_token(request.form.get("csrf_token"))
        type_, amount_raw, category, description, date_str = _read_form_fields()
        errors, amount = validate_transaction(type_, amount_raw, category, date_str)

        if errors:
            for error in errors:
                flash(error, "error")
        else:
            create_transaction(g.user["id"], type_, amount, category, description or None, date_str)
            flash("Transaction added.", "success")
            return redirect(url_for("transactions.index"))

    return render_template(
        "transactions/form.html", categories=CATEGORIES, transaction=None, today=date.today().isoformat()
    )


@transactions.route("/<int:transaction_id>/edit", methods=("GET", "POST"))
@login_required
def edit(transaction_id):
    transaction = get_transaction_for_user(transaction_id, g.user["id"])
    if transaction is None:
        abort(404)

    if request.method == "POST":
        validate_csrf_token(request.form.get("csrf_token"))
        type_, amount_raw, category, description, date_str = _read_form_fields()
        errors, amount = validate_transaction(type_, amount_raw, category, date_str)

        if errors:
            for error in errors:
                flash(error, "error")
        else:
            update_transaction(
                transaction_id, g.user["id"], type_, amount, category, description or None, date_str
            )
            flash("Transaction updated.", "success")
            return redirect(url_for("transactions.index"))

    return render_template("transactions/form.html", categories=CATEGORIES, transaction=transaction, today=None)


@transactions.route("/<int:transaction_id>/delete", methods=("POST",))
@login_required
def delete(transaction_id):
    validate_csrf_token(request.form.get("csrf_token"))

    transaction = get_transaction_for_user(transaction_id, g.user["id"])
    if transaction is None:
        abort(404)

    delete_transaction(transaction_id, g.user["id"])
    flash("Transaction deleted.", "success")
    return redirect(url_for("transactions.index"))


def _read_form_fields():
    return (
        request.form.get("type", ""),
        request.form.get("amount", ""),
        request.form.get("category", ""),
        request.form.get("description", "").strip(),
        request.form.get("date", ""),
    )
