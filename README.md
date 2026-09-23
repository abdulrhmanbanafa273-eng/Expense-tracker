# Expense Tracker

> Status: planning phase. No application code yet — see REQUIREMENTS.md and
> ARCHITECTURE.md for what's being built and why.

## Overview
A full-stack expense tracker: register, log in, record income and expenses, and see a
dashboard with totals, a monthly summary, and a category breakdown. Built as a
portfolio project to demonstrate authentication, database design, CRUD, authorization,
and testing in a real Flask application.

## Features
- [ ] User registration, login, logout (hashed passwords, session-based auth)
- [ ] Add / edit / delete / view transactions
- [ ] Dashboard: totals, balance, transaction count, recent activity
- [ ] Monthly summary and category breakdown with a chart
- [ ] Filtering, search, and sorting on the transactions list
- [ ] Responsive layout (desktop / tablet / mobile)
- [ ] Automated tests for auth, CRUD, and calculations

See [REQUIREMENTS.md](REQUIREMENTS.md) for the full feature list and scope, and
[ARCHITECTURE.md](ARCHITECTURE.md) for the request flow, database schema, and the
reasoning behind the technical decisions.

## Technologies
- **Frontend:** HTML5, CSS3, vanilla JavaScript
- **Backend:** Python, Flask
- **Database:** SQLite, accessed via raw `sqlite3` (parameterized queries, no ORM)
- **Charts:** Chart.js (via CDN), for the category breakdown

## Project Structure
```
expense-tracker/
├── app/
│   ├── __init__.py       # app factory
│   ├── db.py             # sqlite3 connection helpers
│   ├── models/           # data access (raw SQL)
│   ├── routes/           # Flask blueprints (HTTP layer)
│   ├── services/         # validation and calculations
│   ├── templates/
│   └── static/
│       ├── css/
│       └── js/
├── schema.sql
├── instance/              # SQLite database file lives here (git-ignored)
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── REQUIREMENTS.md
├── ARCHITECTURE.md
└── run.py
```

## Installation
Coming once Phase 2 (project scaffolding) lands.

## Environment Variables
Coming once Phase 2 lands. Will follow the same `.env` / `.env.example` pattern as the
weather dashboard project — a `SECRET_KEY` for signing session cookies, never committed.

## Running Locally
Coming once Phase 2 lands.

## Testing
Coming once Phase 10 (automated tests) lands.

## Screenshots
Coming once the UI is built out.

## Future Improvements
TBD.

## What I Learned
TBD — written at the end of the project.

## License
MIT
