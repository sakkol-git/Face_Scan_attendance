from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from attendance import sheets


class TestAttendanceSheetsIntegration(unittest.TestCase):
    @patch("attendance.sheets.Credentials.from_service_account_file")
    @patch("attendance.sheets.authorize")
    def test_open_live_logs_sheet_uses_default_params(
        self,
        mock_authorize: MagicMock,
        mock_from_service_account_file: MagicMock,
    ) -> None:
        credentials = MagicMock()
        worksheet = MagicMock()
        client = MagicMock()
        spreadsheet = MagicMock()
        mock_from_service_account_file.return_value = credentials
        mock_authorize.return_value = client
        client.open.return_value = spreadsheet
        spreadsheet.worksheet.return_value = worksheet

        result = sheets.open_live_logs_sheet()

        mock_from_service_account_file.assert_called_once_with(
            "credentials.json",
            scopes=sheets.SCOPES,
        )
        client.open.assert_called_once_with("AttendanceDB")
        spreadsheet.worksheet.assert_called_once_with("Live_Logs")
        self.assertIs(result, worksheet)


if __name__ == "__main__":
    unittest.main()
