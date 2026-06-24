# Changelog

## [0.14.1] - 2026-06-24

### Fixed
- Audience exports now report the true number of people written to the file, and every export — Meta, Google, and Reddit — leaves out people with no identifier the platform can match, so the file carries only reachable rows and the count you see matches what's in it.

## [0.14.0] - 2026-06-24

### Improved
- `/watt:quickstart` is now `/watt:configure` — a setup and connectivity check you can run any time something stops connecting, not just at first install. It verifies your Signal Graph connection and that your exports can download for you, and walks you through fixing anything that's off, one step at a time.
- `/watt:configure` now asks up front whether you're on a personal or organization account, then shows only the setup steps that apply to you — one clear move at a time, with a link to the full guide instead of a wall of instructions.
- `/watt:configure` is more reliable at confirming your exports can download, so a working setup is no longer mistaken for a blocked one.

## [0.13.0] - 2026-06-24

### Improved
- `/watt:quickstart` now walks setup one step at a time — connecting the Signal Graph and getting your Claude settings right are separate beats, and each waits for you before it moves on.
- `/watt:quickstart` now covers turning on automatic updates so you don't get stranded on a stale version, including the manual refresh path, and links the matching setup guide so you can follow along with screenshots instead of memorizing the steps.
- `/watt:quickstart` now points you to Opus for the signal-engineering work, where its larger context and reasoning pay off most.

### Removed
- Watt no longer surfaces support-ticket updates or new-version notices automatically at the start of a session. You can still ask `/watt:help` what's changed, whether you're on the latest, and the status of your tickets whenever you want.

## [0.12.0] - 2026-06-23

### New
- When you start working in Watt, it now surfaces any of your support tickets that changed in the last few days — so a team reply, a status change, or a fix reaches you right where you are.
- `/watt:help` now works on every surface, including the Claude Chat app, and opens with a menu of the common things you can ask — what you can do, why something isn't working, what's changed, or reaching the team.

### Improved
- `/watt:help` gets you unstuck faster: it answers how-to questions from the live docs, points you to the right command, and when you report a bug or request a signal or feature it suggests a workaround and files it for the team.
- Watt now makes clear it's built for Claude Cowork, Claude Code, and the Claude Agent SDK: `/watt:quickstart` confirms your platform before setup, and `/watt:audience` and `/watt:explore` flag it when you're somewhere Watt can't run, like the Claude Chat app.
- `/watt:explore` now points you to `/watt:audience` when you bring it a list of people, so it's clear where to read or build from a list you already own.
- `/watt:explore` now explains the figures on each signal the first time you see them — its size, how fresh it is, and how closely it matches your idea — so the findings read clearly from the start.
- `/watt:explore` now makes clear that the signals you keep are yours to combine and choose among when you build an audience in `/watt:audience`.

### Fixed
- `/watt:explore` now shows each signal under a clean, readable name, keeping the category path wherever that's what tells two close signals apart — so look-alike signals at different sizes read as the distinct signals they are.
- Reddit exports from `/watt:audience` now produce a file that loads directly into Reddit Ads, with emails and mobile device IDs in the exact format Reddit's customer-list upload expects.

## [0.11.0] - 2026-06-19

### New
- Watt now tells you at the start of a session when a newer version is available, so you know when to update.
- Ask Watt what's new — `/watt:help` now tells you what's changed in your version and whether you're on the latest.

### Improved
- `/watt:quickstart` now spells out connection setup step by step — installing and authorizing the Signal Graph connector, and the exact capability settings (network access and the domain allowlist) that let your audience exports download.
- `/watt:explore` stays focused on discovery: it keeps your working folder clean and carries the signals you keep straight into `/watt:audience` when you're ready to build an audience.
- Going deep on an angle in `/watt:explore` returns faster, and the wait now shows clear progress while Watt sweeps the graph for signals.
- When you ask `/watt:explore` how your kept signals stack up, it now shows the read as a visual with the scoring laid out per signal — so you can see at a glance which are tightest, freshest, and most distinctive.

## [0.10.0] - 2026-06-19

