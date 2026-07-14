# Agent Instructions for tasks2

## Project Overview

**Purpose:** Python Flask task management app using Google Sheets as the persistent data store, with Google OAuth 2.0 authentication.

**Setup Reference:** See [readme.md](readme.md) for detailed setup, including local development, OAuth configuration, and `.env` requirements.

---

## Quick Start Commands

```bash
# Local development
python3 app.py                 # Start Flask dev server on http://localhost:8080

# Testing
python3 -m pytest -q           # Run test suite

# Docker
docker build . && docker run -p 8080:8080  # Build and run containerized app
```

**Required before running:** `.env` file with `FLASK_SECRET_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `TASKS_SPREADSHEET_ID`. See [Configuration Reference](readme.md#configuration-reference).

---

## Architecture & Key Modules

| File | Purpose | Key Exports |
|------|---------|-------------|
| [app.py](app.py) | Flask app factory, HTTP routes (`/api/tasks`, `/api/tasks/sort`, etc.) | `create_app()` |
| [auth.py](auth.py) | Google OAuth flow, session identity, `@protected` route decorator | `AuthManager`, `protected()` |
| [config.py](config.py) | Environment-based `Settings` dataclass (immutable) | `Settings`, `get_settings()` |
| [sheets_service.py](sheets_service.py) | Google Sheets CRUD wrapper (list, add, sort, triage) | `SheetsService` |
| [tests/](tests/) | Unit tests with mocked services; use `authenticated_client()` fixture | — |

**Frontend:** [templates/index.html](templates/index.html) + [static/app.js](static/app.js) (vanilla JS, no frameworks).

---

## Code Patterns & Conventions

- **Type hints** required throughout (Python 3.12+)
- **Dependency injection:** Route handlers receive `auth_manager`, `sheets_service`, `settings` as parameters for testability
- **Protected routes:** Use `@protected` decorator to require authentication
- **Custom exceptions:** `AuthenticationError`, `SheetsServiceError` for domain-specific errors
- **Immutable settings:** `Settings` dataclass loaded once from environment at app start
- **Frontend security:** HTML output escaped via `escapeHtml()` before DOM insertion
- **Spreadsheet columns:** `Category`, `Task`, `Colour`, `T Date`, `Hash` (must be preserved in any sheet operations)

---

## Common Tasks

### Adding a New Route

1. Check if authentication is required → use `@protected` decorator
2. Inject dependencies: `auth_manager`, `sheets_service`, `settings`
3. Add tests in `tests/test_routes.py` with mocked services
4. Example: See `POST /api/tasks` in [app.py](app.py)

### Modifying Spreadsheet Handling

1. Update `SheetsService` methods in [sheets_service.py](sheets_service.py)
2. Preserve column structure: `Category`, `Task`, `Colour`, `T Date`, `Hash`
3. Add tests in `tests/test_sheets_service.py` with mocked Sheets API
4. Document expected spreadsheet format in code comments

### Testing

- **Unit tests:** Mock `AuthManager` and `SheetsService` (see `conftest.py` fixtures)
- **Integration:** Use `authenticated_client()` fixture to simulate logged-in user
- **Run tests:** `python3 -m pytest -q` (or specific file: `pytest tests/test_routes.py`)

---

## Known Gotchas & Development Notes

- **OAuth redirect URI:** Must exactly match deployed domain (e.g., `http://localhost:8080/auth/google/callback` for local, HTTPS for production)
- **In-memory credentials:** User credentials stored in `AuthManager._credentials` dict, lost on app restart (appropriate for single-server deployments)
- **Flask secret key differs per environment:** Use unique keys for dev/staging/production; store secrets via deployment platform's secret manager
- **Spreadsheet accessibility:** Users must have access to the configured spreadsheet or operations will fail
- **Auto-creation:** App auto-creates `Tasks` sheet and headers on first access if missing
- **No separate database:** All persistent data lives in Google Sheets (no migrations, no ORM)

---

## Testing Strategy

- **Mocking:** Mock Google Sheets API calls and OAuth flows to keep tests fast and deterministic
- **Fixtures:** `authenticated_client()` provides Flask test client with valid session
- **Coverage:** Run `pytest` to check test coverage; aim for 80%+ on modified files

See [tests/](tests/) for examples.

---

## Deployment

- **Docker image:** `Dockerfile` uses Python 3.12, installs deps, runs Gunicorn with 1 worker and 8 threads
- **Environment variables:** Set `FLASK_SECRET_KEY`, `GOOGLE_CLIENT_SECRET`, and other secrets via deployment platform's secret manager (not in Docker image)
- **Port:** App listens on `8080` (configurable, see [app.py](app.py))

---

## Related Documentation

- [Spreadsheet Structure](readme.md#spreadsheet-structure) — Required columns and data layout
- [Authentication](readme.md#authentication) — OAuth flow and session handling
- [Setup Guide](readme.md#setup) — Detailed GCP, OAuth, and local environment configuration
- [TODO](todo.md) — Pending work and known issues
