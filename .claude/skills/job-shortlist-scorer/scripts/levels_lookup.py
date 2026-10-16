#!/usr/bin/env python3
"""Look up average total compensation per level for a company on levels.fyi.

Usage:
    python levels_lookup.py <company-slug> [job-family-slug ...]

    python levels_lookup.py stripe
    python levels_lookup.py databricks software-engineering-manager

The company slug is the one in levels.fyi URLs, e.g. facebook for Meta and google for
Google. Job families default to software-engineering-manager and software-engineer.

The script reads the public company salary page and prints one line per level: the
level name, average TC, average base, number of data points, and the overall US
percentiles. It uses only the standard library. If levels.fyi rate-limits (an empty
reply) it retries a few times, then reports the page as unavailable instead of failing.
"""

import json
import re
import sys
import time
import urllib.request

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/128 Safari/537.36"
DEFAULT_FAMILIES = ["software-engineering-manager", "software-engineer"]


def fetch(url, tries=3):
    for attempt in range(tries):
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                body = resp.read().decode("utf-8", "replace")
            if body:
                return body
        except Exception:
            pass
        time.sleep(5 * (attempt + 1))
    return ""


def page_data(company, family):
    html = fetch(f"https://www.levels.fyi/companies/{company}/salaries/{family}")
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return None
    return json.loads(m.group(1))["props"]["pageProps"]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    company = sys.argv[1]
    families = sys.argv[2:] or DEFAULT_FAMILIES
    for family in families:
        data = page_data(company, family)
        if not data or not data.get("averages"):
            print(f"{company} / {family}: unavailable (no data or rate-limited)")
            continue
        tc = (data.get("percentiles") or {}).get("tc") or {}
        print(f"{company} / {family}  US TC p25={tc.get('p25')} p50={tc.get('p50')} p75={tc.get('p75')}")
        for row in data["averages"]:
            total = row.get("total") or 0
            base = row.get("base") or 0
            print(f"  {row.get('level', '?'):<28} avg TC ${total / 1000:,.0f}k  base ${base / 1000:,.0f}k  n={row.get('count')}")
        time.sleep(1)


if __name__ == "__main__":
    main()
