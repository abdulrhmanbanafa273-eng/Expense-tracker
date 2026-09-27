from datetime import date

from flask import Blueprint, g, redirect, render_template, request, url_for

from app.auth import login_required
from app.services.dashboard_service import get_dashboard_summary, get_month_context

dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/")
@login_required
def index():
    today = date.today()
    year = request.args.get("year", type=int, default=today.year)
    month = request.args.get("month", type=int, default=today.month)

    if not (1 <= month <= 12):
        return redirect(url_for("dashboard.index"))

    summary, recent_transactions = get_dashboard_summary(g.user["id"], year, month)
    month_context = get_month_context(year, month)

    return render_template(
        "dashboard/index.html",
        summary=summary,
        recent_transactions=recent_transactions,
        month=month_context,
    )
