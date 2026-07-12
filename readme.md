# Task Management System

A responsive Python web application for managing tasks stored in Google Sheets. The application uses Flask for the web interface and is hosted on Google Firebase.

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
- Google Firebase Hosting fronting the Flask service on Cloud Run
- Firebase Authentication with Google-account sign-in
- Google OAuth consent for per-user Google Sheets access
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
Users must sign in with their Google account through Firebase Authentication before accessing task data. They must also grant the application Google Sheets access through OAuth consent. The Sheets authorization is used on behalf of the signed-in user; no service-account credentials or user passwords are stored.

No security credentiatals (other than tokens to confirm successful login) should be stored

## Setup

1. Create and activate a Python 3.12 virtual environment.
   - Windows: `python -m venv .venv && .venv\Scripts\activate`
   - macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`
2. Install dependencies:
   - `python -m pip install --upgrade pip`
   - `python -m pip install -r requirements.txt`
3. Copy `.env.example` to `.env`.
4. Populate `.env` with the required configuration values, including:
   - `FLASK_SECRET_KEY`
   - `TASKS_SPREADSHEET_ID`
   - `TASKS_SHEET_NAME`
   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`
   - `GOOGLE_OAUTH_REDIRECT_URI`
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_API_KEY`
   - `FIREBASE_AUTH_DOMAIN`
   - `FIREBASE_APP_ID`
   - `FIREBASE_SERVICE_ACCOUNT_JSON` (optional)
5. Enable Firebase Authentication Google sign-in and configure the Google OAuth consent screen.
6. Enable the Google Sheets API for the account used by the application.

## Local development

1. Start the Flask application locally:
   - `python app.py`
2. Open `http://localhost:8080` in a browser.
3. Sign in with Google and grant the application access to the configured spreadsheet.

### First-time run

The application will ensure the configured spreadsheet contains a `Tasks` sheet. If the sheet does not exist, it will be created automatically and the task header row will be written.

The deployed application must use HTTPS and must not store persistent task data outside Google Sheets.

## Deployment

Deploy the Flask application to Cloud Run and connect it to Firebase Hosting using the rewrite in `firebase.json`. For GitHub-based deployment, use Firebase Hosting GitHub integration or a GitHub Actions workflow that runs `firebase deploy` after building the service.

The deployment configuration must provide:

- Flask application hosting through Cloud Run
- Firebase Authentication
- Google Sheets API access
- Secure configuration for OAuth client values, Firebase verification, and Flask session secrets
- A responsive browser-accessible web URL

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
- Authentication controls access through Firebase Authentication and Google sign-in.
- Tests verify task operations, spreadsheet integration, authentication, and responsive UI behavior.

## setup instructions
1. Install the Firebase CLI: `npm install -g firebase-tools`
2. Sign in to Firebase: `firebase login`
3. Initialize Firebase Hosting in this project: `firebase init hosting`
   - Choose an existing Firebase project or create a new one.
   - Select the default `public` directory or keep the configured `public` path.
   - Configure rewrites to route all traffic to the Cloud Run service.
4. Verify the `firebase.json` rewrite section points to the Cloud Run service.
5. Deploy the project: `firebase deploy`
6. Open the deployed Firebase Hosting URL in a browser.
7. Sign in with Google and grant the app access to the configured Google Sheets spreadsheet.
