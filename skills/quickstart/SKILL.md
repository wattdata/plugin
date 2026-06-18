---
name: quickstart
description: New to Watt? Start here. A short, guided first run that ends with a real audience you built — pick a starter audience or describe your own in plain English, watch Watt find the signals behind it and stack them into an audience with a measured size, then choose what's next — export it, see who's in it, or keep exploring. Pick this if you just installed Watt or want to see how it works — "how does Watt work", "where do I start" — or type /watt:quickstart.
compatibility: Requires the remote Watt MCP server (network access).
---

# Watt Quickstart (interactive)

## Purpose

This is the user's **first time** with Watt. Your job is the warm on-ramp into their **first built audience** — greet them, help them land on a good audience description (a starter brief, or their own with light coaching), then walk them through the build so they come out the other side holding a real audience with a measured size — and seeing the doors out of it. Keep the whole thing under ~5 minutes of wall time.

**You are not re-implementing the build.** Discovery, scoring, curation, the compose strategies, the rendering, and the landing all live in the `/watt:audience` build flow — the `audience-generate` spine and its `audience-generate-search` leaf. This skill adds the first-run framing *around* that flow: the brief beat in front, the junction's teach-back behind. When you reach the build, **follow those skills as written** — don't paraphrase or re-document them here.

## Works with

- **Called by:** the user (`/watt:quickstart`) — usually on the SessionStart greeting's first-run suggestion.
- **Hands off to:** `audience-generate` (its `-search` leaf) — this skill drives that flow as written, arriving with the brief and landing mode already settled.
- **Hands off to (the junction):** the leaf's landing offer, delivered with first-run framing — `audience-activate` (export it), `audience-analyze` (see who's in it), or `/watt:explore` (the stack carries in as covered territory) — each run as written. The close names `/watt:help` for every other way in (an owned list, lookalikes, grouping, a B2B lead list).

## Entry

- **`/watt:quickstart` typed** — usually because the SessionStart greeting suggested it on a first run.
- **"How does Watt work?" / "where do I start?"** — a new user asking for orientation; run the same walkthrough.

## The flow

### 1 — Greet, then confirm Watt is connected

Greet them by name if you have one, otherwise just "Hey." Before anything else, make sure Watt is connected — it runs on its **Signal Graph connector**, and the build can't work until that's enabled.

**Probe silently.** Make one lightweight Signal Graph call as a connectivity check — a quick `trait_search` (e.g. for "running"), which touches no audience and materializes nothing; the result is the liveness signal, not something you act on. Narrate it in one warm line ("Let me make sure Watt's connected…"), not as plumbing.

