from __future__ import annotations

import html
import re
from dataclasses import dataclass, field

_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


def strip_html(text: str | None) -> str:
    """Turn (possibly double-escaped) HTML into plain text."""
    if not text:
        return ""
    text = html.unescape(html.unescape(text))
    return _SPACE.sub(" ", _TAG.sub(" ", text)).strip()


def normalize(text: str) -> str:
    return _SPACE.sub(" ", re.sub(r"[^a-z0-9+/ ]", " ", text.lower())).strip()


@dataclass
class Job:
    source: str
    company: str
    title: str
    location: str
    url: str
    description: str = ""
    remote: bool = False
    salary: str = ""
    posted: str = ""
    # Filled in by the pipeline.
    tab: str = ""
    score: int = 0
    matched_skills: list[str] = field(default_factory=list)

    @property
    def key(self) -> str:
        """Identity used to avoid logging the same role twice across sources."""
        return f"{normalize(self.company)}|{normalize(self.title)}"
