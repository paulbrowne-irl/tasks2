from unittest.mock import Mock

import pytest

from sheets_service import SheetsService, SheetsServiceError


def make_service(values):
    api = Mock()
    api.spreadsheets().values().get().execute.return_value = {"values": values}
    return SheetsService(api, "sheet-1", "Tasks")


def test_reads_tasks_and_preserves_header_fields():
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
    api = Mock()
    service = SheetsService(api, "sheet-1", "Tasks")

    service.add_task("Work", "Call customer")

    api.spreadsheets().values().append.assert_called_once()
    body = api.spreadsheets().values().append.call_args.kwargs["body"]
    assert body["values"] == [["Work", "Call customer"]]


def test_sort_by_colour_delegates_to_sheet_sort():
    api = Mock()
    service = SheetsService(api, "sheet-1", "Tasks")

    service.sort_by_colour()

    api.spreadsheets().batchUpdate.assert_called_once()


def test_google_api_errors_are_translated():
    api = Mock()
    api.spreadsheets().values().get().execute.side_effect = RuntimeError("offline")
    service = SheetsService(api, "sheet-1", "Tasks")

    with pytest.raises(SheetsServiceError, match="Google Sheets"):
        service.list_tasks()
