# Shortlist Rubric (v2)

The rubric turns a resume and a job posting into the same numbers every run. Judgment
goes into one place, rating each dimension 0–5 against the anchors below. Everything
after that is arithmetic, done by `scripts/score.py`.

## Contents
1. Dimensions and weights
2. Rating anchors per dimension
3. Hard gates and caps
4. Company tiers and selectivity (4b: compensation floor)
5. From fit score to shortlist chance, label and priority
6. Worked example

---

## 1. Dimensions and weights

| Key | Dimension | Weight | What it asks |
|---|---|---|---|
| `role_similarity` | Role similarity to current profile | 20 | Would the candidate do roughly the same *job* they do now: same function (people manager vs. IC), same kind of work? |
| `domain_fit` | Domain & tech-stack fit | 20 | Does the product area and stack (e.g. networking, infra, distributed systems, Kubernetes, C/C++/Python) match the resume? |
| `required_coverage` | Required-qualifications coverage | 20 | What fraction of the posting's *required* bullets the resume clearly demonstrates. |
| `seniority_scope` | Seniority, years & scope | 15 | Level, years of experience, team/org size and scope compared with the resume. |
| `location_auth` | Location & work authorization | 15 | Can the candidate work where the job is, under the job's authorization terms? |
| `preferred_signals` | Preferred quals & differentiators | 10 | Nice-to-haves covered plus standout signals (patents, awards, scale, promotions). |

Weights sum to 100. Fit score = Σ (rating / 5 × weight), giving 0–100.

The rubric carries the user's stated priorities: **location** (`location_auth` and the
location gates), **top-tier companies** (company tier, section 4), **a job like the
current one** (`role_similarity` is weighted as heavily as any dimension, and
`domain_fit` backs it up) and **a total-comp floor** (section 4b).

---

## 2. Rating anchors

Use whole numbers 0–5. Pick the highest anchor the evidence fully supports. When you
are between two, take the lower one: a recruiter reading quickly gives no benefit of
the doubt. Cite the resume line or posting line behind each rating.

### role_similarity (20)
- **5** Same function and same kind of work. A people manager of engineers moving to an engineering-manager role on infrastructure or platform software; a TL moving to a Staff/TL role on similar systems.
- **4** Same function with a modest shift: the same management role in an adjacent product area, or Staff/Principal IC for someone with a TL history.
- **3** Same family with a real change: manager to Director/Head (bigger scope), manager to hands-on Staff IC, or platform work to product/application engineering.
- **2** Function mostly changes: a manager moving to a heavily hands-on Senior IC coding role, or into TPM-like or solutions work.
- **1** Different function that still shares some skills.
- **0** Unrelated function.

### domain_fit (20)
- **5** Core domain match: networking, data-center infrastructure, network or observability software, distributed systems on Kubernetes, in the resume's own languages.
- **4** Adjacent infrastructure: cloud infrastructure, compute/storage platforms, SRE or reliability, developer platforms, security infrastructure with a networking angle.
- **3** General backend or distributed systems in a different product domain (payments, data platforms, ads infrastructure).
- **2** Domain is mostly new, but the stack transfers (e.g. ML infrastructure, databases internals).
- **1** Different domain and stack (frontend, mobile, consumer product, ML research).
- **0** Non-software or hardware design.

### required_coverage (20)
List every *required* qualification in the posting and mark each one met, partial or missing.
Coverage = (met + 0.5 × partial) / total.
- **5** ≥ 90 %, **4** 75–89 %, **3** 60–74 %, **2** 40–59 %, **1** 20–39 %, **0** < 20 %.

A requirement counts as met only when the resume shows it (a named skill, technology or
responsibility, or an obvious equivalent). An inference does not count.

What goes into the list:
- **Include** concrete, checkable requirements: years, degree, languages, technologies,
  domains, team or scope size, specific responsibilities ("has managed managers", "led hiring").
