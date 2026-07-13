# Task Management System

A responsive Python Flask application for managing tasks stored in Google Sheets.

## What it does

Users can:

- View and refresh task information from the configured Google Spreadsheet.
- Add tasks using a category and task name.
- Sort tasks by colour.
- Track completed work using the `z done` marker.
- Track the latest task change using the `T Date` field.
- Run task-sheet triage to review and organise task sheets.
- Process configured email messages and archive processed messages where applicable.

## Technology

- Python
- Flask
- Responsive HTML, CSS, and browser JavaScript
- A production WSGI server, such as Gunicorn
- Flask sessions and Google OAuth for authenticated Google Sheets access
- Google Sheets API for all persistent task data

No separate application database is used. Task data and task metadata remain in Google Sheets.

## Spreadsheet structure

The application uses a configured Google Spreadsheet containing a `Tasks` sheet. Task operations must preserve the existing spreadsheet structure, including:

- Category and task-name data
- The `z done` completion marker
- The `T Date` latest-change field
- Colour and priority information
- Supporting task metadata, including hash information where applicable

## Web interface

The Flask web application provides a responsive interface for mobile and desktop browsers. It includes:

- A task list or task-information display
- Controls to add a task
- A control to refresh task information
- A control to sort tasks by colour
- A control to run task-sheet triage
- Status or output messages for completed actions

## Authentication
The application uses Flask sessions to protect task data. Users grant the application access to Google Sheets through OAuth consent; the Sheets authorization is used on behalf of the signed-in user. No user passwords are stored.

Keep OAuth client secrets and the Flask secret key outside source control.

## Setup

1. Create and activate a Python 3.12 virtual environment.
   - Windows: `python -m venv .venv && .venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
2. Install dependencies:
   - `python -m pip install --upgrade pip`
   - `python -m pip install -r requirements.txt`
3. In [Google Cloud Console](https://console.cloud.google.com/), create or select a project and enable the **Google Sheets API** and **Google Drive API** in **APIs & Services** → **Library**.
4. In **APIs & Services** → **OAuth consent screen**, configure the app name and support email, select the appropriate audience, and add yourself as a test user while the app is in testing. Add the `.../auth/spreadsheets` scope if prompted to select scopes.
5. In **APIs & Services** → **Credentials**, create an **OAuth client ID** of type **Web application**. Add these authorised redirect URIs:
   - `http://localhost:8080/auth/google/callback` for local development.
   - `https://YOUR_DOMAIN/auth/google/callback` for each deployed domain.
   Copy the resulting client ID and client secret. Keep the client secret private.
6. Create a Google Spreadsheet for the tasks. Its ID is the portion between `/d/` and `/edit` in its URL, for example `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`. The signed-in users must have access to this spreadsheet. The application creates the `Tasks` sheet and headers on first use if they are missing.
7. Copy `.env.example` to `.env`, then replace its placeholder values. Do not commit `.env` or send its contents to anyone.

### Configuration reference

| Variable | How to obtain it |
| --- | --- |
| `FLASK_SECRET_KEY` | Generate a new random value locally, for example `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`. Use a different value per environment. |
| `TASKS_SPREADSHEET_ID` | Copy it from the Google Spreadsheet URL as described in step 6. |
| `TASKS_SHEET_NAME` | Use `Tasks`, or the exact name of the worksheet the app should use. |
| `GOOGLE_CLIENT_ID` | Copy **Client ID** from the web OAuth client created in Google Cloud Console. |
| `GOOGLE_CLIENT_SECRET` | Copy **Client secret** from that same OAuth client. Treat it as a secret. |
| `GOOGLE_OAUTH_REDIRECT_URI` | Use one of the exact redirect URIs added to the OAuth client, such as `http://localhost:8080/auth/google/callback` locally. Use the HTTPS deployed URL in production. |

Use your deployment platform's secret management facility for `FLASK_SECRET_KEY` and `GOOGLE_CLIENT_SECRET`.

## Local development

With the virtual environment activated and `.env` configured, start the standalone Flask development server:

```bash
python3 app.py
```

On Windows, use `python app.py` instead. Open `http://localhost:8080` in a browser, sign in with Google, and grant the application access to the configured spreadsheet.

To run the test suite:

```bash
python3 -m pytest -q
```

### First-time run

The application will ensure the configured spreadsheet contains a `Tasks` sheet. If the sheet does not exist, it will be created automatically and the task header row will be written.

In production, serve the application over HTTPS and do not store persistent task data outside Google Sheets.

## Deployment

Deploy the application as a standard WSGI service. The included `Dockerfile` runs the Flask application with Gunicorn and can be used by any container-compatible hosting platform.

### Before you begin

1. Complete the [Setup](#setup) section and configure the production OAuth redirect URI.
2. Set `FLASK_SECRET_KEY`, `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_OAUTH_REDIRECT_URI`, `TASKS_SPREADSHEET_ID`, and `TASKS_SHEET_NAME` in the deployment environment.
3. Ensure the deployment domain uses HTTPS and matches the redirect URI registered with Google.

### First deployment

The repository includes a `Dockerfile` that installs `requirements.txt` and starts the Flask factory with `gunicorn 'app:create_app()'`. Build and deploy that image using your chosen container platform. Alternatively, install the requirements in a Python environment and run:

```bash
gunicorn --bind 0.0.0.0:8080 'app:create_app()'
```

Verify the health endpoint after deployment:

```bash
curl https://YOUR_DOMAIN/health
```

The response must be `ok`.

### Finish OAuth setup

In the Google OAuth client's **Authorized redirect URIs**, add:

   ```text
https://YOUR_DOMAIN/auth/google/callback
   ```

Set the same URL as `GOOGLE_OAUTH_REDIRECT_URI` in the deployment environment. Open the application, authorize Sheets access, and add a test task. If authorization reports a redirect error, compare the error with the exact hostname and callback path configured above.

### Later deployments

Build and deploy a new application image or release using the normal workflow of the selected WSGI hosting platform.

## Testing

Tests should cover at least these scenarios:

1. Refresh task information and verify that data is read from the `Tasks` sheet.
2. Add a task with a category and task name and verify that it is appended to the spreadsheet.
3. Sort tasks by colour and verify the resulting organisation.
4. Run task-sheet triage and verify that task sheets are reviewed and organised.
5. Verify that unauthenticated users cannot access task data.

Run the project’s configured Python test command after installing the test dependencies.

## Project structure

The project is organised around these responsibilities:

- Flask routes and application services handle authenticated web requests.
- HTML templates, CSS, and browser JavaScript provide the responsive user interface.
- A spreadsheet service reads and updates task data through the Google Sheets API.
- Flask sessions control access, while Google OAuth grants access to the configured spreadsheet.
- Tests verify task operations, spreadsheet integration, authentication, and responsive UI behavior.
