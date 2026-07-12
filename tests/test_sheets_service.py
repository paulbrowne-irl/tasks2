"""Unit tests for Google Sheets task storage behavior."""

from unittest.mock import Mock

import pytest

from sheets_service import SheetsService, SheetsServiceError


def make_service(values):
    # Build a mocked Sheets API with an existing Tasks worksheet.
    api = Mock()
    api.spreadsheets().get().execute.return_value = {
        "sheets": [{"properties": {"title": "Tasks", "sheetId": 0}}]
    }
    api.spreadsheets().values().get().execute.return_value = {"values": values}
    return SheetsService(api, "sheet-1", "Tasks")


def test_reads_tasks_and_preserves_header_fields():
    # Spreadsheet columns map to task fields without losing metadata.
    service = make_service(
        [
            ["Category", "Task", "Colour", "T Date", "Hash"],
            ["Work", "Call customer", "Blue", "2026-07-12", "abc"],
        ]
    )

    result = service.list_tasks()

    assert result[0]["category"] == "Work"
    assert result[0]["task_name"] == "Call customer"
    assert result[0]["colour"] == "Blue"
    assert result[0]["t_date"] == "2026-07-12"
    assert result[0]["hash"] == "abc"


def test_add_task_appends_category_and_name():
    # Adding a task appends values rather than replacing existing rows.
    api = Mock()
    api.spreadsheets().get().execute.return_value = {
        "sheets": [{"properties": {"title": "Tasks", "sheetId": 0}}]
    }
    service = SheetsService(api, "sheet-1", "Tasks")

    service.add_task("Work", "Call customer")

    api.spreadsheets().values().append.assert_called_once()
    body = api.spreadsheets().values().append.call_args.kwargs["body"]
    assert body["values"] == [["Work", "Call customer"]]


def test_sort_by_colour_delegates_to_sheet_sort():
    # Colour sorting is implemented as a Google Sheets batch update.
    api = Mock()
    api.spreadsheets().get().execute.return_value = {
        "sheets": [{"properties": {"title": "Tasks", "sheetId": 0}}]
    }
    service = SheetsService(api, "sheet-1", "Tasks")

    service.sort_by_colour()

    api.spreadsheets().batchUpdate.assert_called_once()


def test_google_api_errors_are_translated():
    # Low-level API failures become application-level SheetsServiceError values.
    api = Mock()
    api.spreadsheets().get().execute.return_value = {
        "sheets": [{"properties": {"title": "Tasks", "sheetId": 0}}]
    }
    api.spreadsheets().values().get().execute.side_effect = RuntimeError("offline")
    service = SheetsService(api, "sheet-1", "Tasks")

    with pytest.raises(SheetsServiceError, match="Google Sheets"):
        service.list_tasks()


def test_creates_task_sheet_if_missing():
    # A missing configured worksheet is created and given the required headers.
    api = Mock()
    sheets_api = api.spreadsheets.return_value
    sheets_api.get.return_value.execute.return_value = {"sheets": []}
    sheets_api.batchUpdate.return_value.execute.return_value = {
        "replies": [{"addSheet": {"properties": {"sheetId": 123}}}]
    }
    sheets_api.values.return_value.update.return_value.execute.return_value = {}
    sheets_api.values.return_value.get.return_value.execute.return_value = {
        "values": [["Category", "Task", "Colour", "T Date", "Hash"]]
    }

    service = SheetsService(api, "sheet-1", "Tasks")
    result = service.list_tasks()

    assert sheets_api.get.call_args.kwargs == {
        "spreadsheetId": "sheet-1",
        "includeGridData": False,
    }
    sheets_api.batchUpdate.assert_called_once()
    sheets_api.values.return_value.update.assert_called_once()
    assert result == []
