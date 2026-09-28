from calendar import month_name
from datetime import date

from app.models.transaction import (
    get_category_breakdown_for_user,
    get_totals_by_type_for_user,
    get_transactions_for_user,
)

RECENT_TRANSACTIONS_LIMIT = 10


def get_dashboard_summary(user_id, year, month):
    """Totals (income/expenses/balance/count) and recent transactions for one month."""
    rows = get_totals_by_type_for_user(user_id, year, month)

    income = 0.0
    expenses = 0.0
    count = 0
    for row in rows:
        count += row["count"]
        if row["type"] == "income":
            income = row["total"] or 0.0
        elif row["type"] == "expense":
            expenses = row["total"] or 0.0

    summary = {
        "income": income,
        "expenses": expenses,
        "balance": income - expenses,
        "count": count,
    }

    recent_transactions = get_transactions_for_user(user_id, year, month, limit=RECENT_TRANSACTIONS_LIMIT)

    return summary, recent_transactions


def get_category_breakdown(user_id, year, month):
    """Category totals for one month, as plain dicts (chart-ready, JSON-serializable)."""
    rows = get_category_breakdown_for_user(user_id, year, month)
    return [{"category": row["category"], "total": row["total"]} for row in rows]


def get_month_context(year, month):
    """Build the display label and prev/next (year, month) pairs for a given month."""
    if month == 1:
        previous_month = (year - 1, 12)
    else:
        previous_month = (year, month - 1)

    if month == 12:
        next_month = (year + 1, 1)
    else:
        next_month = (year, month + 1)

    today = date.today()

    return {
        "label": f"{month_name[month]} {year}",
        "previous": previous_month,
        "next": next_month,
        "is_current": (year == today.year and month == today.month),
    }
