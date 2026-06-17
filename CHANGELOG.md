# Changelog

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
