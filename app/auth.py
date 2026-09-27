import functools

from flask import g, redirect, url_for


def login_required(view):
    """Redirect to the login page if no user is logged in for this session."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view