### Improved
- `/watt:quickstart` is now a focused first-run setup — it introduces Watt, walks you through connecting the Signal Graph and the Claude settings you need (whether you're on a personal or organization account), then points you to explore, build, or get help with ready-to-run example prompts.

### Fixed
- Clickable choices now render reliably wherever Watt asks you to pick — selecting an option no longer depends on a renderer that could fail to load.

## [0.9.0] - 2026-06-17

### New
- `/watt:quickstart` now confirms Watt is connected before your first build and walks you through connecting if it isn't — including the admin route when your plan needs one to enable it; `/watt:help` can walk you through the same.
- When Watt isn't connected yet, `/watt:quickstart` can now offer a one-click Connect right in the chat.
- When you export to Meta, Google, or Reddit, `/watt:audience` now tells you your expected audience size — roughly how many of those people the platform will likely reach, in real numbers — and `/watt:help` explains what drives it and how to lift it.

### Improved
- If Watt ever needs (re)connecting while you're working, `/watt:quickstart`, `/watt:explore`, and `/watt:audience` now consistently show you how to fix it — the connect steps plus links to set it up or have your Claude organization admin enable it.
- Before exporting, `/watt:audience` now confirms up front that it's connected and ready to run the export, and if it isn't — or your organization's settings block the export — gives the exact steps and a doc link to get unblocked, including a line to forward to your admin.
- Exporting an audience to Meta, Google, or Reddit now names each platform plainly and describes the audience size you can expect in clearer, everyday language.

## [0.8.0] - 2026-06-16

### Improved
- Smoother first run — Watt no longer adds its own sign-in instructions to your first request.

### Fixed
- Visuals and `/watt:help` now load cleanly at the start, without the stray errors that could precede the first one.

## [0.7.0] - 2026-06-15

### Improved
- Watt's built-in help draws on its full capability map, so "what can I do" answers cover everything Watt can do.

## [0.6.0] - 2026-06-15

### New
- Export an audience to Reddit as a platform-ready file — pick Reddit at export and `/watt:audience` writes the upload file, with the same scale-and-identifier confirmation as Meta and Google.

## [0.5.0] - 2026-06-15

### New
- Every audience or signal set you build is saved to a CSV file you can open in any spreadsheet, keep, reopen, or share — the full composition in one place.

## [0.4.0] - 2026-06-13

### Improved
- Interactive visuals can use the full range of the host's controls, so they render more consistently.

## [0.3.0] - 2026-06-12

### Improved
- Watt's in-chat visuals now adapt to your light or dark theme — they sit cleanly in whichever you're using, with text that stays easy to read, instead of always rendering on a fixed dark card.

## [0.2.0] - 2026-06-12

### Improved
- `/watt:quickstart` now ends with a real audience you built. Pick a starter audience — each showing a different way Watt can build one — or describe your own with help shaping the description, watch the signals behind it become an audience with a measured size, then export it, see who's in it, or keep exploring. The close points to `/watt:help` for the other ways in, like starting from a customer list you own.

### Fixed
- Signal scores during an audience build are cleaner — a size-related factor was being counted twice, which could distort the rankings you curate by.

## [0.1.0] - 2026-06-11

Initial public release.

Watt for Claude Code runs on the **Signal Graph** through the Watt MCP server.
Describe the people you want to reach in plain English; Watt finds the signals
behind the idea, builds the audience, reads who it reaches, and exports it.

- **`/watt:explore`** — interrogate the Signal Graph for an idea: what exists,
  how big and fresh each signal is, and what's adjacent. Read-only.
- **`/watt:audience`** — build an audience to a size you pick, the widest
  credible reach, or the highest-intent few; profile a market; read who an
  audience reaches; or export it to Meta or Google. You can also start from a
  list you own — match it, expand it to its widest reach or whole households,
  find more people like it, or learn what defines it.
- **`/watt:quickstart`** — a short guided walkthrough for new users.
- **`/watt:help`** — what Watt can do, whether the data you need exists, or
  reach the team.

US-only data; person audiences; adults only.
