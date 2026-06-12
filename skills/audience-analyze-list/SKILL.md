---
name: audience-analyze-list
description: Read who a supplied list of people is — take a list of people as identifiers (emails, phones, names, addresses, inline or as a CSV) to resolve, or as already-resolved entity IDs (a roster from grouping, or a pasted entity-ID set), and render the discovered half of the read (the traits that define them against the world by lift, plus segmentation). No specified-signals section — the user gave people, not signals. The list way into audience-analyze, behind /watt:audience. Aggregates only — never individual records, never an export. Not a user command. Use when the user brings a list of people and asks who they are — "profile my customer list", "what do these people have in common", "read this roster's groups".
user-invocable: false
compatibility: Talks to the remote Watt MCP server — network access and browser OAuth on the first tool call. Inline visuals and the closing decision follow the render contract (`context/visuals.md`), degrading gracefully where the host can't render or return a pick.
---

# Analyze a supplied list of people

## Purpose

`audience-analyze-list` is the way into the read when the user brings **a list of people, not signals**. The list arrives in one of two forms, and they differ only in whether resolution is needed:

- **identifiers** — a customer CSV, a pasted set of emails/phones/names/addresses → resolve them to Watt entities first.
- **entity IDs** — a **roster** from the grouping objective, or any pre-resolved entity-ID set the user holds → already entities; skip resolution and read them directly.

Either way, because no signals were specified, there is **no your-signals half** — only the **discovered** read: the traits that define these people against the world by lift, plus per-domain segmentation.

This is a delta over `audience-analyze`: the unique work here is **getting the list to a chainable entity set** — resolving identifiers, or taking an entity-ID set as-is; the discovered read and the shareable report are the parent's shared procedure (`audience-analyze` → *The read & report*), composed with verbatim — discovered-only.

## Works with

- **Called by:** the `audience-analyze` router, when the user supplied a list of people — a CSV/identifiers to resolve, or a pre-resolved entity-ID set (a roster from grouping).
- **Dispatches:**
  - **`audience-resolver`** *(identifiers only)* — the supplied identifiers → a `workflow://` entity-IDs URI plus the counts (identifiers submitted, entities resolved). The set-touching identity work lives in the advisor, never in this leaf. **Skipped entirely when the list is already entity IDs** — there is nothing to resolve.
  - **`audience-profiler`** — mode B (the entity-IDs URI, no signals) → the discovered-only read. The parent's shared dispatch.

## Language

Inherits the parent's table (lift explained once; sample named). The headcount here is a count of the people in hand, not a market `total`: "N people resolved from your list" for identifiers, or "N people in the set" / "N in this group" for an entity-ID set or roster.

## The flow

### 1 — Get the list to an entity-ID set

Two input shapes; the only difference is whether resolution is needed.

- **Identifiers** (a pasted set, or a CSV — uploaded or to upload). Name the identifier types present (email, phone, name, address); addresses need explicit handling, so call them out. **Dispatch `audience-resolver`** with the identifiers (inline) or the `csv_resource_uri`, the `entity_type`, and a `workflow_id`. It matches them, dedupes, and returns the `entity_ids_uri` plus the counts — `input_identifier_count` and `resolved_count` (and `below_floor_count`). Narrate them plainly ("5,000 identifiers in, 4,200 people resolved — reading those"). The leaf never resolves identifiers itself and never sees a resolved record — only the URI and the counts come back.
- **Entity IDs already** (a roster's `roster_uri` from grouping, or a pasted entity-ID set). These *are* the resolved entities — **skip the resolver entirely**; take the URI as-is and the count of IDs in it. For a roster, the user can read the **whole set** (the `roster_uri`) or a **single group** (its `entity_ids_uri`); the `group_label` classification is what lets a per-group read be a separate dispatch.

### 2 — Run the shared read (discovered-only)

Hand off to the parent's shared read & report (`audience-analyze` → *The read & report*): dispatch **`audience-profiler`** in mode B with the `entity_ids_uri` (the resolved set, or the roster/group URI taken as-is), the `headcount`, and the `workflow_id` — **no signals**, so the read is discovered-only. Render the dashboard with the discovered half (defining traits by lift, segmentation, the intent panel by reach); there is no your-signals section. Offer the shareable report — built with `--no-specified` so it drops Section 1 — and the next step (for a roster, a per-group read is the natural deeper cut, one mode-B dispatch per group). The state file's `last_workflow` is `audience-analyze-list`.

## How to behave

- **The list is people, not signals** — so the read is discovered-only, and the dashboard says so plainly rather than showing an empty your-signals section.
- **Aggregates only, and IDs never become records here.** The resolver returns entity IDs; the profiler reads aggregates over them. No name, email, address, or contact data is ever pulled, shown, or written — turning IDs back into people is `audience-activate`'s lane, behind its own confirmation.
- **Honest about the match.** For identifiers, both counts are on screen — identifiers submitted vs. people resolved — and the read covers who matched, not everything uploaded; say so. For an entity-ID set or roster there's no match step (they're already entities) — the count is the set size, and for a roster the pruned/coverage from the build still applies.
- **Narrate the dispatch and report the return** in one plain line each — counts, never identifier values or records.
- **US-only, adults-only, person audiences only.**

## Refuse cleanly

- **"Enrich my list / give me their emails and phones."** That's enrichment/export — `audience-activate`'s lane, behind its confirmation. This leaf reads the list as aggregates only.
- **"Show me which of my people matched."** Aggregates only — the read is over the matched set as a whole, not a per-row report; the counts say how many matched.
- **A brief instead of a list** ("people interested in X") → that's `audience-analyze-search` (discover signals) — route there.

## Failure modes

- **The resolver matches few or none** (bad identifiers, wrong column mapping) — surface the counts (how few of the submitted identifiers resolved) and the likely cause; never read an empty or near-empty set as if it were the list.
- **The profiler errors mid-read.** Surface where it stopped and what completed; never fill a panel with plausible numbers.
