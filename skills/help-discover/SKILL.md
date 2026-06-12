---
name: help-discover
description: Go and check whether the Signal Graph holds what the user is asking about — the concierge. Given a question about whether the data exists, dispatch the finder to probe live, then synthesize a plain answer — what's there, how big and fresh, or no honest match and the closest thing. Read-only; never sizes, builds, resolves, or exports. The concierge leaf behind /watt:help. Not a user command. Use when the ask is whether Watt has something — "do you have data on X", "is there a signal for Y", "can Watt reach Z", "is Watt any good for W".
user-invocable: false
compatibility: Talks to the remote Watt MCP server — network access and browser OAuth on the first tool call. The candidate card is a signal render in the Watt palette. Inline visuals and the closing decision follow the render contract (`context/visuals.md`), degrading gracefully where the host can't render or return a pick.
---

# Concierge — does the graph hold it?

## Purpose

`help-discover` is the concierge: when a user wants to know whether Watt holds the data they're after, it **goes and finds out for them** — no interview, no work on their part. They ask, it says "hang tight," it probes the graph, and it comes back with a straight answer: yes, here's what exists and how big and fresh each signal is (per-signal facts — never a combined count, which is `/watt:audience`'s job); or no, nothing tight — here's the closest. It exists so a user can learn what the graph holds without driving `/watt:explore` themselves.

**Answer from a real probe, never from belief.** Every "yes" and every "no" traces to a live `signal-finder` dispatch this turn — never to what you assume the graph contains. A "no" that wasn't actually checked, or a signal named without a probe behind it, is the failure this leaf exists to prevent. **Never invent a signal or pass a weak match off as a fit.**

## Works with

- **Called by:** the `/watt:help` router (a data-availability question), or `help-guide` when a how-to turns out to be a does-it-exist question.
- **Dispatches:** **`signal-finder`** — concepts → traits: the validated, concept-grouped candidate sweep that does the actual checking. Narrow scope for one angle; full scope for a broad "what do you have on X", bounded to the question.
- **Hands off to:** `/watt:explore` (to keep going interactively, go wider, or keep signals — they carry into its flow), `/watt:audience` (when the answer is yes and the user wants the actual people), or **`help-ticket`** — a `signal_request`, pre-filled from what was searched, **only when the probe found no honest match**.

## The flow

One probe-and-answer per turn; render the result, end on a decision, then stop. The probe runs on the user's question alone — asking *is* the go-ahead (per the shared canon); don't re-interview before checking. Mention a browser sign-in will pop before the first Watt call.

### 1 — Read the question into concepts

Turn the ask into the concept(s) to check, in the user's own words — one committed angle for a focused question ("do you have data on weekend backpackers"), the few distinct concepts for a broader one ("is Watt good for outdoor-gear shoppers"). Hold their internal role silently (a must-have, a distinguishing interest, an exclusion); the boolean vocabulary never reaches the user. If the question is non-US, about minors, or employer/job-title-as-target, name the limit now and pivot (US-only; parents/guardians of the age range for minors; interest/demographic/location framing for employer-as-target) rather than probing a shape the graph can't target.

### 2 — Go check — dispatch `signal-finder`

Say you're checking ("Hang tight — looking at what the graph holds for weekend backpacking…"), then dispatch `signal-finder` by the concept(s) and their roles, `entity_type` (default `person`), and any domain hints. Narrow scope for one angle; full scope only for an explicit "show me everything across this". Track the dispatch as a session task; complete it on return. Give a one-line read of what came back ("18 signals behind this; strongest ~640K, fresh") — never the structured payload.

### 3 — Answer, as a candidate card

Synthesize the finder's return into a plain answer to the *yes/no* question, then show the evidence. Render the strongest 5–8 candidates as a **candidate card** — name · what it means · ~size (human-rounded) · freshness · why it surfaced — a **signal render in the Watt palette** (the one help surface that shows signals), per the render contract. The honest count of the rest rides along. If the finder returned `unmatched_concepts`, say so plainly: *"nothing tight for 'X' — the closest is 'Y'; want that, or is this a gap?"*

### 4 — End on the next move

Close on one decision, delivered per the render contract. The real options by outcome:

- **Found it** → keep going in `/watt:explore` (go wider, sharpen, keep signals for later), build the people with `/watt:audience`, check another concept (a fresh probe), or done.
- **No honest match** → file a `signal_request` so the team knows the gap (`help-ticket`, pre-filled with the concept and what was searched), try a different angle, or done.

Never auto-run explore or audience — name the command and let the user choose. When signals are worth carrying forward, route so they travel in session context; never hand the user a record to copy.

## How to behave

- **Probe before you answer; report what came back.** No yes/no without a dispatch behind it, and one plain line on what returned before you act on it.
- **Read-only, discovery-only.** Sizes and freshness are per-signal facts straight from the graph; never count a *combination*, materialize a set, resolve, enrich, or export — that's `/watt:audience`. "How many people match all of this" is downstream's job, not yours.
- **The candidate card is a signal render — Watt palette.** It's the same render explore shows; the rest of help (tickets, the guide) is host-default.
- **Never invent a signal.** No strong match → surface the closest and flag it as a gap; don't fabricate a hash or dress a weak match as a fit.
- **A ticket is the fallback, not the reflex.** Offer a `signal_request` only after a real probe came up empty — never in place of checking.

## Refuse cleanly

- **"Build it / how many in total / get me the list"** → `/watt:audience`, named honestly; the concierge checks what exists, it doesn't assemble people.
- **Employer / job-title as the defining target** → not a supported shape; redirect to interest, demographic, or location framing (employment-domain signals may still surface as description of what the graph holds).
- **Minors / non-US** → adults-only and US-only; pivot to parents/guardians of the age range, or name the US-only limit — don't return a silent empty result.

## Failure modes

- **The dispatch fails or returns nothing usable.** Say so in one plain line and offer the next move — re-probe, a different angle, or a `signal_request` if it's a real gap — never fill the answer with signals you didn't get back.
