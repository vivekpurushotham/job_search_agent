"""Daily run: fetch jobs, filter, score, and append the best new ones per tab.

  python -m job_agent.main             # scheduled run (only proceeds at run_hour local time)
  python -m job_agent.main --force     # run now regardless of the hour
  python -m job_agent.main --dry-run   # print matches, don't touch the sheet
"""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from .config import load_config, load_resume_text
from .filters import keep
from .models import Job
from .scoring import resume_skills, score
from .sources import fetch_all

log = logging.getLogger("job_agent")


def select(jobs: list[Job], seen: dict[str, set[str]], resume_terms: set[str], cfg: dict) -> dict[str, list[Job]]:
    """Best new jobs per tab, highest score first, skipping anything already logged."""
    picked: dict[str, list[Job]] = {t["name"]: [] for t in cfg["tabs"]}
    keys_this_run: set[str] = set()
    candidates = []
    for job in jobs:
        if not job.title or not job.url or not keep(job, cfg):
            continue
        job.score = score(job, resume_terms, cfg)
        if job.score >= cfg["min_score"]:
            candidates.append(job)
    for job in sorted(candidates, key=lambda j: j.score, reverse=True):
        already = seen.get(job.tab, set())
        if job.url in already or job.key in already or job.key in keys_this_run:
            continue
        if len(picked[job.tab]) < cfg["max_per_tab"]:
            picked[job.tab].append(job)
            keys_this_run.add(job.key)
    return picked


def is_run_hour(cfg: dict) -> bool:
    # GitHub cron is UTC-only, so the workflow fires at both 15:00 and 16:00 UTC
    # and this check keeps whichever one is 8 AM Pacific given daylight saving.
    return datetime.now(ZoneInfo(cfg["timezone"])).hour == cfg["run_hour"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="run regardless of local time")
    parser.add_argument("--dry-run", action="store_true", help="print matches, don't write the sheet")
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

    cfg = load_config()
    if not (args.force or args.dry_run or is_run_hour(cfg)):
        log.info("Not %d:00 in %s; skipping this trigger", cfg["run_hour"], cfg["timezone"])
        return 0

    resume_terms = resume_skills(load_resume_text(), cfg)
    log.info("Resume skills found: %s", ", ".join(sorted(resume_terms)))
    jobs = fetch_all(cfg)

    if args.dry_run:
        picked = select(jobs, {}, resume_terms, cfg)
        for tab, rows in picked.items():
            print(f"\n== {tab} ({len(rows)}) ==")
            for j in rows:
                print(f"{j.score:>3}  {j.company} | {j.title} | {j.location} | {j.url}")
        return 0

    from . import sheets

    sheet = sheets.open_sheet()
    tabs = {t["name"]: sheets.get_tab(sheet, t["name"]) for t in cfg["tabs"]}
    seen = {name: sheets.existing_keys(ws) for name, ws in tabs.items()}
    picked = select(jobs, seen, resume_terms, cfg)
    for name, rows in picked.items():
        sheets.append_jobs(tabs[name], rows)
        log.info("%s: added %d new jobs", name, len(rows))
    return 0


if __name__ == "__main__":
    sys.exit(main())
