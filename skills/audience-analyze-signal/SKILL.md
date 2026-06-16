---
name: audience-analyze-signal
description: Read who a built audience reaches when the signals are already in hand — a signal stack fresh from generate, an explore pool, a pasted audience record, or signals the user names — skip discovery, materialize, and render the two-section read (your signals + discovered). The signals-in-hand way into audience-analyze, behind /watt:audience. Aggregates only — never individual records, never an export. Not a user command. Use when a built audience is in session or the user supplies its signals and asks who's in it — "who's actually in this audience", "what do these people look like".
user-invocable: false
compatibility: Talks to the remote Watt MCP server — network access and browser OAuth on the first tool call. Inline visuals and the closing decision follow the render contract (`context/visuals.md`), degrading gracefully where the host can't render or return a pick.
---

# Analyze an audience from its signals

## Purpose

`audience-analyze-signal` is the way into the read when the **signals already exist** — a signal stack fresh from `audience-generate`, an `/watt:explore` signal pool, a pasted audience record from a past session, or signals the user names. There's no discovery and no pivot loop: take the signals as given, materialize them, and hand the built stack to the shared read.

This is a delta over `audience-analyze`: the unique work here is just **resolving the supplied signals into a built signal stack**; the read and the shareable report are the parent's shared procedure (`audience-analyze` → *The read & report*), composed with verbatim — not restated.

## Works with

- **Called by:** the `audience-analyze` router, when a built audience is in session or the user supplied its signals.
- **Dispatches:**
  - **`signal-finder`** *(only when the user supplied bare names)* — to resolve each named signal to its verified trait. Never used to discover *more* signals — the user's set is the set.
  - **`audience-profiler`** — mode A (the stack) → the two-section read. The parent's shared dispatch.

## Language

Inherits the parent's table (signals / must-haves / exclusions; lift explained once; sample named). The `role` column in an audience record — `defining` (any-of) / `must-have` (all-of) / `exclusion` (none-of) — carries the boolean shape exactly; the operator never sees AND/OR/NOT.

## The flow

### 1 — Take the signals as given

- **A built audience in session** (fresh from generate, or composed in `audience-analyze-search`) — use it directly. Confirm which one in a word if there's any doubt.
- **A re-supplied audience record** — read from the saved record file in the working directory, pasted in, or compacted in context — the `role` column (`defining` / `must-have` / `exclusion`) carries the expression exactly as built, and names ride beside hashes; take it as the stack. A past session's reach/headcount is "measured then", not re-measured silently. **On a refresh-shaped ask** ("refresh this", "is it still ~2M?"), the read's fresh materialization *is* the re-measure: after the read, **re-write the audience record** per the record contract (`context/record.md`) with today's measured reach against the header's original target (`reach 2.1M (band 1M–5M) · refreshed`), location and roles unchanged.
- **A signal pool** (an `/watt:explore` session's kept signals, or a lookalike pool) — **auto-compose it to the default stack**: signals the pool marks must-have go *all-of*, its exclusions *none-of*, everything else *any-of* (one OR union). **If the pool carries no role markers at all, ask once** — *"any must-haves or must-have-nots in here, or read them all as one group?"* — then build. This is a deterministic reading of the user's picks, the same way a record's `role` column reconstructs an expression — never a strategy compose; refining the pool into a tuned stack is `audience-generate`'s lane, offered if the read shows it's wanted.
- **Signals the user names, no hashes** — the leaf cannot fabricate a hash. Dispatch `signal-finder` once to resolve each name to its verified trait (driving from meaning), surface the matches for a one-touch confirm, and only then build the stack. Never pass a name off as a hash, never guess one.

Build the expression from the `role` column — `defining` any-of, `must-have` all-of, `exclusion` none-of — and reuse the record's `workflow_id` if it carries one, else generate one. If the supplied set carries no measured reach, measure the headcount once with a count-only entity find (`format: "none"`, location applied if the record fences one).

### 2 — Run the shared read

Hand off to the parent's shared read & report (`audience-analyze` → *The read & report*) in **mode A** — the signal stack you took in hand (expression, signals, location, reach, `workflow_id`). The router owns the dispatch, the two-section dashboard, the report, and the next-step options. The state file's `last_workflow` is `audience-analyze-signal`.

## How to behave

- **The user's set is the set.** This leaf reads what was supplied; it doesn't discover more signals or pivot pools. Adding signals is a re-pivot back through `audience-generate` or `audience-analyze-search`.
- **Never invent a signal** — a bare name is resolved through `signal-finder` and confirmed, never assigned a guessed hash.
- **Don't re-measure silently** — a past session's reach is labeled "measured then"; only an unmeasured supplied set gets a fresh count-only measurement. The one exception is a refresh-shaped ask, where the read's materialization *is* the explicit re-measure (step 1).
- **Narrate the dispatch and report the return** in one plain line each — never the structured payload.
- **Aggregates only** — the read and the report carry no record, identifier, or PII; that's `audience-activate`'s lane.
- **US-only, adults-only, person audiences only.**

## Refuse cleanly

- **"Show me the actual people."** Aggregates only — individuals live downstream in the export, behind the activate step's confirmation.
- **A list of identifiers / a CSV of people.** That's the `audience-analyze-list` way in — say so; this leaf reads from signals, not a people list.
- **"Add some more signals to this."** That's a re-pivot — route to `audience-generate` (build) or `audience-analyze-search` (discover more from a brief); this leaf reads the set as given.

## Failure modes

- **A supplied signal name resolves to nothing strong.** Surface the closest match flagged; never silently substitute or fabricate a hash.
- **A reach probe or the profiler errors.** Surface where it stopped and what was measured; never fill the gap with an estimate.
