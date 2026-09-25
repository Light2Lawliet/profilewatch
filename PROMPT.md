## Prompt 1 — foundation

Build "ProfileWatch" — an SRE-style reputation monitor for small-business
profiles on experience.com, going beyond a single SRS-style score.

Tech stack: Python 3 + FastAPI, Anthropic SDK, python-dotenv, Uvicorn.
Static HTML/CSS/JS frontend — no framework, no build step. Environment
(.env): ANTHROPIC_API_KEY, ANTHROPIC_MODEL (default claude-sonnet-5),
PROFILEWATCH_HEALTH_THRESHOLD, PROFILEWATCH_ANCHOR_DATE.

File layout — keep all source under src/, keep docs at the repo root:
```
README.md
CLAUDE.md
PROMPT.md
.env.example
src/
  main.py
  profilewatch.html
  profilewatch.css
  requirements.txt
  data/
    accounts.json
```
`main.py` loads `.env` from the repo root (its parent directory), not from
next to itself. Also create a `.gitignore` covering `.env`, `.venv/`,
`__pycache__/`, `*.pyc` before the first commit.

Everything lives in that one `main.py` — no `src/app/` package, no
`models.py`/`scoring.py`/`config.py` split, and no `tests/` directory.
This is a short demo build; a single file is correct here.

First thing, before writing any code: `cp .env.example .env` and paste in
a real `ANTHROPIC_API_KEY`.

Before writing code, create a CLAUDE.md at the repo root with these working
rules and follow them for the rest of the session: (1) state assumptions
rather than silently picking one when something's ambiguous, (2) minimum
code that solves what's asked, no speculative flexibility, (3) touch only
what a step actually requires, (4) define a verification check for every
step and run it before calling that step done.

For now, build the data model and the core scoring engine only — no Claude
calls, no frontend yet:

- Seed ~30 small-business accounts (reviews, directory listings, 4-week
  health history), most of them built from real reviews and listing
  details pulled from experience.com business-profile pages (and other
  review platforms where useful) — not invented from scratch. Re-date
  whatever you fetch to fall within the demo's fixed anchor window rather
  than keeping the real fetch-time dates. Hand-build just a handful of
  accounts to guarantee these specific edge cases, since real businesses
  won't reliably have them on demand: a NAP mismatch, a churn decline, a
  recurring complaint theme.
- Cap it at 4-8 reviews per account, not more — this is a triage demo, and
  an account showing a wall of a dozen-plus incidents defeats the point of
  triage. Every review's text must be genuinely distinct — don't reuse the
  same sentence verbatim across reviews, even on different accounts, and
  strip any fetch artifacts (annotations, truncation markers, name-only
  entries) rather than keep them. Most accounts should have a normal,
  varied response rate; reserve a literal 0%-response account for the one
  or two edge cases designed to show that problem.
- Compute a 0–100 health score per account from six weighted signals:
  response speed 20 / response quality 15 / rating level 25 / rating
  trend 10 / complaint themes 10 / NAP consistency 20.
- Auto-detect exactly these five incident types — all five, don't drop
  any of them: `low_health_score` (score below the SLA threshold),
  `unanswered_negative_review` (a 1-2★ review with no reply after 24h —
  this is the single most important one; show the actual review text when
  it fires), `low_quality_response` (a 1-2★ review that got a reply but
  the reply doesn't actually address it), `nap_drift` (listings disagree
  on name/address/phone), `rating_velocity_decline` (recent reviews
  trending down vs. older ones). `recurring_complaint_theme` is a softer
  opportunity, not a hard incident — don't swap it in as the fifth type.
- Auto-detect a churn-risk flag (declining health over consecutive weeks).
- Expose it all via `GET /api/accounts`.

## Prompt 2 — Claude integration

Now add four Claude-powered endpoints, each returning structured JSON
(`output_config.format`, JSON schema):

- `POST /api/accounts/{id}/explain` — root cause + draft review reply +
  action plan (only when there's an open incident)
- `POST /api/accounts/{id}/save-play` — CSM outreach paragraph (only for
  churn-flagged accounts)
- `POST /api/accounts/{id}/success-plan` — ranked priorities, for any
  account
- `POST /api/digest` — one weekly digest across all accounts

No cap on Anthropic API usage. Use the stronger model for
explain/success-plan (harder synthesis), a lighter/faster one for
save-play/digest (simpler, more templated) — match the model to the job.

CRITICAL schema constraint — this breaks 100% of these endpoints if
missed, and it's easy to miss: do NOT build the JSON schema by calling
`SomeModel.model_json_schema()` on a Pydantic model. Pydantic's
auto-generated schema never sets `additionalProperties: false`, and it
uses `$ref`/`$defs` for any nested model — the Anthropic API rejects both
of those with a 400 (`'additionalProperties' must be explicitly set to
false`). Write each schema by hand as a plain dict literal instead:
`additionalProperties: false` on every object, including nested ones. Also:
`minItems`/`maxItems` on an array only accepts 0 or 1, never a range like
2-4 — put step-count guidance in the prompt text, not the schema.

## Prompt 3 — dashboard

Now build the frontend: a sortable, triage-ranked dashboard (worst-first by
default, not raw score) with a trend sparkline + score breakdown bar per
card, inline incident drill-down that needs no Claude call, and buttons
wired to the four endpoints above. Fully responsive on any device or
browser — the card grid must scale its column count with viewport width
(`repeat(auto-fill, minmax(340px, 1fr))`), not a fixed count. Just as
important: the page's own outer container must NOT have a `max-width` +
`margin: 0 auto` capping it — that leaves dead space on both sides on any
screen wider than the cap, which is the single most common way this ends
up looking "doesn't fit the screen" even when the grid itself is
responsive. Only pad the container; never cap its width.

Status filter pills, exactly these six: all, critical, warn, healthy,
churn risk, needs response.

Dark theme (near-black background, light text), with experience.com's
brand blue as the accent instead of a generic blue: #0065B1 for the
primary button's solid fill (white text on top), #1A8FF1 for
everything else that uses the accent as text/border (links, pills,
badges). Keep the health-score status colors (green/amber/red for
healthy/warn/critical) as plain traffic-light semantics, not rebranded to
blue.

Serve `profilewatch.html` on `GET /` and `profilewatch.css` on
`GET /profilewatch.css` via FastAPI's `FileResponse` with an explicit
`Cache-Control: no-cache` header on both — Safari applies heuristic
caching to a plain `FileResponse` otherwise, which can keep serving a
stale copy of the CSS across edits.

## Prompt 4 — verify

Run it, verify every endpoint and incident type actually fires, and check
it renders responsively across Chrome/Firefox/Safari — fix anything that
fails. Call the explain/save-play/success-plan/digest endpoints for real
against the live Anthropic API — not mocked — at least once each; a mocked
response can pass while the real call 400s on a schema problem, which
defeats the point of verifying at all.

## Prompt 5 — polish

If there's time left: add a couple more accounts, grab a few screenshots
for `demo/`, and do a final copy pass.

## Tool

Claude Code

## What it produces

experience.com's XMP platform already includes reputation management, but
boils a business's standing down to one number — the Search Rank Score
(SRS), a gamified measure of search-result engagement. ProfileWatch
decomposes that into six explainable signals instead, flags incidents and
churn risk before they become obvious, and has Claude draft a root-cause
explanation, review reply, action plan, save play, or success plan on
demand — prescribing fixes, not just reporting a number.

## How to use it

Step 1: pip install -r src/requirements.txt Step 2: cp .env.example .env —
fill in ANTHROPIC_API_KEY Step 3: python src/main.py Step 4: Open
localhost:8000
