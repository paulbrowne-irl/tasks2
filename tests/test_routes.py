"""Route tests for authentication boundaries and task operations."""

from dataclasses import dataclass
from unittest.mock import Mock

import pytest

from app import create_app
from auth import Identity


@dataclass
class FakeSettings:
    flask_secret_key: str = "test-secret"
    spreadsheet_id: str = "sheet-1"
    sheet_name: str = "Tasks"


@pytest.fixture
def services():
    # Provide isolated fake authentication and Sheets services to route tests.
    auth = Mock()
    sheets = Mock()
    sheets.list_tasks.return_value = [{"category": "Work", "task_name": "Call", "colour": "Blue"}]
    return auth, sheets


def test_unauthenticated_task_api_is_rejected(services):
    # Requests without a Flask session must receive a 401 response.
    auth, sheets = services
    client = create_app(FakeSettings(), auth, sheets).test_client()

    response = client.get("/api/tasks")

    assert response.status_code == 401
    assert response.json["error"] == "Authentication required"


def authenticated_client(app):
    client = app.test_client()
    with client.session_transaction() as session:
        session["user_uid"] = "user-1"
        session["user_email"] = "user@example.com"
    return client


def test_authenticated_task_api_returns_rows(services):
    # A Flask session can retrieve spreadsheet-backed task rows.
    auth, sheets = services
    client = authenticated_client(create_app(FakeSettings(), auth, sheets))

    response = client.get("/api/tasks")

    assert response.status_code == 200
    assert response.json["tasks"][0]["task_name"] == "Call"


def test_add_task_validates_and_delegates(services):
    # Valid task input is delegated to the Sheets service and returns 201.
    auth, sheets = services
    client = authenticated_client(create_app(FakeSettings(), auth, sheets))

    response = client.post(
        "/api/tasks",
        json={"category": "Work", "task_name": "Call customer"},
    )

    assert response.status_code == 201
    sheets.add_task.assert_called_once_with("Work", "Call customer")


def test_add_task_rejects_empty_values(services):
    # Empty category or task names are rejected before any spreadsheet write.
    auth, sheets = services
    client = authenticated_client(create_app(FakeSettings(), auth, sheets))

    response = client.post(
        "/api/tasks",
        json={"category": "", "task_name": "Call customer"},
    )

    assert response.status_code == 400
    sheets.add_task.assert_not_called()


def test_sort_and_triage_routes_delegate(services):
    # Organisation actions delegate to the matching Sheets service methods.
    auth, sheets = services
    client = authenticated_client(create_app(FakeSettings(), auth, sheets))

    sort_response = client.post("/api/tasks/sort")
    triage_response = client.post("/api/task-sheets/triage")

    assert sort_response.status_code == 200
    assert triage_response.status_code == 200
    sheets.sort_by_colour.assert_called_once_with()
    sheets.triage_task_sheets.assert_called_once_with()
