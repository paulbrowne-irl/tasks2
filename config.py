from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    flask_secret_key: str
    spreadsheet_id: str
    sheet_name: str = "Tasks"
    google_client_id: str | None = None
    google_client_secret: str | None = None
    google_oauth_redirect_uri: str | None = None
    firebase_project_id: str | None = None
    firebase_api_key: str | None = None
    firebase_auth_domain: str | None = None
    firebase_app_id: str | None = None
    firebase_service_account_json: str | None = None
    google_scopes: tuple[str, ...] = (
        "https://www.googleapis.com/auth/spreadsheets",
    )


def load_settings() -> Settings:
    secret = os.getenv("FLASK_SECRET_KEY")
    spreadsheet_id = os.getenv("TASKS_SPREADSHEET_ID")
    if not secret:
        raise ValueError("FLASK_SECRET_KEY is required")
    if not spreadsheet_id:
        raise ValueError("TASKS_SPREADSHEET_ID is required")

    return Settings(
        flask_secret_key=secret,
        spreadsheet_id=spreadsheet_id,
        sheet_name=os.getenv("TASKS_SHEET_NAME", "Tasks"),
        google_client_id=os.getenv("GOOGLE_CLIENT_ID"),
        google_client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        google_oauth_redirect_uri=os.getenv("GOOGLE_OAUTH_REDIRECT_URI"),
        firebase_project_id=os.getenv("FIREBASE_PROJECT_ID"),
        firebase_api_key=os.getenv("FIREBASE_API_KEY"),
        firebase_auth_domain=os.getenv("FIREBASE_AUTH_DOMAIN"),
        firebase_app_id=os.getenv("FIREBASE_APP_ID"),
        firebase_service_account_json=os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON"),
    )
