# Task Management System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a responsive Flask task-management web application hosted on Firebase, authenticated with Google, and backed exclusively by Google Sheets.

**Architecture:** Flask serves HTML templates and JSON task actions. Firebase Authentication provides Google identity; the backend verifies Firebase ID tokens. Google OAuth consent separately grants the signed-in user Sheets access, and a Sheets adapter performs all persistent task operations while preserving the configured spreadsheet structure.

**Tech Stack:** Python 3.11+, Flask, Google OAuth/Sheets client libraries, Firebase Admin SDK, HTML/CSS/JavaScript, pytest, Firebase deployment configuration.

---

### Task 1: Project foundation and configuration

**Files:**
- Create: `app.py`
- Create: `config.py`
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `.gitignore`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write the failing configuration tests**

Test that required configuration names are documented, defaults are safe for local execution, and missing production secrets are reported clearly.

- [ ] **Step 2: Run the tests and verify they fail**

Run: `python -m pytest tests/test_config.py -v`

Expected: FAIL because the application configuration modules do not yet exist.

- [ ] **Step 3: Add the Flask foundation and configuration**

Define environment-backed settings for `FLASK_SECRET_KEY`, Firebase service-account configuration, Google OAuth client configuration, `GOOGLE_SHEETS_SCOPES`, `TASKS_SPREADSHEET_ID`, and `TASKS_SHEET_NAME`. Create the Flask app factory and health route without embedding credentials.

- [ ] **Step 4: Run the tests and verify they pass**

Run: `python -m pytest tests/test_config.py -v`

Expected: PASS.

### Task 2: Authentication and Google OAuth

**Files:**
- Create: `auth.py`
- Modify: `app.py`
- Test: `tests/test_auth.py`

- [ ] **Step 1: Write failing authentication tests**

Cover rejected requests without a Firebase token, accepted requests with a verified identity, OAuth consent redirect generation, and callback error handling.

- [ ] **Step 2: Run the tests and verify they fail**

Run: `python -m pytest tests/test_auth.py -v`

Expected: FAIL because authentication helpers and routes do not yet exist.

- [ ] **Step 3: Implement authentication**

Verify Firebase ID tokens with Firebase Admin when configured, provide a safe local-test seam, create Google OAuth authorization URLs with the minimum Sheets scope, exchange callback codes for user credentials, and keep credential material server-side and out of templates.

- [ ] **Step 4: Run the tests and verify they pass**

Run: `python -m pytest tests/test_auth.py -v`

Expected: PASS.

### Task 3: Google Sheets task service

**Files:**
- Create: `sheets_service.py`
- Test: `tests/test_sheets_service.py`

- [ ] **Step 1: Write failing spreadsheet-service tests**

Cover reading the `Tasks` sheet, adding a category/task-name row, sorting by colour, preserving `z done` and `T Date`, and translating Google API failures into application errors.

- [ ] **Step 2: Run the tests and verify they fail**

Run: `python -m pytest tests/test_sheets_service.py -v`

Expected: FAIL because the Sheets service does not yet exist.

- [ ] **Step 3: Implement the Sheets adapter**

Create a dependency-injected service around the Google Sheets API. Read configured ranges, append task rows, update only the required values for task operations, preserve metadata columns, expose colour sorting, and provide task-sheet triage as an explicit service operation.

- [ ] **Step 4: Run the tests and verify they pass**

Run: `python -m pytest tests/test_sheets_service.py -v`

Expected: PASS.

### Task 4: Flask task routes

**Files:**
- Modify: `app.py`
- Create: `templates/index.html`
- Test: `tests/test_routes.py`

- [ ] **Step 1: Write failing route tests**

Cover the authenticated task page, refresh endpoint, add-task validation, sort endpoint, triage endpoint, JSON success responses, and JSON error responses.

- [ ] **Step 2: Run the tests and verify they fail**

Run: `python -m pytest tests/test_routes.py -v`

Expected: FAIL because the task routes and template do not yet exist.

- [ ] **Step 3: Implement the routes**

Add authenticated routes for page rendering and task operations. Validate non-empty category/task name fields, return structured JSON, and map service errors to user-visible retryable errors.

- [ ] **Step 4: Run the tests and verify they pass**

Run: `python -m pytest tests/test_routes.py -v`

Expected: PASS.

### Task 5: Responsive frontend

**Files:**
- Create: `static/styles.css`
- Create: `static/app.js`
- Modify: `templates/index.html`
- Test: `tests/test_frontend.py`

- [ ] **Step 1: Write failing frontend tests**

Verify the page contains labelled task controls, refresh/add/sort/triage actions, status output, responsive viewport metadata, and accessible button/input names.

- [ ] **Step 2: Run the tests and verify they fail**

Run: `python -m pytest tests/test_frontend.py -v`

Expected: FAIL because the responsive template and static assets do not yet exist.

- [ ] **Step 3: Implement the frontend**

Build a responsive layout using semantic HTML, CSS grid/flex layout, labelled inputs, keyboard-usable controls, status messaging, and browser JavaScript that calls the Flask JSON endpoints and refreshes the task display.

- [ ] **Step 4: Run the tests and verify they pass**

Run: `python -m pytest tests/test_frontend.py -v`

Expected: PASS.

### Task 6: Firebase deployment and documentation

**Files:**
- Create: `firebase.json`
- Create: `.firebaserc.example`
- Modify: `readme.md`
- Test: `tests/test_deployment_files.py`

- [ ] **Step 1: Write failing deployment/documentation tests**

Verify Firebase configuration exists, required environment variables are documented, and the README explains local setup, Google OAuth, Sheets configuration, testing, and deployment.

- [ ] **Step 2: Run the tests and verify they fail**

Run: `python -m pytest tests/test_deployment_files.py -v`

Expected: FAIL because deployment configuration and implementation-specific setup documentation do not yet exist.

- [ ] **Step 3: Add deployment configuration and update documentation**

Configure Firebase deployment for the Flask service, document Google Cloud OAuth consent setup, Firebase Authentication, Sheets API access, secret injection, local execution, and test commands. Do not place credentials in source control.

- [ ] **Step 4: Run the tests and verify they pass**

Run: `python -m pytest tests/test_deployment_files.py -v`

Expected: PASS.

### Task 7: Full verification

- [ ] **Step 1: Run the full test suite**

Run: `python -m pytest -q`

Expected: all tests pass.

- [ ] **Step 2: Run syntax and import checks**

Run: `python -m compileall app.py auth.py config.py sheets_service.py`

Expected: exit code 0 with no syntax errors.

- [ ] **Step 3: Run the local Flask smoke test**

Start the app with the documented local command and verify `/health` returns HTTP 200 and the unauthenticated task page/API returns HTTP 401 or redirects to authentication.

### Spec coverage

- Task viewing, refresh, add, colour sorting, and task-sheet triage: Tasks 3–5.
- Spreadsheet structure and Google Sheets-only persistence: Task 3.
- Google-account authentication and OAuth consent: Task 2.
- Flask/Python web application and Firebase deployment: Tasks 1, 4, and 6.
- Responsive and accessible UI: Task 5.
- Error/status handling: Tasks 3–5.
- README and test documentation: Task 6.
