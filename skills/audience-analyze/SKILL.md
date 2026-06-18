---
name: audience-analyze
description: Read who a built audience reaches, as aggregates over a deterministic sample — and, on request, a shareable signal membership report. The read step behind /watt:audience; routes to the way in that fits what the user has — a brief, signals they already hold, or a list of people. Aggregates only — never individual records, never contact data, never an ad-platform export. Not a user command — /watt:audience is the front door. Use when a read-shaped ask arrives — "who's actually in this audience", "what do these people look like", "an audience profile for my client" — or to sanity-check a signal stack before exporting.
user-invocable: false
compatibility: Requires the remote Watt MCP server (network access).
---

# Analyze an audience

## Purpose

`audience-analyze` — the read step behind `/watt:audience` — answers the question generate can't: generate guaranteed an audience's *size* (or, for a profile, measured its headcount); this read shows what it *means*. The user walks away with a dashboard in two halves: **your signals** — the stack's own signals by share and how many each person hits — and **discovered** — the net-new traits that define these people against the world by lift, plus segmentation, skews, freshness. For a market **profile**, this read *is* the deliverable: on request it writes the two halves to a self-contained shareable report file.

There are three ways into that read, by what the user brings — and this skill **routes** to the one that fits:

- **a brief** — they describe the audience in business terms and want the signals discovered for them → `audience-analyze-search`.
- **signals they already hold** — a signal stack from generate, an explore pool, or a list of signals they name → `audience-analyze-signal`.
- **a list of people** — identifiers to resolve and profile → `audience-analyze-list` (discovered half only — no signals were specified).

**Route; don't run.** Your job at this level is the routing question and the shared canon below — the language, the aggregates-only lane, and the read-and-report procedure every leaf composes with. The leaf does the discovery, the dispatch, and the render.

## Works with

- **Called by:** the `/watt:audience` router, or a sibling leaf's offer (`audience-generate` at its landing — a build to sanity-check, or a profile whose report is the deliverable; `audience-activate` after delivery) — with a built audience in session, a re-supplied audience record, or a fresh read-shaped ask.
- **Hands off to:** the three leaves —
  - **`audience-analyze-search`** — brief → discover signals → organize into pools → operator pivot → materialize → read.
  - **`audience-analyze-signal`** — a supplied stack/signal list → materialize → read (skips discovery).
  - **`audience-analyze-list`** — a supplied list of people, as identifiers (resolve to entities) or as already-resolved entity IDs (a roster from grouping — skip the resolve) → discovered-only read.

  (After the read, the user continues into `audience-generate` to re-pivot or `audience-activate` to export — offered at the closing question, step 3.)

## Language

Shared across every leaf — the surface the user reads is always business language; the boolean operators never reach them.

| The user says | What it means |
|---|---|
| signal | a trait |
| must-have | an AND gate every person satisfies |
| exclusion | an AND_NOT — people to leave out |
| audience, market, the people | the person set the signal stack reaches |
| reach, market size, headcount | the count the build/resolve measured |

New to this surface: **lift** is explained once, in plain English — *"how much more common a trait is in your audience than in the population — 5.6× means these people are 5.6 times likelier than average to have it"* — then used freely. *Sample* is named honestly: for the search and signal flavors the read is computed over a fixed, reproducible slice of the audience, and the dashboard says how big; the **list flavor reads the supplied set whole** — no sampling — and the dashboard says that instead.

## Entry — pick the way in

- **A built audience is in session** (fresh from generate, or just composed in a leaf) → `audience-analyze-signal`, with that stack. Confirm which one in a word if there's any doubt, then go.
- **A re-supplied audience record** — the user pastes a previous session's record (signals with names and hashes by role group, plus reach/headcount) → `audience-analyze-signal`; take the role groups as the expression exactly as built, and a past session's figures are "measured then", not re-measured silently.
- **A brief, no signals yet** — "who's in the market for X", "an audience profile for a Nashville roofer" → `audience-analyze-search`, with everything they've said.
- **A list of people** → `audience-analyze-list` — the one input the read can profile without composed signals; discovered half only. The list comes either as **identifiers** (a CSV / pasted emails — `-list` resolves them) or as **already-resolved entity IDs** — a **roster** from the grouping objective, or any entity-ID set the user holds — where `-list` skips the resolve and reads them directly. A roster carries `group_label`, so the whole set (its `roster_uri`) or a single group (its `entity_ids_uri`) can be read; either way there's no specified-signals half — these are people, not a signal stack the user named.
- **Nothing to read and no brief** → there's nothing here yet; route to `audience-generate` (build) or `/watt:explore` (just curious) honestly.

