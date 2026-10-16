---
name: job-shortlist-scorer
description: Score and rank job postings against a resume and estimate the chance of being shortlisted, using a fixed, weighted rubric (role similarity, domain fit, required-skills coverage, seniority, location/work authorization, preferred signals, plus company tier) and filters out roles below a total-compensation floor (default $300k TC, checked against levels.fyi data). For each job it returns a shortlist-chance %, a Strong/Possible/Stretch/Poor label, reasons for, gaps and risks, and concrete resume tweaks. Several jobs come back ranked in a compact table. Use this whenever the user asks to score, rank, triage or compare job postings or roles, asks "what are my chances for this role", "should I apply to this", "how well do I fit this job" or "which of these jobs is best for me", pastes a job description or a careers/Greenhouse/Ashby/LinkedIn job URL next to a resume, or wants JSON fit scores for a job-search pipeline, or asks whether a role pays enough. Use it even if the user never says "score".
---

# Job Shortlist Scorer

Estimate how likely a resume is to be **shortlisted**, meaning it gets past the resume screen to a
recruiter or hiring-manager conversation, for one or more job postings. Explain why, and say how
to raise that chance.

The output has to be **consistent run to run**. That is why the work is split in two:
you rate six dimensions against fixed anchors, and `scripts/score.py` does all the
arithmetic (weights, company selectivity, gate caps, labels, ranking). Two runs over the
same inputs should give the same ratings, so cite evidence for each rating and don't
improvise new criteria.

## Inputs

1. **Resume** (required). This may be a file path (PDF, DOCX, MD or TXT), pasted text, or
   something the user pointed to earlier in the conversation. If none is given, ask for one.
   Don't guess the candidate's background. Read the whole resume once and pull out a
   *candidate profile*: current title and function (manager or IC), years of experience,
   largest team or scope, domains, languages and technologies, location, work authorization,
   and standout signals.
   Keep contact details (phone, email) out of everything you write. The Read tool reads PDFs
   directly, so `pdftotext` and `pypdf` aren't required.
2. **Job postings** (one or more). Each needs a title, company, location and description. If you
   only get a URL, fetch it. For Greenhouse, the JSON API returns the full text:
   `https://boards-api.greenhouse.io/v1/boards/<board>/jobs/<id>` (the `content` field is
   HTML-escaped HTML). For Ashby, use `https://api.ashbyhq.com/posting-api/job-board/<board>`.
   If a posting has no description, score what you have, set `"low_confidence": true`, and say so.
3. **Preferences** (optional). These can be target companies (they replace the Tier 1 list),
   preferred location, remote preference, or a total-comp floor. Unless the user says otherwise,
   the defaults in the rubric apply. They reflect four priorities: location, top-tier companies,
   roles similar to the candidate's current job, and **at least $300k total comp**.

## Workflow

1. **Read `references/rubric.md`** (and `references/comp.md` for the pay check) before the first job you score. The rubric defines the six dimensions,
   their weights, the 0–5 anchors, the hard gates, and the company tiers.
2. **For each job:**
   - List the posting's *required* qualifications, and separately its *preferred* ones.
     Mark each required item met, partial or missing against the resume, citing the
     resume evidence. That list drives `required_coverage` and most of the gaps.
   - Rate the six dimensions 0–5 using the anchors. When you are between two anchors, take the
     lower one. Recruiters skim, and an optimistic rating makes the score useless.
   - Check every hard gate (citizenship or clearance, on-site in another metro, degree,
     years-of-experience upper bound, absent core technology) and list any that fire.
   - Assign the company tier (1/2/3).
   - Estimate total comp with `references/comp.md`: map the posting to a company level and
     read levels.fyi averages, falling back to the posted base range × factor. Fill in
     `est_total_comp` and `comp_flag`. If `high` is below the floor, add gate
     `comp_below_floor`. A posted *base* range alone is never a reason to exclude.
   - Write 3–5 **reasons for**, the top **gaps and risks**, and 2–3 **resume tweaks**. Rules for
     these are in the next section.
3. **Score.** Put every job into one JSON list and run:
   ```bash
   python3 <skill-dir>/scripts/score.py jobs.json
   ```
   Keep scratch files in the session's scratchpad or temp directory, not the user's project.
   The script adds `fit_score`, `shortlist_chance`, `label`, `priority_score` and `rank`.
   Don't override its numbers. If a number looks wrong, revisit the ratings instead.
4. **Report** in the format below.

## Writing reasons, gaps and tweaks

These are the part the user acts on, so make them specific to this posting and this resume.

- **Reasons for.** Each reason pairs a requirement with evidence, e.g. "Asks for experience leading
  teams building distributed systems → 4 years managing 7 engineers on Nexus Dashboard (Kubernetes)".
  Skip generic praise.
- **Gaps and risks.** Name the missing requirement or the risk, and how a screener is likely to read it.
  Cover these kinds where they apply: missing required skill, seniority or scope mismatch (too
  junior *or* too senior), domain mismatch, location or work-authorization constraint, and
  keyword gaps an ATS would trip on. Order them by impact.
