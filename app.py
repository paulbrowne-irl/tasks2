"""Flask application routes and Google Sheets integration points."""

from __future__ import annotations

import os
from functools import wraps
from typing import Any, Callable

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from auth import AuthManager, AuthenticationError, Identity
from config import Settings, load_settings
from sheets_service import SheetsService, SheetsServiceError


def create_app(
    settings: Settings | Any | None = None,
    auth_manager: AuthManager | None = None,
    sheets_service: SheetsService | Any | None = None,
) -> Flask:
    # Build the Flask application, register dependencies, and expose all web routes.
    settings = settings or load_settings()
    app = Flask(__name__)
   
    app.config["SETTINGS"] = settings
    app.extensions["auth_manager"] = auth_manager or AuthManager()
    app.extensions["sheets_service"] = sheets_service

    def current_identity() -> Identity:
        # Read the established identity from the signed Flask session.
        uid = session.get("user_uid")
        if not uid:
            raise AuthenticationError("Authentication required")
        return Identity(uid=uid, email=session.get("user_email"))

    def current_sheets_service(identity: Identity) -> SheetsService | Any:
        # Select an injected test service or construct a user-authorized Sheets service.
        if app.extensions["sheets_service"] is not None:
            return app.extensions["sheets_service"]
        credentials = app.extensions["auth_manager"].google_credentials_for(identity.uid)
        if credentials is None:
            raise SheetsServiceError("Google Sheets authorization is required")
        return _sheets_service_for_credentials(settings, credentials)

    def protected(handler: Callable[..., Any]) -> Callable[..., Any]:
        # Wrap routes so unauthenticated API requests are rejected consistently.
        @wraps(handler)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            # Authenticate the request before invoking the protected route handler.
            try:
                identity = current_identity()
            except AuthenticationError:
                if request.path == "/" and "text/html" in request.accept_mimetypes:
                    return redirect(url_for("login"))
                return jsonify(error="Authentication required"), 401
            return handler(identity, *args, **kwargs)

        return wrapped

    @app.get("/health")
    def health() -> tuple[str, int]:
        # Return a lightweight health response for deployment probes.
        return "ok", 200

    @app.get("/login")
    def login() -> str:
        # Render the page that begins the server-side Google OAuth flow.
        return render_template("login.html")

    @app.get("/")
    @protected
    def index(identity: Identity) -> str:
        # Render the authenticated task-management interface.
        return render_template("index.html", identity=identity)

    @app.get("/api/tasks")
    @protected
    def list_tasks(identity: Identity) -> Any:
        # Return the current task rows from Google Sheets.
        try:
            return jsonify(tasks=current_sheets_service(identity).list_tasks())
        except SheetsServiceError as exc:
            return jsonify(error=str(exc)), 502

    @app.post("/api/tasks")
    @protected
    def add_task(identity: Identity) -> Any:
        # Validate and append a new category/task pair to the spreadsheet.
        payload = request.get_json(silent=True) or {}
        category = str(payload.get("category", ""))
        task_name = str(payload.get("task_name", ""))
        if not category.strip() or not task_name.strip():
            return jsonify(error="Category and task name are required"), 400
        try:
            current_sheets_service(identity).add_task(category, task_name)
        except SheetsServiceError as exc:
            return jsonify(error=str(exc)), 502
        return jsonify(message="Task added"), 201

    @app.post("/api/tasks/sort")
    @protected
    def sort_tasks(identity: Identity) -> Any:
        # Ask the spreadsheet service to sort tasks by colour.
        try:
            current_sheets_service(identity).sort_by_colour()
        except SheetsServiceError as exc:
            return jsonify(error=str(exc)), 502
        return jsonify(message="Tasks sorted by colour")

    @app.post("/api/task-sheets/triage")
    @protected
    def triage_task_sheets(identity: Identity) -> Any:
        # Run the task-sheet organisation operation and return its status.
        try:
            result = current_sheets_service(identity).triage_task_sheets()
        except SheetsServiceError as exc:
            return jsonify(error=str(exc)), 502
        if not isinstance(result, dict):
            result = {"status": "Task sheets reviewed and organised"}
        return jsonify(result)

    @app.get("/auth/google/start")
    def google_start() -> Any:
        # Start Google OAuth to establish identity and authorize Sheets access.
        url, state = app.extensions["auth_manager"].google_authorization_url()
        session["google_oauth_state"] = state
        return redirect(url)

    @app.get("/auth/google/callback")
    def google_callback() -> Any:
        # Validate the OAuth callback, establish a Flask session, and store credentials.
        if request.args.get("error"):
            return jsonify(error="Google authorization was not completed"), 400
        state = session.get("google_oauth_state")
        if not state or state != request.args.get("state"):
            return jsonify(error="Invalid Google authorization state"), 400
        try:
            credentials = app.extensions["auth_manager"].exchange_google_code(request.args["code"])
            identity = app.extensions["auth_manager"].identity_for_credentials(credentials)
            app.extensions["auth_manager"].save_google_credentials(identity.uid, credentials)
        except (AuthenticationError, KeyError, ValueError):
            return jsonify(error="Google Sheets authorization could not be completed"), 502
        session["user_uid"] = identity.uid
        session["user_email"] = identity.email
        session.pop("google_oauth_state", None)
        return redirect(url_for("index"))

    return app


def _sheets_service_for_credentials(settings: Settings, credentials: Any) -> SheetsService:
    # Build the Google Sheets API client using the authenticated user's credentials.
    from googleapiclient.discovery import build

    api = build("sheets", "v4", credentials=credentials, cache_discovery=False)
    return SheetsService(api, settings.spreadsheet_id, settings.sheet_name)


if __name__ == "__main__":
    # Run the Flask development server when this module is executed directly.
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
