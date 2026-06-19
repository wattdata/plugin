---
name: help-guide
description: Answer what the user can do with Watt and how — the capability and how-to guide. Explains the surfaces (explore, the audience steps), what a signal is, what's possible and what isn't, what's changed in this version and whether a newer one is out, and points to the command that does the job — all from the capability index and the shipped changelog, with a pointer to the published docs for depth. Touches no Signal Graph; read-only — never builds, sizes, or files. The guide leaf behind /watt:help. Not a user command. Use when the ask is about using Watt itself — "what can I do", "how do I build an audience", "what are signals", "what's the expected audience size / why did only some of my list match / what's a match rate", "where do I start", "is Watt a fit for me", "what's new / what changed in this version / what version am I on / am I up to date".
user-invocable: false
compatibility: May use web search / fetch to look up the published docs.
---

# Guide — what you can do with Watt

## Purpose

`help-guide` is the `--help` for Watt — it answers *what can I do* and *how do I do it* in plain language, so a user who's unsure where to start leaves knowing the surface and the next command to type. It answers from the **capability index** — **load `${CLAUDE_PLUGIN_ROOT}/context/index.md` through the shell when this skill runs** (`cat` it — the file tool can't always see the plugin directory; it's the canonical map of what's live, loaded on demand, not always in context), together with the orientation already in context. It reads nothing from the Signal Graph and files nothing; it explains, points to the command that acts, and links the matching docs page (`context/docs.md`) for depth.

**Answer the question, then point to the command that does it.** The guide's job is done when the user knows what's possible and which command acts on it — not when a ticket is filed. A how-to that can't be answered from the capability map offers a human, never a guess about a feature that may not exist.

## Works with

- **Called by:** the `/watt:help` router, when the ask is about using Watt.
- **Hands off to:** `/watt:explore` and `/watt:audience` — the surfaces the answer points to (the user types the command when ready; nothing is auto-run); `/watt:quickstart` for a "where do I start". Routes to **`help-discover`** if the question is really *does the graph hold X* rather than *how do I*, and offers **`help-ticket`** (a `human_help` or `feature_request`) when the capability map can't answer.

## Entry

- **A capability question** — "what can Watt do", "is Watt a fit for me", "what's possible" → the capability overview (the flow).
- **A how-to** — "how do I build an audience", "how does explore work", "how do I export to Meta" → answer the specific path, end on the command.
- **A concept question** — "what's a signal", "what's a size band", "what does lift mean", "what's the expected audience size / why did only some of my list match / what's a match rate" → a plain-English definition (expected audience size: how many of the exported people the platform will likely reach, in real numbers; it's the platform's own measure, not Watt's accuracy; unreached people are still real; the levers are more identifier types per person, fresher data, and the platform's list-size minimum). **Speak in expected audience size, never "match rate" — if the user arrives with that word, recognize it and translate to audience-size terms.** Keep the first answer self-contained — **don't surface a docs link by default; only if the user presses for more on the audience size (why it comes in lower, how to lift it)** route them to the *Activating the audience* page (Learn → Build an audience), found live per `context/docs.md`.
- **A "where do I start"** — point to `/watt:quickstart`, or `/watt:explore` on a topic they name.
- **A version or "what's changed" ask** — "what's new", "what changed in this version", "what version am I on", "am I up to date" → answer from the **shipped changelog** (the version-and-changes flow below), not the capability map.
- **A connection or setup question** — "how do I connect Watt", "Watt isn't connected", "the connector's grayed out" → point to `/watt:quickstart`, which owns the connect path and recovery docs and walks them through it (and the admin route when a team or org plan has it locked).

## The flow

One answer, one render, one decision — then stop.

### 1 — Answer from the capability map