- **It works** → say so in a line ("You're connected.") and move straight on to the brief — the probe is setup, the brief decision is this turn's question. Don't make a connected user click anything.
- **It errors with a connection / auth / not-enabled error, or the connector isn't on the connection** → they need to enable it. (A transient error — a one-off 5xx or timeout — isn't this: retry the probe once before concluding the connector's missing, so a connected user isn't pushed into the connect flow.) An auth step that *errors* — a `complete_authentication` that reports no OAuth flow in progress, a probe that comes back unauthenticated — is the connect failure itself, not a transient: don't retry the `authenticate` / `complete_authentication` tools in a loop and don't go diagnosing the connector or the MCP registry; the orientation's *Getting connected* note is the rule. Surface the connect step the way that note prescribes — in Cowork, the inline Connect card (the note gives the exact `search_mcp_registry` → `suggest_connectors` recipe); on other hosts, the install path — and always hand them both docs: the setup walkthrough (https://wattdata.ai/docs/get-started/quickstart) and the Claude organization guide for an admin to enable it (https://wattdata.ai/docs/integrate/claude-organization). Take the full path from there — don't re-type it. Then put an answerable decision per the render contract (`context/visuals.md`):
  - **"I've connected it"** → re-run the probe to validate. Connected → move on to the brief. Still failing → say the connection still isn't live, and offer to walk the path again or the grayed-out branch below; don't loop silently.
  - **"It's grayed out / I can't enable it"** → a team or org plan needs an admin to turn it on. Hand them the Claude organization setup guide (https://wattdata.ai/docs/integrate/claude-organization) to send their admin, and offer to pick the quickstart back up once it's enabled.

  A typed free-text answer always wins — if they say they've done it, re-probe; if they name a different blocker, read it and respond. This connection beat is the **one place quickstart names the connector**; once connected, the no-internals rule holds for the rest of the run.

### 2 — Settle the brief (no tool calls)

One sentence on what Watt does:

> "Watt builds audiences from plain English — describe people, and it finds the signals the Signal Graph actually holds for them, stacks them into an audience, and measures how many people that reaches. Let's build your first one."

Then the brief decision, rendered per the render contract (`context/visuals.md`). Four options — three **starter briefs**, each a *different way Watt stacks an audience*, plus their own idea. Each starter carries its one-line tease so the pick itself teaches the range:

- **"Weekend hikers — about 5–10M people"** — *lands inside a size band: signals stacked one at a time, the reach measured after every step.*
- **"Homeowners in-market for solar"** — *precision: the few signals that lift the most over a must-have, for the people most likely to act.*
- **"Everyone plausibly interested in hair products"** — *the widest credible reach the signals support.*
- **"Describe my own"** — they say who they're curious about, in plain English.

Carry each starter's landing mode silently — the band (5M–10M), precision (the homeowner gate carried as the must-have base), max-reach — so the build flow routes without re-asking.

**Coach their own brief by reading it back, not by lecturing.** A good description has three parts: **who** (what these people are *doing* or *into* — a behavior, interest, intent, or life-stage; never an employer or job title), **where** *(optional — a state, metro, or ZIP)*, and **the landing** (about how many, the widest credible reach, or the highest-intent few). Read their draft back against those parts, name what's already strong, and ask **at most one question** to fill what's missing — usually the landing: *"Want a target size, the widest reach, or the highest-intent few?"*

### 3 — Run the build as written

Brief and landing mode in hand, **run the `/watt:audience` build flow** — the `audience-generate` shared spine (discover → score → curate) and the `audience-generate-search` leaf (the landing mode's strategy) own everything from here; drive them exactly as they document. The first-run adjustments are framing only:

- **Route silently on what's settled.** A starter brief arrives with its landing mode answered — skip the objective question, never the work.
- **Keep starter builds single-angle.** The starters are one concept each by design — one discovery beat, one scored slice, one curation pick — so the build lands in a handful of turns. Don't suggest extra angles or pivots unless the user asks. Their own brief runs the spine at full width.
- **End each turn at the question.** The spine's gates — confirm the reading, approve the scored set, the compose go-ahead — are the product, doubly so on a first run. Don't collapse beats.
- **Narrate in plain English** ("Checking what the graph holds for the hiking side of this…"). Because it's their first time, explain a touch more than the flow would for a returning user — one clause of why per beat, never a lecture about traits, hashes, or internals.

### 4 — Land the payoff

The leaf lands the audience: the stack rendered, the record saved to its file, the measured reach leading. That number — "your picks reach 2.4M people" — is the payoff, and it's theirs: their description, their keeps, measured for real. Let the leaf's landing render carry it; add nothing but warmth.

### 5 — The junction — teach back, then hand off

The leaf's landing already offers the three doors; on a first run, deliver that offer as the quickstart junction. Lead with the teach-back, short and concrete:

> "That's the loop: you **described** people, Watt **found** the signals it actually holds for them, you **picked** what belonged, and it **stacked** them into an audience and **measured** it. And this was one way in — you can also start from a customer list you own, expand it, find lookalikes, group an audience by where it concentrates, or build a B2B lead list. `/watt:help` walks every way to use Watt."

Then the decision, rendered per the render contract — three doors, each with what it means:

- **"Export it"** — a platform-ready file for Meta, Google, or Reddit → `audience-activate` (its own confirmations included).
- **"See who's in it"** — what these people actually look like, as aggregates → `audience-analyze`.
- **"Keep exploring"** — what's adjacent to what you built; your signals carry over → `/watt:explore`.

Whichever they pick, the receiving skill runs as written; quickstart's framing ends here.

### 6 — Mark onboarding complete (silent)

Run this **when the junction is rendered, before the user's pick** — a receiving skill's own state write afterward stands; quickstart never re-writes after the handoff. It stops the SessionStart hook suggesting the quickstart next time:

```bash
STATE_DIR="${CLAUDE_PLUGIN_DATA:-${HOME}/.claude/plugins/data/watt}"
mkdir -p "$STATE_DIR"
cat > "$STATE_DIR/state.json" <<EOF
{
  "version": 1,
  "first_run_complete": true,
  "completed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "last_workflow": "quickstart"
}
EOF
```

Don't mention this to the user — it's plumbing.

## How to behave

- **Warm but brief.** One or two sentences per beat, not paragraphs.
- **Talk like a coworker** showing them a tool, not a tutorial.
- **Don't pick the brief for them.** The opening decision — a starter or their own — is non-negotiable; that's the whole point of "interactive."
- **One beat per turn, ending at the question.** Don't dump the whole build in one message — their choices are the loop.
- **If they redirect mid-flow** ("actually can you build X instead"), drop the current brief and run theirs through the same flow.
- **Never invent signals.** No strong match → surface the closest and flag it. (The build flow enforces this too; keep it true here.)
- **Don't lecture about MCP, traits, hashes, workflows, or any internals.** They don't care yet. The connection beat in step 1 is the sole exception — it names the connector because the user has to act on it; once connected, keep the internals out.
- **Stay inside the budget.** ~5 minutes of wall time; if their own brief sprawls into many angles, offer to land the first stack now and chase the rest after.

## Refuse cleanly

- **Employer / job-title as the defining criterion.** Not supported — redirect to interest, demographic, or location framing.
- **A non-US audience, or one about minors.** Out of scope, as everywhere in the plugin — say so plainly; a brief about minors pivots to parents/guardians of that age range.

## Failure modes

- **Discovery comes back thin for their own brief.** Say so plainly and offer the closest angle the graph does hold — or a starter brief, named as the known-good path ("want to see it work on hikers first, then come back to yours?").
- **A starter build lands thin or off-band.** The build flow's own edge handling owns it (off-band leverage, the over-broad finding); keep the framing honest — a real number with a caveat beats a padded demo.
- **The connector won't connect (step 1).** If the re-probe still fails after they say they've enabled it, don't start the build on a dead connection, and don't loop the auth tools or go diagnosing the registry to force it through — name that it isn't live yet, and come back with the fix: the setup docs (https://wattdata.ai/docs/get-started/quickstart) and the Claude organization guide to send their admin (https://wattdata.ai/docs/integrate/claude-organization), always. Then offer to pick up once it's on. A quickstart that pushes past a missing connection just dies at the first real call.
