"""Adzuna job search API (free tier: 250 requests/day)."""
from __future__ import annotations

import logging
import os

import requests

from ..models import Job, strip_html

log = logging.getLogger(__name__)
URL = "https://api.adzuna.com/v1/api/jobs/us/search/1"


def fetch(cfg: dict) -> list[Job]:
    app_id, app_key = os.environ.get("ADZUNA_APP_ID"), os.environ.get("ADZUNA_APP_KEY")
    if not (app_id and app_key):
        log.info("ADZUNA_APP_ID/ADZUNA_APP_KEY not set; skipping Adzuna")
        return []
    jobs = []
    for tab in cfg["tabs"]:
        for query in tab["queries"]:
            params = {
                "app_id": app_id,
                "app_key": app_key,
                "what_phrase": query,
                "where": "San Francisco",
                "distance": 80,  # km: reaches San Jose and the East Bay
                "max_days_old": cfg["lookback_days"],
                "results_per_page": 50,
                "content-type": "application/json",
            }
            resp = requests.get(URL, params=params, timeout=30)
            resp.raise_for_status()
            for item in resp.json().get("results", []):
                lo, hi = item.get("salary_min"), item.get("salary_max")
                salary = "-".join(f"${int(v):,}" for v in (lo, hi) if v)
                if salary and item.get("salary_is_predicted") == "1":
                    salary += " (estimated)"
                jobs.append(
                    Job(
                        source="Adzuna",
                        company=(item.get("company") or {}).get("display_name", ""),
                        title=strip_html(item.get("title")),
                        location=(item.get("location") or {}).get("display_name", ""),
                        url=item.get("redirect_url") or "",
                        description=strip_html(item.get("description")),
                        salary=salary,
                        posted=(item.get("created") or "")[:10],
                    )
                )
    return jobs
