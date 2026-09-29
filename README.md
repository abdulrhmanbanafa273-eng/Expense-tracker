# Expense Tracker

A full-stack expense tracker: register, log in, record income and expenses, and see a
dashboard with totals, a monthly summary, and a category breakdown chart. Built as a
portfolio project to practice a real full-stack workflow — authentication, database
design, CRUD, authorization, testing, and a security pass — with a genuine Git history
to match.

## Overview
Register an account, log in, and start recording transactions (income or expenses,
each with a category, optional description, and date). The dashboard shows your
balance, income, expenses, and transaction count for any month, plus a chart of
spending by category and your most recent activity. The full transaction list can be
filtered by type/category/date range, searched by description, and sorted.

## Features
- [x] User registration, login, logout (hashed passwords, session-based auth, CSRF
      protection on every form)
- [x] Add / edit / delete / view transactions, scoped so a user can only ever touch
      their own
- [x] Dashboard: balance, income, expenses, transaction count, recent activity — all
      computed live from the database
- [x] Monthly summary (browse any past month)
- [x] Category breakdown chart (Chart.js)
- [x] Filtering, search, and sorting on the transactions list
- [x] Responsive layout (desktop / tablet / mobile)
- [x] 27 automated tests covering auth, CRUD, calculations, and user isolation

See [REQUIREMENTS.md](REQUIREMENTS.md) for the original planning doc and
[ARCHITECTURE.md](ARCHITECTURE.md) for the request flow, database schema, and the
reasoning behind the technical decisions (why raw SQL instead of an ORM, why
server-rendered pages instead of a JSON API, why folders instead of flat files).

## Technologies
- **Frontend:** HTML5, CSS3, vanilla JavaScript (no framework, no build step)
- **Backend:** Python, Flask
- **Database:** SQLite, accessed via raw `sqlite3` (parameterized queries throughout,
  no ORM)
- **Charts:** Chart.js, loaded via CDN
- **Testing:** pytest, against a real temporary SQLite database per test (no mocking
  of the database layer)

## Architecture
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
Full reasoning in [ARCHITECTURE.md](ARCHITECTURE.md).

## Project Structure
```
expense-tracker/
├── app/
│   ├── __init__.py         # app factory
│   ├── auth.py             # login_required decorator
│   ├── db.py                # sqlite3 connection helpers + `flask init-db`
│   ├── models/               # data access (raw SQL only, one file per resource)
│   ├── routes/                # Flask blueprints - auth, transactions, dashboard
│   ├── services/                # validation, CSRF, dashboard/category calculations
│   ├── templates/
│   └── static/
│       ├── css/
│       └── js/
├── schema.sql
├── instance/                    # SQLite database file lives here (git-ignored)
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── REQUIREMENTS.md
├── ARCHITECTURE.md
└── run.py
```

## Installation
```bash
git clone https://github.com/abdulrhmanbanafa273-eng/Expense-tracker.git
cd Expense-tracker
python -m venv venv
```

Activate the virtual environment:
```bash
venv\Scripts\activate       # Windows
source venv/bin/activate    # macOS / Linux
```

Install dependencies:
```bash
pip install -r requirements.txt          # just to run the app
pip install -r requirements-dev.txt      # to also run the tests (includes the above)
```

## Environment Variables
Copy `.env.example` to `.env` and fill in a real value — `.env` is git-ignored and is
never committed:
```bash
copy .env.example .env      # Windows
cp .env.example .env        # macOS / Linux
```

| Variable | Description |
|---|---|
| `SECRET_KEY` | Signs session cookies. Generate one with `python -c "import secrets; print(secrets.token_hex(32))"`. The app refuses to start without it — there's no insecure default |
| `FLASK_DEBUG` | `True` for local development only. Defaults to `False` if unset |

## Running Locally
Initialize the database (creates `instance/expense_tracker.sqlite` from `schema.sql`):
```bash
flask --app app init-db
```
This is a real migration step, not automatic on startup — the app factory shouldn't
have side effects like writing to disk just from being instantiated. Run it once, or
again any time you want to wipe all data and start fresh.

Then run the app:
```bash
python run.py
```
Open http://127.0.0.1:5000 — it will redirect you to log in.

## Testing
```bash
pytest -v
```
27 tests covering:
- **Auth:** registration (including duplicate-username and mismatched/short-password
  rejection), that passwords are actually hashed in the database, login success and
  failure, logout clearing the session, unauthenticated redirects, and a forged CSRF
  token being rejected with 400
- **Transactions:** add/edit/delete, input validation (negative amount, invalid
  category, missing date), and — the most important one — that a second user cannot
  view, edit, or delete the first user's transactions under any circumstance, including
  with filters and sorting applied
- **Dashboard:** a new user sees an all-zero dashboard, income/expenses/balance compute
  correctly, a transaction in a different month doesn't leak into the current month's
  totals or category breakdown, and the breakdown correctly excludes income

Every test runs against a real (temporary) SQLite database created fresh per test —
nothing here mocks the database layer.

## Security Notes
- Passwords are hashed with Werkzeug's `generate_password_hash` (PBKDF2), never stored
  or logged in plaintext
- Every transaction query is scoped by `WHERE user_id = ?` using the session's user id
  — ownership is enforced in SQL, not just checked in application code afterward
- All SQL uses parameterized queries; the one place a query needs a dynamic column name
  (sort order) validates it against a fixed whitelist first, since SQL placeholders
  can't parameterize identifiers
- CSRF tokens are required on every state-changing form, compared with
  `hmac.compare_digest` (not `==`, which can leak timing information)
- `SECRET_KEY` has no insecure default — the app raises an error on startup if it's
  missing, rather than silently falling back to a guessable value
- Session cookies are `HttpOnly` and `SameSite=Lax`
- `.env` is git-ignored and was never committed (checked across the full git history,
  not just the current working tree)

## Screenshots
Not included in this repo yet. Run the app locally (see above), register an account,
and add a few transactions to see the dashboard, chart, and transaction list.

## Future Improvements
- Geolocation-based "use my location" style conveniences don't apply here, but a
  recurring-transactions feature (e.g. auto-log monthly rent) would be a natural next
  step
- User-defined custom categories (would need a real `categories` table instead of the
  current fixed list)
- CSV export of transactions
- Password reset flow (currently out of scope - no email sending is set up)

## What I Learned
- Structuring a Flask app in layers (`routes/` → `services/` → `models/`) once there's
  enough surface area (auth + two resources + analytics) to justify it, versus the
  flatter structure that made sense for a smaller single-resource project
- Why raw SQL with parameterized queries is a legitimate, teachable choice, not just
  "the thing you do before you learn an ORM" — it makes SQL injection prevention
  concrete instead of hidden behind an abstraction
- Enforcing authorization *in the query itself* (`WHERE id = ? AND user_id = ?`) rather
  than fetching a row and checking ownership afterward — there's no code path where the
  check can accidentally be skipped
- Hand-rolling CSRF protection (a per-session token + `hmac.compare_digest`) to
  understand what a framework like Flask-WTF is actually doing under the hood
- A security review isn't just "did I remember HTTPS" — the two real bugs I found
  (a guessable default `SECRET_KEY`, a non-constant-time CSRF comparison) only showed
  up from deliberately re-reading finished code looking for weaknesses, not from normal
  feature testing
- Verifying a test actually catches the bug it claims to, by temporarily breaking the
  real behavior (via safe in-memory monkeypatching, not editing the security-sensitive
  source itself) and confirming the test would have failed

## License
MIT
