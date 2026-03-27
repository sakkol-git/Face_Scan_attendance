"""Google Sheets attendance persistence utilities."""

from __future__ import annotations

import logging
import threading
from typing import Any

import gspread
from google.oauth2.service_account import Credentials

from attendance.sheets_upload import upload_to_sheet

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def authorize(credentials: Credentials) -> gspread.Client:
    """Return an authorized Google Sheets client."""
    return gspread.authorize(credentials)


def open_live_logs_sheet(
    credentials_file: str = "credentials.json",
    spreadsheet_name: str = "AttendanceDB",
    worksheet_name: str = "Live_Logs",
) -> Any:
    """Open and return the configured attendance worksheet."""
    credentials = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)
    client = authorize(credentials)
    return client.open(spreadsheet_name).worksheet(worksheet_name)


def upload_to_sheets(sheet: Any, name: str, status: str) -> None:
    """Append one attendance record to the target sheet."""
    upload_to_sheet(sheet=sheet, name=name, status=status, logger=logger)


def upload_to_sheets_async(sheet: Any, name: str, status: str) -> threading.Thread:
    """Upload attendance in a background thread."""
    thread = threading.Thread(target=upload_to_sheets, args=(sheet, name, status), daemon=True)
    thread.start()
    return thread
