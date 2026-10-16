# Compensation reference: estimating total comp (TC)

Use this to fill `est_total_comp` and to apply the floor in rubric section 4b.
TC means base + target bonus + **one year** of equity vesting.

## How to estimate (in order of preference)

1. **Company is in the table below.** Map the posting to a level using the level-mapping
   notes, then take that level's average as `mid`. Set `low` to the average of the level below
   and `high` to the average of the level above. When the posting is ambiguous (e.g. "Engineering
   Manager" with no level), use the two most likely levels as `low` and `high`. If there is no
   level below, set `low` = 0.75 × mid. If there is no level above, set `high` = 1.3 × mid.
   If the company has levels.fyi data for the *other* ladder only (IC data but no EM data, or
   the reverse), map across using the parallel ladders in rubric `seniority_scope`
   (Senior EM ≈ Staff, EM ≈ Senior). Then set `high` to the larger of that figure and
   base × factor (rule 3). Use `comp_flag: "borderline"` whenever the two sources disagree
   about the floor.
2. **Company is not in the table, and you have web access.** Run
   `python3 scripts/levels_lookup.py <levels-fyi-slug>`, or open
   `https://www.levels.fyi/companies/<slug>/salaries/software-engineering-manager` (or
   `/software-engineer`), and apply rule 1. Cite "levels.fyi (fetched <date>)".
3. **No levels.fyi data, but the posting lists a base range** (common in CA, WA, NY and CO).
   Multiply the base midpoint by the company-type factor below to get `mid`, multiply the top
   of the base range by the factor to get `high`, and multiply the bottom of the range by it to
   get `low`.

   | Company type | TC ÷ base factor |
   |---|---|
   | Public big tech or Tier 1 | 1.8 |
   | Public tech, Tier 2 | 1.5 |
   | Late-stage private (Series D+, valued privately) | 1.35 |
   | Early-stage startup (Series A–C) | 1.15 |
   | Non-tech enterprise, government contractor | 1.15 |
4. **Nothing to go on.** Set `comp_flag: "unknown"`, keep the job, and say TC could not be
   estimated.

Set `source` to `"levels.fyi"`, `"posting base × factor"` or `"none"`.

## Reference table (levels.fyi, US-wide averages, fetched 2026-10-16)

Bay Area offers usually run 5–15 % above these US-wide averages. Data points are thin at some
levels (n < 5); treat those as rough. Refresh with `scripts/levels_lookup.py` when this table
is more than about 6 months old.

### Engineering Manager track (avg TC, $k)

| Company | First-line EM | Senior EM / EM of EMs | Director |
|---|---|---|---|
| Google | L5 382 · **L6 641** | L7 880 | L8 1,364 |
| Meta | M0 563 · **M1 730** | M2 1,330 | D1 1,769 |
| Apple | M1 410 · **M2 567** | M3 772 | D1 1,451 |
| Amazon | L5 SDM 312 · **L6 SDM 429** | Sr SDM (L7) 631 | Director 1,213 |
| Netflix | **Manager 648** | Sr Manager 788 | Director 1,214 |
| Microsoft | 64: 279 · **Principal EM (65) 343** | 66: 413 | Sr Director 531 · Partner 803 |
| NVIDIA | M2 359 · **M3 509** | M4 606 | M5 714 |
| LinkedIn | **Manager 481** | Sr Manager 751 | Director 796 |
| Uber | EM1 415 · **EM2 645** | Sr EM 837 | Director 1,451 |
| Airbnb | **M1 640** | M2 784 | M3 1,230 |
| Stripe | M0 425 · **M1 604** | M2 858 | M3 1,504 |
| Databricks | **M2 440** | M3 941 | M4 1,151 |
| Snowflake | **M3 656** | M4 766 | M6 867 |
| Salesforce | Manager 265 · **Sr Manager 330** | Director 412 | Sr Director 610 |
| Cloudflare | L3 182 · **L4 245** (n = 5, thin) | — | — |
| Pinterest | M15 422 · **M16 598** | M17 816 | M18 978 |
| Cisco (current employer, for reference) | Grade 11 283 · **Grade 12 424** | Grade 13 557 | Grade 14 855 |

The **bold** level is where a 20-year Senior EM would most likely land.

### Senior / Staff / Principal IC track (avg TC, $k)

| Company | Senior | Staff | Senior Staff / Principal |
|---|---|---|---|
| Google | L5 457 | L6 665 | L7 954 |
| Meta | E5 456 | E6 771 | E7 1,773 |
| Apple | ICT4 362 | ICT5 582 | ICT6 766 |
| Amazon | SDE III 387 | Principal 602 | Sr Principal 1,155 |
| Netflix | L5 511 | L6 741 | L7 1,141 |
| Microsoft | Senior 232–271 | Principal 335–393 | 67: 567 · Partner 812 |
| NVIDIA | IC4 380 | IC5 462 | IC6 653 |
| LinkedIn | Senior 306 | Staff 480 | Sr Staff 878 |
| Uber | Senior 439 | Staff 614 | Sr Staff 803 |
| Airbnb | G9 475 | G10 633 | G11 1,140 |
| Stripe | L3 472 | L4 621 | L5 943 |
| Databricks | L4 423 | L5 588 | L6 1,285 |
| Snowflake | IC2 361 | IC3 568 | IC4 820 |
| Salesforce | Senior MTS 264 · Lead MTS 319 | Principal MTS 556 | Architect 552 · Principal Architect 1,124 |
| Cloudflare | L4 292 | L5 347 | — |
| Pinterest | IC14 319 | IC15 490 | IC16 735 |

### What this means for a $300k floor

- Nearly every first-line EM, Staff and Principal role at Tier 1 companies clears $300k.
- **Watch these:** Salesforce Manager (≈ 265), Microsoft level-64 manager (≈ 279) and senior IC
  roles, Cloudflare EM (≈ 182–245, thin data), Cloudflare Staff (≈ 347, borderline), and
  Salesforce Lead MTS (≈ 319). Here the level decides it. Use `borderline` unless the posting
  clearly sits at the low level.
- "Senior Software Engineer" (below Staff) is often near the floor outside the top payers.
  Check the level before ranking it.

## Level-mapping hints

- Titles like "Engineering Manager II", "Senior Engineering Manager" or "Manager of Managers",
  or a posting asking for 8+ years of management experience, point to the middle column.
- Posted base ranges help place the level. At Tier 1, an EM base top of $250k+ usually means
  first-line EM at a senior level, and $300k+ usually means Senior EM or Director.
- Staff = "Staff", "Senior Staff", or roles asking 10–12+ years. Principal = "Principal",
  "Senior Staff+", or roles asking 15+ years with org-wide scope.
