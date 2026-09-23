# Architecture & Database Design

## Request flow

```
Browser (HTML form / link)
        |
        v
Flask route (routes/auth.py, transactions.py, dashboard.py)
        |  -- checks session (login_required)
        v
services/  (validation, calculations: totals, category breakdown, monthly summary)
        |
        v
models/  (raw SQL via Python's sqlite3, parameterized queries)
        |
        v
SQLite file (instance/expense_tracker.sqlite)
        |
        v
Route renders a Jinja2 template  -->  Browser
```

## Why server-rendered pages, not a JSON API
The weather dashboard used a fetch-driven frontend calling a JSON API, because it was
consuming a third-party API and wanted a dynamic, no-reload search experience. This app
is a CRUD app built around forms (add/edit/delete a transaction), and the simplest,
most standard way to build that in Flask is server-rendered Jinja2 templates with plain
HTML forms using the POST-redirect-GET pattern — not a hand-built REST layer underneath
JavaScript. JavaScript is only used where it earns its place: rendering the
category-breakdown chart, and small UX niceties like confirm-before-delete.

## Why raw `sqlite3`, not an ORM
This is deliberate, not a shortcut. Writing SQL by hand with `?` placeholders — never
string-formatting user input into a query — is exactly what "SQL injection prevention"
means in practice, and it's a concrete, explainable answer in an interview. An ORM
(like SQLAlchemy) would hide that mechanism behind an abstraction layer. This follows
the same pattern as Flask's own official tutorial: a `schema.sql` file plus a small
`db.py` that manages one connection per request via Flask's `g` object.

## Why folders (`models/`, `routes/`, `services/`) instead of flat files
The weather dashboard had one resource (weather) and no auth, so flat files made sense.
This app has two resources (users, transactions), authentication, and calculated
analytics — enough surface area that a single `routes.py` would get unwieldy.
- `routes/` — HTTP layer only: parse the request, check auth, call a service, render a
  template. No SQL here.
- `services/` — business logic: validation, totals, category/monthly aggregation. No
  SQL here either.
- `models/` — the only layer that touches SQL, via parameterized queries.

## Authentication
On login, `session["user_id"]` is set. Flask signs that cookie using `SECRET_KEY` (from
`.env`), so it can't be forged without the key. A small `login_required` decorator
checks the session and redirects to `/login` if it's missing. Passwords are hashed with
Werkzeug's `generate_password_hash` / `check_password_hash` (PBKDF2) — already a Flask
dependency, so no new library is needed.

## Authorization (user isolation)
Every transaction query filters by `WHERE user_id = ? AND id = ?`, using the *session's*
user id — never a value trusted from the URL alone. Trying to edit or delete someone
else's transaction returns 404, not a permissions error, so a user can't even confirm
that another user's transaction ID exists.

## CSRF protection
A random token (`secrets.token_hex`) is generated per session, embedded as a hidden
field in every form, and checked on POST. This is a few lines of code, so it doesn't
need a dependency like Flask-WTF.

## Database schema

```sql
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE transactions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type        TEXT NOT NULL CHECK (type IN ('income', 'expense')),
    amount      REAL NOT NULL CHECK (amount > 0),
    category    TEXT NOT NULL,
    description TEXT,
    date        TEXT NOT NULL,                              -- the transaction's own date
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))      -- when the row was inserted
);

CREATE INDEX idx_transactions_user_id ON transactions (user_id);
```

Notes:
- **`amount` is always positive; `type` carries the sign.** Balance is
  `SUM(amount WHERE type='income') - SUM(amount WHERE type='expense')` — no sign-flip
  bugs, and `CHECK (amount > 0)` enforces it at the database level too.
- **`date` vs `created_at` are separate on purpose.** `date` is what the user picked
  (when the expense happened); `created_at` is an audit trail (when the row was
  inserted). They usually match but don't have to.
- **Categories are a fixed Python list, not a table.** A `categories` table would be the
  "correct" normalized design if users could create custom categories, but that's out of
  scope for v1 — a constant list is trivial to expand without a migration.
- **`ON DELETE CASCADE`** keeps a user's transactions consistent if the user row is ever
  removed (mainly relevant for tests, since account deletion isn't a v1 feature).
- **The index on `user_id`** matters because nearly every query in this app is scoped to
  one user; without it, every dashboard/filter query would be a full table scan as data
  grows.
