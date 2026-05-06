"""Google Sheets attendance persistence utilities."""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass
from queue import Queue
from typing import Any

import gspread
from google.oauth2.service_account import Credentials

from attendance.sheets_records import build_attendance_row
from attendance.sheets_upload import append_row_to_csv, upload_to_sheet

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


@dataclass(frozen=True, slots=True)
class UploadTask:
    name: str
    status: str


class SheetUploadWorker:
    """Background worker for non-blocking Google Sheets uploads."""

    def __init__(
        self,
        sheet: Any,
        *,
        max_retries: int = 3,
        backoff_base_seconds: float = 1.0,
        backoff_max_seconds: float = 8.0,
        dedupe_cooldown_seconds: float = 0.0,
        fallback_csv_path: str | None = None,
        worker_logger: logging.Logger | None = None,
    ) -> None:
        self._sheet = sheet
        self._queue: Queue[UploadTask] = Queue()
        self._max_retries = max(0, max_retries)
        self._backoff_base = max(0.1, backoff_base_seconds)
        self._backoff_max = max(self._backoff_base, backoff_max_seconds)
        self._dedupe_cooldown_seconds = max(0.0, dedupe_cooldown_seconds)
        self._fallback_csv_path = fallback_csv_path
        self._logger = worker_logger or logging.getLogger(__name__)
        self._lock = threading.Lock()
        self._in_flight: set[str] = set()
        self._last_enqueued: dict[str, float] = {}
        self._uploaded: set[str] = set()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def enqueue(self, name: str, status: str) -> bool:
        now = time.monotonic()
        with self._lock:
            if name in self._uploaded:
                return False
            last_enqueued = self._last_enqueued.get(name)
            if last_enqueued is not None and now - last_enqueued < self._dedupe_cooldown_seconds:
                return False
            if name in self._in_flight:
                return False
            self._in_flight.add(name)
            self._last_enqueued[name] = now

        self._queue.put(UploadTask(name=name, status=status))
        return True

    def _run(self) -> None:
        while True:
            task = self._queue.get()
            try:
                self._upload_with_retry(task)
            finally:
                self._queue.task_done()

    def _upload_with_retry(self, task: UploadTask) -> None:
        if self._sheet is None:
            self._handle_fallback(task, "Sheet unavailable")
            return

        try:
            for attempt in range(self._max_retries + 1):
                if upload_to_sheet(self._sheet, task.name, task.status, logger=self._logger):
                    with self._lock:
                        self._uploaded.add(task.name)
                    return
                sleep_seconds = min(self._backoff_base * (2**attempt), self._backoff_max)
                time.sleep(sleep_seconds)

            self._handle_fallback(task, "Max retries exceeded")
        finally:
            with self._lock:
                self._in_flight.discard(task.name)

    def _handle_fallback(self, task: UploadTask, reason: str) -> None:
        if not self._fallback_csv_path:
            self._logger.warning("Attendance for %s not persisted (%s).", task.name, reason)
            return

        row = build_attendance_row(task.name, task.status)
        if append_row_to_csv(self._fallback_csv_path, row, logger=self._logger):
            self._logger.warning("Attendance for %s saved to fallback CSV (%s).", task.name, reason)
        else:
            self._logger.warning("Attendance for %s failed to persist (%s).", task.name, reason)
