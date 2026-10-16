"""Keyword-overlap match score (0-100).

A stand-in until the shortlisting-chance skill exists. Weights:
  55  share of the job's skill keywords that also appear in the resume
  15  seniority words in the title (senior/staff/principal/director...)
  15  networking / infrastructure domain terms in the job
  15  company is on the target list
"""
from __future__ import annotations

import re

from .models import Job, normalize

_SENIOR = re.compile(r"\b(senior|sr|staff|principal|distinguished|lead|director|head|vp)\b", re.I)


def _terms_in(text: str, terms: list[str]) -> set[str]:
    text = text.lower()
    return {t for t in terms if re.search(r"(?<![\w+/])" + re.escape(t.lower()) + r"(?![\w+/])", text)}


def resume_skills(resume: str, cfg: dict) -> set[str]:
    return _terms_in(resume, cfg["skills"])


def is_target_company(company: str, cfg: dict) -> bool:
    name = normalize(company)
    return any(re.search(rf"\b{re.escape(normalize(t))}\b", name) for t in cfg["target_companies"])


def score(job: Job, resume_terms: set[str], cfg: dict) -> int:
    text = f"{job.title} {job.description}"
    job_terms = _terms_in(text, cfg["skills"])
    matched = job_terms & resume_terms
    job.matched_skills = sorted(matched)

    skill = 55 * len(matched) / len(job_terms) if job_terms else 0
    seniority = 15 if _SENIOR.search(job.title) else 0
    domain = min(15, 5 * len(_terms_in(text, cfg["domain_terms"])))
    target = 15 if is_target_company(job.company, cfg) else 0
    # Short descriptions (some APIs truncate) would overrate a 1-of-1 match.
    if len(job_terms) < 3:
        skill *= len(job_terms) / 3
    return round(min(100, skill + seniority + domain + target))
