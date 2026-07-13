"""Tests for Cloud Run, container, and environment configuration files."""

import json
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_firebase_hosting_rewrites_to_flask_cloud_run_service_without_app_hosting():
    # Optional Firebase Hosting must route requests to the deployed Flask service.
    config = json.loads((ROOT / "firebase.json").read_text())
    rewrite = config["hosting"]["rewrites"][0]
    assert rewrite["run"]["serviceId"] == "task-management"
    assert rewrite["run"]["pinTag"] is True
    assert "apphosting" not in config


def test_dockerfile_runs_flask_app():
    # The container must invoke the Flask application factory through Gunicorn.
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "python:3.12-slim" in dockerfile
    assert "app:create_app()" in dockerfile
    assert "${PORT:-8080}" in dockerfile


def test_env_example_documents_required_configuration():
    # New deployments need a documented set of non-secret configuration names.
    text = (ROOT / ".env.example").read_text()
    for key in (
        "FLASK_SECRET_KEY",
        "TASKS_SPREADSHEET_ID",
        "GOOGLE_CLIENT_ID",
        "GOOGLE_OAUTH_REDIRECT_URI",
        "FIREBASE_PROJECT_ID",
    ):
        assert key in text
