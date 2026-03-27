from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from attendance import sheets


class TestAttendanceSheets(unittest.TestCase):
    @patch("attendance.sheets.gspread.authorize")
    def test_authorize_delegates_to_gspread(self, mock_authorize: MagicMock) -> None:
        credentials = MagicMock()
        expected_client = MagicMock()
        mock_authorize.return_value = expected_client

        client = sheets.authorize(credentials)

        mock_authorize.assert_called_once_with(credentials)
        self.assertIs(client, expected_client)

    @patch("attendance.sheets.Credentials.from_service_account_file")
    @patch("attendance.sheets.authorize")
    def test_open_live_logs_sheet_uses_expected_chain(
        self,
        mock_authorize: MagicMock,
        mock_from_service_account_file: MagicMock,
    ) -> None:
        credentials = MagicMock()
        client = MagicMock()
        spreadsheet = MagicMock()
        worksheet = MagicMock()

        mock_from_service_account_file.return_value = credentials
        mock_authorize.return_value = client
        client.open.return_value = spreadsheet
        spreadsheet.worksheet.return_value = worksheet

        result = sheets.open_live_logs_sheet(
            credentials_file="credentials.json",
            spreadsheet_name="AttendanceDB",
            worksheet_name="Live_Logs",
        )

        mock_from_service_account_file.assert_called_once_with(
            "credentials.json",
            scopes=sheets.SCOPES,
        )
        mock_authorize.assert_called_once_with(credentials)
        client.open.assert_called_once_with("AttendanceDB")
        spreadsheet.worksheet.assert_called_once_with("Live_Logs")
        self.assertIs(result, worksheet)

    def test_upload_to_sheets_appends_expected_payload(self) -> None:
        sheet = MagicMock()

        sheets.upload_to_sheets(sheet=sheet, name="Alice", status="Present")

        sheet.append_row.assert_called_once()
        row = sheet.append_row.call_args.args[0]
        self.assertEqual(row[2], "Alice")
        self.assertEqual(row[3], "Present")
        self.assertRegex(row[0], r"^\d{4}-\d{2}-\d{2}$")
        self.assertRegex(row[1], r"^\d{2}:\d{2}:\d{2}$")

    @patch("attendance.sheets.logger.exception")
    def test_upload_to_sheets_swallows_append_errors(self, mock_logger_exception: MagicMock) -> None:
        sheet = MagicMock()
        sheet.append_row.side_effect = RuntimeError("network issue")

        sheets.upload_to_sheets(sheet=sheet, name="Alice", status="Present")

        sheet.append_row.assert_called_once()
        mock_logger_exception.assert_called_once()

    @patch("attendance.sheets.upload_to_sheets")
    def test_upload_to_sheets_async_starts_thread(self, mock_upload: MagicMock) -> None:
        thread = sheets.upload_to_sheets_async(sheet=MagicMock(), name="Alice", status="Present")
        thread.join(timeout=1)

        mock_upload.assert_called_once()


if __name__ == "__main__":
    unittest.main()
