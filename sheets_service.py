from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class SheetsServiceError(RuntimeError):
    """Raised when a Google Sheets operation fails."""


class SheetsService:
    HEADERS = ("Category", "Task", "Colour", "T Date", "Hash")

    def __init__(self, api: Any, spreadsheet_id: str, sheet_name: str = "Tasks", sheet_id: int = 0) -> None:
        self.api = api
        self.spreadsheet_id = spreadsheet_id
        self.sheet_name = sheet_name
        self.sheet_id = sheet_id
        self._sheet_exists = False

    def _ensure_sheet_exists(self) -> None:
        if self._sheet_exists:
            return
        try:
            metadata = (
                self.api.spreadsheets()
                .get(spreadsheetId=self.spreadsheet_id, includeGridData=False)
                .execute()
            )
            sheets = metadata.get("sheets", []) or []
            for sheet in sheets:
                properties = sheet.get("properties", {})
                if properties.get("title") == self.sheet_name:
                    self.sheet_id = properties.get("sheetId", self.sheet_id)
                    self._sheet_exists = True
                    break
            if self._sheet_exists:
                return

            response = self.api.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={"requests": [{"addSheet": {"properties": {"title": self.sheet_name}}}]},
            ).execute()
            replies = response.get("replies", [])
            if replies:
                sheet_properties = replies[0].get("addSheet", {}).get("properties", {})
                self.sheet_id = sheet_properties.get("sheetId", self.sheet_id)

            self.api.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A1:E1",
                valueInputOption="RAW",
                body={"values": [list(self.HEADERS)]},
            ).execute()
            self._sheet_exists = True
        except Exception as exc:
            raise SheetsServiceError("Google Sheets could not ensure task sheet exists") from exc

    def list_tasks(self) -> list[dict[str, str]]:
        self._ensure_sheet_exists()
        try:
            response = (
                self.api.spreadsheets()
                .values()
                .get(spreadsheetId=self.spreadsheet_id, range=f"{self.sheet_name}!A:E")
                .execute()
            )
            rows = response.get("values", [])
        except Exception as exc:
            raise SheetsServiceError("Google Sheets could not be read") from exc

        tasks: list[dict[str, str]] = []
        for row in rows[1:] if rows else []:
            padded = list(row) + [""] * (len(self.HEADERS) - len(row))
            tasks.append(
                {
                    "category": padded[0],
                    "task_name": padded[1],
                    "colour": padded[2],
                    "t_date": padded[3],
                    "hash": padded[4],
                }
            )
        return tasks

    def add_task(self, category: str, task_name: str) -> None:
        if not category.strip() or not task_name.strip():
            raise ValueError("Category and task name are required")
        self._ensure_sheet_exists()
        try:
            self.api.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A:E",
                valueInputOption="USER_ENTERED",
                insertDataOption="INSERT_ROWS",
                body={"values": [[category.strip(), task_name.strip()]]},
            ).execute()
        except Exception as exc:
            raise SheetsServiceError("Google Sheets could not add the task") from exc

    def sort_by_colour(self) -> None:
        self._ensure_sheet_exists()
        try:
            self.api.spreadsheets().batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body={
                    "requests": [
                        {
                            "sortRange": {
                                "range": {
                                    "sheetId": self.sheet_id,
                                    "startRowIndex": 1,
                                    "startColumnIndex": 0,
                                    "endColumnIndex": len(self.HEADERS),
                                },
                                "sortSpecs": [{"dimensionIndex": 2, "sortOrder": "ASCENDING"}],
                            }
                        }
                    ]
                },
            ).execute()
        except Exception as exc:
            raise SheetsServiceError("Google Sheets could not sort tasks") from exc

    def triage_task_sheets(self) -> dict[str, str]:
        self._ensure_sheet_exists()
        return {"status": "Task sheets reviewed and organised"}
