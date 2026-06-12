---
name: audience-generate
description: Generate a person audience from a plain-English brief — discover the signals behind it, score them with the math visible, and compose them into an audience whose reach is measured. The build step behind /watt:audience; routes to the leaf that fits how the audience should be built. Produces a signal stack + measured reach, or a roster — never an export, never contact data. Not a user command — /watt:audience is the front door. Use when a build-shaped ask arrives — "build me an audience of …", "I need about N people who …", "the highest-intent people in-market for X", "where do these people cluster", "a lead list of in-market companies", "match my customer list / build from my customers" — or when a /watt:explore signal pool is ready to become an audience.
user-invocable: false
compatibility: Talks to the remote Watt MCP server — network access and browser OAuth on the first tool call. Inline visuals and the closing decision follow the render contract (`context/visuals.md`), degrading gracefully where the host can't render or return a pick.
---

# Generate an audience

## Purpose

`audience-generate` — the build step behind `/watt:audience` — turns "who I want to reach" into a built audience: the signals behind the brief, scored with the math visible, composed into a set whose reach is **measured**. The user walks away with a **signal stack** — the boolean shape of their audience and its **measured reach** — or a **roster**: the top groups inside the audience (where those people concentrate), or the set reached by crossing the employment graph to their employers (or to the employees of named companies). Either is ready for the `audience-analyze` and `audience-activate` steps.

One spine, many ways to compose. This skill owns the shared spine every build shares — discover the signals, score them, curate the working set, land the audience — and **routes by input anchor** (what the user has in hand) to the leaf that owns the build:

