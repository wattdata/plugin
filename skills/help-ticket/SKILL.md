---
name: help-ticket
description: Reach the Watt team — draft and file a bug, a data-signal request, a feature request, or a human-help escalation, and check or list the tickets already filed. Files only on the user's explicit go-ahead on the exact text; reads (check, list) run freely. The team-channel leaf behind /watt:help, and the fallback the guide and concierge route to when a need can't be resolved. Not a user command. Use when the ask is to tell the team something — "something's broken / it's returning wrong data", "you should have a signal for X", "I wish Watt could…", "I need a human", "what have I filed", "status of WATT-212".
user-invocable: false
compatibility: Requires the remote Watt MCP server (network access).
---

# Reach the team

## Purpose

`help-ticket` is the channel to the Watt team — report a bug, request a data signal or a feature, or reach a human, and check or list what's been filed, all without leaving Claude. It closes the feedback loop: a filed ticket comes back with an ID and a status. It's the single surface over the `support` tool, and the **last resort** in `/watt:help` — reached when the guide can't answer a how-to, the concierge found a real data gap, or the user came to report something directly.

**Never file a ticket without the user's explicit go-ahead on the exact text being sent.** Filing creates a real ticket in Watt's queue — the flow is always draft → show the exact ticket → file only on confirmation, never from inference. Reads (check, list) aren't outward-facing and run freely.

## Works with

- **Called by:** the `/watt:help` router (a problem / request / human ask, or a status / list read), and the sibling leaves as their fallback — `help-discover` with a `signal_request` pre-filled from an empty probe, `help-guide` with a `feature_request` or `human_help` when the capability map can't answer.

## Language

Map the user's plain words to a ticket type; never make them learn the enum. The raw enum (`signal_request`, `human_help`) and the call params (`action`, `save_ticket`) never reach the user — show the friendly labels **Bug · Data-signal request · Feature request · Talk to a human**. If a request is genuinely torn between two types, ask once — don't guess.

| User says | You file as |
|---|---|
| "this is broken / it's returning wrong data" | `bug` |
| "you should have data on X / I need a signal for Y" | `signal_request` |
| "I wish Watt could… / can you add…" | `feature_request` |
| "let me talk to a person / escalate this" | `human_help` |
| "what have I filed / status of WATT-212 / did you fix it" | a read (`my_tickets` / `get_ticket`) |

## The flow

One decision per turn; render the beat's visual, then stop.

### 1 — File a ticket — draft, confirm, then file

Classify the type, then draft the `body` from the conversation in the customer's own voice, concrete: **bug** — symptom + steps + expected vs. actual + scope (pull from session context, e.g. a call that just failed); **signal / feature** — the need and the why (for a signal request from the concierge, the concept and what was searched); **human_help** — the ask + context.

Render the draft as the turn's decision (per the render contract) — friendly type, full body, the referenced ticket if a follow-up, and **File it · Edit · Cancel**:

```
Draft — Data-signal request
Coverage missing: LinkedIn engagement signals (posts, comment activity).
Wanted for reaching active B2B social posters.
following up on: WATT-198          → File it · Edit · Cancel
```

Only on **File it**, call `support` `action=save_ticket` with `type`, `body`, and `reference_ticket_id` if it follows a ticket the user saw. On `ok: true`, relay `message` verbatim and show the `ticket_id` + `status`. On **Edit**, revise and re-render; on **Cancel**, drop it. On `ok: false`, surface the safe `message`, **keep the drafted text** so they can retry, and don't pretend it filed. If `message` warns `reference_ticket_id` couldn't be resolved, the ticket still filed — relay that too.

### 2 — Check a ticket — `get_ticket`

Call `support` `action=get_ticket` with `ticket_id`; render the **ticket-detail** visual: ID · friendly type · status · `last_modified` · the `body`, and any team updates the response carries. On `ok: false`, relay the graceful not-found `message` and **make no claim** about whether the ticket exists or whose it is — not-found and access-denied are byte-identical by design, so any guess leaks information you don't have.

### 3 — List my tickets — `my_tickets`

Call `support` `action=my_tickets`, adding a `filter` when the user narrows (e.g. `type=bug&status=open`); render the **ticket-list** visual: one row per ticket — ID · friendly type · a one-line summary · status · `last_modified`. If `next_cursor` is present and the user wants more, page with it as `cursor` — never silently truncate; say *"showing N, more available."* End at a decision: open one (step 2), file a related ticket (step 1 with `reference_ticket_id`), or done.

### 4 — Close

Offer the next move, then stop.

## How to behave

- **Relay the tool's `message`; never claim a ticket filed or changed unless `ok: true`.** The customer's trust in the feedback loop depends on it.
- **The ticket render is host-default, not the Watt palette** — a ticket is neither a signal nor an audience render, so mark its root `data-non-watt` (per the shared canon). It carries no `trait_hash` composition — the record contract (`context/record.md`) governs those, and a ticket isn't one — so there's no record file; the list is the visual, with a compact plain-text copy where the host can't render:

```
Watt tickets
WATT-212 · Data-signal request · Open    · 2026-06-10
WATT-198 · Bug                 · Shipped · 2026-05-28
```

- **Don't echo PII or org metadata** — the tool strips internals from `message`; relay it as given, don't reconstruct or speculate beyond it.

## Refuse cleanly

- **A capability or how-to question** ("what can I do", "how do I build an audience") → that's `help-guide`, not a ticket. **A does-the-data-exist question** ("what signals exist for X") → `help-discover` checks the graph before any ticket is considered. (A complaint about a *specific bad result* is in scope — file it as a bug.)
- **"File it" with nothing said** → ask what the ticket should say first; never file an empty ticket.
- **"Delete / edit / reopen / change status"** → not supported this version; offer a follow-up ticket with `reference_ticket_id` so the team has the context.

## Failure modes

- **The `support` tool isn't on the connection.** The support channel is rolling out, so a given org's Watt connection may not have it yet. If the tool is absent, say the help channel isn't enabled on their connection yet rather than erroring out — and don't fabricate a filing.
