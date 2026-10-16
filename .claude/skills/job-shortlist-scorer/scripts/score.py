#!/usr/bin/env python3
"""Turn per-dimension ratings into fit, shortlist chance, label and priority.

Implements section 5 of references/rubric.md so every run does the same arithmetic.

Usage:
    python score.py ratings.json            # read from a file
    cat ratings.json | python score.py      # or from stdin

Input: a JSON list (or a single object) of jobs. Each job needs:
    "ratings": {dimension: 0-5, ...}   all six dimensions below
    "tier": 1 | 2 | 3
    "gates": [gate_id, ...]            optional, ids from GATE_CAPS
Any other fields (title, company, reasons, gaps, ...) are passed through untouched.

Output: the same jobs, with fit_score, shortlist_chance, label, priority_score and
excluded added, and a rank field. Jobs that are not excluded come first, sorted by
priority_score and then shortlist_chance, both descending. Jobs excluded by the
compensation floor (gate comp_below_floor) come last.
"""

import json
import sys

WEIGHTS = {
    "role_similarity": 20,
    "domain_fit": 20,
    "required_coverage": 20,
    "seniority_scope": 15,
    "location_auth": 15,
    "preferred_signals": 10,
}

SELECTIVITY = {1: 0.80, 2: 0.88, 3: 0.95}
TIER_BONUS = {1: 12, 2: 6, 3: 0}

GATE_CAPS = {
    "citizenship_or_clearance": 3,
    "sponsorship_terms": 3,
    "onsite_other_metro_no_relocation": 20,
    "required_degree_missing": 25,
    "years_upper_bound_exceeded": 30,
    "core_tech_absent": 40,
}

# Gates that remove a job from the ranking rather than capping its chance.
EXCLUDING_GATES = {"comp_below_floor"}


def label_for(chance):
    if chance >= 65:
        return "Strong"
    if chance >= 45:
        return "Possible"
    if chance >= 25:
        return "Stretch"
    return "Poor"


def location_bonus(rating):
    if rating >= 5:
        return 5
    if rating >= 3:
        return 0
    return -10


def score_job(job):
    ratings = job["ratings"]
    missing = set(WEIGHTS) - set(ratings)
    if missing:
        raise ValueError(f"{job.get('company', '?')} / {job.get('title', '?')}: missing ratings {sorted(missing)}")
    for dim, value in ratings.items():
        if dim in WEIGHTS and not (isinstance(value, int) and 0 <= value <= 5):
            raise ValueError(f"rating {dim}={value!r} must be an integer 0-5")

    tier = int(job.get("tier", 3))
    if tier not in SELECTIVITY:
        raise ValueError(f"tier must be 1, 2 or 3, got {tier}")

    fit = sum(ratings[d] / 5 * w for d, w in WEIGHTS.items())
    chance = round(fit * SELECTIVITY[tier])

    gates = job.get("gates") or []
    known = set(GATE_CAPS) | EXCLUDING_GATES
    unknown = [g for g in gates if g not in known]
    if unknown:
        raise ValueError(f"unknown gates {unknown}; known: {sorted(known)}")
    for gate in gates:
        if gate in GATE_CAPS:
            chance = min(chance, GATE_CAPS[gate])

    priority = chance + TIER_BONUS[tier] + location_bonus(ratings["location_auth"])

    return {
        **job,
        "fit_score": round(fit),
        "shortlist_chance": chance,
        "label": label_for(chance),
        "priority_score": priority,
        "excluded": any(g in EXCLUDING_GATES for g in gates),
    }


def main():
    raw = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    data = json.loads(raw)
    jobs = data if isinstance(data, list) else [data]
    scored = sorted(
        (score_job(j) for j in jobs),
        key=lambda j: (not j["excluded"], j["priority_score"], j["shortlist_chance"]),
        reverse=True,
    )
    for i, job in enumerate(scored, 1):
        job["rank"] = i
    json.dump(scored, sys.stdout, indent=2)
    print()


if __name__ == "__main__":
    main()
