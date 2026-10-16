"""Google Sheets tracker. The agent only appends rows; it never edits existing ones,
so your Status, Applied date and Notes are always safe."""
from __future__ import annotations

import json
import os
from datetime import date

import gspread

from .models import Job, normalize

HEADERS = [
    "Date found", "Company", "Title", "Location", "Remote", "Salary", "Link",
    "Source", "Match score", "Status", "Applied date", "Notes",
]
COL = {h: i for i, h in enumerate(HEADERS)}


def open_sheet() -> gspread.Spreadsheet:
    creds = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    return gspread.service_account_from_dict(creds).open_by_key(os.environ["SHEET_ID"])


def get_tab(sheet: gspread.Spreadsheet, name: str) -> gspread.Worksheet:
    """Return the tab, creating it with a header row the first time."""
    try:
        ws = sheet.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = sheet.add_worksheet(title=name, rows=1000, cols=len(HEADERS))
    if not ws.row_values(1):
        ws.update(range_name="A1", values=[HEADERS])
        ws.freeze(rows=1)
    return ws


def existing_keys(ws: gspread.Worksheet) -> set[str]:
    """Links and company|title keys already logged, so no job is added twice."""
    keys = set()
    for row in ws.get_all_values()[1:]:
        row += [""] * (len(HEADERS) - len(row))
        if row[COL["Link"]]:
            keys.add(row[COL["Link"]])
        keys.add(f"{normalize(row[COL['Company']])}|{normalize(row[COL['Title']])}")
    return keys


def to_row(job: Job) -> list[str]:
    note = f"Matched: {', '.join(job.matched_skills[:8])}" if job.matched_skills else ""
    return [
        date.today().isoformat(), job.company, job.title, job.location,
        "Yes" if job.remote or "remote" in job.location.lower() else "No",
        job.salary, job.url, job.source, str(job.score), "New", "", note,
    ]


def append_jobs(ws: gspread.Worksheet, jobs: list[Job]) -> None:
    if jobs:
        ws.append_rows([to_row(j) for j in jobs], value_input_option="RAW", insert_data_option="INSERT_ROWS")
