# After the build — what to actually do

This is your checklist, not the AI's. Once Claude Code has finished
working through `PROMPT.md`, follow this to confirm it actually works and
get it ready to submit. Nothing technical to write here — just things to
click, look at, and fill in.

## 1. Look at it yourself before trusting it

Open `localhost:8000` in a real browser tab (hard-refresh once —
Cmd+Shift+R — in case an earlier version got cached).

- Does the grid actually show ~30 cards, or is it empty/blank? An empty
  grid almost always means the backend and frontend disagree on field
  names — tell Claude Code exactly that if it happens, don't just ask it
  to "try again."
- Pick one card with a red "critical" badge. Does it show real incident
  text (an actual review quote, a real date), or generic placeholder-y
  text?
- Click through all six filter pills (all / critical / warn / healthy /
  churn risk / needs response) — does the grid actually change each time,
  or does clicking do nothing?
- Resize the browser window (or just look at it on your phone too) — does
  the number of columns change with the width, or does it stay stuck?

## 2. Click every AI button at least once

This is the part that actually needs a real Anthropic API key, so do this
after confirming `.env` has one.

- On a card with an incident: click **Explain & draft response**. You
  should see a root cause, a draft reply, and a numbered action plan
  appear in a few seconds. If you get an error banner instead, read what
  it says — a schema error and a missing-API-key error look different and
  need different fixes.
- On a card flagged **Churn risk**: click **Generate save play**. One
  paragraph should appear.
- On any card, including a healthy one: click **Get success plan**. This
  one should work even with zero open incidents — if it doesn't, that's a
  real bug, not expected behavior.
- Click **Generate Weekly Digest** at the top. This one covers every
  account in a single call, so give it 30-60 seconds before assuming
  it's stuck.

If any of the four hang forever or error out, that's worth fixing before
you move on — don't wait until you're demoing live to find out.

## 3. Take your screenshots now, while it's working

Put these in a `demo/` folder in your branch:

1. The full dashboard, default view (grid + summary tiles + filters).
2. One card's incident detail expanded (click the ▸ next to an incident).
3. One of the AI panels open with a real result showing (success plan or
   explain both work well for this).

## 4. Fill in the README output card

This is what the automated scoring tool actually reads first. Put these
fields near the top of `README.md`, above the longer product description:

```
**Name + Role:** [your name] — [your role]
**Problem I solved:** experience.com customers judge their reputation by
one opaque SRS number with no trend or explanation — they either let
issues slide or churn because "checking the dashboard" is one more chore.
**What I built:** ProfileWatch — an SRE-style monitoring dashboard that
decomposes reputation into six explainable signals (response speed &
quality, rating level & trend, complaint themes, NAP consistency),
auto-detects incidents and churn risk, and has Claude draft root-cause
explanations, review replies, action plans, and success plans on demand.
**Tool used:** Claude Code
**Time without AI:** 2-3 engineering days for a comparable scoring engine
+ dashboard + AI integration
**Time with AI today:** [however long it actually took you]
**Will I use this next week?** [YES/MAYBE — one honest sentence why]
**Where it lives:** this branch
```

Only you can fill in name/role and the honest "will I use this" answer —
everything else above is already accurate to what got built.

## 5. Export the chat and push

1. In the Claude Code session that built this, type `/export`, save it as
   `ai-chat-export.json` in your branch root.
2. Confirm your branch has `README.md`, `prompt.md`, `ai-chat-export.json`,
   and `demo/` with the three screenshots — the four required items.
3. Commit (a few commits across the build look more genuine than one
   giant one, but don't force it if it's already done) and push before
   13:00. Don't leave the push to the last five minutes.

## If something's actually broken

- **Blank grid / "undefined" everywhere**: backend and frontend disagree
  on field names. Tell Claude Code which field is missing (open the
  Network tab, look at the `/api/accounts` response, compare it to what
  `PROMPT.md` says the field should be called).
- **Every AI button errors immediately**: check `.env` actually has
  `ANTHROPIC_API_KEY` set, and that you restarted the server after adding
  it.
- **AI buttons error with something about "additionalProperties"**: this
  is the schema bug `PROMPT.md` warns about — the JSON schema wasn't
  hand-written as a plain dict. Point Claude Code at that exact paragraph
  in `PROMPT.md` again.
- **A card shows a dozen-plus incidents piled up**: the fixture has too
  many reviews per account or too many unanswered ones — this is a data
  problem, not a display bug.
