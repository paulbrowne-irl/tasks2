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
3. Create a Firebase project at [Firebase console](https://console.firebase.google.com/). Firebase creates or connects a Google Cloud project; use this same Google Cloud project for the remaining Google configuration.
4. In **Firebase Authentication** → **Sign-in method**, enable the **Google** provider. Add your deployed Hosting domain under **Authentication** → **Settings** → **Authorized domains** when deploying.
5. In **Project settings** → **General** → **Your apps**, add a **Web app**. Copy the values from its Firebase SDK configuration. They provide the Firebase values listed below; the web API key identifies the Firebase project and is not a secret.
6. In [Google Cloud Console](https://console.cloud.google.com/), select the Firebase project's Google Cloud project. Enable both **Google Sheets API** and **Google Drive API** in **APIs & Services** → **Library**. (Drive API is useful for spreadsheet access and selection even though task operations use the Sheets API.)
7. In **APIs & Services** → **OAuth consent screen**, configure the app name and support email, select the appropriate audience, and add yourself as a test user while the app is in testing. Add the `.../auth/spreadsheets` scope if Google asks you to select scopes.
8. In **APIs & Services** → **Credentials**, create an **OAuth client ID** of type **Web application**. Add these authorised redirect URIs:
   - `http://localhost:8080/auth/google/callback` for local development.
   - `https://YOUR_DOMAIN/auth/google/callback` for each deployed Firebase Hosting or custom domain.
   Copy the resulting client ID and client secret. Keep the client secret private.
9. Create a Google Spreadsheet for the tasks. Its ID is the portion between `/d/` and `/edit` in its URL, for example `https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/edit`. The signed-in users must have access to this spreadsheet. The application creates the `Tasks` sheet and headers on first use if they are missing.
10. Copy `.env.example` to `.env`, then replace its placeholder values. Do not commit `.env` or send its contents to anyone.

### Configuration reference

| Variable | How to obtain it |
| --- | --- |
| `FLASK_SECRET_KEY` | Generate a new random value locally, for example `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`. Use a different value per environment. |
| `TASKS_SPREADSHEET_ID` | Copy it from the Google Spreadsheet URL as described in step 9. |
| `TASKS_SHEET_NAME` | Use `Tasks`, or the exact name of the worksheet the app should use. |
| `GOOGLE_CLIENT_ID` | Copy **Client ID** from the web OAuth client created in Google Cloud Console. |
| `GOOGLE_CLIENT_SECRET` | Copy **Client secret** from that same OAuth client. Treat it as a secret. |
| `GOOGLE_OAUTH_REDIRECT_URI` | Use one of the exact redirect URIs added to the OAuth client, such as `http://localhost:8080/auth/google/callback` locally. Use the HTTPS deployed URL in production. |
| `FIREBASE_PROJECT_ID` | Firebase Console → Project settings → General → **Project ID**. |
| `FIREBASE_API_KEY` | The `apiKey` field in the Firebase Web app SDK configuration. Restrict it to your app's domains in Google Cloud Console where appropriate. |
| `FIREBASE_AUTH_DOMAIN` | The `authDomain` field in the Firebase Web app SDK configuration, usually `YOUR_PROJECT_ID.firebaseapp.com`. |
| `FIREBASE_APP_ID` | The `appId` field in the Firebase Web app SDK configuration. |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | Optional. Cloud Run normally uses its attached service account through Application Default Credentials, so leave this blank unless your deployment setup explicitly requires a service-account credential. Never commit a service-account JSON key. |

For Cloud Run, store `FLASK_SECRET_KEY`, `GOOGLE_CLIENT_SECRET`, and any optional service-account material in Secret Manager and expose them as environment variables. The public Firebase configuration values may be regular environment variables.

## Local development

1. Start the Flask application locally:
   - `python app.py`
2. Open `http://localhost:8080` in a browser.
3. Sign in with Google and grant the application access to the configured spreadsheet.

### First-time run

The application will ensure the configured spreadsheet contains a `Tasks` sheet. If the sheet does not exist, it will be created automatically and the task header row will be written.

The deployed application must use HTTPS and must not store persistent task data outside Google Sheets.

## Deployment

This project serves the Flask application from Cloud Run and sends requests to it through Firebase Hosting. The checked-in `firebase.json` expects a Cloud Run service named `task-management` in `europe-west1`.

### Before you begin

1. Complete the [Setup](#setup) section, including Firebase Authentication, the OAuth client, and the Google APIs.
2. In Google Cloud Console, attach a billing account to the Firebase project. Cloud Run requires billing to be enabled, even if usage remains within free allowances.
3. Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install) and Firebase CLI. The Firebase CLI requires a supported Node.js installation.

   ```bash
   npm install -g firebase-tools
   gcloud auth login
   firebase login
   ```

4. Set the active project, replacing `YOUR_PROJECT_ID` with the Firebase **Project ID** (not its display name):

   ```bash
   gcloud config set project YOUR_PROJECT_ID
   firebase use --add
   ```

   When `firebase use --add` asks for an alias, use `default`. Alternatively, copy `.firebaserc.example` to `.firebaserc` and replace its placeholder project ID. Do not run `firebase init hosting` in this repository: it can overwrite the existing rewrite configuration in `firebase.json`.

5. Enable the Cloud Run, Cloud Build, Artifact Registry, Secret Manager, Sheets, and Drive APIs:

   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com sheets.googleapis.com drive.googleapis.com
   ```

### Configure the deployed application

1. Add both of these URLs to the authorised redirect URIs of the Google OAuth web client created during setup. Replace `YOUR_PROJECT_ID` with the actual Firebase project ID:

   - `https://YOUR_PROJECT_ID.web.app/auth/google/callback`
   - `https://YOUR_PROJECT_ID.firebaseapp.com/auth/google/callback`

   Set `GOOGLE_OAUTH_REDIRECT_URI` to the `.web.app` URL below. Add a matching URL for a custom domain before switching to it.
2. Store the private values in Secret Manager. Use a password manager or terminal prompt to supply the real values; do not paste secrets into a committed file.

   ```bash
   printf '%s' 'YOUR_FLASK_SECRET_KEY' | gcloud secrets create flask-secret-key --data-file=-
   printf '%s' 'YOUR_GOOGLE_CLIENT_SECRET' | gcloud secrets create google-oauth-client-secret --data-file=-
   ```

   If a secret already exists, add a version instead: `printf '%s' 'VALUE' | gcloud secrets versions add SECRET_NAME --data-file=-`.
3. Create a dedicated runtime service account and grant it access before deploying:

   ```bash
   gcloud iam service-accounts create task-management-runtime --display-name="Task Management Cloud Run runtime"
   gcloud secrets add-iam-policy-binding flask-secret-key --member="serviceAccount:task-management-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
   gcloud secrets add-iam-policy-binding google-oauth-client-secret --member="serviceAccount:task-management-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
   gcloud projects add-iam-policy-binding YOUR_PROJECT_ID --member="serviceAccount:task-management-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com" --role="roles/firebaseauth.admin"
   ```

   The final role lets the application verify Firebase ID tokens. Review and narrow it later if your organisation has a more restrictive Firebase IAM policy.

### Deploy Cloud Run

From the repository root, run the following. It builds from `requirements.txt`, starts this app's Flask factory with Gunicorn, and exposes the service publicly so Firebase Hosting can reach it.

```bash
gcloud run deploy task-management \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --port 8080 \
  --service-account "task-management-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --command gunicorn \
  --args "--bind=0.0.0.0:8080,--workers=1,--factory,app:create_app" \
  --set-secrets "FLASK_SECRET_KEY=flask-secret-key:latest,GOOGLE_CLIENT_SECRET=google-oauth-client-secret:latest" \
  --set-env-vars "TASKS_SPREADSHEET_ID=YOUR_SPREADSHEET_ID,TASKS_SHEET_NAME=Tasks,GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID,GOOGLE_OAUTH_REDIRECT_URI=https://YOUR_PROJECT_ID.web.app/auth/google/callback,FIREBASE_PROJECT_ID=YOUR_PROJECT_ID,FIREBASE_API_KEY=YOUR_FIREBASE_API_KEY,FIREBASE_AUTH_DOMAIN=YOUR_PROJECT_ID.firebaseapp.com,FIREBASE_APP_ID=YOUR_FIREBASE_APP_ID"
```

Replace every `YOUR_...` value before running it. Keep the service name and region exactly as shown unless you also update `firebase.json` to match. Visit the Cloud Run URL printed by the command and confirm that `/health` returns `ok`.

### Deploy Firebase Hosting and verify

1. Deploy only Hosting, which preserves the Cloud Run service and publishes the rewrite:

   ```bash
   firebase deploy --only hosting
   ```

2. Open `https://YOUR_PROJECT_ID.web.app/health`. It should return `ok` through the Hosting rewrite.
3. Open `https://YOUR_PROJECT_ID.web.app/`, sign in with Google, and approve the Sheets permission. Confirm that adding a task updates the configured spreadsheet.
4. If sign-in reports an unauthorised domain or redirect URI, return to Firebase Authentication and the Google OAuth client and add the exact domain/URI shown in the error. Changes may take a few minutes to propagate.

For later releases, redeploy Cloud Run with the same `gcloud run deploy` command and then run `firebase deploy --only hosting`. Because `pinTag` is enabled in `firebase.json`, each Hosting deploy is pinned to the current Cloud Run revision. For GitHub automation, use a service account with the equivalent Cloud Run, Artifact Registry, Secret Manager, and Firebase Hosting permissions; never commit `.env`, `.firebaserc` with credentials, or secret values.

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
