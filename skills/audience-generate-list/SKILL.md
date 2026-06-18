---
name: audience-generate-list
description: Build a person audience from an owned list — customers, leads, accounts — resolving it to Watt entity IDs and emitting a roster, or learning what defines it and handing back a tunable signal pool. The list-anchored way into a build, behind /watt:audience. Four plays — resolve-only, expand (households via addresses), lookalike (the signals that define the list, to tune), overlay (score and rank against signals); group and traverse aren't built. Produces a roster of entity IDs or a signal pool — never an export, never contact data. Not a user command — /watt:audience is the front door. Use when a list arrives to build from — "match my customer list", "find more like my customers", "rank my list by intent", "score the people from my last run". A read intent is audience-analyze-list.
user-invocable: false
compatibility: Requires the remote Watt MCP server (network access).
---

# Build an audience from an owned list

## Purpose

`audience-generate-list` is the build leaf anchored on an **owned list** — the user arrives with people they already hold (customers, leads, accounts, engagement data), not a plain-English description of who to reach. It resolves that list to Watt entity IDs and emits a **roster**: the matched set, ready for the `audience-activate` and `audience-analyze` steps.

The "list" can already be resolved: **a roster from a prior pass** (a `workflow://` entity-IDs URI, or a pasted roster record) is the same anchor — people the user holds — just past the resolve step. It enters here to be **re-transformed**: overlay scores it, lookalike profiles it for its defining signals; the resolve is skipped, and the roster's classification columns ride along into the play (the play's *output* roster carries its own columns, per the worker contract). (Re-*expanding* a roster needs raw identifiers, which entity IDs alone don't carry — that's the export-addresses-then-expand round-trip below; grouping/crossing a roster aren't available here.)

The leaf is split from its sibling `audience-generate-search` by **input anchor** — an owned list here, a description there. The structural consequence is that elicitation starts from *what the list is*, not from "describe who you want to reach"; there is no discovery, no scoring, no composing.

**This leaf ships four plays.** Two **match the list** — resolve-only and expand, both resolution-driven, differing only in *how wide* the match is. One **learns from the list** — lookalike. One **scores the list** — overlay:

- **resolve-only ("matched / customer match")** — resolve the list to a **tight** matched set (the resolver's default floor), the people who are genuinely on the list. Dispatches `audience-resolver`; the roster classification is minimal (`source_provenance`).
- **expand ("the widest match set")** — resolve the list **wide**: every entity any identifier plausibly matches (Noisy-OR, 1:many), gated only by a floor that defaults to `0`. For maximum addressable reach — the wide roster feeds identifier maximalism at `audience-activate`. Dispatches `strategy-expand`; the roster carries each entity's match confidence and corroboration count.
- **lookalike ("more like them")** — don't match the list, *learn what defines it*. Resolve the seed, then profile it for the signals that set it apart — **durable identity by lift** (interests, affinity, demographics, life-stage) plus the **top intents by reach within the seed** — and hand that **signal pool** back for the operator to tune. Dispatches `audience-resolver` then `audience-profiler` (mode B); emits a curatable signal pool, **not** a roster. It builds no audience itself — the tuned pool carries into a compose.
- **overlay ("score / rank my list")** — resolve the list, then lay a pool of signals over the resolved set and **score each person** by how many of those signals they express (`overlay_score = Σ weightᵢ × matchᵢ`; weights default to `1`, so the default score is a plain count). Returns the whole list **ranked** — lead-scoring, "who's hot", prioritize-the-pipeline — and can optionally be cut to the matched slice (keep people expressing ≥ N signals — the *intersection*, "my list who also do X"). Unlike the other plays, overlay needs a **brief for the signal pool** — the brief defines the *layer to score by*, never the population (the list stays the population). Dispatches `audience-resolver`, then the parent's `signal-finder` / `signal-profiler` to build the scored pool, then `strategy-overlay` to score and rank.

**Households fall out of expand, they aren't a separate play.** Because an address resolves 1:many to everyone at it, an expand run whose match columns include addresses returns the **co-residents** — so household expansion is reachable today on an address-bearing list. From an email/phone-only list, the supported route is the **round-trip**: build the roster, export it with addresses via `audience-activate`, then feed those addresses back through expand. What's *not* built is a one-shot button that does the person→address enrichment inside this leaf (enrichment is the activator's lane), nor seed-vs-co-resident provenance tagging on the result.

The shared **group** / **traverse** strategies are **not available** in this leaf: name them honestly when asked, never build or dispatch them.

This is a thin delta over `audience-generate`: the unique work is getting the owned list to something the operator can build from — a **chainable entity-ID set** (resolve-only via `audience-resolver`, expand via `strategy-expand`), the **signals that define the list** (lookalike via `audience-profiler`), or the **scored-and-ranked list** (overlay via `strategy-overlay`). The parent's lane (build, not export; entity IDs only), language, and landing plumbing are composed with verbatim. The parent's full discover→score→**compose** spine still does **not** run here — a list isn't a brief, and no play composes a new set: lookalike *profiles the resolved seed* (the profiler's read of who's already on the list) and stops at the signal pool; **overlay** is the one play that runs a `signal-finder` / `signal-profiler` search — but over a brief that defines the *scoring layer*, never the population, and it scores the resolved list rather than composing a set.

## Works with

- **Routed from:** the `audience-generate` router, when the build starts from an **owned list** (the list anchor) rather than a description.
- **Dispatches:**
  - **`audience-resolver`** *(resolve-only play, and the lookalike seed-resolve)* — the supplied identifiers (inline) or a `csv_resource_uri`, plus the `entity_type` and a `workflow_id` → a `workflow://` entity-IDs URI and the counts (`input_identifier_count`, `resolved_count`, `below_floor_count`). The set-touching identity work lives in the advisor; this leaf never resolves identifiers itself and never sees a resolved record — only the URI and the counts come back.
  - **`strategy-expand`** *(expand play)* — the supplied identifiers (inline) or a `csv_resource_uri` **plus the `lookup_columns` mapping the leaf elicited** (which columns to match on; required on the CSV path), the `entity_type`, an overridable `quality_floor` (default `0`), and a `workflow_id` → a `workflow://` **roster** URI (columns `entity_id, match_confidence, match_criteria_count`), a small ID-only `sample`, and the `coverage` counts (`input_identifiers`, `resolved`, `below_floor`, `quality_floor`). The worker owns the wide `entity_resolve` 1:many pass and the dedupe/floor script; this leaf never resolves identifiers itself and never sees a resolved record — only the roster URI, the sample, and the counts come back. The leaf chooses the columns and (when a transform is needed) builds the artifact; the worker resolves against exactly the `lookup_columns` it's handed.
  - **`audience-profiler`** *(lookalike play, mode B)* — the seed's `entity_ids_uri` (from the resolver), the `entity_type`, and a `workflow_id` → a structured two-half read of the seed: the **durable identity by lift** (`discovered`) and the **top intents by reach within the seed** (the `breakdown` intent panel, tagged by size). The leaf runs it in **mode B (`entity_set`)** — an entity set, no signal stack — exactly as `audience-analyze-list` does; the advisor groups the **full** seed (never a sample — sparse intents need the whole set) and returns aggregates only. This leaf renders them as the tunable signal pool and never sees a record.
  - **`signal-finder` / `signal-profiler`** *(overlay play)* — the parent's discovery + scoring advisors, dispatched here to turn the overlay **brief** (the layer to score by — "in-market for X", "engaged with Y") into a resolved, scored **signal pool**. One angle per `signal-finder` dispatch; `signal-profiler` scores the pool by `trait_hash`, the brief as the grounding frame. The pool defines what to score the resolved list *against* — never who's on the list.
  - **`strategy-overlay`** *(overlay play)* — the resolved list (an `entity_ids_uri` from `audience-resolver`), the scored **signal pool** (expressions over `trait_hash`es), an optional per-signal `weights` map (the operator's; default every signal `1`), the `entity_type`, and a `workflow_id` → a `workflow://` **roster** URI (columns `entity_id, overlay_score, signals_matched, rank`), a small ID-only `sample`, and `coverage` (`source_size`, `scored`, `scored_zero`). The worker **only scores and ranks** — it returns the whole list, never cut; slicing to the intersection (keep `signals_matched ≥ N`) is this leaf's post-step. Weights flow operator → leaf → worker; the worker never elicits them.
- **Hands off to:** `audience-activate` (export the matched set — Meta, Google, or Reddit) and `audience-analyze` (read who the matched set is) — offered at the landing, on the user's say-so. For the **lookalike** play the deliverable is the tuned signal pool, not a matched set: hand it to **`audience-generate-search`** to compose into an audience (the working set pre-seeded — discovery skipped for what's already there, a landing mode picked there), or to **`audience-analyze`** to read it.

## Language

Inherits the parent's table; neither shipped play uses its boolean vocabulary. The terms this leaf owns:

- **The list** — what the user holds, in their words: *my customers*, *my leads*, *my accounts*, *lapsed customers*, *this engagement list*. The anchor is the list itself, never a description of who they want.
- **Matched / matched set** — the people from the list Watt could resolve to entities. Say *matched* and *who carries forward*; never "resolution rate", "co-residents", or a tool name at the surface.
- **Tight vs. wide** — the resolve-only play is the *tight* match (who's genuinely on the list); the expand play is the *widest* match (every entity an identifier could point to). Say *the widest set of matches* / *every match* for expand; never a tool name.
- **Households** — when the expand list carries addresses, the widest match includes *the co-residents at those addresses*; you may say so plainly (*"everyone at those addresses", "the whole household"*). Don't promise households for an email/phone-only list — there, name the round-trip (export addresses, then expand them).
- The headcount is a count of people in hand, not a market `total`: *"N identifiers in, M people matched"*.
- **The seed / more like them** — for the lookalike play, the list is the *seed*: proven people the operator wants more of. Say *the signals that describe your seed*, *what sets them apart*, *more people like them*; never "lookalike model" or a tool name.
- **The signal pool** — lookalike's deliverable: the signals that define the seed, for the operator to tune. *Durable identity* (what stably sets them apart — interests, demographics, life-stage) vs. the *intent layer* (what they're in-market for, surfaced by how common it is in the seed). Say *tune the pool* — keep what generalizes, drop what's just "they're already my customer".
- **Score / rank (overlay)** — *score my list*, *who's most in-market*, *rank by intent*. Say *score each person by how many of these signals they express* and *ranked highest to lowest*; the **pool** is *the signals to score against* (a brief, not the list). The optional cut is *the ones who also do X* — keep the people matching enough of the pool. Never say "boolean", "overlay", or a tool name at the surface.

Both unavailable `-list` strategies (the shared **group** / **traverse**) stay internal — not surfaced as a live choice; name them honestly only if asked by name.

## Entry

- **An owned list arrives** (a pasted set of emails/phones/names/addresses, or a CSV — uploaded or to upload) with a build/export intent. This leaf's lane — resolve it and emit the matched roster.
- **A roster from a prior pass arrives** ("score the people from my last run", "find more like the households we expanded", a `workflow://` entity-IDs URI or a pasted roster record with a transform intent). Same anchor, already resolved — **skip the resolve**: pick the play (overlay or lookalike run directly; expand needs raw identifiers — offer the round-trip; group/traverse aren't available here) and the URI is the population. The classification columns ride through untouched. A roster with a *read* intent is `audience-analyze-list`; with an *export* intent, `audience-activate`.
- **Routed here from `audience-generate` with the list anchor but no list in hand yet.** Ask for it: *"Share the list — paste the identifiers, or upload a CSV. What does it contain (emails, phones, names, addresses)?"*
- **A list with a READ intent** ("who are these people", "what do they have in common", "profile my customer list"). That's `audience-analyze-list`, not this leaf — both dispatch the same resolver, but analyze reads aggregates and this leaf builds toward export. Route there.
- **A plain-English brief with no list** ("people interested in solar", "build me an audience of weekend hikers"). That's the description anchor — route to `audience-generate-search`; don't resolve a list that wasn't given.
- **A widen/maximize-reach intent on a list** ("expand my list to every match", "the widest reach from my MAIDs and phones", "every entity these identifiers hit"). That's the **expand play** — settle the list, then dispatch `strategy-expand` (floor `0`).
- **A household / co-resident intent** ("expand to their households", "everyone at these addresses"). Not a separate play: if the list has addresses, that's the **expand play** (the co-residents come back in the union); if it's email/phone only, offer the round-trip (export addresses via `audience-activate`, then expand them). Only a one-shot in-leaf household grow is unbuilt.
- **A lookalike intent on a list** ("find more like my customers", "more people like my best buyers", "what defines this list", "the signals that describe my seed"). That's the **lookalike play** — settle the seed, resolve it, then profile it (`audience-profiler` mode B) and hand back the tunable signal pool. It learns from the list; it doesn't match it, and it builds no audience itself.
- **A score/rank intent on a list** ("score my customers by who's most in-market for solar", "rank my list by intent", "who on my list is hottest for X", "my list who also do X", "score my pipeline"). That's the **overlay play** — settle and resolve the list, elicit the **brief for the signal pool** (what to score by), then dispatch `signal-finder` / `signal-profiler` to build the pool and `strategy-overlay` to score and rank. The brief defines the scoring layer, not the population.
- **A suppression / do-not-target ask** ("suppress my actives", "exclude these from the campaign"). The *audience* is just one of the plays above (often resolve-only); making it a platform **exclusion** list is `audience-activate`'s call (target-vs-exclude polarity), not a generate play — say so and route the export there.

## The flow

Four plays ship. Two **match the list** (resolve-only and expand), one **learns from it** (lookalike), one **scores it** (overlay). All share step 1 — settle the list and take it — then the play decides the rest: the matching plays pick how wide and emit a roster (steps 3–6); lookalike profiles the seed and hands back a signal pool (steps L1–L3); overlay resolves the list, scores it against a pool, and ranks (steps O1–O4). Each beat ends at the user's decision; nothing resolves, profiles, scores, or lands without a go-ahead.

### 1 — Settle what the list IS, and take it

Start from the list, not a brief. Confirm **what the list is** (customers / lapsed / accounts / leads — it frames the matched set and the downstream read) and **how it arrives**. For lookalike this list is the *seed* — proven people the operator wants more of — settled the same way (what it is, its identifier shape, addresses called out):

- **A roster from a prior pass** — a `workflow://` entity-IDs URI, or a pasted roster record. Already resolved: confirm what the set is and which play they want, then **skip the resolve entirely** — the URI is the population, there are no `lookup_columns` to settle, and the roster's classification columns ride along untouched.
- **Inline** — a pasted set of identifiers.
- **A CSV** — uploaded already (a `workflow://…/uploads/…csv` resource), or one the user will upload now.

Name the **identifier types present** — email, phone, name, address. **Addresses need explicit handling** — call them out, because they resolve on a different call shape (the worker names their types explicitly; a default email-only resolve 500s on addresses). This input-shape handling mirrors `audience-analyze-list`'s step 1 exactly; the only difference is the downstream intent (build/export here vs. read there).

**For a CSV, settle which columns to match on** — the worker resolves against exactly the columns you map (`lookup_columns`) and ignores the rest, so "match on these two of the twenty" needs no file surgery: just map the two. Two cases *do* need a prepared artifact, which **the leaf builds in the sandbox before dispatch** (the worker never reshapes a file):

- **Split names** — first-name + last-name columns must be concatenated into one full-name column first; mapped separately they match near-zero. (Split *address* columns don't need this — the resolver concatenates them street-first on its own.)
- **Row filtering / deriving** — "only the active rows", dropping test accounts, deriving a column the resolver can't express.

When neither applies, pass the user's `csv_resource_uri` straight through with the chosen `lookup_columns`. When one does, write the cleaned CSV in the sandbox, upload it (`generate_upload_url`), and hand the worker that artifact's URI plus the `lookup_columns` for it — the column choice and any reshape are the leaf's, never the worker's. End the turn confirming the list, its shape, and the match columns before resolving.

### 2 — Pick the play

The user's words usually answer this — route silently when so (*"customer match"* → resolve-only, *"the widest reach"* → expand, *"more like them"* → lookalike); otherwise land the choice as the decision, per the render contract (`context/visuals.md`), with the tradeoff plain:

- **Matched (resolve-only)** — the *tight* set: who's genuinely on the list, at the resolver's default match floor. Fewer, higher-confidence. The customer-match shape.
- **Expanded** — the *widest* set: every entity an identifier plausibly points to (Noisy-OR, 1:many, floor `0`). More entities, lower-confidence tail — chosen to **maximize addressable reach**, because the wide roster feeds identifier maximalism at export. The match confidence rides with every row, so the tail is never hidden.
- **Lookalike** — don't match the list at all: *learn what defines it* and get back the signals to build a fresh audience from — for *more people like the seed*, not the seed itself.
- **Overlay** — match the list, then *score* each person against a pool of signals you define and rank them (lead-scoring / who's hot), optionally keeping just the slice who match enough of the pool.

The matching plays (matched / expanded) continue through steps 3–6; **lookalike branches to L1–L3** and **overlay branches to O1–O4** below. A floor other than the default is the user's to ask for on the matching plays (a tighter expand, a looser match) — otherwise resolve-only takes the resolver default and expand takes `0`.

### 3 — Resolve to entity IDs (matching plays — the play's worker)

For resolve-only and expand: on the user's go, dispatch the play's worker with the identifiers (inline) or the `csv_resource_uri` (the user's, or the sandbox artifact from step 1) **plus the chosen `lookup_columns`**, the `entity_type`, and a `workflow_id`. The leaf never resolves identifiers itself and never sees a resolved record — only the URI(s), the sample, and the counts come back.

- **resolve-only → `audience-resolver`** — returns the `entity_ids_uri` and the counts (`input_identifier_count`, `resolved_count`, `below_floor_count`). Narrate plainly ("5,000 identifiers in, 4,200 people matched").
- **expand → `strategy-expand`** (pass `quality_floor: 0` unless the user set one, and the `lookup_columns` for the CSV) — runs the wide `entity_resolve` 1:many pass and returns the **roster URI**, an ID-only `sample`, and `coverage` (`input_identifiers`, `resolved`, `below_floor`, `quality_floor`). Narrate plainly ("5,000 identifiers in, 6,300 entities matched wide at floor 0"). Because the match is 1:many, **`resolved` can exceed the identifiers in** — say so; it's a union, not a per-row rate. When the match columns include addresses, that union includes the co-residents at them.

### 4 — Confirm coverage honestly

Put the counts on screen — **submitted vs. matched** — and say plainly that the **matched set is who carries forward**. For resolve-only, the mapping is many-to-many: report the two counts as given, never a per-row matched/unmatched rate. For expand, name the floor and what it bought (floor `0` = widest net, every match kept; corroboration is global pooling — one entity matched two values — not two inputs confirmed as one person). Either way: if few or none matched (bad identifiers, wrong column mapping, an address list on the wrong call shape), surface the counts and the likely cause as the turn's finding — don't land an empty roster as a result.

### 5 — Emit the roster

Emit the matched set in the **shared roster record** frame — the same serialization the crossing roster from `audience-generate-search` uses, so `audience-activate` and `audience-analyze` consume it identically. The classification columns differ by play; render the matched set as the inline visual (per the render contract) — the count, the classification, the coverage — and write the roster record per the record contract (`context/record.md`):

- **resolve-only** — columns `entity_id, source_provenance` (value `seed`); no rank, no groups, no score.

```
# Watt record · kind: roster · play: resolve-only · audience: matched from your customer list
# matched: 4,200 of 5,000 identifiers submitted (below floor: 350)
# roster_uri: workflow://…/roster.csv    entity_type: person
entity_id,source_provenance
e_8821,seed
e_4410,seed
…    (sample; full set behind roster_uri)
```

- **expand** — columns `entity_id, match_confidence, match_criteria_count` (the worker's roster, verbatim); no rank, no groups. The confidence + corroboration columns are the audit trail for *why each entity is in the set*, and must survive downstream.

```
# Watt record · kind: roster · play: expand · audience: expanded from your list · widest match · floor 0
# match_confidence — Noisy-OR per entity (1.0 strong … low = weak single match)
# match_criteria_count — how many of your identifiers corroborated it
# matched: 6,300 entities from 5,000 identifiers submitted (below floor: 0)
# roster_uri: workflow://…/roster.csv    entity_type: person
entity_id,match_confidence,match_criteria_count
e_8821,0.95,3
e_4410,0.88,2
…    (sample; full set behind roster_uri)
```

The `roster_uri` carries the full entity-ID set (IDs only — never contact data) as a CSV of these same columns; the rows in the record are a sample, and the `# matched:` line stays honest about how the count relates to what was submitted. The roster record file is the canonical serialization — its column header row must survive downstream, the shape `audience-activate` and `audience-analyze` consume.

### 6 — Hand off

Offer the downstream in one line, in plain words: **export the matched set** (`audience-activate` — Meta, Google, or Reddit) or **read who they are** (`audience-analyze`). Either runs on their say-so. For an expanded roster, the export is where the wide set pays off — each entity is enriched back out to all its identifier types so the platform can reach more of them on its side (the activator's lane, behind its confirmation). Then record the run (silent plumbing — don't mention it), with `last_workflow` set to `audience-generate-list`:

```bash
STATE_DIR="${CLAUDE_PLUGIN_DATA:-${HOME}/.claude/plugins/data/watt}"
mkdir -p "$STATE_DIR"
cat > "$STATE_DIR/state.json" <<EOF
{
  "version": 1,
  "first_run_complete": true,
  "completed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "last_workflow": "audience-generate-list"
}
EOF
```

### L1 — Resolve the seed (lookalike)

On the user's go, dispatch `audience-resolver` with the seed identifiers (inline) or the `csv_resource_uri` plus the chosen `lookup_columns`, the `entity_type`, and a `workflow_id` — the same resolve as resolve-only, here producing the **seed to profile**, not a deliverable roster. **A roster input skips this step** — its `entity_ids_uri` is the seed as-is (no namesake risk: the entities were already resolved upstream); go straight to L2. Confirm coverage honestly (submitted vs. matched; the matched seed is what gets profiled). **Watch for name-match inflation** — a name-heavy seed resolves *wide* to namesakes (a 10-person list can match thousands of same-name strangers), and because lookalike builds the *whole profile* on the seed, that noise washes out the real signature: far more damaging here than the count is for resolve-only. When the match is dominated by fuzzy name matching, flag it and offer to tighten to email/phone-confirmed identifiers for a sharper seed before profiling. End the turn at the go-ahead to profile: *"4,200 of your 5,000 matched — profile these to find what defines them?"* Never profile an empty or near-empty seed as if it were the list (surface the counts and the likely cause instead).

### L2 — Profile the seed, present the signal pool (lookalike)

On the go, dispatch `audience-profiler` in **mode B** (`entity_set`) with the seed's `entity_ids_uri`, `entity_type`, and `workflow_id`. It groups the **full** seed (never a sample — intent traits are sparse, and sampling thins them into noise) and returns two halves:

- **Durable identity, by lift** — the interests, affinities, demographics, and life-stage that stably set the seed apart from the world. Lift surfaces these reliably.
- **Top intents by reach within the seed** — the intent layer. Intent traits have tiny membership, so they never clear the lift floor; reach-rank (how common each intent is *inside* the seed) is how they surface. Say so plainly — these are the seed's *common* intents and may include generic ones; tuning prunes them.

Narrate the read plainly ("Your 4,200 customers over-index hardest on X and Y; their most common in-market intents are Z…"). Render the result as the **tunable signal pool** (per the render contract) — each signal with its lift or reach, size, freshness, and which half it came from — and write the signal-pool record per the record contract (`context/record.md`); the keep/drop **tuning** is the decision the render lands. The user **tunes**: keep the portable signals, drop the self-referential ones (owning the product, the brand's own app) and the generic high-reach intents that describe everyone. This is the decision beat — the turn ends at the tuned pool.

```
# Watt record · kind: pool · play: lookalike · audience: lookalike from your customer seed · 4,200 people profiled
# tuned: kept N, dropped M    next: carry into a compose, or read · seed not suppressed from a later compose
# half — identity = by lift vs. the world · intent = by reach within the seed
# pool_uri: workflow://…
half,name,lift_or_reach,size,freshness,domain,trait_hash
identity,<signal name>,lift 7.2×,~410K,fresh,interest,…
intent,<intent name>,31% of seed,~1.2M,fresh,intent,…
```

### L3 — Hand off the pool (lookalike)

The tuned signal pool is the deliverable; lookalike builds no audience itself. Offer the next move in one line: **compose it into an audience** — carry the pool into `audience-generate-search` with the working set pre-seeded (discovery skipped for what's already there; that leaf settles the roles with the user and re-scores the pool per role before any compose — the pool's lift-or-reach figures are profiling metrics, never compose scores) — or **read it** via `audience-analyze`. Lookalike does **not** suppress the seed from a later compose: a composed lookalike audience may re-include people already on the seed — out of scope here; say so if asked, don't fake an exclusion. Then record the run exactly as step 6 does (`last_workflow` = `audience-generate-list`).

### O1 — Resolve the list (overlay)

On the user's go, resolve the list to the **matched set** via `audience-resolver` — the same resolve as resolve-only (overlay scores who's genuinely on the list, the tight match), with the identifiers/`csv_resource_uri` and chosen `lookup_columns`, the `entity_type`, and a `workflow_id`. Confirm coverage honestly (step 4). The resolved `entity_ids_uri` is the population to score. **A roster input skips this step** — its `entity_ids_uri` is already the population; go straight to O2.

### O2 — Elicit the brief for the scoring pool, discover, and score it (overlay)

Overlay needs a **brief** — but it defines *what to score by*, never who's on the list. Ask: *"What should I score your list by — in-market for what, engaged with what, interested in what?"* Read it as angles and, one angle per beat, dispatch `signal-finder` (narrow scope, the population's entity type — `person` for a list; a crossed *business* roster re-entering discovers business-side signals, `entity_type: "business"`) for the candidate signals, then `signal-profiler` to score them (by `trait_hash`, the brief as the grounding frame) — the parent's discover→score procedure, composed with verbatim. Render the scored pool as the inline visual (per the render contract) — name · what it means · ~size · relevance · freshness · score — and write the pool record per the record contract (`context/record.md`). End the turn on the pick: which signals make up the pool, and — if the operator wants — a **per-signal weight** (default every signal `1`, so the default score is a plain count of signals expressed). Nothing is scored until the user approves the pool.

### O3 — Score and rank (the worker), then choose rank-or-cut (overlay)

On the user's go, dispatch `strategy-overlay` with the resolved `entity_ids_uri`, the approved pool (expressions by `trait_hash`), the `weights` map (the operator's, or omitted for uniform), the `entity_type`, and the `workflow_id`. Narrate plainly ("Scoring your 18,400 matched customers against the 6-signal pool…"). It returns the **roster** ranked by `overlay_score`, an ID-only `sample`, and `coverage` (`source_size`, `scored`, `scored_zero`). The worker scores the **whole** list — nobody is cut. Land the closing decision per the render contract:

- **Ranked roster (the default)** — the whole list, highest to lowest. For lead-scoring / "who's hot" / prioritize-the-pipeline; activate can take the top-N by rank.
- **Intersection (the cut)** — keep only the people expressing **≥ N** of the pool's signals (default N = 1, "anyone who matches at all"; the operator can raise it to "the majority"). This is the leaf's own filter on the ranked roster — *"my list who also do X"*. Say how many remain.

Render the ranked set as the inline visual (per the render contract) — the top rows by `overlay_score` + `signals_matched`, `scored_zero` called out — and write the roster record per the record contract (`context/record.md`). Be honest: the `scored_zero` people express none of the pool — a real result, not a drop; with uniform weights `overlay_score` is just a count, not a precision verdict.

### O4 — Emit the roster and hand off (overlay)

Emit the scored set in the **shared roster record** frame — columns `entity_id, overlay_score, signals_matched, rank`. When the intersection cut was applied, the emitted roster is the kept rows and **the record says so**: a `# set:` header line reads `intersection (signals_matched ≥ N) — 4,100 of 18,400 kept`, and a `# full_set_uri:` line retains the worker's full ranked `roster_uri` — so a downstream consumer is never handed the slice as if it were the whole list, and the full ranking stays reachable:

```
# Watt record · kind: roster · play: overlay · audience: your customer list, scored · pool: 6 signals (uniform weights)
# overlay_score — Σ (weight × match) over the pool; default weight 1
# signals_matched — how many of the 6 pool signals the person expresses
# rank — 1 = expresses the most
# matched: 18,400 of 20,000 identifiers submitted    scored_zero: 1,210
# (for a roster re-entry this reads `population: N people from your prior pass` — no identifiers were submitted)
# roster_uri: workflow://…/roster.csv    entity_type: person
entity_id,overlay_score,signals_matched,rank
e_2231,5,5,1
e_8890,4,4,2
…    (sample; full set behind roster_uri)
```

Then offer the downstream in one line — **export the top of the list** (`audience-activate` — top-N by rank) or **read who the high scorers are** (`audience-analyze`) — and record the run exactly as step 6 does (`last_workflow` = `audience-generate-list`).

## How to behave

- **The list is the anchor — start from what it is, not who they want.** Elicit the list and its shape first; no play composes a new set from a description. resolve-only and expand run no discovery or scoring at all; lookalike profiles the resolved seed; **overlay** runs the parent's discover→score advisors, but only to build a *signal pool to score the resolved list by* — the list stays the population.
- **Never resolve identifiers yourself.** The play's worker — `audience-resolver` (resolve-only, lookalike's seed-resolve, and overlay's list-resolve) or `strategy-expand` (expand) — owns the set-touching identity work and returns the URI(s) + counts; the leaf never calls `entity_resolve` or `resolve_and_enrich_rows` directly, and never sees a resolved record.
- **Resolve-only, expand, lookalike, and overlay ship; the shared group / traverse don't.** Group / traverse aren't available in this leaf — name them honestly when asked, never dispatch them. The strategy workers this leaf dispatches are `strategy-expand` (expand) and `strategy-overlay` (overlay); lookalike dispatches `audience-profiler` (mode B); overlay also dispatches the parent's `signal-finder` / `signal-profiler` to build its pool; and resolve-only, lookalike's seed-resolve, and overlay's list-resolve all go through `audience-resolver`. Households are *not* a separate strategy: they fall out of expand on an address-bearing list, or via the export-addresses-then-expand round-trip; only a one-shot household-from-a-non-address-list (which would need enrichment, the activator's lane) is unbuilt.
- **Lookalike learns from the list — it doesn't match it, and it stops at the signal pool.** Resolve the seed, profile it (mode B) for its defining signals, hand the tunable pool back; never compose or measure an audience here — composing is the operator's next move down the `audience-generate-search` path. Profile the **full** seed, never a sample: intent traits are sparse, and sampling thins them into noise.
- **Overlay scores; it never composes.** The overlay brief defines the *signals to score the resolved list against*, never who's on the list. `signal-finder` / `signal-profiler` build the pool; `strategy-overlay` scores the resolved list against it and ranks the whole set — nobody cut. The **intersection cut** (keep `signals_matched ≥ N`) is this leaf's filter on the returned roster, applied only if the user asks. Suppression is **not** an overlay thing — target-vs-exclude is `audience-activate`'s call.
- **Honest about the match.** Counts on screen — submitted vs. matched — and the matched set is who carries forward, said plainly. For resolve-only never imply a per-row matched/unmatched rate; for expand say the count is a 1:many union (it can exceed the identifiers in) and name the floor. Never present a near-empty match as the list (or, for lookalike, profile a near-empty seed as if it were the list).
- **A roster or a signal pool — never contact data.** The matching plays end at a roster of ID-only entities + the roster record file; lookalike ends at the tunable signal pool (aggregates — signals with hashes, never people). Either way, no contact data — no row-level records, no enriched file of people; turning IDs back into people is `audience-activate`'s lane, behind its own scale-and-identifiers confirmation. (The record file the leaf writes carries entity IDs and signals only, never PII.)
- **End every turn at its question** — the list and its shape, the play, the go-ahead to resolve, the coverage read, lookalike's go-ahead to profile and its tuned pool, the downstream pick. A roster or pool the user didn't steer is the failure, not the deliverable.
- **US-only, adults-only, person audiences only.** (A crossed *business* roster re-entering for overlay is the people-anchored B2B exception — its entity type rides through the scoring dispatches.)

## Refuse cleanly

- **"Who are these people / what do they have in common / profile my list."** That's a read — `audience-analyze-list`. Same resolve step, different intent: it reads aggregates, this leaf builds toward export. Route there.
- **"My list who also do X / score my pipeline / who's hottest."** That's the **overlay** play — run it, don't refuse: resolve the list, build a scoring pool from the brief, rank (and optionally cut to the slice matching enough of the pool). (*"Find more like my customers"* is the **lookalike** play — run it too.)
- **"Suppress my actives / exclude these from the campaign."** Not a generate play — the *audience* is a normal play above (often resolve-only), and turning it into a platform **exclusion** list is `audience-activate`'s call (target-vs-exclude polarity). Build the set here, route the exclude decision to activate.
- **"Expand to their households / co-residents."** Not a separate play — and reachable: if the list has **addresses**, expand already returns the co-residents at them (run it). If it's **email/phone only**, name the round-trip — export the matched set with addresses via `audience-activate`, then expand those addresses. Only a one-shot in-leaf household grow (which needs enrichment, the activator's lane) is unbuilt; don't promise that, offer the round-trip.
- **A plain-English brief with no list** ("people interested in solar"). That's the description anchor — `audience-generate-search`. Route there; don't resolve a list that wasn't given.
- **"Enrich my list / give me their emails and phones."** That's export — `audience-activate`'s lane, behind its confirmation. This leaf emits a roster of entity IDs only.
- **"Show me which of my people matched."** The roster is the matched set as a whole; the counts say how many matched. No per-row matched/unmatched report — the leaf never echoes a resolved record.
- **Non-US / minors.** Decline / pivot to parents, as everywhere in the plugin.

## Failure modes

- **The resolver matches few or none** (bad identifiers, wrong column mapping, an address list resolved on the wrong call shape) — surface the counts (how few of the submitted identifiers matched) and the likely cause as the turn's finding; never emit an empty or near-empty roster as if it were the audience.
- **The resolver errors or halts mid-resolve.** Relay its `note` plainly — which batch, how many unresolved — and stop; never hand back a partial matched set as if it were whole, and never fill the gap with an estimate.
- **(lookalike) The seed is too small to profile.** A handful of matched entities yields a noisy, unreliable pool — surface that the seed was too small to define a stable signature as the turn's finding; don't present a thin pool as the audience's defining signals.
- **(lookalike) The seed resolved wide on names — namesake inflation.** A name-heavy list matches many same-name strangers (a 10-person seed → thousands), and their noise drives the whole profile (the real signature washes out, the intent layer thins). Surface the name-driven inflation as the coverage finding and offer to tighten to email/phone-confirmed identifiers before profiling — never profile a namesake-inflated seed as if it were the list.
- **(lookalike) The profiler caps or halts on a very large seed.** The advisor groups the full seed; if the server caps the aggregation or a step halts, relay the profiler's `note` plainly (which step, what was returned) and stop — never silently profile a truncated slice as if it were the whole seed, and never pad the pool with guessed signals.
- **(overlay) The pool barely matches the list.** If almost nobody on the resolved list expresses any pool signal (`scored_zero` ≈ the whole set), that's a real finding, not a failure — surface it with the counts; don't re-score at a looser pool to inflate it, and don't present an all-zero ranking as a meaningful order.
