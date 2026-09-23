# Project Requirements & Feature List

## Goal
A full-stack Expense Tracker where a user registers, logs in, and records income and
expense transactions. A dashboard shows totals and recent activity, and a monthly/
category analytics view shows where the money is going. Built to demonstrate a real
full-stack workflow (auth, database design, CRUD, authorization, testing) for a
portfolio.

## Functional requirements

### Authentication
- Register with a username and password
- Log in / log out
- Passwords are hashed, never stored or logged in plaintext
- Session-based auth (no third-party login, no email verification)

### Transactions
- Add income or expense
- Edit an existing transaction
- Delete a transaction (with confirmation)
- View a list of transactions
- Fields: type (income/expense), amount, category, optional description, date
- Categories (v1, expandable later): Food, Transport, Shopping, Entertainment, Bills,
  Health, Education, Salary, Other
- A user can only ever view, edit, or delete their own transactions

### Dashboard
- Total income, total expenses, current balance, transaction count
- Recent transactions list
- All figures computed live from the database — never hardcoded

### Analytics (Week 2)
- Monthly summary: view income/expenses/balance for the current month or a past month
- Category breakdown, shown with a chart
- Filter transactions by category, type (income/expense), and date range
- Search transactions by description
- Sort by date, amount, or category

### Validation
- Amount must be greater than zero
- Required fields cannot be empty
- Dates must be valid
- Category must be one of the known values
- Invalid or missing transaction IDs are handled safely (404, not a crash)

## Non-functional requirements
- Python + Flask backend, SQLite database, vanilla HTML/CSS/JS frontend
- No ORM — raw `sqlite3` with parameterized queries (see ARCHITECTURE.md for why)
- No frontend framework, no build step
- Automated tests for auth, transaction CRUD, and financial calculations
- Secrets (session secret key) via environment variables, never committed

## Out of scope (for this project)
- Multi-currency support
- Password-reset via email
- OAuth / third-party login
- Shared or multi-user budgets
- Recurring/automated transactions
- Receipt or file uploads

## Roadmap

| Week | Phase | Focus |
|---|---|---|
| 1 | 1 | Planning (this document + ARCHITECTURE.md) and initial Git setup |
| 1 | 2 | Project scaffolding: folder structure, Flask app factory, schema, app boots |
| 1 | 3 | Authentication: register/login/logout, hashing, sessions, CSRF |
| 1 | 4 | Transactions CRUD with validation and ownership checks |
| 1 | 5 | Dashboard: totals, count, recent transactions from the DB |
| 2 | 6 | Monthly summary |
| 2 | 7 | Category breakdown + chart |
| 2 | 8 | Filtering, search, sorting |
| 2 | 9 | Responsive UI pass, empty/loading states, confirm-delete UX |
| 3 | 10 | Automated tests (auth, CRUD, calculations, user isolation) |
| 3 | 11 | Security + refactor pass |
| 3 | 12 | Final README, screenshots note, release tag |
