import os

import pytest

from config import Settings, load_settings


def test_load_settings_reads_required_environment(monkeypatch):
    monkeypatch.setenv("FLASK_SECRET_KEY", "test-secret")
    monkeypatch.setenv("TASKS_SPREADSHEET_ID", "sheet-123")
    monkeypatch.setenv("TASKS_SHEET_NAME", "Tasks")

    settings = load_settings()

    assert isinstance(settings, Settings)
    assert settings.flask_secret_key == "test-secret"
    assert settings.spreadsheet_id == "sheet-123"
    assert settings.sheet_name == "Tasks"


def test_load_settings_rejects_missing_secret(monkeypatch):
    monkeypatch.delenv("FLASK_SECRET_KEY", raising=False)
    monkeypatch.setenv("TASKS_SPREADSHEET_ID", "sheet-123")

    with pytest.raises(ValueError, match="FLASK_SECRET_KEY"):
        load_settings()
