---
name: audience-analyze-search
description: Read who a market is, starting from a plain-English brief — discover → pivot → read. The discovery-first way into audience-analyze, behind /watt:audience; size is an output, never a target. Aggregates only — never individual records, never an export. Not a user command. Use when a read-shaped ask arrives with a brief and no signals yet — "who's in the market for X", "profile this audience", "an audience profile for my client".
user-invocable: false
compatibility: Requires the remote Watt MCP server (network access).
---

# Analyze a market from a brief

## Purpose

`audience-analyze-search` is the way into the read for a user who arrives with a **brief, not signals** — "who's in the market for roofing near Nashville", "profile this audience". It discovers the signals behind the brief, organizes them into three pools, lets the operator steer which signals land in which pool, materializes the audience, and hands it to the shared read. **Size is an output, never a target** — there's no band and no strategy worker; the headcount is whatever the composed signals land at.

This is a delta over `audience-analyze`: the unique work here is **getting from a brief to a built signal stack**; once that stack exists, the read and the shareable report are the parent's shared procedure (`audience-analyze` → *The read & report*), composed with verbatim — not restated.

## Works with

- **Called by:** the `audience-analyze` router, when the user brought a brief and no signals.
- **Dispatches** (the same discover → profile → suggest advisors explore uses, here ending in a built-and-read audience):
  - **`signal-finder`** — one concept per beat: a pool's concept (in the user's phrasing, tagged with its role) → validated candidate signals with evidence.
  - **`signal-profiler`** — scores the gathered signals against the model (relevance · freshness · rarity/specificity · breadth/size · coverage), grounded on the brief, so the operator can see how each stacks up and curate. Traits-only — it never touches a set of people.
  - **`signal-recommender`** *(optional, at a pivot checkpoint)* — adjacent concepts / unprobed domains worth adding to a pool.
  - **`audience-profiler`** — mode A (the built stack) → the two-section read. The parent's shared dispatch.

## Language

Inherits the parent's table (signals / must-haves / exclusions; lift explained once; sample named). Internally the three pools map to the boolean shape — **defining → OR (`core`)**, **must-have → AND (`must_have`)**, **exclusion → AND_NOT (`exclusion`)** — but the operator only ever sees *defining signals*, *must-haves*, *exclusions*. No AND/OR/NOT, no boolean-"pools" jargon at the surface (*signal pool*, the kept-signals carrier, is the user's word and fine).

## The flow

One decision per turn, landed per the render contract (`context/visuals.md`). Track each advisor dispatch as a session task.

### 1 — Settle the brief and the place

- **The brief.** Must carry at least one defining behavior, interest, or intent — a pure-demographics brief gates a market, it doesn't define one; ask what these people are *doing* or *into*. If it reads as demographics-only, push back before discovering.
- **The place.** National (no filter), a radius (geocode the center; confirm a below-rooftop point before using it), or a named boundary (state / county / DMA / ZIP — looked up as a geo trait, added as a must-have; never guess a geo hash). A radius rides every measurement as the location filter.

There is no size-band question — this reads a market, it doesn't size to one.

### 2 — Draft the three pools, then discover

Read the brief into three pool descriptions in plain English — **defining** (what makes this audience *this* audience: the intents, behaviors, affinities that distinguish them — lean specific), **must-haves** (structural gates true of everyone — life stage, household, income; favor broad, leave empty if none), **exclusions** (hard disqualifiers only; minimal — an exclusion silently shrinks the studied market). Show the three; let the operator amend before any search.

Then, for each confirmed concept, dispatch `signal-finder` in narrow scope — the operator's phrasing, the concept's role, `entity_type: "person"`, domain hints the brief implies. One concept per beat; narrate the dispatch and a one-line read of the return. signal-finder validates and enriches (similarity, size, domain, skew, freshness, hash) and flags anything unmatched — never invent a signal.

### 3 — Profile the pool, surface, pivot

Dispatch **`signal-profiler`** on the gathered candidates — by `trait_hash`, with the **brief as the grounding frame** so relevance is comparable across signals from different concepts. It runs the scoring model and returns each signal's feature vector (relevance · freshness · rarity/specificity · breadth/size · coverage) — the read of how the pool stacks up. The model owns that math; never hand-score a signal.

Render the profiled pool per the render contract, grouped by role (defining / must-have / exclusion): each signal with name · what it means · reach (size) · actively-searching (intent) · match-to-brief (relevance) · concentration (rarity) — strongest first within each group, sizes human-rounded, the profiler's axes visible so "why is X above Y" is answerable from the render. The working-set record is written per the record contract (`context/record.md`). Then end the turn at the pivot question.

**Pivot** — one action per turn, any order: include/exclude a signal; **move a signal between roles** (defining ↔ must-have ↔ exclusion); add a concept (a fresh narrow `signal-finder` dispatch, then re-profile); drop or expand a concept; or ask for adjacencies (`signal-recommender`). A fresh batch of candidates is re-profiled by `signal-profiler` before it's shown. **Exclusions are explicit-include only** — a proposed exclusion is not in the working set until the operator confirms it, because a mis-applied exclusion silently distorts every downstream stat. Keep the working set inside sane bounds (roughly 5–20 defining, 0–3 must-haves, 0–5 exclusions); if it drifts outside, surface it and let the operator's judgment land it — never auto-trim.

### 4 — Materialize, then run the shared read

When the operator locks the picks, build the expression — defining *any-of*, must-haves *all-of*, exclusions *none-of* — generate one `workflow_id`, and measure the headcount once with a count-only entity find (`format: "none"`, the radius location applied if set). Report it plainly ("**240,000 people** in this market") — never tune the picks toward a number.

Then hand off to the parent's shared read & report (`audience-analyze` → *The read & report*) in **mode A** — the signal stack you just built and measured (expression, signals, location, headcount, `workflow_id`). The router owns the dispatch, the two-section dashboard, and the report.

## How to behave

- **End every turn at its question** — pool amendments, picks, pivots, the lock. A stack the operator didn't steer is the failure, not the deliverable.
- **Narrate every dispatch and script run in plain English;** one-line read of the return before acting. Never dump a structured payload.
- **Show the math.** The profiler's feature-vector axes are on screen; the operator answers "why is X above Y" from the render.
- **Size is the output.** Never invent a band, never tune the picks toward a number; report the headcount the signals land at.
- **Never invent a signal** — unmatched concepts surface with the closest match flagged, in discovery and geo lookup alike.
- **Aggregates only** — the read and the report carry no record, identifier, or PII; that's `audience-activate`'s lane.
- **US-only, adults-only, person audiences only.** Non-US is out of scope; briefs about minors pivot to parents/guardians of that age range.

## Refuse cleanly

- **Bare signal names as the whole brief.** Drive from meaning: *"Tell me who you're trying to reach and what they're doing — named signals can join once we see them in context."*
- **A target size / "build me N people."** That's the build flow (`audience-generate`); here size is the output. Offer generate if they want to size to a band.
- **"Show me the actual people."** Aggregates only — individuals live downstream in the export, behind the activate step's confirmation.
- **Employer / job-title as the defining criterion / business audiences / non-US / minors.** Redirect or decline as everywhere in the plugin.

## Failure modes

- **`signal-profiler` errors or returns thin.** Say so; surface the candidates in the finder's similarity order with their evidence, and let the operator pivot from there — never hand-score to fill the gap.
- **A reach probe or an advisor errors.** Surface where it stopped and what was measured; never fill the gap with an estimate.
