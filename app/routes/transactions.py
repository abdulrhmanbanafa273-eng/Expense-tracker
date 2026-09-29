from datetime import date

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.auth import login_required
from app.models.transaction import (
    CATEGORIES,
    create_transaction,
    delete_transaction,
    get_transaction_for_user,
    search_transactions_for_user,
    update_transaction,
)
from app.services.csrf import validate_csrf_token
from app.services.validators import validate_transaction

transactions = Blueprint("transactions", __name__, url_prefix="/transactions")


@transactions.route("/")
@login_required
def index():
    filters = {
        "type": request.args.get("type", ""),
        "category": request.args.get("category", ""),
        "date_from": request.args.get("date_from", ""),
        "date_to": request.args.get("date_to", ""),
        "q": request.args.get("q", "").strip(),
        "sort": request.args.get("sort", "date"),
        "order": request.args.get("order", "desc"),
    }

    all_transactions = search_transactions_for_user(
        g.user["id"],
        category=filters["category"] or None,
        type_=filters["type"] or None,
        date_from=filters["date_from"] or None,
        date_to=filters["date_to"] or None,
        search=filters["q"] or None,
        sort=filters["sort"],
        order=filters["order"],
    )
    return render_template(
        "transactions/list.html", transactions=all_transactions, categories=CATEGORIES, filters=filters
    )


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