- **Exclude** pure soft-skill or values bullets ("excellent communicator", "thrives in
  ambiguity", "creates psychological safety"). Resumes can't prove them and screeners don't
  screen on them, so counting them only penalizes postings with long values sections.
- An item that the posting marks "preferred", "nice to have" or "bonus" belongs in
  `preferred_signals`, even when it sits inside the "requirements" list. If the posting has
  only *one* qualifications list, whatever its heading ("Desirable skills", "What we look
  for"), treat that list as required.
- Compound items: "experience with X, Y and Z" counts as one item, met if the resume shows most
  of it and partial if it shows some. Split it only when the posting itself lists them as separate
  bullets.
- Record the counts as `required_met`, `required_partial` and `required_total`.

### seniority_scope (15)
Compare the posting's level, years and scope with the resume. This dimension measures
*level* only. A change of function, such as people manager to IC, is scored in
`role_similarity`, so don't count it twice. Treat these as parallel ladders when counting
notches: Senior Engineer ≈ Engineering Manager, Staff ≈ Senior EM, Principal ≈ Director,
Distinguished ≈ VP.
- **5** Level and scope match: the years asked for are met, and team or org size is comparable (e.g. a senior manager with a team of about 7 against a role managing 6–12).
- **4** One notch off in either direction, still credible (e.g. a team of 7 against "managers of managers preferred").
- **3** Two notches off, or a clear scope gap such as Director over several teams when the candidate has managed one team.
- **2** Large level gap (VP/Head of a large org), or a clear down-level that recruiters may read as overqualified.
- **1** Very large mismatch.
- **0** Entry-level or new-grad role.

### location_auth (15)
Rate the best option the posting offers this candidate. If any of the listed locations is
in the candidate's metro, rate it as an in-metro job. Other cities on the list don't lower
the rating. In-office expectations (hybrid, 3 days a week, 50 % in office) are normal for
an in-metro job and also don't lower it.
- **5** One listed location is in the candidate's metro (on-site, hybrid or remote), or the job is remote within the candidate's country. The candidate already has work authorization, so no sponsorship is needed.
- **4** Nearest office is in a neighbouring metro within commuting range, or the posting is "remote" but asks for regular travel to an office outside the metro.
- **3** Remote with tight constraints the candidate may not meet (a timezone or state list that is unclear for them).
- **2** On-site or hybrid only in other metros, and the posting mentions relocation.
- **1** On-site or hybrid only in other metros, with no relocation mentioned.
- **0** Hard blocker (see gates).

### preferred_signals (10)
- **5** Covers most nice-to-haves and adds distinct differentiators: patents, awards, record of promotions, large-scale production systems, hiring and mentoring results.
- **3** Covers some nice-to-haves, or has strong differentiators *relevant to this role* but few of the nice-to-haves. Generic awards count as relevant for management roles. Domain-specific patents count only if the domain matches.
- **1** Few nice-to-haves and nothing standout for this role.
- (2 and 4 are in-between ratings.)

---

## 3. Hard gates and caps

Apply these after computing the fit score. They model screens that end the process no
matter how good the fit is.

| Condition | Effect |
|---|---|
| Requires US citizenship, security clearance or ITAR "US person" status that the candidate lacks | chance capped at 3, label Poor |
| Requires sponsorship terms the candidate cannot meet (rare when the candidate needs no sponsorship) | chance capped at 3 |
| On-site or hybrid only in other metros, with no relocation or remote option | chance capped at 20 |
| Requires a degree or certification the candidate lacks, listed as *must have* (e.g. "PhD required") | chance capped at 25 |
| Years-of-experience range has a hard upper bound the candidate clearly exceeds (e.g. "3–5 years") | chance capped at 30 |
| Requires a language or technology central to the job that is entirely absent from the resume (e.g. "expert in Go", and Go never appears) | chance capped at 40 |
| Estimated total compensation is clearly below the candidate's floor (section 4b) | **excluded**: kept in the JSON with `excluded: true`, left out of the ranked table |

Record every gate that fires in the `gates` list of the output.

Export-control language ("may require an export license", deemed-export rules) is **not** a
gate for a candidate with valid work authorization. The employer handles the license. List it
as a risk only.

**When `core_tech_absent` fires.** It fires only when the technology is named as a *must*
(required list, "expert in X", "deep experience with X") **and** it is what the team builds
or works in every day. It does not fire for a technology that appears only as one example
in a broader list ("distributed systems, e.g. Spark, Kafka, or similar") or only in the
team description. Those cases lower `domain_fit` and `required_coverage` instead.

---

## 4. Company tiers and selectivity

Selectivity models how competitive the applicant pool is. Top-tier companies receive many
more qualified applicants, so the same fit gives a lower shortlist chance there. Company
tier also raises **priority**, because the user prefers top-tier companies.

| Tier | Default membership | Selectivity multiplier | Priority bonus |
|---|---|---|---|
| 1 | Google, Meta, Apple, Amazon/AWS, Netflix, Microsoft, NVIDIA, LinkedIn, Uber, Airbnb, Stripe, Databricks, Snowflake, Salesforce, Cloudflare, Pinterest, OpenAI, Anthropic | 0.80 | +12 |
| 2 | Other well-known public or late-stage tech companies (e.g. Arista, Juniper/HPE, Palo Alto Networks, ServiceNow, Workday, Atlassian, Datadog, Confluent, Rubrik, Okta, Coinbase, DoorDash, Roblox, Intuit, Adobe, VMware/Broadcom) | 0.88 | +6 |
| 3 | Everyone else (startups, smaller or less-known firms) | 0.95 | 0 |

If the user gives their own target-company list, it replaces the Tier 1 list. Put a
company you are unsure about in Tier 2 and say so.

## 4b. Compensation floor

The user only wants roles whose **total compensation** (base + bonus + yearly equity) is
at least their floor. The default floor is **$300,000 TC**. A floor the user states
replaces it.

Estimate TC for each job as a low/mid/high range, using `references/comp.md` (levels.fyi
data per company and level, plus how to estimate when there's none). Then:

| Estimate | Result |
|---|---|
| `high` < floor (even an optimistic offer is below it) | gate `comp_below_floor`: job excluded |
| `mid` < floor ≤ `high` | not excluded; set `comp_flag: "borderline"` and list it as a risk |
| `mid` ≥ floor | `comp_flag: "ok"` |
| no basis for an estimate | `comp_flag: "unknown"`; keep the job and say so |

A posted *base* range is not TC. Bay Area tech postings list base only, and equity often
equals or exceeds base at Tier 1 and Tier 2 companies. Never exclude a job only because its
posted base range is below the floor.

---

## 5. Fit score → chance → label → priority

```
fit        = Σ rating_d / 5 × weight_d                      (0–100)
chance     = round(fit × selectivity), then apply any gate caps
label      = Strong   if chance ≥ 65
             Possible if 45 ≤ chance < 65
             Stretch  if 25 ≤ chance < 45
             Poor     if chance < 25
priority   = chance + tier bonus + location bonus           (used for ranking)
location bonus = +5 if location_auth = 5, 0 if 3–4, −10 if ≤ 2
```

Rank multiple jobs by **priority** (highest first), breaking ties by chance. Jobs excluded
by the compensation floor go after every other job, whatever their score. Priority puts
the user's preferences (top-tier companies, a workable location) on top of an honest
shortlist chance. Chance is never inflated to reflect what the user wants.

"Shortlist chance" is a calibrated relative estimate of getting past the resume screen to
a recruiter or hiring-manager conversation. It is not a measured probability. Its value is
that it compares jobs consistently against each other.

`scripts/score.py` implements this section exactly. Use it instead of doing the arithmetic by
hand, so that runs are identical.

---

## 6. Worked example

Ratings: role_similarity 5, domain_fit 4, required_coverage 4, seniority_scope 4, location_auth 5,
preferred_signals 3. Company is Tier 1. No gates fire.

```
fit      = 20 + 16 + 16 + 12 + 15 + 6 = 85
chance   = round(85 × 0.80) = 68                → Strong
priority = 68 + 12 + 5 = 85
```