- **Resume tweaks.** Each tweak must be concrete and truthful. Rewrite or reorder what the
  candidate actually did so it uses the posting's language. Don't invent experience. A good
  tweak names the resume section and gives a draft bullet or a phrase to add, e.g. "In the
  Senior EM role, lead with the 100+ API OpenAPI migration and say 'API platform'. The posting
  uses that phrase three times." If a gap can't be closed truthfully, say so and suggest the
  cover note or recruiter message address it instead.

## Output format

### Several jobs: ranked table first

Rank by priority (shortlist chance plus the company-tier and location preferences). Show the
table, then a short section per job.

```
| # | Company | Role | Location | Chance | Fit | Label | Est. TC | Top reason | Biggest gap |
|---|---------|------|----------|--------|-----|-------|---------|------------|-------------|
| 1 | Stripe  | Engineering Manager, Network Infra | SF / Remote US | 68% | 85 | Strong | ~$600k | ... | ... |
```

Before the table, give a one-line candidate profile (current role, years, domain, location,
work authorization), so the reader can check what the scores are based on.

Leave excluded jobs (TC below the floor) out of the table. After it, list them in one line
each: "Filtered out (TC below $300k): Company — Title (est. $Xk, source)". Mark borderline
comp with "⚠" in the Est. TC cell.

Keep the table cells short, about 8 words each. Under the table, give one line on how ranking works:
"Ranked by priority = chance + top-tier bonus + location bonus; chance itself is
not inflated by preferences."

### Per-job section

```
### <rank>. <Company> — <Title> · <Label>, <chance>% (fit <fit>/100)
<location> · Tier <n> · est. TC $<low>–<high>k (<source>) · gates: <none | list>

Ratings: role <r>/5 · domain <r>/5 · required <r>/5 (<met> met, <partial> partial of <total>) · seniority <r>/5 · location <r>/5 · preferred <r>/5

**Why you'd be shortlisted**
- ...

**Gaps and risks**
- ...

**Resume tweaks for this job**
1. ...
```

A single job uses the per-job section alone, with no table.

### Machine-readable JSON

Include this when the user asks for JSON or the request comes from a program (the daily job agent
calling through the Claude API). In that case return **only** the JSON, with no prose and no code
fences, so the caller can `json.loads` it directly. The shape is the output of `scripts/score.py`:

```json
[
  {
    "rank": 1,
    "job_id": "greenhouse:stripe:1234567",
    "company": "Stripe",
    "title": "Engineering Manager, Network Infrastructure",
    "location": "San Francisco, CA",
    "url": "https://stripe.com/jobs/listing/...",
    "tier": 1,
    "ratings": {
      "role_similarity": 5,
      "domain_fit": 4,
      "required_coverage": 4,
      "seniority_scope": 4,
      "location_auth": 5,
      "preferred_signals": 3
    },
    "required_met": 6,
    "required_partial": 1,
    "required_total": 7,
    "est_total_comp": {"low": 425000, "mid": 604000, "high": 858000, "source": "levels.fyi"},
    "comp_flag": "ok",
    "excluded": false,
    "gates": [],
    "fit_score": 85,
    "shortlist_chance": 68,
    "label": "Strong",
    "priority_score": 85,
    "reasons": ["...", "..."],
    "gaps": ["...", "..."],
    "resume_tweaks": ["...", "..."],
    "low_confidence": false,
    "rubric_version": "v2"
  }
]
```

Field notes for callers:
- `shortlist_chance`: integer 0–100. `label` is one of `Strong` (≥65), `Possible` (45–64),
  `Stretch` (25–44) or `Poor` (<25).
- `fit_score`: weighted rubric total before company selectivity and gates.
- `priority_score`: the sort key. It may exceed 100 or go below 0.
- `gates`: ids from the rubric (`citizenship_or_clearance`, `sponsorship_terms`,
  `onsite_other_metro_no_relocation`, `required_degree_missing`, `years_upper_bound_exceeded`,
  `core_tech_absent`, `comp_below_floor`).
- `excluded`: true when `comp_below_floor` fired. Callers should drop these jobs. They come
  last in the output, so dropping them doesn't disturb the ranking.
- `comp_flag`: `ok`, `borderline` (mid below the floor, high at or above it), `unknown`, or
  `below_floor`. `est_total_comp` values are yearly USD.
- `job_id`: pass through whatever id the caller supplied. Otherwise use `<source>:<board>:<id>`
  when known, else null.
- A caller without a code-execution tool can send only the ratings, tier and gates, and run
  `scripts/score.py` (stdlib-only Python) locally. This guarantees identical arithmetic.

## Calibration notes

- "Shortlist chance" is a relative, calibrated estimate, not a measured probability. Say this once
  when reporting, and don't repeat it per job.
- Over-qualification is a real screen-out risk. A 20-year senior manager applying to a plain
  "Senior Software Engineer" role loses points in `seniority_scope` and `role_similarity`, and
  the gaps should say why.
- Remote roles open to the candidate's country count as in-metro for `location_auth`.
- If the description says "or equivalent experience", treat a degree requirement as met by
  experience. No gate fires.
