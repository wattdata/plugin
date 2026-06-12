---
name: audience-activate
description: Export a built audience as a platform-ready file — confirms the platform, the scale, and the identifier types with the user, then materializes the audience and runs the deterministic writer script, returning the finished file and honest row counts. Meta Customer Match and Google Customer Match are the supported platforms. Never runs unconfirmed. Not a user command — /watt:audience is the front door. Use when an export-shaped ask arrives — "export it", "push it to Meta", "push it to Google", the audience as a file.
user-invocable: false
compatibility: Talks to the remote Watt MCP server — network access and browser OAuth on the first tool call. python3 runs the bundled writer script. Inline visuals and the closing decision follow the render contract (`context/visuals.md`), degrading gracefully where the host can't render or return a pick.
---

# Activate an audience

## Purpose

`audience-activate` — the export step behind `/watt:audience` — turns a built audience into the deliverable: a file shaped to the target platform's spec by its bundled writer script — one script per platform under `scripts/writers/`. The writer scripts present are the platforms that ship — **Meta Customer Match and Google Customer Match**, each its own self-contained writer script. The user picks the platform and confirms exactly what will happen, and walks away with the file, its row counts, and the reproducibility handle.

**Nothing exports unconfirmed.** Before any dispatch, state plainly: the platform, roughly how many people, which identifier types ride along, what the platform's spec does to them, and the exact row ceiling. Each platform's writer owns that transform, and they differ — confirm the one the user picked: a **Meta** file **hashes** emails, phones, names, cities, states, zips, and country, with mobile-ad IDs riding raw (Meta's one unhashed match key); a **Google** file hashes emails, phones, and names but keeps country and zip **in the clear**, with mobile device IDs written to a separate unhashed list. The user's explicit yes — including that number — is the gate. Anything truncated or pruned is named **before** the run, never discovered after.

## Works with

- **Called by:** the `/watt:audience` router, or a sibling leaf's offer (`audience-generate` at its landing, `audience-analyze` at its closing question) — with a built signal stack or a roster in session, or a re-supplied audience record.
- **Dispatches:** **`audience-activator`** — the confirmed audience (a signal stack's `expression_string`, or a roster's `entity_ids_uri`), ceiling, and writer-script path → pages pulled (or IDs enriched), transform run, file paths and row counts back. The platform's writer script (`scripts/writers/<platform>.py`) owns hashing and layout.
- **Hands off to:** `audience-analyze` — offered after delivery if the user hasn't had the read; another run for a different slice stays here.

## Language

This surface says *export*, *Customer Match*, *hashed* — and explains the hashing once, plainly: *"Customer Match files carry hashed identifiers — your file holds digests, not raw emails, except the fields the platform matches in the clear."* (Meta hashes everything but the mobile-ad ID; Google leaves country and zip in the clear and lists device IDs unhashed.) The stack vocabulary (signals, must-haves, exclusions) carries over from generate; AND/OR/AND_NOT still never reach the user.

## Entry

- **A built signal stack is in session** (fresh from generate or analyze). Go to the confirmation (flow step 1).
- **A re-supplied audience record** — signals with names and hashes by role group, plus reach, from a past session. Take it as given: its role groups reconstruct the expression exactly as built — a deterministic reading, not a modification — its `location:` line carries the fence the run re-applies (`none (national)` means no filter — dropping the line would silently widen the export), its `entity_type` rides into the dispatch, and its reach is "measured then" until the run re-measures. **A refresh-shaped re-supply** ("re-run this export") is exactly this path — the materialization is the refresh — and after delivery, **re-emit the audience record** with today's measured total against the header's original target and the `· refreshed` suffix (`reach 26.1M (band 1M–5M) · refreshed`), so the user walks away with the updated recipe alongside the file.
- **A roster** — from any roster-emitting strategy (grouping or crossing from `audience-generate-search`; expand or overlay from `audience-generate-list`): an ID-only entity set already chosen, with classification columns that vary by strategy. **Grouping** gives ranked groups (`group_label`, `cell_lift`, `cell_size`, `rank`; `roster_uri` for the whole, an `entity_ids_uri` per group). **Overlay** gives a **ranked list** (`overlay_score`, `signals_matched`, `rank` — rows, not groups). **Crossing** and **expand** give an **unordered membership set** — no rank, no groups (crossing: `entity_id` + `source_provenance`; expand: `entity_id` + match confidence columns). Whichever it is, the entities are already chosen — there's no expression to materialize; the export shape is the choice (flow step 1). Take the record as given; never re-rank, re-group, or re-score it.
- **A signal pool** (an `/watt:explore` session's kept signals, or a lookalike pool) with an export intent. A pool has no expression yet — **auto-compose it to the default stack first**: pool-marked must-haves *all-of*, exclusions *none-of*, the rest *any-of*; **if the pool carries no role markers, ask once** (*"any must-haves or must-have-nots, or export them all as one group?"*) before composing. A deterministic reading of the user's picks (the same operation as reconstructing a record's role groups), never a strategy compose — note plainly that a *tuned* build is `audience-generate`'s lane if they want it. Measure the headcount once (count-only), then go to the confirmation with that real number.
- **No audience anywhere.** Nothing to export — route to the `audience-generate` step honestly.
- **A platform with no writer script** ("push to TikTok"). Say what ships today — Meta and Google — before anything else; offer a shipped-platform run if it serves.

## The flow

### 1 — Pick the platform, confirm with the real numbers

Resolve the platform's writer script first — `scripts/writers/<platform>.py` in this skill's own directory (today that's `scripts/writers/meta.py` and `scripts/writers/google.py`; if the runtime relocated the files, locate it before promising anything). The `<platform>.py` scripts present are the platform menu (a file whose name begins with `_`, like `_common.py`, is shared plumbing — never a platform): today that's **Meta and Google**, so the platform is the user's **first pick** — name the menu and let them choose before anything else. Run `python3 <script> --list-identifiers` and use its answer — for both Meta and Google: email, phone, name, address, maid — as the identifier list you confirm; the script is the source of truth, not memory.

Work out the ceiling honestly: the server's export budget caps a five-identifier pull at **600,000 rows per run** — so the ceiling is the smallest of the audience's measured reach, the user's own number, and 600,000. If reach exceeds what one run can carry, that's said **now** ("your audience is 2.4M; one export run carries up to 600K of it").

**A roster adds one choice — the export shape**, and the roster's classification bounds what's offered:

- **The whole set** — one file over the entire `roster_uri` (capped at the run budget). Always available; for a membership-only roster (crossing's qualified set, expand's widest match — no rank, no groups) it's the shape — there's nothing to take a "top-N" of, and no groups to split.
- **Top-N by rank** — the best-ranked slice as one file. **Only when the roster carries a `rank`** (grouping and overlay today) — never offered for an unranked membership set. For a grouped roster the slice is the top groups (e.g. "the top 5 groups, ~190K people" — the combined entity-ID set of those groups); for an overlay roster it's the top rows (e.g. "the top 500 by score"). One activator dispatch over the chosen set.
- **One file per group** — a file per group, the `group_label` naming each (e.g. five files, one per metro). One activator dispatch per group's `entity_ids_uri`, each capped by the same 600K-per-run budget. **Only when the roster has groups** (the grouping objective).

Name the shape choice in the confirmation alongside platform, scale, and identifiers — for one-file-per-group, the scale is per file and the file count is part of what the user authorizes.

Then the gate — landed per the render contract (`context/visuals.md`) — one decision, all the facts in it. State the chosen platform's actual transform; the two differ, so confirm the right one:

> **Meta** — Exporting **weekend hikers**, reach 2.4M, this run pulls up to **600,000 people** with email, phone, name, address, and mobile-ID identifiers, written into a Meta Customer Match file (PII hashed; mobile-ad IDs raw, as Meta matches them). People with no email or phone are dropped (Meta can't match them). Go?

> **Google** — Exporting **weekend hikers**, reach 2.4M, this run pulls up to **600,000 people** into a Google Customer Match file (emails, phones, and names hashed; country and zip in the clear; mobile device IDs written to a separate unhashed list). People with no email, phone, or device ID are dropped (nothing left for Google to match). Go?

An explicit yes including the number is the only thing that opens the gate. "Just do it" without the scale on screen is not a confirmation — put the numbers up and ask once.

### 2 — Dispatch the export

Dispatch `audience-activator` with the confirmed platform, the confirmed ceiling, the location, the artifact's `workflow_id`, the script's absolute path, and the prune choice — plus the audience itself, in whichever form the input takes:

- **A signal stack** — the `expression_string` exactly as built.
- **A roster** — the `entity_ids_uri` for the set the user confirmed, never an expression. **The whole set**: one dispatch over the full `roster_uri` (the shape for an unranked crossing set). **Top-N by rank** (ranked rosters only): one dispatch over the entity-ID set of the chosen top-N — the combined set of the chosen groups (grouped roster) or the top rows (overlay roster) — with the slice named as the activator's `output_label` (e.g. `top_5_groups`, `top_500_by_score`). **One file per group** (grouped rosters only): one dispatch per group's `entity_ids_uri`, passing that group's `group_label` as the activator's `output_label` — the label prefixes the file's name and rides back in the return's `files` entry, which is what anchors each delivered file to its group across the loop. Confirm the file count is within reason before looping, and narrate each. (Classification columns don't ride through enrichment — the writer reads identifier columns only; group identity travels as the dispatch's `output_label`, never as a column in the platform file.)

Narrate its progress as it reports — pages pulled, transform running, counts moving. Track the dispatch as a session task; complete it on return.

### 3 — Deliver, with the gaps named

Render the return:

- **The file(s)** — path and row count of **each** file the writer produced. Some platforms emit more than one, and row counts differ by file: Meta writes one `meta_audience.csv` whose rows can exceed persons (one row per identifier pair); Google writes two — `google_audience.csv` (one row per person) and `google_audience_maid.csv` (the device-ID list, a separate match path, so its count differs from the person file). Report every file, not just the first.
- **The reconciliation** — total matched vs exported vs pruned, each named. A shortfall the user didn't hear about before the run is a failure; repeat it here regardless.
- **The verification line** — the activator's shape-check conclusion (each output file's header matches the platform's spec, with identifier fields digested where the spec hashes them and plaintext where it doesn't).
- **The handles** — `workflow_id` (the same export, reproducible) and the raw page URLs (1-hour traceability; they carry the unhashed identifier values if the user needs those — the platform file is the deliverable).

Offer the natural next steps in one line: another run for a different slice, an `audience-analyze` read if they haven't had one, or done. Then record the run (silent plumbing — don't mention it):

```bash
STATE_DIR="${CLAUDE_PLUGIN_DATA:-${HOME}/.claude/plugins/data/watt}"
mkdir -p "$STATE_DIR"
cat > "$STATE_DIR/state.json" <<EOF
{
  "version": 1,
  "first_run_complete": true,
  "completed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "last_workflow": "audience-activate"
}
EOF
```

## How to behave

- **The gate is the product.** Every fact in the confirmation — platform, count, identifiers, what the spec does to them, prune — is there because the user is authorizing a real export at real scale. Never soften, batch, or skip it; never treat an earlier session's yes as this run's yes.
- **Counts, paths, conclusions in chat; rows in the file.** The deliverable carries the data — quoting records into the transcript adds nothing. The activator holds the same line.
- **Name every gap before and after.** Budget clamps, pruned persons, a total beyond the ceiling — said before the run, reconciled after it. A silent shortfall shipped as complete is this surface's worst failure.
- **The script is the spec.** Hashing and layout live in the platform's writer script; neither you nor the activator ever narrates, re-implements, or patches them. A transform change is a plugin change, not a runtime favor.
- **Narrate dispatches and report returns** in one plain line each — never the structured payload.

## Refuse cleanly

- **"Skip the hashing / give me the raw emails."** The Meta file is hashed because that's what Meta matches on — a raw file would be rejected. The raw page URLs from the run carry the unhashed values for an hour; point there.
- **A platform with no writer script.** *"Meta and Google Customer Match are the supported platforms."* Don't improvise a CSV "close enough" for another platform — its layout and hashing rules differ, and a wrong file burns the user's match rate.
- **"Export it all" past the budget.** The 600K-per-run ceiling is the server's export budget, not a preference — offer the run at the ceiling, honestly framed.
- **An export with no built audience.** Generate first — there's nothing confirmed to pull.

## Failure modes

- **A page fails or expires mid-run.** The activator halts and surfaces it; tell the user what was pulled and that no file was produced from a partial pull. Re-running with the same `workflow_id` is the recovery.
- **The server rejects the request over its cost budget.** It suggests a lower limit — bring that number back to the user as a fresh confirmation; never lower it silently, and never change the expression to chase a smaller count.
- **The script errors.** Surface its message and stop; the transform is never hand-finished.
- **The confirmation gate must be answered.** However it lands per the render contract, nothing runs until the user answers it.
