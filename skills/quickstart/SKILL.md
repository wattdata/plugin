---
name: quickstart
description: New to Watt? Start here. A short, guided walkthrough that shows you what Watt can do — pick a topic you care about (or try the demo) and watch it surface the audience signals behind it, one step at a time. Pick this if you just installed Watt or want to see how it works — "how does Watt work", "where do I start" — or type /watt:quickstart.
compatibility: Drives the remote Watt MCP server via /watt:explore, so it needs network access and browser OAuth on the first tool call. Inline visuals and the closing decision follow the render contract (`context/visuals.md`), degrading gracefully where the host can't render or return a pick.
---

# Watt Quickstart (interactive)

## Purpose

This is the user's **first time** with Watt. Your job is to be the warm on-ramp into `/watt:explore` — greet them, set expectations, then walk them into the explore loop on something real so they come out the other side actually understanding a corner of the Signal Graph. Keep the whole thing under ~5 minutes of wall time.

**You are not re-implementing Explore.** The graph-grounded interview — probe, ask, pick — its checkpoints, its rendering, and its state-write all live in `/watt:explore`. This skill adds the first-run framing *around* that flow and then hands off. When you reach the loop, **follow the `/watt:explore` skill as written** — don't paraphrase or re-document it here.

## Works with

- **Called by:** the user (`/watt:quickstart`) — usually on the SessionStart greeting's first-run suggestion.
- **Hands off to:** `/watt:explore` — this skill drives that flow as written (explore's advisors run under it); at the close, it names `/watt:audience` as where a signal pool becomes a sized audience.

## Entry

- **`/watt:quickstart` typed** — usually because the SessionStart greeting suggested it on a first run.
- **"How does Watt work?"** — a new user asking for orientation; run the same walkthrough.

## The flow

### 1 — Greet and introduce (no tool calls yet)

Greet them by name if you have one, otherwise just "Hey." Then in one sentence, say what Watt does. Something like:

> "Watt lets you describe people in plain English and *see what the Signal Graph actually knows about them* — the signals behind the idea, how big and fresh each one is, and what's nearby that you wouldn't think to ask. Want to try it on something you care about, or should I run a quick demo with 'people interested in hair products'?"

Render this as the decision, per the render contract (`context/visuals.md`). Two options:

- **"Use my own idea"** — they'll describe the people they're curious about
- **"Run the hair-products demo"** — default, recommended for the very first time

Wait for their answer. If they pick their own idea and haven't said what it is yet, ask: "Cool — who are you curious about? Describe them in plain English."

If you have not made a Watt MCP call this session yet, before the first tool call mention:

> "Heads up — first Watt call this session will pop your browser to sign in. Just sign in and come back."

### 2 — Hand into the explore loop

You now have an idea (theirs or the demo's). **Run the `/watt:explore` flow on it** — that skill owns probing the graph for what it holds, asking one concrete question at a time, and letting each answer steer the next probe, with the pool read (`signal-profiler`) and what's adjacent (`signal-recommender`) as user-gated checkpoints. Drive it exactly as Explore documents:

- **End each turn at the question.** Explore probes the graph, shows a few honest facts, and asks one concrete question only the user can answer — then stops. Don't collapse beats — the steering between them is the point, doubly so on a first run.
- **The opening matters most on a first run.** Explore reads the idea back as a first graph-informed question — the angles it heard, grounded in what a quick probe turned up — before it goes anywhere deep. Let that happen; it's where the user learns to think in signals.
- **Narrate each probe and dispatch in plain English** ("Checking what the graph holds for the hair-care side of this…"). Never dump the structured payload a probe or advisor returns.
- **The thorough sweep is the user's to invoke.** Explore probes lightly by default; the deeper `signal-finder` dive runs only when the user commits to an angle and asks to go deep — don't reach for it on their behalf.
- Because it's their first time, you can explain a touch more than Explore would for a returning user — but keep it light, and don't lecture about traits, hashes, or internals.

### 3 — Land the payoff

The payoff is the signal pool taking shape: their picks landing in the pool record and its inline visual, round by round — that's the "oh, neat" beat, and it's theirs, not yours. When they've kept signals across a couple of angles, Explore offers the read of what they've composed; render it the way Explore does — the pool view, the fenced record quietly beneath as the durable carrier. Lead with the plain-English summary of what they composed, then the signals with their sizes and freshness, and what's adjacent and unexplored.

Make it feel alive, but let the data carry it — and let the user's picks drive when it arrives.

### 4 — Teach them what just happened, and hand off

End with a short, concrete handoff. Don't lecture. Something like:

> "That's the whole loop: you **described** people in plain English, Watt **probed** the graph for what it actually holds, **asked** you one concrete question at a time, you **picked what belonged**, and it **read what you'd composed** and **pointed** at what else is worth a look. From here, just **describe anyone you're curious about in chat** — 'people who own boats in Florida', 'home cooks into Korean food' — and I'll explore it.
>
> Want to explore another angle?"

Explore stops at discovery — it never builds a list, counts a combination, enriches, or exports. Keep that true in the quickstart. If they ask for the people themselves, name the next step honestly: building a sized audience from signals is `/watt:audience` — their signal pool carries straight into it.

### 5 — Mark onboarding complete (silent)

Run this so the SessionStart hook stops suggesting the quickstart next time:

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
- **Narrate what you're doing as you do it** — in plain English, never API jargon.
- **Don't run the demo without asking.** The first prompt — the beat's decision, per the render contract — is non-negotiable; that's the whole point of "interactive."
- **One beat per turn, ending at the question.** Don't dump the whole loop in one message. Give the user space to pick, redirect, or ask questions — their choices are the loop.
- **If they redirect mid-flow** ("actually can you look at X instead"), drop the current idea and run their request through the same loop.
- **Never invent signals.** If there's no strong match for a concept, surface the closest and flag it — don't fabricate or silently substitute. (Explore enforces this too; keep it true here.)
- **Don't lecture about MCP, traits, hashes, workflows, or any internals.** They don't care yet.

## Refuse cleanly

- **Employer / job-title as the defining criterion.** Not supported — redirect to interest, demographic, or location framing.

## Failure modes

- **OAuth fails / browser closed.** Stop. Tell them to sign in and retype `/watt:quickstart`.
- **A probe (or a `signal-finder` deep dive) returns nothing relevant.** Show what came back, tell them honestly it's not a great match, suggest a related angle ("Watt doesn't have a tight 'X' signal, but here's the closest — want me to explore with that?").
- **A concept comes back thin or empty.** Say so plainly and probe a different angle with them — a thin read rendered honestly beats a padded one.
