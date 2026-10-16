from __future__ import annotations

import re

from .models import Job

_NON_US = re.compile(
    r"\b(uk|united kingdom|london|ireland|dublin|canada|toronto|vancouver|india|bangalore|bengaluru|"
    r"hyderabad|germany|berlin|munich|france|paris|netherlands|amsterdam|spain|poland|israel|"
    r"singapore|japan|tokyo|australia|sydney|brazil|mexico|emea|apac|latam|europe)\b"
)


def classify_tab(title: str, cfg: dict) -> str | None:
    """Spreadsheet tab for this title, or None if it is not a target role."""
    if re.search(cfg["exclude_title_pattern"], title, re.I):
        return None
    for tab in cfg["tabs"]:
        if re.search(tab["title_pattern"], title, re.I):
            return tab["name"]
    return None


def location_ok(job: Job, cfg: dict) -> bool:
    loc = job.location.lower()
    if any(city in loc for city in cfg["location"]["bay_area"]):
        return True
    if cfg["location"].get("include_remote_us"):
        remote = job.remote or "remote" in loc
        return remote and not _NON_US.search(loc)
    return False


def description_ok(job: Job, cfg: dict) -> bool:
    return not re.search(cfg["exclude_description_pattern"], job.description, re.I)


def keep(job: Job, cfg: dict) -> bool:
    """Assign the job's tab and report whether it passes every filter."""
    tab = classify_tab(job.title, cfg)
    if not tab:
        return False
    job.tab = tab
    return location_ok(job, cfg) and description_ok(job, cfg)
