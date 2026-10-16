# Job search agent: working notes

Daily (8 AM Pacific, GitHub Actions) job finder that appends matches to a Google Sheet. See README.md for setup.

## Decisions (agreed with the user)
- Runs on GitHub Actions; output is the Google Sheet only (no email/Slack).
- Two tabs: "Engineering Manager" (EM / Sr EM / Director / Head of Eng) and "Senior Engineer & TL" (Senior / Staff / Principal / Tech Lead / Architect).
- Location: SF Bay Area plus remote US. No visa sponsorship needed; skip roles requiring US citizenship or clearance.
- Top 5 new matches per tab per day. Target companies (FAANG-like, in config.yaml) get a ranking boost; others still appear.
- The agent finds and logs jobs only. It never applies.
- Sheet rows are append-only: never overwrite Status, Applied date or Notes the user edits.
- Ranking is keyword overlap for now. A separate "shortlist chance" skill (.claude/skills/job-shortlist-scorer/) is being built and will replace or supplement `job_agent/scoring.py`.

## Rules
- Never commit the resume or any keys: they come from GitHub secrets (RESUME_TEXT etc.). Local `resume.pdf` / `resume.txt` are git-ignored.
- Keep code Python 3.9-compatible (the local Mac python); CI uses 3.12.
- Test: `.venv/bin/python -m pytest -q`. Live check without touching the sheet: `python -m job_agent.main --dry-run`.

## Open items
- Domain preference (networking/infra boosted vs neutral), whether to include Cisco, and the exact tab title mapping still need final confirmation from the user.
