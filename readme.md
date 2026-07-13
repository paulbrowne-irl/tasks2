# Task Management System

A responsive Python web application for managing tasks stored in Google Sheets. The application uses Flask for the web interface and is deployed to Google Cloud Run.

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
- Google Cloud Run for the Flask service
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

For Cloud Run, store `FLASK_SECRET_KEY` and `GOOGLE_CLIENT_SECRET` in Secret Manager and expose them as environment variables. The public Firebase configuration values may be regular environment variables.

## Local development

1. Start the Flask application locally:
   - `python app.py`
2. Open `http://localhost:8080` in a browser.
3. Sign in with Google and grant the application access to the configured spreadsheet.

### First-time run

The application will ensure the configured spreadsheet contains a `Tasks` sheet. If the sheet does not exist, it will be created automatically and the task header row will be written.

The deployed application must use HTTPS and must not store persistent task data outside Google Sheets.

## Deployment

Deploy the Flask application directly to Cloud Run. Firebase remains in use for browser sign-in, but Firebase App Hosting and `firebase deploy` are not used to build or run this Python application.

### Before you begin

1. Complete the [Setup](#setup) section, including the Firebase web app, Google sign-in, OAuth client, Google Sheets API, and Google Drive API.
2. Attach a billing account to the Google Cloud project. Cloud Run requires billing to be enabled, even when usage is within free allowances.
3. Install the [Google Cloud CLI](https://cloud.google.com/sdk/docs/install), then sign in and choose the Firebase project's Google Cloud project:

   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

4. Enable the required services:

   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com secretmanager.googleapis.com sheets.googleapis.com drive.googleapis.com
   ```

### Create secrets and the runtime identity

Use Secret Manager for private values. Do not commit `.env` or paste real secrets into deployment scripts.

```bash
printf '%s' 'YOUR_FLASK_SECRET_KEY' | gcloud secrets create flask-secret-key --data-file=-
printf '%s' 'YOUR_GOOGLE_CLIENT_SECRET' | gcloud secrets create google-oauth-client-secret --data-file=-
gcloud iam service-accounts create task-management-runtime --display-name="Task Management Cloud Run runtime"
gcloud secrets add-iam-policy-binding flask-secret-key --member="serviceAccount:task-management-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
gcloud secrets add-iam-policy-binding google-oauth-client-secret --member="serviceAccount:task-management-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com" --role="roles/secretmanager.secretAccessor"
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID --member="serviceAccount:task-management-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com" --role="roles/firebaseauth.admin"
```

If a secret already exists, add a version instead: `printf '%s' 'VALUE' | gcloud secrets versions add SECRET_NAME --data-file=-`.

The runtime service account uses Application Default Credentials to verify Firebase ID tokens. The `firebaseauth.admin` role is a straightforward first-time setup choice; review and narrow it later if your organisation has a more restrictive Firebase IAM policy.

### First deployment

The repository includes a `Dockerfile` that installs `requirements.txt` and starts the Flask factory with `gunicorn 'app:create_app()'`. This removes the need for `GOOGLE_ENTRYPOINT`, `app.yaml`, or a `Procfile`.

From the repository root, deploy the service. Replace each `YOUR_...` value before running the command.

```bash
gcloud run deploy task-management \
  --source . \
  --region europe-west1 \
  --allow-unauthenticated \
  --service-account "task-management-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
  --set-secrets "FLASK_SECRET_KEY=flask-secret-key:latest,GOOGLE_CLIENT_SECRET=google-oauth-client-secret:latest" \
  --set-env-vars "TASKS_SPREADSHEET_ID=YOUR_SPREADSHEET_ID,TASKS_SHEET_NAME=Tasks,GOOGLE_CLIENT_ID=YOUR_GOOGLE_CLIENT_ID,FIREBASE_PROJECT_ID=YOUR_PROJECT_ID,FIREBASE_API_KEY=YOUR_FIREBASE_API_KEY,FIREBASE_AUTH_DOMAIN=YOUR_PROJECT_ID.firebaseapp.com,FIREBASE_APP_ID=YOUR_FIREBASE_APP_ID"
```

Cloud Run prints the service URL on success. Save it, then verify the health endpoint:

```bash
curl https://YOUR_CLOUD_RUN_HOSTNAME/health
```

The response must be `ok`.

### Finish authentication setup

Cloud Run assigns a stable service URL such as `https://task-management-HASH.europe-west1.run.app`. Use the exact hostname returned by the first deployment.

1. In Firebase Authentication, add the Cloud Run hostname (without `https://` or a path) to **Authorized domains**.
2. In the Google OAuth client's **Authorized redirect URIs**, add:

   ```text
   https://YOUR_CLOUD_RUN_HOSTNAME/auth/google/callback
   ```

3. Set that same complete URL in Cloud Run and deploy a new revision:

   ```bash
   gcloud run services update task-management \
     --region europe-west1 \
     --update-env-vars "GOOGLE_OAUTH_REDIRECT_URI=https://YOUR_CLOUD_RUN_HOSTNAME/auth/google/callback"
   ```

Open the Cloud Run service URL, sign in with Google, grant Sheets access, and add a test task. If authentication reports an unauthorised domain or redirect URI, compare the error with the exact hostname and callback path configured above.

### Later deployments

Run the same `gcloud run deploy task-management --source .` command to build and release a new revision. Cloud Run keeps previous revisions available for rollback in the Google Cloud Console.

`firebase.json` is retained only as an optional Firebase Hosting-to-Cloud-Run rewrite. Do not add an `apphosting` section or run `firebase deploy` to deploy this backend: Firebase App Hosting expects a Node.js framework build and is not the deployment target for this Flask service.

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
