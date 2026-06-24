---
name: quickstart
description: New to Watt? Start here. A quick guided setup that gets you up and running in a few minutes — connect Watt to the Signal Graph, get your Claude settings right, and learn the handful of ways to use it, then jump straight into whichever one you pick. Pick this if you just installed Watt or aren't sure where to begin — "how does Watt work", "where do I start", "help me get set up" — or type /watt:quickstart.
---

# Watt Quickstart

## Purpose

This is the user's first few minutes with Watt. The skill gets them up and running — connected to the Signal Graph, their Claude settings dialed in, and pointed at the three ways to use Watt — then gets out of the way, so they leave able to do something, not just having read about it.

**However it goes, the user ends up able to use Watt — or holding the one exact next step to get there.** When connecting stalls, that means handing over the precise move (the admin link, or `/watt:help`) and stopping — retrying or guessing only loops on a connection that isn't ready yet.

## Works with

- **Called by:** the user (`/watt:quickstart`).
- **Hands off to:** `/watt:audience`, `/watt:explore`, and `/watt:help` — via the Interactive-input choices that close the run (and `/watt:help` earlier, if they get stuck connecting).

## The flow

### 1 — Introduce Watt

Open with a genuine, upbeat welcome, then remind them what Watt is, in its own framing: it indexes the world's signals and makes them consumable — a new kind of search built for AI to traverse petabytes of raw signal. Today it's especially strong at one thing: turning a plain-English description of people into a real, measured audience. That's why they're here.

Then tell them what quickstart will do:
- **Finish getting set up** — they're already in Claude and almost there; just connect Watt to the Signal Graph so everything works.
- **Show you around** — the ways to use Watt and a few best practices, then turn you loose.

Keep it to a few lines, and make no tool calls yet — the work starts once they've confirmed their platform.

### 2 — Confirm the platform

Before anything else, confirm they're somewhere Watt actually runs — in the Claude Chat app only these skill files load, not the subagents, hooks, context, scripts, or Signal Graph connector the rest of Watt needs.

Ask which platform they're using, as Interactive inputs (per the render contract — choices use Claude's native clickable options, not the visualize renderer): **Claude Chat**, **Claude Cowork**, **Claude Code**, **Agent SDK**, and **Something else**. A typed reply always wins.
- **Claude Cowork**, **Claude Code**, or **Agent SDK** → supported; move to step 3.
- **Claude Chat** or **Something else** → tell them plainly Watt supports only Claude Cowork, Claude Code, and the Agent SDK, and they'll need to switch before continuing. Don't try to connect from here — stop on that note.

### 3 — Get connected

Two steps every time: **(1)** install and connect the Signal Graph connector, **(2)** turn on the Claude settings that make Watt work. What varies is whether they're on a **personal** account or a **Claude organization** (team/enterprise) — orgs keep these settings org-wide, so changing them needs the **Owner** role.

Assume the person doing this isn't technical and isn't a Claude expert — they're likely a marketer, not a developer. Favor clarity over brevity here: name exactly what to click in plain words, one move at a time, and don't assume they know their way around Claude's settings or an admin console. Hand them clean, clickable links — never explain URL schemes or how the link works; that's plumbing they don't need.

**Step 1 — the connector.** Send them to Watt's connector page — https://claude.ai/customize/plugins/watt%40plugin/connectors — and have them check the **Install** button:
- **Clickable** → walk them through it, one move at a time:
  1. Click **Install** to set up the bundled Signal Graph connector.
  2. A connector dialog appears already filled in — click **Add**.
  3. On the connector's entry, click **Connect** to start the login.
  4. Log in with your Watt business email to authorize.

  That's the whole connector. (Personal accounts, or an org where Watt's already approved.)
- **Grayed out** → their organization hasn't approved Watt yet, which takes an Owner. Send this link to whoever owns the org — or follow it yourself if that's you — and pause until it's approved: https://wattdata.ai/docs/integrate/claude

**Step 2 — the settings.** Watt's exports come back as download links from a cloud-storage domain, so Claude needs permission to reach it — that's what these settings unlock.
- **Personal account** → open **Settings → Capabilities** (https://claude.ai/settings/capabilities) and set two things so audiences can be saved and exported:
  1. Turn on **Allow network egress**, so Claude can reach cloud storage.
  2. In the domain allowlist, choose **All domains** — Watt's export links come from a cloud-storage domain, and anything narrower can block the download.

  Cowork is already on, so once those two are set they're done.
- **Organization account** → the same two capability settings plus Cowork, but org-wide and gated on the **Owner** role: under **Capabilities** (https://claude.ai/admin-settings/capabilities), turn on **Allow network egress** and set the domain allowlist to **All domains**, then enable Cowork (https://claude.ai/admin-settings/cowork). If they're the Owner, they set all of it; if not, send the admin the link from step 1.

**End the beat with a tappable confirmation, not an open-ended wait.** Offer **"I'm connected"** and **"I'm stuck"** as Interactive inputs (per the render contract — choices use Claude's native clickable options, not the visualize renderer); a typed reply always wins. You can't detect the connection yourself, and probing one mid-setup just fails and tempts a retry loop — so go on their pick. On **"I'm connected"**, run a single `trait_search` (e.g. "home"), narrated in a warm line, as a quick liveness check, then move to step 4. On **"I'm stuck"** — or if it just won't connect — don't push it; point them to `/watt:help`.

### 4 — Find your way around

Point them at the three ways to use Watt — one line each, plain language:
- **`/watt:audience`** — the main way in, where you'll spend most of your time. Describe who you want to reach; Watt engineers the signals into an audience, then you analyze who's in it or activate it on one or more platforms.
- **`/watt:explore`** — see what the Signal Graph holds right now. The fastest way to answer "what's possible, what's Watt good at, where's my edge."
- **`/watt:help`** — get unstuck anytime, from Watt or our team. Ask how to do something or how it works, request a new signal or feature, or report an issue.

Then two tips worth more than they look:
- **Run Watt in Claude Cowork on Opus.** You're doing real data science over enormous data — exports can take a few minutes, and you'll sometimes stash an intermediate file to disk; Cowork handles both. And Opus's larger context earns its price on signal engineering.
- **Describe the *why*, not the *how*.** Tell Watt who you're trying to reach and why they buy — what they care about — not a spec like "30–45, $200k+ HHI, in California." That's just list-pulling. Give Watt the why and it figures out the how better than a person can: sell to bar owners — hard to find, not on LinkedIn — and the graph knows who's buying bar POS systems, plus fifty other angles on them.

Then set them loose — the handoff happens right here in the chat. Offer the three ways in as Interactive inputs (per the render contract); when they pick one, invoke that skill's command and let it take over from there. Don't fire a canned task of your own — the skills are guided and will ask what they actually want. A typed reply always wins. The three:
- **Build an audience** → `/watt:audience`
- **Explore what's out there** → `/watt:explore`
- **Get help** → `/watt:help`
