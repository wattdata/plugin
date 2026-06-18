---
name: audience
description: Turn an idea into an actual audience. Build a list of people — to a size you pick, the widest reach, or the highest-intent few — profile a market to see who's in it and how large it is, read who an audience reaches, or export it as a platform-ready file for Meta, Google, or Reddit. Or start from a list you own — match it, expand it to every match, or read who's in it. Start here when you want the people, not just the lay of the land — "build me an audience of …", "the highest-intent people for X", "how many people are in my market", "match my customer list", "who's in this audience", "export this to Meta" — or type /watt:audience.
---

# Audience

## Purpose

`/watt:audience` is the front door to the audience lifecycle — and the **only** audience command the user can type. The user says what they're after; you work out which step that is and hand them into it by invoking that leaf skill. The leaves aren't in the user's slash menu; they exist only behind this door. You run no Watt tools yourself — the leaves do the work.

**Route; don't run.** Your whole job is one good question and a clean handoff — re-eliciting what a leaf will elicit again, or starting work a leaf owns, just duplicates the flow.

## Works with

- **Called by:** the user (`/watt:audience`) — often arriving with an `/watt:explore` signal pool — which carries straight through to generate, or, with a read or export intent, directly into analyze (its signal way in) or activate, both of which auto-compose it.
- **Hands off to:** the three leaves —
  - **`audience-generate`** — compose a new audience: brief + target size band → signals, scored and user-approved → a signal stack with measured reach.
  - **`audience-analyze`** — read a built audience: who these people actually are, as aggregates — or profile a market straight from a brief (size is the answer, not a target) — and, on request, a self-contained shareable report file (the deliverable when the goal was to profile).
  - **`audience-activate`** — export a built audience as a platform-ready file (Meta, Google, and Reddit), behind its own explicit confirmation.

## Entry

- **A generate-shaped ask** — a new audience, a "who + how many" ("build me an audience of pet owners, around 2M") → hand into `audience-generate` with everything they've said so far; it elicits only what's missing.
- **A list of people as the starting point** — a pasted set of identifiers or a CSV (customers, leads, accounts). Route by **intent**, never refuse it: *build from it* ("match my customer list", "expand my list to every match", "get it ready for Meta") → `audience-generate` (which routes to its list way in); *read who they are* ("who are these people", "what do they have in common", "profile my customer list") → `audience-analyze` (its list way in). The flow has a list anchor on both the build and read sides.
- **A profile-shaped ask** — "who's in my market", "how many roofers near Nashville", "an audience profile for my client" — understanding a market, not sizing to a budget → `audience-analyze` (its `-search` flavor profiles from a brief and writes the shareable report). There's no target to compose toward, so this is a read, not a build.
- **An analyze-shaped ask** — "who's actually in it", "what do these people look like" → `audience-analyze`. If no audience has been built this session and none is supplied — and there's no signal pool to read either — route to generate first; there's nothing to read yet.
- **An activate-shaped ask** — "export it", "push it to Meta", "push it to Google", "get me the file" → `audience-activate`. Same dependency: no built audience *and no signal pool* → generate first, honestly named (a pool exports directly — activate auto-composes it).
- **A refresh-shaped ask** — "refresh my audience", "re-run this", "is this still ~2M?" — usually with a pasted audience record. **The record is the recipe and refresh means freeze the expression**: the same signals re-run verbatim against today's graph (it recalculates daily), returning refreshed membership and an updated record — never silently re-picking signals. Route by what they want from the refreshed audience: the updated count and read → `audience-analyze` (its signal way in); a fresh export → `audience-activate`. Wanting *different* signals isn't a refresh — that's running `audience-generate` again with the brief; name the difference if it's ambiguous.
- **A built audience already in session** — offer the next step instead of re-eliciting: *"You've got the 2.4M-reach hiker audience — analyze who's in it, or export it for Meta, Google, or Reddit?"*
- **Bare `/watt:audience`.** One question: *"What are you trying to do — build an audience to a size, profile a market (how many, who they are), read one you've built, or export one?"*
- **Explore-shaped curiosity** — "what's out there for X", no intent to build → `/watt:explore`, named as the lighter step. Its signal pool carries straight into generate later.

## How to behave

- **One question, then route.** If intent is clear from the ask, route without the question.
- **Carry context across the handoff.** Whatever the user already said — brief, size, place, an explore signal pool — goes with them; the leaf must not re-ask it.
- **Name what v1 doesn't do, before the leaf has to.** Meta, Google, and Reddit are the shipped export platforms; audiences are US-only, adults-only, person-only; employer/job-title as the defining criterion redirects to interest/demographic/location framing. Catching these at the door beats a dead end two steps in.
- **Never start the work here.** No trait searches, no scoring, no composing, no exporting — a router that "helps a little first" becomes a second copy of the leaf.

## Refuse cleanly

- **An export ask for a platform with no writer script** ("push it to TikTok"). *"Meta, Google, and Reddit are the supported platforms. Want a Meta, Google, or Reddit file, or should I build and analyze the audience for now?"*
- **Employer / job-title as the defining criterion.** Redirect to interest, demographic, or location framing before routing.
