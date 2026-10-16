from __future__ import annotations

import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent


def load_config(path: str | os.PathLike | None = None) -> dict:
    with open(path or ROOT / "config.yaml") as f:
        return yaml.safe_load(f)


def load_resume_text() -> str:
    """Resume text from the RESUME_TEXT secret, or a local file for dev runs.

    The resume holds personal contact details, so it is never committed:
    resume.txt / resume.pdf are git-ignored.
    """
    text = os.environ.get("RESUME_TEXT", "").strip()
    if text:
        return text
    txt = ROOT / "resume.txt"
    if txt.exists():
        return txt.read_text()
    pdf = ROOT / "resume.pdf"
    if pdf.exists():
        from pypdf import PdfReader

        return "\n".join(page.extract_text() or "" for page in PdfReader(pdf).pages)
    raise SystemExit("No resume found: set RESUME_TEXT or add resume.txt / resume.pdf")