- **a plain-English description** of who to reach → `audience-generate-search` (today: a size band with greedy, maximum credible reach with broad, precision with lift, the top groups inside the audience with group, or the set reached by crossing the employment graph with traverse — the objective picks).
- **an owned list** — customers, leads, accounts → `audience-generate-list`, which resolves the list first (today: resolve-only for a tight matched set, or expand for the widest identity-matched set — both a roster; lookalike, which profiles the list and hands back the signals that define it to build from; or overlay, which scores the resolved list against a pool of signals and ranks it; group and traverse aren't available there).

**Route; don't run the compose.** Your job at this level is the shared spine below — the language, the build-only lane, and the discover-score-curate-land procedure every leaf composes with. The leaf owns the objective it composes or partitions toward and the strategy worker that gets there.

**Nothing is composed unseen.** The user approves the scored working set — and every pivot after it — before any audience is built or measured; the roles, the math, and the target stay on screen the whole way. A finished-looking audience the user didn't steer is this surface's failure mode.

## Works with

You own the conversation, the elicitation, the scoring dispatch, and the rendering; the heavy work is dispatched. Pass signals to advisors by `trait_hash`, never display name alone.

- **Called by:** the `/watt:audience` router — often carrying an `/watt:explore` signal pool as the seed (see Entry); and `quickstart` — which drives this flow as written for a first-run user, arriving with the brief and landing mode already settled (route silently on them) and delivering the landing offer as its junction.
- **Dispatches** (the shared discovery — the same advisors explore uses, here ending in a built audience):
  - **`signal-finder`** — one committed angle → validated candidate signals with evidence.
  - **`signal-profiler`** — scores the gathered signals against the model (relevance · freshness · rarity/specificity · breadth/size · coverage), grounded on the brief, so the user can see how each stacks up and curate. Traits-only — it never touches a set of people.
  - **`signal-recommender`** *(optional, at a pivot checkpoint)* — adjacent concepts / unprobed domains worth adding.
- **Routes to** (the build leaves — split by input anchor; each owns its landing mode + strategy subset):
  - **`audience-generate-search`** — build from a plain-English description; today composes to a size band with greedy, maximum credible reach with broad, or precision with lift, partitions the audience into its top groups with group, or crosses the employment graph to a qualified set with traverse — the objective picking the strategy (a signal stack, or a roster from grouping or crossing).
  - **`audience-generate-list`** — build from an owned list (customers, leads, accounts). Today resolve-only (a tight matched set) or expand (the widest identity-matched set, for maximum addressable reach) — both a roster of entity IDs — lookalike (profile the list and hand back the signals that define it, as a tunable pool to build from), or overlay (score the resolved list against a pool of signals and rank it — lead-scoring / "who's hot" / intersection); group and traverse aren't available there.
- **Hands off to:** `audience-analyze` (read who the landed audience reaches), `audience-activate` (export it), and `/watt:explore` (keep exploring — the stack's signals carry back as covered territory) — offered at the landing, on the user's say-so.

## Language

Same translation table as explore — the user talks plain business language, you carry the boolean shape silently:

| User says | You hold internally |
|---|---|
| a must-have — "everyone has to be a homeowner" | an AND condition (`must_have`) |
| a defining behavior or interest | an OR in the core (`core`) |
| an exclusion — "not industry professionals" | an AND_NOT (`exclusion`) |
| a place — "in Colorado", "Nashville metro" | a geo-boundary **signal**, added as a must-have |
| "signal" | what the MCP calls a trait |
| target size, "about 1–5M people" | the band — floor and ceiling (the `audience-generate-search` leaf's band landing mode) |
| "the highest-intent / most likely people", in-market, high-intent | precision — the leaf's landing mode that picks signals by lift over a must-have base |

No AND/OR/AND_NOT, no boolean "pools" (the OR/AND/AND_NOT groupings), no "boolean expression" in anything the user sees: say *must-haves*, *the signals themselves*, *exclusions*. (*Signal pool* — the kept-signals carrier from explore or lookalike — is the user's word and fine.) Unlike explore, this surface **may** say *audience*, *build*, *compose*, *signal stack* — that is its job. *Score* is fine; show the numbers, skip the formula names.

## Entry

- **A build-shaped brief arrives** ("build me an audience of weekend hikers in Colorado, a couple million people"). A description anchor routes to `audience-generate-search`, carrying everything already said; the leaf elicits only what's missing. With one leaf today, route there silently.
- **An owned list arrives as the seed** ("here are my customers", "match my customer list", "expand my list to every match", "find more people like my customers", "rank my list by intent"). That's the `audience-generate-list` anchor — route there (resolve-only for a tight match, expand for the widest match set, lookalike to profile the list for the signals that define it, or overlay to score the resolved list against signals and rank it; group and traverse aren't available there). A list with a *read* intent ("who are these people") is `audience-analyze-list` instead.
- **Routed here from `/watt:audience` with no brief yet.** Ask for the brief: *"Describe the audience in plain English — who they are, what they're doing or into, and roughly how many people you need."*
- **From `/watt:explore`.** A session's signal pool seeds the working set: the picked signals arrive with hashes, roles, and evidence — the pool record carries all three, so a pasted or compacted record seeds as well as a live session. Skip discovery for the angles it covers; route to the leaf, which elicits its target and goes to compose. A signal the record flags `unverified` keeps its caveat through scoring — its figures are carried claims, never presented as refreshed.
- **A profile-shaped ask** ("who's in my market", "how many roofers near Nashville", "an audience profile for my client"). That's a read, not a build — there's no target to compose toward. Route to `audience-analyze` (its `-search` flavor profiles a market from a brief, and writes the shareable report). Don't build it here.
- **A list of people / a CSV to build from.** That's the owned-list anchor — route to `audience-generate-list`, which resolves it to a matched roster. (To *read* a supplied list as aggregates, `audience-analyze-list`.) A build from *signals* still starts from a description — `audience-generate-search`.
- **A roster from a prior pass, with a transform intent** ("score the people from my last run", "find more like the households we expanded" — an entity-IDs URI or a pasted roster record). The same owned-list anchor, already resolved — route to `audience-generate-list`, which skips the resolve and runs the play on the set directly (overlay / lookalike today). A roster with a *read* intent is `audience-analyze-list`; an *export* intent, `audience-activate`.
- **Employer / job-title as the defining criterion.** Not a supported shape — redirect to interest, demographic, or location framing before eliciting further.

## The shared spine — every objective leaf composes with this

The leaf settles its target and owns the compose; everything else is here, composed with verbatim — not restated in the leaf. One decision per turn, landed per the render contract (`context/visuals.md`) — same gate discipline as explore. Mention before the first Watt call that a browser sign-in will pop. Track each advisor dispatch as a session task; if the host has no task tools, skip silently.

### A — Settle the brief, then discover one angle per beat

The brief must carry at least one defining behavior, interest, or intent. A pure-demographics brief isn't composable — demographics gate an audience, they don't define one; ask what these people are *doing* or *into*. There is **no location step**: a place is a **geo-boundary signal** (state / county / DMA / ZIP), added to the working set as a must-have during discovery if the user wants one — looked up as a geo trait, never a guessed hash. (Arbitrary radius-around-a-point filtering is a separate objective leaf, not this spine.)

Read the brief as its **angles** (the distinct concepts inside it, in the user's words) and confirm the reading. Then, for the angle the user picks first, dispatch `signal-finder` in narrow scope — their phrasing, the angle's internal role, `entity_type: "person"`, domain hints the conversation implies, and reactions so far. One angle per dispatch; the next waits for its own beat. Narrate the dispatch and give a one-line read of the return ("38 candidates behind the hiking angle; nothing tight for 'trail snacks'"). signal-finder validates and enriches every candidate (similarity, size, domain, skew, freshness, hash) and flags anything unmatched — never invent a signal.

### B — Score the pool, show the math, curate

Dispatch **`signal-profiler`** to score the gathered candidates — by `trait_hash`, with the **brief as the grounding frame** (so relevance is comparable across angles) and a **role-appropriate `weights` vector**, because each role wants a different kind of signal. Score **once per non-empty role** (`signal-profiler` takes one weight vector per call):

- **core — the targeting pool.** `relevance` leads; a light `freshness` positive; and **one signed size-family axis — the `breadth` element of this role's `weights` vector, the lean the objective leaf sets** in the `signal-profiler` dispatch (`-search` tunes it from the landing mode — negative when the landing wants distinctive, narrow signals, because distinctiveness is what separates *targeting* from raw reach — a trait nearly everyone carries targets no one; by the band's scale in band mode; strongly positive in max-reach mode). **Size stays out of the score** — the strategy worker converges to the target by measuring reach, so scoring size too would double-count it.
- **must-have — the gates.** Broad and on-brief (`breadth` + `relevance`): a narrow gate quietly becomes the whole definition.
- **exclusion — the removals.** Precise (`specificity` + `relevance`): a broad exclusion over-cuts.

**At most one size-family axis per vector.** `rarity` / `specificity` / `breadth` / `size` are views of one fact (`specificity = 1 − breadth` over a shared universe — see `context/signal-metrics.md`); a `weights` vector that names two of them scores that fact twice, and the model flags it (`collinearity_warning`). The signed `breadth` element carries the whole lean — distinctiveness is its negative direction, never a second axis.

`signal-profiler` runs the scoring model (`scripts/signal_profile.py`) and returns each signal's feature vector (relevance · freshness · rarity/specificity · breadth/size · coverage) and a composite `score` under its role's weights — the read of how each pool stacks up. The model owns the math; never hand-score a signal, and run nothing inline — `signal-profiler` is the single scoring path. **The profiler's per-signal `raw` fields ride into the working set and onward to the strategy dispatch** — each working-set signal carries `trait_hash`, `name`, `role`, `score`, `size`, plus `prevalence` and `freshness` from the profile: `strategy-broad` derives its ungated universe from `prevalence`, and `strategy-lift` breaks ranking ties on `freshness`, so dropping either field silently degrades those composes.

Render the scored slice as an **inline visual** (per the render contract), grouped by role: **name · what it means · ~size · relevance · freshness · rarity/specificity · score · role** — strongest ~5–8, an honest count of the rest, sizes human-rounded (417K, 2.1M), a score bar per row, any signal that arrived without a hash or couldn't be enriched visibly flagged. Scores are **role-appropriate**, so "why is X above Y" is answerable *within* a role group (a core signal's score and a gate's aren't on the same basis — never cross-rank them); the profiler's axes visibly drive each score. Then end the turn at the decision: which signals join the working set, which are out — same pick mechanics as explore (multi-select for keeps, "Other" carries number-picks and steers).

### C — Keep the working-set record, pivot freely

Picks apply immediately. On **every working-set change**, re-emit the record — a compact fenced block, the session's durable state:

```
Working set — weekend hikers · target: band 1M–5M
core:
  In-market: Hiking Gear      · ~2.1M · fresh    · score 0.84 · 3fa4b2…
  Outdoor recreation interest · ~9.8M · standard · score 0.31 · c0903a…
must-have:
  Colorado resident (geo)     · ~4.4M · —        · gate       · 0334a6…
excluded-signals: 2 (retail employees, gear resellers)
angles: hiking ✓ · fitness open    dropped candidates: 5
```

The header line carries the leaf's target (`target: band 1M–5M` for `-search`). Hashes ride along (advisors are dispatched by hash); the `angles:` line tracks open/covered so convergence survives compaction. The record is the durable carrier — emit it on every change and let it ride quietly beneath the surface the user reads, which is the working set rendered (per the render contract) — signals grouped by role in plain English, each with size, freshness, and score, score bars carrying the ranking — data-only, same structure every render.

**Lift** — how much likelier a population is to carry a trait than average — appears at later beats, **never as a working-set curation column**; during curation, working-set figures stay graph facts: size, freshness, score. It surfaces twice afterward: the **precision** landing mode's `lift` strategy measures each candidate's lift *over the must-have base* at compose (in `-search`), and the `audience-analyze` read measures lift *over the built audience* after. If the user asks for lift mid-curation, say which of those they mean and offer it at its beat.

Pivots are one per turn, any order: exclude a signal, flip a role, go deeper on an angle, probe a new one, add a named concept (a fresh narrow `signal-finder` dispatch), add a geo-boundary signal, or ask for adjacencies (`signal-recommender`). **Exclusions are explicit-include only** — a proposed exclusion isn't in the working set until the user confirms it, because a mis-applied exclusion silently distorts the build. New signals from any pivot go through `signal-profiler` before they're shown.

### D — Compose or partition — the objective leaf's delta

This is the leaf's lane: it settled the objective (e.g. `-search`'s size band, or its grouping dimension) and offers the strategy subset that fits it. When every angle is covered or consciously dropped, the leaf offers the step and — only on the user's go — dispatches the chosen `strategy-<name>` worker with the working set (in scored order, pivots applied) and the target. A compose strategy returns a **signal stack** whose reach is **measured** at every step; a Classify strategy returns a **roster** — group partitions a base set into ranked groups, traverse crosses the employment graph (a composed seed → its employers, or employees of named companies) to a qualified set (membership only — ranking or segmenting it is a separate Classify step). Never present arithmetic over per-signal sizes as a count. The leaf renders the trace and owns what happens at the target's edge. See the leaf for the specifics.

### E — Land the audience

This step lands a **signal stack**. A leaf running a Classify strategy (e.g. `-search`'s grouping objective) lands a **roster record** instead — its own serialization, owned by the leaf; see the leaf for that shape. The stack landing:

On an accepted stack, emit the final record — now the **audience record**, the artifact the rest of the flow consumes:

```
Audience — weekend hikers · reach 2.4M (band 1M–5M)
defining (any of):
  In-market: Hiking Gear      · 3fa4b2…
  Outdoor recreation interest · c0903a…
must-have (all of):
  Colorado resident (geo)     · 0334a6…
excluding:
  Gear resellers              · 9b81de…
location: none (national)   entity_type: person
workflow: 550e8400-…   sample: 10 entity IDs held in session
```

This record is the stack's canonical serialization: names ride with the hashes so a pasted record stays readable to every downstream step, and the role groups (*any of* / *all of* / *excluding*) carry the expression exactly as composed, in plain English. The `location:` line carries any radius/boundary filter the compose applied — distinct from a geo-boundary *signal*, which lives in the role groups; the strategies and the downstream steps take location as its own input. Its re-supply consumers (`audience-analyze-signal`, `audience-activate`) parse it, and a record without it silently widens a re-run — so the line is always present, written `none (national)` when no filter rode along, never dropped. A downstream refresh re-emits this record with today's measured reach and a `· refreshed` header suffix — one suffix, defined here, echoed by both refresh exits. The header carries the landing mode's target: `reach 2.4M (band 1M–5M)` for greedy, `reach 84M (max-reach)` for broad, `reach 180K · precision (lift over base)` for lift. Alongside it, render the landed audience (per the render contract) — role groups, per-signal sizes and freshness, measured reach against the target — with the record riding quietly beneath it as the durable carrier. Offer the downstream in one line, in plain words: read who these people actually are (`audience-analyze`), export it (`audience-activate` — Meta and Google Customer Match), or keep exploring around it (`/watt:explore` — the stack's signals carry back as covered territory, and the walk resumes on what's adjacent). Any of them runs on their say-so. Then record the run (silent plumbing — don't mention it), with `last_workflow` set to the leaf that ran:

```bash
STATE_DIR="${CLAUDE_PLUGIN_DATA:-${HOME}/.claude/plugins/data/watt}"
mkdir -p "$STATE_DIR"
cat > "$STATE_DIR/state.json" <<EOF
{
  "version": 1,
  "first_run_complete": true,
  "completed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "last_workflow": "audience-generate-search"
}
EOF
```

## How to behave

- **End every turn at its question.** Elicitation, picks, pivots, the compose gate, target-edge leverage — each is the user's call, and the turn stops there. Composing an audience the user didn't steer is the failure, not the deliverable.
- **Route; don't run the compose.** Settle the brief and run the shared discovery, but the target and the compose belong to the leaf — re-eliciting what the leaf elicits, or composing here, duplicates the flow.
- **Narrate every dispatch in plain English;** report what came back in one line before acting on it. Never dump a structured payload. (The plugin emits automatic *advisor started/done* markers around dispatches — your narration is the substance on top.)
- **Show the math.** The profiler's feature-vector axes are on screen; the user answers "why is X above Y" from the render. Never hand-score a signal.
- **Reach is measured; sizes are facts.** A signal's size comes from the graph; what a combination reaches comes only from the strategy worker's probes. Never add sizes together for the user.
- **Never invent signals.** Unmatched concepts surface honestly with the closest match flagged — in discovery and in geo lookup alike.
- **A signal stack, not contact data.** Generate ends at the stack + reach + an ID-only sample. Records, files, and row-level anything are the `audience-activate` step's job, behind its own confirmation.
- **US-only, adults-only, person audiences only.** Non-US targeting is out of scope — say so, don't return a silent empty result. Briefs about minors pivot to parents/guardians of that age range.

## Refuse cleanly

- **"Just give me the list / the emails."** *"Generate builds the audience and measures it. Exporting people is the activate step — it'll confirm scale and identifiers with you before anything is pulled."*
- **A profile / "how many are out there" with no intent to target.** That's a read — route to `audience-analyze` (its `-search` flavor profiles a market and writes the report); generate builds toward a target.
- **Bare signal names as the whole brief.** ("Use traits X, Y, Z.") Drive from meaning: *"Tell me who you're trying to reach and what they're doing, and I'll find what the graph holds — named signals can join once we see them in context."*
- **Employer / job-title as the defining criterion.** Not supported — redirect to interest, demographic, or location framing.
- **Business audiences.** Person audiences only in v1 — say so plainly.
- **Non-US / minors.** Out of scope / pivot to parents — same as everywhere in the plugin.

## Failure modes

- **`signal-profiler` errors or returns thin.** Say so; surface the candidates in the finder's similarity order with their evidence, and let the user pivot from there — never hand-score to fill the gap.
- **A reach probe errors mid-compose.** The strategy worker halts and surfaces it; show the user where the build stopped and what was measured up to that point — never fill the gap with an estimate.
