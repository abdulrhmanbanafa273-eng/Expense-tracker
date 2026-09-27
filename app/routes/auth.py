from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.models.user import UsernameTakenError, create_user, get_user_by_username, verify_password
from app.services.csrf import validate_csrf_token
from app.services.validators import validate_registration

auth = Blueprint("auth", __name__, url_prefix="/auth")


@auth.route("/register", methods=("GET", "POST"))
def register():
    if request.method == "POST":
        validate_csrf_token(request.form.get("csrf_token"))

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        errors = validate_registration(username, password, confirm_password)

        if not errors:
            try:
                create_user(username, password)
            except UsernameTakenError as error:
                errors.append(str(error))

        if errors:
            for error in errors:
                flash(error, "error")
        else:
            flash("Account created. You can now log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "POST":
        validate_csrf_token(request.form.get("csrf_token"))

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = get_user_by_username(username)

        if user is None or not verify_password(user, password):
            flash("Incorrect username or password.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth.route("/logout", methods=("POST",))
def logout():
    validate_csrf_token(request.form.get("csrf_token"))
    session.clear()
    return redirect(url_for("auth.login"))
