# Scan Face Attendance

A Python 3.10+ face-recognition attendance app that detects known faces from webcam frames and logs attendance into Google Sheets.

## Features

- Real-time webcam face detection and labeling
- 3-second continuous face confirmation before attendance is marked
- Continuous scanning after successful marks to track all students
- Attendance status classification (`Present`/`Late`) based on cutoff time
- Duplicate attendance prevention per runtime session
- Google Sheets logging with safe error handling
- Unit-tested core logic and adapters

## Project Structure

- `main.py` - application entrypoint
- `app/` - startup/bootstrap composition helpers
- `camera/` - webcam capture loop, preprocessing, rendering, Qt runtime setup
- `recognition/` - known-face loading and encoding helpers
- `attendance/` - attendance policy, deduplication logic, and Sheets persistence/services
- `utils/` - shared utilities (logging)
- `known_faces/` - known face images (`<name>.jpg`, `<name>.png`, etc.)
- `tests/` - unit tests

## Requirements

- Python 3.10+
- `face_recognition`, `opencv-python`, `gspread`, `google-auth`
- A valid Google service account credentials file: `credentials.json`
- Google Sheet named `AttendanceDB` with worksheet `Live_Logs`

## Run

```bash
source venv/bin/activate
python main.py
```

Press `q` to quit the webcam window.

## Run Tests

```bash
source venv/bin/activate
python -m unittest discover -s tests -t . -v
```

## Seed Sample Attendance Data

Use this one-liner to append sample rows to `Live_Logs`:

```bash
source venv/bin/activate
python -c "from attendance.sheets import open_live_logs_sheet, upload_to_sheets; s=open_live_logs_sheet(); [upload_to_sheets(s, n, st) for n, st in [('Seed_User_1','Present'),('Seed_User_2','Late'),('Seed_User_3','Present')]]"
```

## Notes

- Camera index is currently set to `0` in `main.py`.
- If your camera is different, update `camera_index` in `main.py`.
- Seeding and live logging append rows with current date/time.
# Face_Scan_attendance
