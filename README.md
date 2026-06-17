# Watt

Build custom audiences in minutes — describe the people you want to reach in
plain English, and Watt discovers the signals behind the idea: what exists, how
big and how fresh each signal is, and what's adjacent. When you want the people
and not just the understanding, Watt builds the audience, reads who it reaches,
and exports it as a platform-ready file for Meta or Google.

Watt runs on the **Signal Graph** — petabytes of raw signals traversed in
seconds — through the Watt MCP server. Work that used to take teams of data
engineers, scientists, and analysts now happens in a conversation.

## Install

In Claude Code, run two commands.

**1. Add the Watt marketplace** (this GitHub repo):

```
/plugin marketplace add wattdata/plugin
```

**2. Install the plugin** (`watt@watt` — the `watt` plugin from the `watt` marketplace):

```
/plugin install watt@watt
```

Restart Claude Code, then run any `/watt` command.

## What you can do

- **`/watt:explore`** — interrogate the Signal Graph for an idea: what's there,
  how big and fresh, and what related angles are worth a look. Read-only.
- **`/watt:audience`** — when you want the actual people: build an audience to a
  size you pick, the widest reach, or the highest-intent few; profile a market
  to see who's in it; read who an audience reaches; or export it to Meta or
  Google. You can also start from a list you own — match it, expand it, or learn
  what defines it.
- **`/watt:quickstart`** — a short guided walkthrough if you're new.
- **`/watt:help`** — what Watt can do, whether the data you need exists (it goes
  and checks), or reach the team.

## Requirements

- Claude Code with plugin support.
- Python 3 on your PATH — Watt's local helpers run on it.
- A Watt account — sign-in is handled on first use.
- US-only data; person audiences; adults only.

## Repository layout

The repository root *is* the plugin — the marketplace catalog and the plugin
manifest sit side by side, with the plugin's components at the top level.

```
.claude-plugin/
  marketplace.json   the marketplace catalog
  plugin.json        the plugin manifest
skills/  agents/  hooks/  context/  scripts/  output-styles/
.mcp.json            the Watt MCP server declaration
```

## License

[Apache 2.0](./LICENSE).
