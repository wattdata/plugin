---
name: audience-activate
description: Export a built audience as a platform-ready file — confirms the platform, the scale, and the identifier types with the user, then materializes the audience and runs the deterministic writer script, returning the finished file and honest row counts. Meta, Google, and Reddit are the supported platforms. Never runs unconfirmed. Not a user command — /watt:audience is the front door. Use when an export-shaped ask arrives — "export it", "push it to Meta", "push it to Google", "push it to Reddit", the audience as a file.
user-invocable: false
compatibility: Designed for Claude Cowork, Claude Code, or Agent SDK. Requires the signal-graph MCP connector.
---

# Activate an audience

## Purpose

`audience-activate` — the export step behind `/watt:audience` — turns a built audience into the deliverable: a file shaped to the target platform's spec by its bundled writer script — one script per platform under `scripts/writers/`. The writer scripts present are the platforms that ship — **Meta, Google, and Reddit**, each its own self-contained writer script. The user picks the platform and confirms exactly what will happen, and walks away with the file, its row counts, and the reproducibility handle.

**Nothing exports unconfirmed.** Before any dispatch, state plainly: the platform, roughly how many people, which identifier types ride along, what the platform's spec does to them, and the exact row ceiling. Each platform's writer owns that transform, and they differ — confirm the one the user picked: a **Meta** file **hashes** emails, phones, names, cities, states, zips, and country, with mobile-ad IDs riding raw (the one identifier Meta keeps in the clear); a **Google** file hashes emails, phones, and names but keeps country and zip **in the clear**, with mobile device IDs written to a separate unhashed list; a **Reddit** file hashes emails and takes mobile-ad IDs raw, both in one combined list. The user's explicit yes — including that number — is the gate. Anything truncated or pruned is named **before** the run, never discovered after.

## Works with

- **Called by:** the `/watt:audience` router, or a sibling leaf's offer (`audience-generate` at its landing, `audience-analyze` at its closing question) — with a built signal stack or a roster in session, or a re-supplied audience record.
- **Dispatches:** **`audience-activator`** — the confirmed audience (a signal stack's `expression_string`, or a roster's `entity_ids_uri`), ceiling, and writer-script path → pages pulled (or IDs enriched), transform run, file paths and row counts back. The platform's writer script (`scripts/writers/<platform>.py`) owns hashing and layout.
- **Hands off to:** `audience-analyze` — offered after delivery if the user hasn't had the read; another run for a different slice stays here.

## Language

This surface says *export*, *hashed* — and explains the hashing once, plainly: *"Export files carry hashed identifiers — your file holds digests, not raw emails, except the fields the platform reads in the clear."* (Meta hashes everything but the mobile-ad ID; Google leaves country and zip in the clear and lists device IDs unhashed; Reddit hashes emails and takes mobile-ad IDs raw.) It also names the **expected audience size** the honest way — the real-people range the platform will likely reach from this file, shown as a count, never a percentage or a guarantee (the full posture is below). Watt's word is *audience size*, never *match rate* — if the user arrives with "match rate," recognize it and answer in audience-size terms, never adopt it. The stack vocabulary (signals, must-haves, exclusions) carries over from generate; AND/OR/AND_NOT still never reach the user.

## Entry

