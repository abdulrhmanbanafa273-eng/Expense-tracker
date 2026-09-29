import sqlite3

import click
from flask import current_app, g


def get_db():
    """Open a database connection for this request, reusing it if already open."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")

    return g.db


def close_db(exception=None):
    """Close the request's database connection, if one was opened."""
    db = g.pop("db", None)

    if db is not None:
        db.close()


def init_db():
    """(Re)create all tables from schema.sql. This destroys any existing data."""
    db = get_db()
    with open(current_app.config["SCHEMA_PATH"], "r", encoding="utf-8") as f:
        db.executescript(f.read())


@click.command("init-db")
def init_db_command():
    """CLI command: `flask --app app init-db`. Wipes and recreates all tables."""
    init_db()
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
