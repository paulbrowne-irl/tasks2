"""Tests for the rendered task page and responsive stylesheet."""

from dataclasses import dataclass
from unittest.mock import Mock

from app import create_app


@dataclass
class FakeSettings:
    flask_secret_key: str = "test-secret"
    spreadsheet_id: str = "sheet-1"
    sheet_name: str = "Tasks"


def test_task_page_has_accessible_responsive_controls():
    # The page must expose labelled, keyboard-usable task controls.
    app = create_app(FakeSettings(), Mock(), Mock())
    client = app.test_client()
    with client.session_transaction() as session:
        session["user_uid"] = "user-1"
        session["user_email"] = "user@example.com"
    response = client.get("/")

    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert 'name="viewport"' in body
    assert 'for="category"' in body
    assert 'for="task-name"' in body
    assert 'id="refresh-tasks"' in body
    assert 'id="sort-colour"' in body
    assert 'id="triage-sheets"' in body
    assert 'role="status"' in body


def test_static_styles_include_mobile_breakpoint():
    # The stylesheet must include a narrow-screen layout breakpoint.
    app = create_app(FakeSettings(), Mock(), Mock())
    response = app.test_client().get("/static/styles.css")

    assert response.status_code == 200
    assert "@media (max-width: 640px)" in response.get_data(as_text=True)
