"""Public company job boards: Greenhouse, Ashby and Lever. No API key needed."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

import requests

from ..models import Job, strip_html

log = logging.getLogger(__name__)


def _greenhouse(slug: str) -> list[Job]:
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs?content=true"
    data = requests.get(url, timeout=30).json()
    return [
        Job(
            source="Greenhouse",
            company=j.get("company_name") or slug.title(),
            title=j.get("title") or "",
            location=(j.get("location") or {}).get("name", ""),
            url=j.get("absolute_url") or "",
            description=strip_html(j.get("content")),
            posted=(j.get("first_published") or j.get("updated_at") or "")[:10],
        )
        for j in data.get("jobs", [])
    ]


def _ashby(slug: str) -> list[Job]:
    url = f"https://api.ashbyhq.com/posting-api/job-board/{slug}?includeCompensation=true"
    data = requests.get(url, timeout=30).json()
    jobs = []
    for j in data.get("jobs", []):
        if j.get("isListed") is False:
            continue
        locations = [j.get("location") or ""] + [s.get("location", "") for s in j.get("secondaryLocations") or []]
        comp = (j.get("compensation") or {}).get("scrapeableCompensationSalarySummary") or ""
        jobs.append(
            Job(
                source="Ashby",
                company=slug.title(),
                title=j.get("title") or "",
                location="; ".join(l for l in locations if l),
                url=j.get("jobUrl") or "",
                description=j.get("descriptionPlain") or strip_html(j.get("descriptionHtml")),
                remote=bool(j.get("isRemote")),
                salary=comp,
                posted=(j.get("publishedAt") or "")[:10],
            )
        )
    return jobs


def _lever(slug: str) -> list[Job]:
    data = requests.get(f"https://api.lever.co/v0/postings/{slug}?mode=json", timeout=30).json()
    jobs = []
    for j in data:
        cats = j.get("categories") or {}
        created = j.get("createdAt")
        jobs.append(
            Job(
                source="Lever",
                company=slug.title(),
                title=j.get("text") or "",
                location="; ".join(cats.get("allLocations") or [cats.get("location") or ""]),
                url=j.get("hostedUrl") or "",
                description=j.get("descriptionPlain") or strip_html(j.get("description")),
                remote=j.get("workplaceType") == "remote",
                posted=datetime.fromtimestamp(created / 1000, timezone.utc).strftime("%Y-%m-%d") if created else "",
            )
        )
    return jobs


def fetch(cfg: dict) -> list[Job]:
    jobs: list[Job] = []
    readers = {"greenhouse": _greenhouse, "ashby": _ashby, "lever": _lever}
    for kind, slugs in (cfg.get("boards") or {}).items():
        for slug in slugs or []:
            try:
                jobs.extend(readers[kind](slug))
            except Exception:
                log.exception("%s board %s failed", kind, slug)
    return jobs
