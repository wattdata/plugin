---
name: configure
description: Set up Watt in Claude, or fix it when it stops working. A guided check that confirms you're on a supported surface, verifies Watt's Signal Graph connection and file downloads for you, and walks you through turning on automatic updates — fixing anything that's off, one step at a time. Run it the first time you install Watt, or any time something's not connecting — "set up Watt", "where do I start", "connect Watt", "Watt isn't working", "my export is blocked", "the connector's grayed out" — or type /watt:configure.
compatibility: Designed for Claude Cowork, Claude Code, or Agent SDK. Requires the signal-graph MCP connector.
---

# Configure Watt

## Purpose

`/watt:configure` is the user's setup and connectivity aide. It walks a new user through configuring Watt the first time — and it's the same place a returning user comes back to when something stops connecting. It settles their account type to tailor the path, checks the four things Watt needs, verifies the two it can verify, fixes whatever's off one step at a time, and leaves them able to use Watt.

**Every beat ends able to use Watt — or holding the one exact next step to get there.** When a check fails, hand over the precise move (the click, the admin link, or `/watt:help`) and wait on the user's signal; never retry blindly or guess past a step that isn't done — that just loops on a connection that isn't ready.

## Works with

- **Called by:** the user (`/watt:configure`), or any skill that hits a connection or authentication wall — this is the connect/recovery door the rest of the plugin points to.
- **Hands off to:** `/watt:audience`, `/watt:explore`, and `/watt:help` — via the Interactive-input choices that close the run (and `/watt:help` earlier, when a check stays stuck and they want a human).

## The flow

One beat per turn. Throughout, keep a **setup checklist** on screen and mark each item with a ✓ the moment it clears — so the user always sees where they are and what's left:

1. Account type
2. Supported platform
3. Signal Graph connected
4. File downloads on
5. Automatic updates on

