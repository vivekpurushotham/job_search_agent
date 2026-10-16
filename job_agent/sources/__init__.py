from __future__ import annotations

import logging

from ..models import Job
from . import adzuna, boards, jsearch

log = logging.getLogger(__name__)


def fetch_all(cfg: dict) -> list[Job]:
    """Collect jobs from every configured source; one failing source never stops the run."""
    jobs: list[Job] = []
    for name, fetch in (("jsearch", jsearch.fetch), ("adzuna", adzuna.fetch), ("boards", boards.fetch)):
        try:
            found = fetch(cfg)
            log.info("%s: %d jobs", name, len(found))
            jobs.extend(found)
        except Exception:
            log.exception("%s failed; continuing with other sources", name)
    return jobs
