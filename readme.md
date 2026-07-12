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

## Running the application

1. Install the Python dependencies from `requirements.txt`.
2. Configure Firebase Authentication with Google sign-in enabled.
3. Configure a Google OAuth web client and consent screen with the Sheets scope required by the application.
4. Enable the Google Sheets API and configure the target spreadsheet.
5. Set the required Firebase, Google OAuth, and spreadsheet configuration values from `.env.example`.
6. Start the Flask application using the project’s configured application entry point.
7. Open the application in a browser, sign in with Google, and grant Sheets access.

The deployed application must use HTTPS and must not store persistent task data outside Google Sheets.

## Deployment

Deploy the Flask application to Cloud Run and connect it to Firebase Hosting using the rewrite in `firebase.json`. The deployment configuration must provide:

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
Full setup instructions should be provided in the Readme.md