Render the checklist through the visualize tool (a display visual, not a decision — make the tool's `read_me` setup call before the first render, then honor the render contract as delivered). It's setup UI, not a signal or audience render, so it's host-default styling, never the Watt palette — mark its root `data-non-watt`. **Decisions, though, are Interactive inputs — Claude's native clickable options, not the visualize renderer** — robust even when a render surface is part of what's misconfigured, and a typed reply always wins.

**One path, not all of them.** Steps 4–6 each have a personal-account path and an organization-account path. Step 2 settles which one is theirs — so from there on, show only that path. Never paste both branches, every doc link, and every what-if into the chat; that's noise. Give the user the one move that's theirs right now, plus a single link to the guide if they want to follow along — and let the tappable choices funnel them.

### 1 — Introduce, and show the checklist

Open with a genuine, upbeat welcome, then say plainly what configure is: a quick guided check that gets Watt set up and working in Claude — and the place to come back to any time something stops connecting. Remind them what Watt is, briefly, in its own framing: it indexes the world's signals and makes them consumable — especially strong at turning a plain-English description of people into a real, measured audience.

Then point them at the right surface and model, since it saves a dead end: Watt runs in **Claude Cowork**, **Claude Code**, or the **Agent SDK**, not the Claude Chat app. **Cowork is the easiest place to run it** — it handles Watt's longer exports and the working files it produces — **and Opus is the model to use**, since its larger context and sharper reasoning earn their price on the signal engineering that drives audience quality.

Render the checklist (nothing ticked yet) so they see the shape of what's ahead. Make no tool calls yet — the checks start once we know their account type and platform.

### 2 — Personal or organization account?

This shapes the rest of setup: an **organization** account hands some settings to an Owner, a **personal** one keeps them all in the user's own hands. Settling it now lets every later step show only the path that's actually theirs.

Most people don't know their account type off-hand, so tell them where to look: **click your account at the bottom-left of Claude — under your email it shows your plan.** Then map it for them: **Pro or Max → personal account; Team or Enterprise → part of an organization.** (Screenshots in the guide: https://wattdata.ai/docs/integrate/claude)

Offer the answer as Interactive inputs — they pick one; the plan under their email tells them which, so don't add an "unsure" escape:
- **Personal (Pro/Max)** → tick **Account type** ✓; steps 4–6 show the personal path only.
- **Organization (Team/Enterprise)** → tick **Account type** ✓; steps 4–6 show the organization path, where an Owner sets the org-wide pieces.

Make no tool calls here — it's a single question. Move to step 3.

### 3 — Confirm the platform

Read the cues available to you and infer the most likely surface, then **always confirm it** — a wrong guess sends the rest of setup down the wrong path. Pre-state your read ("Looks like you're in Claude Code — is that right?"); if nothing points clearly, don't force a guess — just ask. Offer the choice as Interactive inputs: **Claude Chat**, **Claude Cowork**, **Claude Code**, **Agent SDK**, **Something else**.
- **Claude Cowork**, **Claude Code**, or **Agent SDK** → supported; tick **Supported platform** ✓ and move to step 4.
- **Claude Chat** or **Something else** → tell them plainly Watt supports only Claude Cowork, Claude Code, and the Agent SDK — in the Chat app only these skill files load, not the connector, hooks, and scripts the rest of Watt needs. They'll need to switch and re-run `/watt:configure`. Don't try to connect from here — stop on that note.

### 4 — Check the Signal Graph connection

This check verifies itself. Narrate it in a warm line, then run a single `trait_search` (e.g. "data") as a liveness probe.
- **Comes back with results** → the connector's live; tick **Signal Graph connected** ✓ and move to step 5.
- **Fails on a connection or authentication problem** → this is exactly what configure is here to fix, so don't bounce it elsewhere — show how to connect. Assume the person isn't technical and isn't a Claude expert; name exactly what to click one move at a time, and hand clean clickable links without explaining how a link works. Show only the path for their account type:
  - **Personal account** → the **Install** button is theirs to use. Send them to Watt's connector page — https://claude.ai/customize/plugins/watt%40plugin/connectors — and walk it one move at a time: **1.** Click **Install** to set up the bundled Signal Graph connector. **2.** A dialog appears already filled in — click **Add**. **3.** On the connector's entry, click **Connect** to start the login. **4.** Log in with your Watt business email to authorize.
  - **Organization account** → Watt has to be approved for your organization by an **Owner** first. Open the connector page — https://claude.ai/customize/plugins/watt%40plugin/connectors — and look at the **Install** button: if it's active, walk the same four steps above; if it's **grayed out**, the org hasn't approved Watt yet — send this link to whoever owns the org (or follow it yourself if that's you) and pause until it's approved: https://wattdata.ai/docs/integrate/claude/org-configuration

  Want the full walkthrough with screenshots? One link: https://wattdata.ai/docs/integrate/claude

  **End on a tappable confirmation, not an open-ended wait** — you can't detect the connection yourself, and probing mid-setup just fails and tempts a retry loop. Offer as Interactive inputs:
  - **Connected** → re-run the `trait_search` probe to confirm. Passes → tick ✓ and move to step 5. Still failing → say so plainly and put them back at the instructions above with the same choices.
  - **Install button is grayed out** *(organization only)* → their org Owner has to approve Watt before they can continue; give them the org-configuration link above to send to the Owner, and offer to re-check once it's approved.
  - **Contact support** → hand to `/watt:help` to reach a human, carrying the symptom (the connector won't connect, and what they've tried) so help opens with a human-help draft ready instead of a blank ask.

### 5 — Check that exports can download

This check verifies itself too. Watt's exports come back as download links from a cloud-storage domain, and reaching that domain is a Claude setting — so the honest test is to fetch one. Narrate it, then run a tiny `entity_find` (entity type person, the age-30 signal `648c0733c3c2b995d8f4e99a3f8ba2a4`, `audience_limit` 10, `format` csv, `domains` ["name"]) to mint a download link, and **try to fetch that link**. That fetch rides Claude's network egress and domain allowlist — the `entity_find` call itself rides the connector and succeeds regardless — so whether the file comes back is the real test.

**Don't mistake a tool limit for a blocked download.** These download links are long, and an over-length URL can make Claude's default fetch tool fail for reasons that have nothing to do with the user's settings. So if that first fetch fails, **don't conclude anything yet — retry it from the code sandbox** (a `curl` or `wget` in bash, or a tiny Python/JS fetch), where the URL-length limit doesn't apply. Only when the sandbox fetch *also* fails is the download genuinely blocked. (If you can't attempt a fetch at all on this surface, don't assert a result — ask the user to open the link and tell you whether it downloads, and treat their answer as the check.)
- **The file comes back** (on either fetch) → downloads work; tick **File downloads on** ✓ and move to step 6.
- **Both the default fetch and the sandbox fetch fail** → that's the allowlist or egress setting, not the connection — show how to turn it on. Same non-technical care as step 4. Show only the path for their account type:
  - **Personal account** → open **Settings → Capabilities** (https://claude.ai/settings/capabilities) and set two things: turn on **Allow network egress**, and in the domain allowlist choose **All domains** — anything narrower can block the download.
  - **Organization account** → these are set org-wide by an **Owner**, under **Capabilities** (https://claude.ai/admin-settings/capabilities) — same two settings — plus turning on **Cowork** (https://claude.ai/admin-settings/cowork). Send the relevant link to whoever owns the org.

  Full walkthrough with screenshots, one link: personal → https://wattdata.ai/docs/integrate/claude/personal-account; organization → https://wattdata.ai/docs/integrate/claude/org-user.

  **End on a tappable confirmation.** Offer as Interactive inputs:
  - **Enabled it** → re-run the download probe (default fetch, then the sandbox fallback). Comes back → tick ✓ and move to step 6. Still blocked → say so and put them back at the instructions.
  - **The option isn't available** *(organization only)* → these settings are org-wide and their Owner hasn't enabled them yet; give them the org-configuration link (https://wattdata.ai/docs/integrate/claude/org-configuration) to send to the Owner, and offer to re-check once it's done.
  - **Contact support** → hand to `/watt:help` to reach a human, carrying the symptom (exports won't download, and what they've tried).

### 6 — Turn on automatic updates

This one **can't be verified** — Claude exposes no way to read the setting — so it's a guided step the user confirms. State plainly why it matters: **Claude never updates the plugin on its own.** Until this is on, they stay on the version they installed — they won't get new features or fixes as we ship them. Everyone should turn it on. Show only the path for their account type:
- **Personal account** → Open **Customize → Plugins → Browse plugins** (https://claude.ai/customize/plugins?browse), find **Watt** on the **Personal** tab, click the **⋯** menu next to it and toggle on **Sync automatically**, then click **Check for updates** once — syncing won't start on its own until you do.
- **Organization account** → If your organization installed Watt for you, it shows under the **Your organization** tab and stays current automatically — nothing for you to do. If you installed it yourself under the **Personal** tab, follow the personal steps above.

**End on a tappable confirmation.** Offer as Interactive inputs:
- **Turned it on** → tick **Automatic updates on** ✓ and move to step 7.
- **My organization manages it** → the org's installation keeps it current automatically — nothing for them to do. Tick ✓ and move on.
- **Contact support** → hand to `/watt:help` to reach a human.

### 7 — Done — show the full checklist, then point the way

Render the checklist with all five items ticked ✓. Tell them Watt is configured and ready, and that they can return to **`/watt:configure`** any time something stops connecting.

One tip worth more than it looks:
- **Describe the *why*, not the *how*.** Tell Watt who you're trying to reach and why they buy — what they care about — not a spec like "30–45, $200k+ HHI, in California." That's just list-pulling. Give Watt the why and it figures out the how better than a person can: sell to bar owners — hard to find, not on LinkedIn — and the graph knows who's buying bar POS systems, plus fifty other angles on them.

Then set them loose — the handoff happens right here in the chat. Offer the three ways in as Interactive inputs; when they pick one, invoke that skill's command and let it take over. Don't fire a canned task of your own — the skills are guided and will ask what they actually want. The three:
- **Build an audience** → `/watt:audience` — describe who you want to reach; Watt engineers the signals into an audience, then you analyze who's in it or activate it on a platform.
- **Explore what's out there** → `/watt:explore` — see what the Signal Graph holds right now; the fastest way to size up an idea.
- **Get help** → `/watt:help` — ask how something works, request a signal or feature, or reach our team.

## How to behave

- **Verify what you can; never claim a setting you can't see.** The connection and the download check verify themselves — run them and report what actually happened. Automatic updates can't be read, so it's confirmed by the user, never asserted as done.
- **The download check needs both attempts before it fails.** A blocked download and a fetch the tool simply couldn't make are not the same thing. The default fetch tool can choke on an over-length download URL — so a first-fetch failure is never the verdict; retry from the code sandbox, and only call downloads blocked when that fails too.
- **Show one path, not all of them.** Step 2 settles personal vs. organization (a required pick), so every later step shows only that account type's path — one move, one link. Don't paste both branches and every what-if into the chat; let the tappable choices funnel.
- **A connection or authentication failure is configure's job, not a transient.** This is the one skill that owns the connect path, so work the connector beat — don't loop the probe, don't go diagnosing the connector or the MCP registry. If a later check fails on connection/auth rather than its own setting, it's the connector again: route back to step 4.
- **Never push past a step that isn't done.** Move on a user's pick, not a guess; re-run the self-verifying probe after they say they fixed it, and say so plainly if it still fails.
- **Configure never files a ticket itself.** Reaching a human is `/watt:help`'s lane — hand off with the symptom in tow; don't call the support channel from here.
