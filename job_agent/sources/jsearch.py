"""JSearch (RapidAPI): Google Jobs aggregation, covers FAANG career sites.

Free tier is ~200 requests/month, so the agent makes one request per
configured query per day (4 queries -> ~120/month).
"""
from __future__ import annotations

import logging
import os

import requests

from ..models import Job, strip_html

log = logging.getLogger(__name__)
URL = "https://jsearch.p.rapidapi.com/search"


def _date_posted(days: int) -> str:
    return "today" if days <= 1 else "3days" if days <= 3 else "week"


def _salary(item: dict) -> str:
    lo, hi = item.get("job_min_salary"), item.get("job_max_salary")
    if not lo and not hi:
        return ""
    period = (item.get("job_salary_period") or "").lower()
    rng = "-".join(f"${int(v):,}" for v in (lo, hi) if v)
    return f"{rng} / {period}" if period else rng


def fetch(cfg: dict) -> list[Job]:
    key = os.environ.get("JSEARCH_API_KEY")
    if not key:
        log.info("JSEARCH_API_KEY not set; skipping JSearch")
        return []
    headers = {"X-RapidAPI-Key": key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"}
    jobs = []
    for tab in cfg["tabs"]:
        for query in tab["queries"]:
            params = {
                "query": f"{query} in {cfg['location']['query']}",
                "country": "us",
                "page": 1,
                "num_pages": 1,
                "date_posted": _date_posted(cfg["lookback_days"]),
            }
            resp = requests.get(URL, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            for item in resp.json().get("data", []):
                loc = ", ".join(p for p in (item.get("job_city"), item.get("job_state")) if p)
                jobs.append(
                    Job(
                        source=f"JSearch ({item.get('job_publisher') or 'web'})",
                        company=item.get("employer_name") or "",
                        title=item.get("job_title") or "",
                        location=loc or ("Remote" if item.get("job_is_remote") else ""),
                        url=item.get("job_apply_link") or "",
                        description=strip_html(item.get("job_description")),
                        remote=bool(item.get("job_is_remote")),
                        salary=_salary(item),
                        posted=(item.get("job_posted_at_datetime_utc") or "")[:10],
                    )
                )
    return jobs
