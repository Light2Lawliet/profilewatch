# ProfileWatch

A demo tool that monitors small-business online reputation the way an SRE
monitors a production service — health score, SLA thresholds, incident
detection, and AI-powered auto-remediation (open-weight models via Groq) — instead of the usual
spreadsheet-and-vibes approach to "reputation management."

## The problem

Local-business customers of an XMP (experience management platform) product
sign up expecting their reviews, listings, and directory presence to be
handled for them. In practice, staying on top of it means:

- Checking five-plus review sites for new feedback
- Noticing which reviews are negative *and* unanswered before they've been
  sitting for days
- Periodically comparing name/address/phone across every directory listing
  by hand, because Google, Yelp, and Bing all drift out of sync on their own
- Doing all of this every week, indefinitely, with no alerting

Most owners don't have the time, so they either let it slide (reputation
quietly erodes) or they churn from the platform because "checking the
dashboard" became one more chore nobody had time for. **Cost to manage** is
consistently the top churn driver for this category of product — not price,
not features.

## What ProfileWatch does

ProfileWatch treats each customer's online reputation as a monitored
service — and goes deliberately further than a single aggregate ranking
score (like experience.com's own SRS): it's a decomposed, trend-aware,
explainable assessment, not another single number.

1. **Computes a 0–100 health score** per account from **six** blended
   signals, each shown as its own scored component rather than buried in one
   opaque number: response speed, response *quality* (whether a reply
   actually addresses the complaint, not just whether one exists), rating
   *level*, rating *velocity* (an older-half vs. recent-half trend, so a
   declining business is caught before a flat average would show it),
   recurring complaint *themes* pulled from review text (billing, equipment,
   attitude, wait time), and NAP (name/address/phone) consistency —
   severity- and directory-authority-weighted, so a transposed phone digit
   is treated as more serious than a missing suite number.
2. **Detects incidents** automatically — a health score below the SLA
   threshold, a 1–2 star review unanswered for more than 24 hours, a reply
   that exists but doesn't actually address the complaint, a rating trend
   declining sharply enough to catch before the blended score reflects it,
   or listings that disagree with each other on name/address/phone.
3. **Auto-remediates with AI**: for every open incident, asks the model for
   a plain-English root-cause explanation, a ready-to-post on-brand reply to
   the most urgent unanswered negative review, and a 2–4 step action plan
   (each step with why it works and a realistic timeframe) — returned as
   structured JSON via the Messages API's `output_config.format`, so it's
   reliably parseable, never a wall of unstructured text to eyeball.
4. **Prescribes a success plan for any account**, not just ones on fire:
   the model ranks the highest-leverage priorities — whether that's fixing an
   open incident or just going from "good" to "excellent" — with a concrete
   action, expected impact, and timeframe per priority, plus a concrete
   definition of what success looks like a month out.
5. **Writes a weekly digest**: one more AI call takes every account's
   current state and incidents and produces a plain-English paragraph plus
   one top priority per account, suitable for pasting into an email to an
   owner who has zero time to open a dashboard.
6. **Flags churn risk**: if an account's health score has declined for two
   or more consecutive weeks (simulated here with historical fixture data)
   — with magnitude and an independently-declining rating-velocity signal
   corroborating it, not just a bare streak — it's flagged, and the model drafts
   a one-paragraph "save play" a Customer Success Manager can act on that
   week — naming the likely disengagement driver and a specific, non-generic
   outreach.

The dashboard itself is built for triage, not just display: accounts sort
by triage priority (open-incident severity + churn risk) by default, not
raw score; every card shows a trend sparkline and a segmented score
breakdown bar; incidents expand inline to show the actual flagged review or
the specific listing fields that disagree — no AI call required just to
see what's wrong; and status/type filters narrow the grid to what actually
needs attention across all 23 accounts.

## How it maps to SRE concepts

| SRE concept | Production service | ProfileWatch |
|---|---|---|
| **Health score / SLI** | Latency, error rate, uptime % | Response-time rate (24h), rating trend, NAP consistency, blended 0–100 |
| **SLA / threshold** | "99.9% uptime" | Health score must stay ≥ 60 (configurable) |
| **Incident** | Service degradation, page fires | Health score breach, unanswered negative review, listing drift |
| **Root-cause analysis** | On-call engineer reads logs/traces | The model reads the account's reviews/listings and explains what's actually wrong |
| **Auto-remediation** | Auto-restart, auto-scale, runbook execution | The model drafts the review reply and names the concrete fix action |
| **On-call digest / status page** | Weekly incident review, status page summary | Weekly plain-English digest across every account |
| **Trend-based alerting** | "Error rate rising for 2+ intervals → page" | "Health score falling for 2+ weeks → churn-risk flag + CSM save play" |

The mapping isn't just cosmetic — it's the same underlying discipline:
*define what "healthy" means numerically, alert on deviation before it
becomes a crisis, and hand whoever's on call something they can act on
immediately instead of raw data.*

## Time-savings impact (estimated)

Assuming an owner currently spends roughly this much time per week per
account doing what ProfileWatch automates:

| Task | Manual time/week | With ProfileWatch |
|---|---|---|
| Checking review sites for new/negative reviews | ~15 min | Health score + incident badges, glanced in seconds |
| Drafting a reply to a negative review | ~10 min (when it happens) | AI drafts it; owner reviews and posts |
| Cross-checking NAP across directories | ~10 min (when it happens) | Auto-detected, flagged instantly |
| Composing a status update / self-check-in | ~10 min | One-click weekly digest, ready to read or forward |

That's roughly **35–45 minutes saved per account per week** — for a platform
managing hundreds or thousands of small-business accounts, that's the
difference between reputation management being a checked-off feature versus
a recurring task the owner (correctly) resents and eventually cancels over.
The churn-risk flag adds a second lever: it turns "we lost the account" into
"CSM had a two-week head start and a drafted save play."

## Stack

- **Backend**: Python + FastAPI (`src/main.py`)
- **Frontend**: static HTML/CSS/JS (`src/profilewatch.html`,
  `src/profilewatch.css`), no framework, no build step
- **Data**: seeded JSON fixture (`src/data/accounts.json`) — 23 accounts (a
  mix of hand-built fixtures and real experience.com-sourced accounts), each
  with reviews (rating, text, date, responded, response text) and directory
  listings, some with intentionally inconsistent NAP data to simulate drift
- **AI**: open-weight `openai/gpt-oss-120b` served by Groq's free tier,
  using strict JSON-schema `response_format` for reliably parseable
  structured output on every AI call

All source (including `requirements.txt`) lives under `src/`; `README.md`,
`CLAUDE.md`, `PROMPT.md`, and `.env`/`.env.example` stay at the repo root.

## Running it

```bash
pip install -r src/requirements.txt
cp .env.example .env   # then edit .env and set GROQ_API_KEY
python src/main.py
```

Run these from the repo root — `.env` is resolved relative to it, not to
`src/`.

`.env` is loaded automatically (via `python-dotenv`) and is gitignored, so it's the
place to update the key going forward — edit `.env`, restart the server. No `.env`
file? Exporting `GROQ_API_KEY` in the shell before running still works exactly
as before.

Then open **http://localhost:8000/**.

- The dashboard, health scores, and incident detection all work without an
  API key.
- "Explain & draft response", "Generate save play", and "Generate Weekly
  Digest" all call the AI model and require `GROQ_API_KEY`. If it's missing,
  the app shows a clear banner and each affected call returns a `503` with
  an explanatory message instead of failing silently or crashing.

### Configuration (optional env vars)

All of these can go in `.env` (see `.env.example`) or be exported in the shell — `.env` wins for local defaults, real env vars still override it.

| Variable | Default | Purpose |
|---|---|---|
| `GROQ_API_KEY` | — | Required for all AI-powered features (free key at console.groq.com) |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Model used for every AI call; must support Groq's strict JSON-schema mode |
| `PROFILEWATCH_HEALTH_THRESHOLD` | `60` | Health score SLA threshold that triggers a `low_health_score` incident |
| `PROFILEWATCH_ANCHOR_DATE` | `2026-08-14` | The "as of" date used for age/recency calculations, so the fixture's dates stay meaningful regardless of when you run the demo |
| `PROFILEWATCH_RESPONSE_RATE_OPPORTUNITY_THRESHOLD` | `50` | Below this 24h-response-rate %, an account gets a soft "low response rate" improvement opportunity even if it's not a hard incident |
| `PROFILEWATCH_SLOW_RESPONSE_DAYS_THRESHOLD` | `3` | Average reply delay (days) above which an account gets a "slow response time" improvement opportunity |
| `PROFILEWATCH_RESPONSE_QUALITY_THRESHOLD` | `50` | Below this response-quality score, a replied-to 1–2★ review triggers a `low_quality_response` incident (acked, didn't fix anything) |
| `PROFILEWATCH_VELOCITY_INCIDENT_THRESHOLD` | `30` | Rating-velocity score below this (with a declining trend) triggers a `rating_velocity_decline` incident |
| `PROFILEWATCH_VELOCITY_OPPORTUNITY_THRESHOLD` | `40` | Softer band above the incident threshold that surfaces a `mild_rating_decline` improvement opportunity instead |

## Deploying (Netlify UI + Render API)

The UI (`netlify.toml`) and API (`render.yaml`) deploy separately from the same GitHub repo.

1. Push the repo to GitHub (check `git status` doesn't list `.env`).
2. **Render** → New → Blueprint → select the repo. Set `GROQ_API_KEY` and `PROFILEWATCH_ACCESS_KEY` (any long random string).
3. **Netlify** → Import the repo. It publishes only `index.html` + `profilewatch.css` into `dist/`.
4. Back on Render, set `PROFILEWATCH_ALLOWED_ORIGINS=https://<your-site>.netlify.app` and redeploy.

The UI calls `https://profilewatch-api.onrender.com` when it isn't on localhost. If your Render service has a different name, update `API_BASE` in `src/profilewatch.html`. When `PROFILEWATCH_ACCESS_KEY` is set, the UI asks for the key once, on the first AI button click, and stores it in the browser. AI calls are also rate-limited per IP (`PROFILEWATCH_AI_RATE_LIMIT_PER_HOUR`, default 30). Render's free tier sleeps when idle, so the first load after a pause can take about 50 seconds.

## API

| Endpoint | Method | Description |
|---|---|---|
| `/api/status` | GET | Whether the AI key is configured, current model, anchor date, health-score formula version |
| `/api/accounts` | GET | All accounts with computed health score (+ per-signal `score_components` breakdown), incidents, opportunities, churn risk — zero AI calls |
| `/api/accounts/{id}` | GET | Single account detail |
| `/api/accounts/{id}/explain` | POST | AI: root cause, suggested review reply, and a 2–4 step `action_plan` (400 if no open incidents) |
| `/api/accounts/{id}/save-play` | POST | AI: CSM save play (400 if not flagged churn-risk) |
| `/api/accounts/{id}/success-plan` | POST | AI: ranked, prescriptive priorities for *any* account — no incident/churn-risk gate |
| `/api/digest` | POST | AI: one paragraph + one top priority per account for a weekly owner email |

Note: `/explain`'s `action_plan` (an ordered array of `{step, action, why_it_works, timeframe}`) replaced the old single-string `fix_action` field — a breaking change for anything consuming the old shape.