**First, load `${CLAUDE_PLUGIN_ROOT}/context/index.md`** through the shell (`cat` it — the file tool can't always see the plugin directory) — the capability index isn't always in context; it's read here, on demand. It's the canonical map; answer only from it (plus the orientation already in context). Answer directly and concretely from the capability index and orientation, in the customer's terms — name the real surfaces by their command (`/watt:explore` to interrogate the graph; `/watt:audience` to build a sized audience, profile a market, read who an audience reaches, or export it for Meta, Google, or Reddit) and the real limits (US-only, person/adults-only, employer/job-title not a defining target, Meta + Google + Reddit export). Name the **commands** — the user's interface — never the internal step names behind them. **Don't invent a capability the index doesn't list** — if it's not there, say so and offer the closest real thing or a human.

### 2 — Render the capability view

Render the answer per the render contract (`context/visuals.md`), in the host's default styling — a guide render is not a signal render, so mark its root `data-non-watt` (per the shared canon) — covering the surface(s) the answer touches, what each does, the example asks that route there, and the honest limits. Scale it to the question: a single how-to needs a small card, "what can I do" earns the fuller map.

### 3 — End on the next move

Close on one decision: the command that does what they asked (try `/watt:explore`, build with `/watt:audience`, see it work via `/watt:quickstart`), check whether the data exists (`help-discover`), or — only if the map couldn't answer — reach the team. Where the topic has a docs page, offer it as the read-more alongside the command (find it live per `${CLAUDE_PLUGIN_ROOT}/context/docs.md`, loaded through the shell the same way). Never auto-run a command; name it and let them choose.

### Version & what's changed

When the ask is *what's new / what changed / what version am I on / am I up to date*, answer from the **shipped changelog**, not the capability map.

- **Read the local changelog.** Load `${CLAUDE_PLUGIN_ROOT}/CHANGELOG.md` through the shell (`cat` it — same reason as the index). It's newest-first and already customer-facing; the **section headers are the version of record** — the top dated `## [x.y.z]` section is the most recent release the changelog records, and an `## [Unreleased]` block above it is work staged for the next release. Summarize the relevant section(s) in the user's terms — what they can now *do* or what got *better* — never read raw markdown back at them.
- **The plugin.json version is secondary.** `.claude-plugin/plugin.json` may read `<version>-pre` on a tracking install (the build number lives in the tag, not the file), so don't lead with that string — speak from the changelog's dated header, and only mention the plugin.json number if the user explicitly asks for the exact installed version.
- **Fold in the update notice if it's already in context.** The session-start update check surfaces a notice when a newer release is out ("a newer version is available: X — you're on Y — what's changed since Y — update at …"). If that notice is in this conversation's context, use it to answer "am I up to date" — *you're on Y, X is available, here's what lands when you update*, and pass along its update link. **Don't fetch anything yourself** — that check owns the network call and only runs it when relevant; if no notice is present, answer "what's in this version" from the local changelog and say only that *no newer version has been flagged this session* (the start-of-session check surfaces one when there is) — don't assert the install is on the latest, which the local changelog can't establish.
- **Render and close** per steps 2–3: a compact "what's changed" card in the host's default styling (`data-non-watt`), ending on a decision — try one of the new things (`/watt:explore` · `/watt:audience`), update (when a newer version is out), or read the full docs.

## How to behave

- **Concrete, from the source — never invented.** Every capability you name traces to the capability index; every version claim traces to the shipped changelog (or the session-start update notice). If you're unsure it's real, say so rather than promising it — and never invent a release, a version number, or a change that isn't written down.
- **Point to the command; don't do its work.** The guide explains and routes; it never probes the graph, composes, or files. A question about whether a *specific* signal exists is `help-discover`'s — route it there.
- **Plain language, no internals.** No advisor names, no boolean operators, no "composition" / "dispatch" jargon — the user's words are signals, must-haves, audiences, size bands.
- **Honest limits, every time.** When a question brushes a boundary (non-US, minors, employer-as-target, an unshipped export platform), name it in the answer rather than letting the user discover it two steps into another skill.

## Refuse cleanly

- **"Do you have data on X / is there a signal for Y"** → that's a question for the graph, not the map → `help-discover` goes and checks. The guide knows the *surfaces*, not the *contents*.
- **"Build it / size it / export it"** → that's `/watt:audience`, named honestly; the guide explains how, it doesn't do it.
- **A capability that isn't shipped** → say it's not available today and offer the closest real path, or a `feature_request` via `help-ticket` — never imply it exists.