Route silently when the shape is already answered — skip the question, never the handoff. Carry everything the user already said into the leaf; it must not re-ask it.

## The read & report — shared canon every leaf composes with

Each leaf reaches the same place — a built audience (a signal stack, or a resolved entity set) — and from there the read is identical. This is the procedure the leaves inherit; they don't restate it.

**Aggregates only.** Every number on screen — and in the report file — is computed over the audience as a whole; no individual record, identifier, or profile is ever pulled, shown, or written. A user who wants the people themselves is asking for `audience-activate`, behind its own confirmation. The report file is *aggregates*, not contact data — a different artifact from activate's PII export.

### 1 — Dispatch the read

On the user's go (arriving at a leaf with a built audience *is* the go), dispatch **`audience-profiler`**:

- with a signal stack (search / signal) — mode A: the `expression_string`, the stack's `signals` (hashes, names, roles), the `location`, the measured reach, and a shared `workflow_id`. Both halves come back.
- with a resolved entity set (list, **or a roster**) — mode B: the `entity_ids_uri` and the resolved count. The discovered half only — no signals were specified. For a roster, the `entity_ids_uri` is the whole `roster_uri` (the audience across its groups) or a single group's set; a per-group read is mode B re-dispatched once per group's `entity_ids_uri`, the `group_label` naming each.

Narrate it plainly ("Reading who your 2.4M actually are — drawing a fixed sample and comparing its traits against the world…"). Track the dispatch as a session task; complete it on return.

### 2 — Render the dashboard

**The read carries section headings throughout** — each part below sits under its own labeled heading (**Summary**, **Your signals**, **Discovered**, **Skews**, **Freshness & band**, **Basis**), in both the rendered dashboard and the shareable report file, so the read scans as a structured document and a reader can jump to the part they want.

Open with **Summary** — the 3–5 sentence plain-English read seeded from the profiler's findings — facts about who these people are, no recommendation. Then the dashboard — the surface the user reads is a rendered visual per the render contract (`context/visuals.md`); the full read is captured in the shareable report file (written on request, step 3). The dashboard and the report both hold the profiler's halves, each under its heading:

