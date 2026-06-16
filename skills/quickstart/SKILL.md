---
name: quickstart
description: New to Watt? Start here. A short, guided first run that ends with a real audience you built — pick a starter audience or describe your own in plain English, watch Watt find the signals behind it and stack them into an audience with a measured size, then choose what's next — export it, see who's in it, or keep exploring. Pick this if you just installed Watt or want to see how it works — "how does Watt work", "where do I start" — or type /watt:quickstart.
compatibility: Drives the remote Watt MCP server via the /watt:audience build flow, so it needs network access and browser OAuth on the first tool call. Inline visuals and the closing decision follow the render contract (`context/visuals.md`), degrading gracefully where the host can't render or return a pick.
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

### 1 — Greet, then settle the brief (no tool calls yet)

Greet them by name if you have one, otherwise just "Hey." One sentence on what Watt does:

> "Watt builds audiences from plain English — describe people, and it finds the signals the Signal Graph actually holds for them, stacks them into an audience, and measures how many people that reaches. Let's build your first one."

Then the brief decision, rendered per the render contract (`context/visuals.md`). Four options — three **starter briefs**, each a *different way Watt stacks an audience*, plus their own idea. Each starter carries its one-line tease so the pick itself teaches the range:

- **"Weekend hikers — about 5–10M people"** — *lands inside a size band: signals stacked one at a time, the reach measured after every step.*
- **"Homeowners in-market for solar"** — *precision: the few signals that lift the most over a must-have, for the people most likely to act.*
- **"Everyone plausibly interested in hair products"** — *the widest credible reach the signals support.*
- **"Describe my own"** — they say who they're curious about, in plain English.

Carry each starter's landing mode silently — the band (5M–10M), precision (the homeowner gate carried as the must-have base), max-reach — so the build flow routes without re-asking.

**Coach their own brief by reading it back, not by lecturing.** A good description has three parts: **who** (what these people are *doing* or *into* — a behavior, interest, intent, or life-stage; never an employer or job title), **where** *(optional — a state, metro, or ZIP)*, and **the landing** (about how many, the widest credible reach, or the highest-intent few). Read their draft back against those parts, name what's already strong, and ask **at most one question** to fill what's missing — usually the landing: *"Want a target size, the widest reach, or the highest-intent few?"*

If no Watt MCP call has happened this session, before the first tool call mention:

> "Heads up — first Watt call this session will pop your browser to sign in. Just sign in and come back."

### 2 — Run the build as written

Brief and landing mode in hand, **run the `/watt:audience` build flow** — the `audience-generate` shared spine (discover → score → curate) and the `audience-generate-search` leaf (the landing mode's strategy) own everything from here; drive them exactly as they document. The first-run adjustments are framing only:

- **Route silently on what's settled.** A starter brief arrives with its landing mode answered — skip the objective question, never the work.
- **Keep starter builds single-angle.** The starters are one concept each by design — one discovery beat, one scored slice, one curation pick — so the build lands in a handful of turns. Don't suggest extra angles or pivots unless the user asks. Their own brief runs the spine at full width.
- **End each turn at the question.** The spine's gates — confirm the reading, approve the scored set, the compose go-ahead — are the product, doubly so on a first run. Don't collapse beats.
- **Narrate in plain English** ("Checking what the graph holds for the hiking side of this…"). Because it's their first time, explain a touch more than the flow would for a returning user — one clause of why per beat, never a lecture about traits, hashes, or internals.

### 3 — Land the payoff

The leaf lands the audience: the stack rendered, the record saved to its file, the measured reach leading. That number — "your picks reach 2.4M people" — is the payoff, and it's theirs: their description, their keeps, measured for real. Let the leaf's landing render carry it; add nothing but warmth.

### 4 — The junction — teach back, then hand off

The leaf's landing already offers the three doors; on a first run, deliver that offer as the quickstart junction. Lead with the teach-back, short and concrete:

> "That's the loop: you **described** people, Watt **found** the signals it actually holds for them, you **picked** what belonged, and it **stacked** them into an audience and **measured** it. And this was one way in — you can also start from a customer list you own, expand it, find lookalikes, group an audience by where it concentrates, or build a B2B lead list. `/watt:help` walks every way to use Watt."

Then the decision, rendered per the render contract — three doors, each with what it means:

- **"Export it"** — a platform-ready file for Meta, Google, or Reddit → `audience-activate` (its own confirmations included).
- **"See who's in it"** — what these people actually look like, as aggregates → `audience-analyze`.
- **"Keep exploring"** — what's adjacent to what you built; your signals carry over → `/watt:explore`.

Whichever they pick, the receiving skill runs as written; quickstart's framing ends here.

### 5 — Mark onboarding complete (silent)

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
- **Don't lecture about MCP, traits, hashes, workflows, or any internals.** They don't care yet.
- **Stay inside the budget.** ~5 minutes of wall time; if their own brief sprawls into many angles, offer to land the first stack now and chase the rest after.

## Refuse cleanly

- **Employer / job-title as the defining criterion.** Not supported — redirect to interest, demographic, or location framing.
- **A non-US audience, or one about minors.** Out of scope, as everywhere in the plugin — say so plainly; a brief about minors pivots to parents/guardians of that age range.

## Failure modes

- **OAuth fails / browser closed.** Stop. Tell them to sign in and retype `/watt:quickstart`.
- **Discovery comes back thin for their own brief.** Say so plainly and offer the closest angle the graph does hold — or a starter brief, named as the known-good path ("want to see it work on hikers first, then come back to yours?").
- **A starter build lands thin or off-band.** The build flow's own edge handling owns it (off-band leverage, the over-broad finding); keep the framing honest — a real number with a caveat beats a padded demo.
