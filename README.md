# Job search agent

Every day at 8:00 AM Pacific, a GitHub Actions job:

1. Pulls new postings from **JSearch** (Google Jobs: covers FAANG career sites), **Adzuna**, and the public **Greenhouse / Ashby** boards of target companies.
2. Keeps Engineering Manager-track and Senior/Staff/Principal/TL roles in the SF Bay Area or remote US, and skips roles requiring US citizenship or a security clearance.
3. Scores each against your resume (keyword overlap for now; see `job_agent/scoring.py`).
4. Appends the top 5 **new** matches per track to your Google Sheet, on two tabs: **Engineering Manager** and **Senior Engineer & TL**.

The agent only adds rows. It never edits existing ones, so your **Status**, **Applied date** and **Notes** are safe. Change titles, companies, locations or limits in [`config.yaml`](config.yaml).

## One-time setup

### 1. Google Sheet + service account (~10 min)
1. Create a Google Sheet. Copy its ID from the URL: `docs.google.com/spreadsheets/d/<SHEET_ID>/edit`.
2. In [Google Cloud Console](https://console.cloud.google.com/): create a project, then enable the **Google Sheets API**.
3. **IAM & Admin → Service accounts → Create service account** (no roles needed). Open it → **Keys → Add key → JSON**, and download the file.
4. In your sheet, click **Share** and add the service account's email (`...@...iam.gserviceaccount.com`) as **Editor**.

The tabs and header row are created automatically on the first run.

### 2. Job search API keys (free tiers)
- **JSearch:** sign up at [rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) and subscribe to the free Basic plan. Copy your `X-RapidAPI-Key`.
- **Adzuna:** register at [developer.adzuna.com](https://developer.adzuna.com/) for an App ID and App Key.

Either source is optional. Without keys, the agent still reads the company boards.

### 3. GitHub secrets
Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Value |
|---|---|
| `SHEET_ID` | the ID from step 1.1 |
| `GOOGLE_SERVICE_ACCOUNT_JSON` | the full contents of the downloaded JSON key |
| `RESUME_TEXT` | your resume as plain text (copy-paste from the PDF) |
| `JSEARCH_API_KEY` | RapidAPI key |
| `ADZUNA_APP_ID` / `ADZUNA_APP_KEY` | Adzuna credentials |

Your resume and keys live only in secrets, never in the repo.

### 4. Turn it on
The schedule only runs from the repo's **default branch** (`main`), so merge this branch first. Then **Actions → Daily job search → Run workflow** to test it straight away.

## Run locally

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt pytest
cp ~/path/to/resume.pdf resume.pdf          # git-ignored
.venv/bin/python -m job_agent.main --dry-run  # print matches, no sheet writes
.venv/bin/python -m pytest -q
```

To write to the sheet locally, export the same variables as the secrets and run with `--force`.

## Notes
- GitHub cron is UTC-only. The workflow fires at 15:00 and 16:00 UTC, and the script keeps whichever one is 8 AM Pacific. GitHub can delay scheduled runs by a few minutes.
- JSearch's free plan allows ~200 requests/month. The agent uses 4 a day (one per search query in `config.yaml`).