- **A built signal stack is in session** (fresh from generate or analyze). Preflight network access (flow step 1), then go to the confirmation (flow step 2).
- **A re-supplied audience record** — read from the saved record file in the working directory, or pasted in: signals with names and hashes by role group, plus reach, from a past session. Take it as given: its role groups reconstruct the expression exactly as built — a deterministic reading, not a modification — its `location:` line carries the fence the run re-applies (`none (national)` means no filter — dropping the line would silently widen the export), its `entity_type` rides into the dispatch, and its reach is "measured then" until the run re-measures. **A refresh-shaped re-supply** ("re-run this export") is exactly this path — the materialization is the refresh — and after delivery, **re-write the audience record** per the record contract (`context/record.md`) with today's measured total against the header's original target and the `· refreshed` suffix (`reach 26.1M (band 1M–5M) · refreshed`), so the user walks away with the updated recipe alongside the export file.
- **A roster** — from any roster-emitting strategy (grouping or crossing from `audience-generate-search`; expand or overlay from `audience-generate-list`): an ID-only entity set already chosen, with classification columns that vary by strategy. **Grouping** gives ranked groups (`group_label`, `cell_lift`, `cell_size`, `rank`; `roster_uri` for the whole, an `entity_ids_uri` per group). **Overlay** gives a **ranked list** (`overlay_score`, `signals_matched`, `rank` — rows, not groups). **Crossing** and **expand** give an **unordered membership set** — no rank, no groups (crossing: `entity_id` + `source_provenance`; expand: `entity_id` + match confidence columns). Whichever it is, the entities are already chosen — there's no expression to materialize; the export shape is the choice (the confirmation, flow step 2). Take the record as given; never re-rank, re-group, or re-score it.
- **A signal pool** (an `/watt:explore` session's kept signals, or a lookalike pool) with an export intent. A pool has no expression yet — **auto-compose it to the default stack first**: pool-marked must-haves *all-of*, exclusions *none-of*, the rest *any-of*; **if the pool carries no role markers, ask once** (*"any must-haves or must-have-nots, or export them all as one group?"*) before composing. A deterministic reading of the user's picks (the same operation as reconstructing a record's role groups), never a strategy compose — note plainly that a *tuned* build is `audience-generate`'s lane if they want it. Measure the headcount once (count-only), then go to the confirmation with that real number.
- **No audience anywhere.** Nothing to export — route to the `audience-generate` step honestly.
- **A platform with no writer script** ("push to TikTok"). Say what ships today — Meta, Google, and Reddit — before anything else; offer a shipped-platform run if it serves.

## The flow

The preflight (step 1) precedes **every** path in — a built stack, a re-supplied record, a roster, or a pool — before any confirmation or number reaches the user.

### 1 — Preflight: confirm the export's tools are reachable

The export runs through the Signal Graph's download/upload tools (`generate_download_url`, `generate_upload_url`). So **before** naming the platform menu or quoting a number, confirm those tools are present on the connection and the connector is authenticated — check that the tools are *registered and available*, not by firing a probe call with placeholder arguments (a missing-argument or validation error isn't a connection failure, and acting on it would push a connected user into the connect flow wrongly). This is cheap, and it spares the user from authorizing an export that then dies because the connector was never live.

What this catches is a missing or unauthenticated connector — caught up front, here. What it **cannot** catch is the code-execution network-egress block: those tools return a presigned URL successfully even when egress is denied, so that failure only surfaces later, when the activator fetches the artifact — and it's handled at pull time by its own entry in [Failure modes](#failure-modes), not here.

- **Tools present, connector authenticated** → note it in a line and move to the platform pick.
- **Tools absent, or a call comes back unauthenticated** → you don't have a live connection to run the export. Stop here, before any confirmation; don't retry blindly, don't loop the auth tools, and don't improvise a local file. Send the user to `/watt:configure` to get the connection fixed — it owns the connect path and the recovery docs. Then have them re-run once it's connected.

### 2 — Pick the platform, confirm with the real numbers

Resolve the platform from what's actually shipped. The writer scripts bundled at `${CLAUDE_PLUGIN_ROOT}/skills/audience-activate/scripts/writers/<platform>.py` are the platform menu — list them with `ls "${CLAUDE_PLUGIN_ROOT}/skills/audience-activate/scripts/writers/"` (a name beginning with `_`, like `_common.py`, is shared plumbing, not a platform): today that's **Meta, Google, and Reddit**, so the platform is the user's **first pick** — name the menu and let them choose before anything else. Then `python3 "${CLAUDE_PLUGIN_ROOT}/skills/audience-activate/scripts/writers/<platform>.py" --list-identifiers` gives the identifier list you confirm — for Meta and Google: email, phone, name, address, maid; for Reddit: email, maid — the script being the source of truth, not memory.

Work out the ceiling honestly: the server's export budget caps a five-identifier pull at **600,000 rows per run** — so the ceiling is the smallest of the audience's measured reach, the user's own number, and 600,000. If reach exceeds what one run can carry, that's said **now** ("your audience is 2.4M; one export run carries up to 600K of it").

**A roster adds one choice — the export shape**, and the roster's classification bounds what's offered:

- **The whole set** — one file over the entire `roster_uri` (capped at the run budget). Always available; for a membership-only roster (crossing's qualified set, expand's widest match — no rank, no groups) it's the shape — there's nothing to take a "top-N" of, and no groups to split.
- **Top-N by rank** — the best-ranked slice as one file. **Only when the roster carries a `rank`** (grouping and overlay today) — never offered for an unranked membership set. For a grouped roster the slice is the top groups (e.g. "the top 5 groups, ~190K people" — the combined entity-ID set of those groups); for an overlay roster it's the top rows (e.g. "the top 500 by score"). One activator dispatch over the chosen set.
- **One file per group** — a file per group, the `group_label` naming each (e.g. five files, one per metro). One activator dispatch per group's `entity_ids_uri`, each capped by the same 600K-per-run budget. **Only when the roster has groups** (the grouping objective).

Name the shape choice in the confirmation alongside platform, scale, and identifiers — for one-file-per-group, the scale is per file and the file count is part of what the user authorizes.

Then the gate — landed per the render contract (`context/visuals.md`) — one decision, all the facts in it. State the chosen platform's actual transform; they differ, so confirm the right one. Each gate also carries the **expected audience size** — of the people in this run, roughly how many the platform will likely reach on its side — computed from the run's people ceiling by `audience_size_range.py`, this skill's own range script (`python3 "${CLAUDE_PLUGIN_ROOT}/skills/audience-activate/scripts/audience_size_range.py" <people_ceiling>` → the rounded `low–high` count to quote). It's a platform-side estimate set in real people, **never a percentage** and never a guarantee — see [expected audience size](#expected-audience-size-the-posture-we-hold):

> **Meta** — Exporting **weekend hikers**, reach 2.4M, this run pulls up to **600,000 people** with email, phone, name, address, and mobile-ID identifiers, written into a Meta file (PII hashed; mobile-ad IDs raw, as Meta reads them in the clear). People with no email, phone, or mobile-ad ID are dropped (Meta has no way to reach them). Of these, your expected audience size on Meta is **~300K–480K** people — a platform-side estimate, not a guarantee. Go?

> **Google** — Exporting **weekend hikers**, reach 2.4M, this run pulls up to **600,000 people** into a Google file (emails, phones, and names hashed; country and zip in the clear; mobile device IDs written to a separate unhashed list). People Google can't match — no email, phone, mailing address, or device ID — are dropped (nothing left for Google to reach them by). Of these, your expected audience size on Google is **~300K–480K** people — a platform-side estimate, not a guarantee. Go?

> **Reddit** — Exporting **weekend hikers**, reach 2.4M, this run pulls up to **600,000 people** into a Reddit file (emails hashed, mobile-ad IDs raw, both in one combined list). People with no email or device ID are dropped (nothing left for Reddit to reach them by). Of these, your expected audience size on Reddit is **~300K–480K** people — a platform-side estimate, not a guarantee. Go?

An explicit yes including the number is the only thing that opens the gate. "Just do it" without the scale on screen is not a confirmation — put the numbers up and ask once.

### 3 — Dispatch the export

Dispatch `audience-activator` with the confirmed platform, the confirmed ceiling, the location, the artifact's `workflow_id`, and the writer script path from step 2 (`${CLAUDE_PLUGIN_ROOT}/skills/audience-activate/scripts/writers/<platform>.py`) — plus the audience itself, in whichever form the input takes:

- **A signal stack** — the `expression_string` exactly as built.
- **A roster** — the `entity_ids_uri` for the set the user confirmed, never an expression. **The whole set**: one dispatch over the full `roster_uri` (the shape for an unranked crossing set). **Top-N by rank** (ranked rosters only): one dispatch over the entity-ID set of the chosen top-N — the combined set of the chosen groups (grouped roster) or the top rows (overlay roster) — with the slice named as the activator's `output_label` (e.g. `top_5_groups`, `top_500_by_score`). **One file per group** (grouped rosters only): one dispatch per group's `entity_ids_uri`, passing that group's `group_label` as the activator's `output_label` — the label prefixes the file's name and rides back in the return's `files` entry, which is what anchors each delivered file to its group across the loop. Confirm the file count is within reason before looping, and narrate each. (Classification columns don't ride through enrichment — the writer reads identifier columns only; group identity travels as the dispatch's `output_label`, never as a column in the platform file.)

Narrate its progress as it reports — pages pulled, transform running, counts moving. Track the dispatch as a session task; complete it on return.

### 4 — Deliver, with the gaps named

Render the return:

- **The file(s)** — path and row count of **each** file the writer produced. Some platforms emit more than one, and row counts differ by file: Meta writes one `meta_audience.csv` whose rows can exceed persons (one row per identifier pair); Google writes two — `google_audience.csv` (one row per person) and `google_audience_maid.csv` (the device-ID list, a separate match path, so its count differs from the person file); Reddit writes one `reddit_audience.csv`, one row per identifier (each email and each device ID on its own row), so its count exceeds persons. Report every file, not just the first.
- **The reconciliation** — total resolved vs exported, with any unmatchable persons the writer skipped named. A shortfall the user didn't hear about before the run is a failure; repeat it here regardless.
- **The expected audience size** — of the people exported, roughly how many the platform will likely reach on its side, from `audience_size_range.py` on the **actual exported people count** — the people actually written, not file rows (Meta's rows can exceed persons) — `python3 "${CLAUDE_PLUGIN_ROOT}/skills/audience-activate/scripts/audience_size_range.py" <exported_people>`. State it in real people, never a percentage: *"Of the 600,000 people in your file, your expected audience size on the platform is ~300K–480K."* Then the one-line posture, plainly: that linked share is the platform's own measure of who it already has on its side, **not** a measure of these people's realness or this audience's accuracy; every exported row is a real person, and one the platform doesn't reach just isn't on its side. If the user wants a larger reached audience, name the levers honestly: more identifier types per person, fresher identifiers, and meeting the platform's own list-size minimum. See [expected audience size](#expected-audience-size-the-posture-we-hold) for the full posture and the lines we won't cross.
- **The verification line** — the activator's shape-check conclusion (each output file's header matches the platform's spec, with identifier fields digested where the spec hashes them and plaintext where it doesn't).
- **The handles** — `workflow_id` (the same export, reproducible) and the raw page URLs (1-hour traceability; they carry the unhashed identifier values if the user needs those — the platform file is the deliverable).

Offer the natural next steps in one line: another run for a different slice, an `audience-analyze` read if they haven't had one, or done.

## Expected audience size: the posture we hold

When the file is uploaded, the platform reaches only the share of the people in it that it already has on its own side. It's always below the count we handed over, and what drives it sits largely outside Watt: the platform's own identity graph, the customer's ad account, how fresh the identifiers are, the channel. **Watt's language for that reached share is the expected audience size** — a real-people range, always. (The platform's dashboard calls the same thing a *match rate* and shows it as a percentage; if the user arrives with that word, answer in audience-size terms — recognize it, don't adopt it.) Hold one honest posture, every run:

- **What it is, and isn't.** The reached share is the *platform's* measure — who that platform already has on its side — **not** a measure of Watt's data quality or this audience's accuracy. Two platforms will reach different amounts of the identical file; that's about them, not the people.
- **Set it in real people, never a percentage.** We don't quote a percentage — a number we don't control, and one that anchors expectations on the platform's side. We show the **expected audience size** for this export's size (`scripts/audience_size_range.py`, the single source of the band), so the read is "of these N people, your expected audience size is X–Y" — concrete, and clearly an estimate.
- **A non-reached row is not a wasted record.** The person is real and correctly in the audience; the platform simply doesn't have them on its side. An unreached row is the platform's coverage gap, not a wrong or junk record.
- **The levers a customer actually has.** More identifier types per person (an email *and* a phone *and* a mobile ID reach more often than any one alone), fresher identifiers, and meeting the platform's list-size minimum. Hashing format is **not** a customer lever — the writer script produces exactly the digest each platform matches on, so a "wrong hash" can't cost reach here.
- **The line we will not cross.** Never guarantee an audience size or a reached count. Never imply Watt's counts equal deliverable reach on a platform — the exported count is real people; how many it reaches is the platform's to report. Promise the audience is real and correctly built; never promise how much of it a given platform will reach.

## How to behave

- **The gate is the product.** Every fact in the confirmation — platform, count, identifiers, what the spec does to them, who gets dropped — is there because the user is authorizing a real export at real scale. Never soften, batch, or skip it; never treat an earlier session's yes as this run's yes.
- **Counts, paths, conclusions in chat; rows in the file.** The deliverable carries the data — quoting records into the transcript adds nothing. The activator holds the same line.
- **Name every gap before and after.** Budget clamps, unmatchable persons skipped, a total beyond the ceiling — said before the run, reconciled after it. A silent shortfall shipped as complete is this surface's worst failure.
- **The script is the spec.** Hashing and layout live in the platform's writer script; neither you nor the activator ever narrates, re-implements, or patches them. A transform change is a plugin change, not a runtime favor.
- **Narrate dispatches and report returns** in one plain line each — never the structured payload.

## Refuse cleanly

- **"Skip the hashing / give me the raw emails."** The Meta file is hashed because that's the form Meta requires — a raw file would be rejected. The raw page URLs from the run carry the unhashed values for an hour; point there.
- **A platform with no writer script.** *"Meta, Google, and Reddit are the supported platforms."* Don't improvise a CSV "close enough" for another platform — its layout and hashing rules differ, and a wrong file shrinks the audience the platform can reach.
- **"Export it all" past the budget.** The 600K-per-run ceiling is the server's export budget, not a preference — offer the run at the ceiling, honestly framed.
- **"Guarantee me an X% match" / "promise these will all match."** No — how much a platform reaches is the platform's to report, driven by factors outside Watt (see [expected audience size](#expected-audience-size-the-posture-we-hold)). Recognize the "match" framing, answer in audience-size terms: give the honest expected audience size and the real levers; never a guaranteed rate or count, and never imply our counts equal what the platform will reach.
- **An export with no built audience.** Generate first — there's nothing confirmed to pull.

## Failure modes

- **A page fails or expires mid-run.** The activator halts and surfaces it; tell the user what was pulled and that no file was produced from a partial pull. Re-running with the same `workflow_id` is the recovery.
- **A Signal Graph call fails on a connection or authentication problem** — including the activator coming back reporting the connector isn't authenticated. This is the connector itself, not the egress block below: that's not a transient to retry and not yours to work around — don't loop the connect or `authenticate` / `complete_authentication` tools, don't go diagnosing the connector or the MCP registry, and don't press on. Stop and send the user to `/watt:configure` to get the connection fixed — it owns the connect path and the recovery docs.
- **Network egress blocks the download (Cowork, a Team or Enterprise org).** In Cowork the transform runs in the code-execution sandbox, which enforces the org's network-egress policy; when that policy blocks the Watt artifact storage, the activator can't pull the page and halts. Don't retry or improvise a local file — the artifact URL is presigned and rotates, so allowlisting one domain won't hold; egress has to be opened fully, an org-admin setting and the only fix. Hand the user the path and a line to forward to their admin, then have them re-run here once it's open:
  - **The admin opens egress** in **Organization settings → Capabilities → Code execution → Allow network egress** (https://claude.ai/admin-settings/capabilities): set the **Domain allowlist** to **All domains**, then save. A line to forward: *"In our Claude organization settings, set Code execution → Allow network egress → Domain allowlist to All domains."*
  - **It takes effect on a new session.** After saving, the user closes and reopens Cowork — the policy applies only to a fresh session — then re-runs. If it still fails, fully log out of Claude and back in, then re-run.
- **The server rejects the request over its cost budget.** It suggests a lower limit — bring that number back to the user as a fresh confirmation; never lower it silently, and never change the expression to chase a smaller count.
- **The script errors.** Surface its message and stop; the transform is never hand-finished.
- **The confirmation gate must be answered.** However it lands per the render contract, nothing runs until the user answers it.
