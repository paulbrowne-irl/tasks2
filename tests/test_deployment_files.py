"""Tests for container and environment configuration files."""

from pathlib import Path


ROOT = Path(__file__).parents[1]


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
    ):
        assert key in text
