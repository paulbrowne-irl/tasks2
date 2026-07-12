# Task Management System Design

## Goal

Build a responsive Flask web application hosted on Google Firebase that authenticates users with Google and stores all persistent task data in Google Sheets.

## Architecture

The Flask application serves responsive HTML templates and browser JavaScript. Firebase Authentication establishes the signed-in Google identity. A separate Google OAuth consent flow grants the signed-in user access to the configured spreadsheet; the backend uses the resulting user authorization to read and write task data without a service account or separate database.

The application is divided into a web layer, task service, Google Sheets adapter, OAuth/authentication integration, and templates/static assets. Spreadsheet operations preserve the `Tasks` sheet, `z done` marker, `T Date` field, category/colour/priority values, and supporting hash metadata.

## User flows

1. A user opens the responsive web application.
2. Firebase Authentication signs the user in with Google.
3. If Sheets authorization is missing, the user grants the requested Google Sheets scope.
4. The user refreshes tasks, adds a task, sorts by colour, or runs task-sheet triage.
5. Flask reads or writes the configured Google Sheet using the user's OAuth authorization.
6. The UI displays success or error status without exposing credentials.

## Security and data

- Persistent task data is stored only in Google Sheets.
- No service-account credentials or user passwords are stored.
- Google OAuth tokens are handled through protected server-side session/secret configuration and are never rendered into page content.
- Unauthenticated users cannot access task data or task operations.

## Testing

Tests cover task retrieval, task creation, colour sorting, task-sheet triage, OAuth/authentication boundaries, spreadsheet error handling, and responsive page rendering.