- **Your signals** *(specified — search/signal flavors only)* — each stack signal by its share of the audience, and the **coverage** distribution: how many of your signals each person hits (most hit just one or two — that's a finding about how the signals overlap). Absent for the list flavor, which specified no signals.
- **Discovered** *(net-new — every flavor)* — **defining traits**: name · prevalence in the audience vs the world · lift, strongest first, under-represented included and labeled (what the audience *lacks* is a finding); stack-own signals are excluded here, so this is genuinely net-new. Plus the per-domain **breakdown**, with the **intent** panel surfaced by reach (top ~10) — intent over-indexes weakly, so it earns a by-size read, not a lift framing.
- **Skews** — one line each, only the real ones.
- **Freshness & band** — the intent share, and where measured reach sits in the band (or the headcount, for a profile), stated once.
- **Basis** — the basis line, always present: *"aggregates over a fixed sample of 5,000 of the 2.4M"* for the search/signal flavors (an aggregate without its basis reads as a census); *"aggregates over all 4,200 people in your list — the whole set, no sampling"* for the list flavor (there it *is* a census of the set — say so).

Author the dashboard as a data-only visual: the sections under their labeled headings — Your signals and Discovered (the two halves), Skews, Freshness & band, and the Basis line in the frame, with Summary leading — a prevalence-vs-world bar and the lift figure beside each defining trait, your-signal shares and the coverage spread, the freshness mix. Show how the read was produced, one line: sample → your-signals membership + trait aggregation (intent split out, geo excluded when fenced) → lift against the world.

### 3 — End at the next decision, and the report on request

One question — landed per the render contract — does this audience read right? The real options, when they fit: **re-pivot** (back into the `audience-generate` step, or back into the leaf's own pivot — the read is the evidence: drop a signal dragging in the wrong people, add an angle that's missing), **save the shareable report** (write the read to a self-contained file — the deliverable for a profile, and offered for any read), **export it** (the `audience-activate` step), **read deeper** (a domain the dashboard didn't cover — a fresh dispatch), or done.

**The signal membership report (the default).** On the user's yes, assemble the profiler's read into a profile JSON — `specified`, `coverage`, `discovered`, `breakdown` (the profiler returns these field names already) — author the 3–5 sentence executive summary, and run the shared report script (`build_report_membership.py` — the default two-section signal membership report; future report types are `build_report_<name>.py` siblings). It lives in **this `audience-analyze` skill's directory** (not the leaf's), so any leaf runs it at `${CLAUDE_PLUGIN_ROOT}/skills/audience-analyze/scripts/build_report_membership.py`; locate it if the runtime relocated the files. For a **discovered-only** read (the list flavor), pass `--no-specified` so the report drops the your-signals section:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/audience-analyze/scripts/build_report_membership.py" --profile /tmp/profile.json \
  --title "<client> — in-market buyers, <geo short>" \
  --location-label "<human geo>" --expression "<human-readable expression>" \
  --headcount <full reach or resolved count> --sample <sample size> \
  --workflow-id <W> --gates '{"must_have":[…],"exclusion":[…]}' \
  --summary "<exec summary>" \
  [--no-specified] \
  --out-html ./<client>_membership_report_<YYYYMMDD>.html \
  --out-json ./<client>_membership_report_<YYYYMMDD>.json
```

It writes a self-contained HTML report (no JavaScript, no CDN — opens offline, aggregates only, no PII) plus a JSON audit. Write the deliverable into the **working directory** — a durable, discoverable home — not a temp path the OS can sweep; only the throwaway `--profile` input lives in `/tmp`. Surface the absolute path. For the *standard* report the math, filters, and layout are the script's — don't hand-rebuild what it already renders.

**A custom report, on request.** When the user wants something the standard report doesn't give — a different cut, extra or fewer stats, their own framing or layout — author a bespoke one on the fly: a self-contained HTML file (no JavaScript, no CDN, opens offline) crafted for the ask, written to the working directory. Two rules keep it honest: **every figure traces to the profiler's aggregates** — the `specified`/`coverage`/`discovered`/`breakdown` you already hold, or a fresh `audience-profiler` dispatch for a cut it didn't cover, never a number you invented — and it stays **aggregates-only — no row, no PII**, like the standard one. The script is the consistent default; this is the escape hatch when the user asks for more.

Then record the run (silent plumbing — don't mention it), with `last_workflow` set to the leaf that ran:

```bash
STATE_DIR="${CLAUDE_PLUGIN_DATA:-${HOME}/.claude/plugins/data/watt}"
mkdir -p "$STATE_DIR"
cat > "$STATE_DIR/state.json" <<EOF
{
  "version": 1,
  "first_run_complete": true,
  "completed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "last_workflow": "audience-analyze-<search|signal|list>"
}
EOF
```

## How to behave

- **One question, then route.** If the way in is clear from the ask, route without the question. Never start the work here — no trait searches, no dispatch, no render; a router that "helps a little first" becomes a second copy of the leaf.
- **Name what v1 doesn't do, before the leaf has to.** Audiences are US-only, adults-only, person-only; employer/job-title as the defining criterion redirects to interest/demographic/location framing. Catching these at the door beats a dead end two steps in.
- **Narrate the dispatch and report the return** in one plain line each — never the structured payload. (Binds the leaves, which own the dispatch.)
- **Facts, not verdicts.** The dashboard says who the audience reaches; whether that's *right* is the user's call. Never grade the audience.
- **Aggregates in, aggregates out — including the file.** No record, identifier, or PII ever — that's distinct from activate's lane. The sample stays in the advisor's pass, never the workspace.

## Refuse cleanly

- **"Show me some of the actual people."** *"Analyze reads the audience as aggregates — individual people only exist downstream, in the export, and the activate step will confirm scale and identifiers with you first."*
- **"Just tell me if it's good."** Give the facts and where they're strong or thin; the call is theirs.
- **An export-shaped ask** ("push it to Meta") → that's `audience-activate`, named honestly; this step reads, it doesn't export.

## Failure modes

- **A tool error mid-read.** The profiler halts and surfaces it; render what completed, name what didn't — never fill a dashboard band with plausible numbers.
- **`python3` missing or `build_report_membership.py` fails.** Say so and offer the in-chat dashboard as the fallback — never hand-assemble the HTML to stand in for the script.
- **A leaf can't reach a built audience** (the user expected one in session and there isn't) → route to `audience-generate` honestly rather than reading an empty set.
- **A Signal Graph call fails on a connection or authentication problem** — including a worker that comes back reporting the connector isn't authenticated. That's not a transient to retry and not yours to work around: don't loop the connect or `authenticate` / `complete_authentication` tools, don't go diagnosing the connector or the MCP registry, and don't press on. Stop and come back to the user with the fix per the orientation's *Getting connected* note — the connect path, the setup docs (https://wattdata.ai/docs/get-started/quickstart), and the Claude organization guide to send their admin (https://wattdata.ai/docs/integrate/claude-organization), always.
