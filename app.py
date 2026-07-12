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
    settings = settings or load_settings()
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.flask_secret_key
    app.config["SETTINGS"] = settings
    app.extensions["auth_manager"] = auth_manager or AuthManager()
    app.extensions["sheets_service"] = sheets_service

    def current_identity() -> Identity:
        authorization = request.headers.get("Authorization")
        return app.extensions["auth_manager"].authenticate_header(authorization)

    def current_sheets_service(identity: Identity) -> SheetsService | Any:
        if app.extensions["sheets_service"] is not None:
            return app.extensions["sheets_service"]
        credentials = app.extensions["auth_manager"].google_credentials_for(identity.uid)
        if credentials is None:
            raise SheetsServiceError("Google Sheets authorization is required")
        return _sheets_service_for_credentials(settings, credentials)

    def protected(handler: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(handler)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
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
        return "ok", 200

    @app.get("/login")
    def login() -> str:
        return render_template(
            "login.html",
            firebase_config={
                "apiKey": getattr(settings, "firebase_api_key", None),
                "authDomain": getattr(settings, "firebase_auth_domain", None),
                "projectId": getattr(settings, "firebase_project_id", None),
                "appId": getattr(settings, "firebase_app_id", None),
            },
        )

    @app.get("/")
    @protected
    def index(identity: Identity) -> str:
        return render_template("index.html", identity=identity)

    @app.get("/api/tasks")
    @protected
    def list_tasks(identity: Identity) -> Any:
        try:
            return jsonify(tasks=current_sheets_service(identity).list_tasks())
        except SheetsServiceError as exc:
            return jsonify(error=str(exc)), 502

    @app.post("/api/tasks")
    @protected
    def add_task(identity: Identity) -> Any:
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
        try:
            current_sheets_service(identity).sort_by_colour()
        except SheetsServiceError as exc:
            return jsonify(error=str(exc)), 502
        return jsonify(message="Tasks sorted by colour")

    @app.post("/api/task-sheets/triage")
    @protected
    def triage_task_sheets(identity: Identity) -> Any:
        try:
            result = current_sheets_service(identity).triage_task_sheets()
        except SheetsServiceError as exc:
            return jsonify(error=str(exc)), 502
        if not isinstance(result, dict):
            result = {"status": "Task sheets reviewed and organised"}
        return jsonify(result)

    @app.get("/auth/google/start")
    def google_start() -> Any:
        uid = session.get("firebase_uid")
        if not uid:
            return jsonify(error="Authenticate with Firebase before granting Sheets access"), 401
        url, state = app.extensions["auth_manager"].google_authorization_url()
        session["google_oauth_state"] = state
        return redirect(url)

    @app.post("/api/auth/session")
    @protected
    def establish_session(identity: Identity) -> Any:
        session["firebase_uid"] = identity.uid
        session["firebase_email"] = identity.email
        return jsonify(message="Identity established", google_authorization=url_for("google_start"))

    @app.get("/auth/google/callback")
    def google_callback() -> Any:
        if request.args.get("error"):
            return jsonify(error="Google authorization was not completed"), 400
        uid = session.get("firebase_uid")
        state = session.get("google_oauth_state")
        if not uid or not state or state != request.args.get("state"):
            return jsonify(error="Invalid Google authorization state"), 400
        try:
            credentials = app.extensions["auth_manager"].exchange_google_code(request.args["code"])
            app.extensions["auth_manager"].save_google_credentials(uid, credentials)
        except Exception:
            return jsonify(error="Google Sheets authorization could not be completed"), 502
        return redirect(url_for("index"))

    return app


def _sheets_service_for_credentials(settings: Settings, credentials: Any) -> SheetsService:
    from googleapiclient.discovery import build

    api = build("sheets", "v4", credentials=credentials, cache_discovery=False)
    return SheetsService(api, settings.spreadsheet_id, settings.sheet_name)


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "8080")))
