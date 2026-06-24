# Watt plugin — pointing to the docs

The published customer docs live at **https://wattdata.ai/docs** — Watt's
long-form companion to the in-plugin help. The docs change over time, so
**don't hardcode or memorize page paths** — find the right page live.

## Reaching a page

- **The index is `https://wattdata.ai/llms.txt`** — a flat list of every docs
  page with a one-line description. Fetch it, find the page whose description
  fits, and take its `/docs/<path>`.
- **Read the page's LLM-native content at the `llms.mdx` prefix** —
  `https://wattdata.ai/llms.mdx/docs/<path>` (e.g.
  `https://wattdata.ai/llms.mdx/docs/get-started/quickstart`). That's the
  markdown form, best for reading in-session.
- **Link the human page** — `https://wattdata.ai/docs/<path>` — when you offer
  the user a read-more. Never link a path you didn't reach through llms.txt; if
  you can't find the page, link the docs root and let them browse.

## When a docs link helps an answer

- **Answer first**, then offer at most one page as a plain markdown link — never
  instead of answering.
- **The plugin changelog is separate** — it lives in the public plugin repo
  (read `https://raw.githubusercontent.com/wattdata/plugin/main/CHANGELOG.md`,
  link the `blob` URL), not under `/docs`. The `/docs/signal-graph/changelog`
  page is the *data* changelog — a different thing; don't answer plugin-version
  questions from it.

The docs are organized roughly as **Get started · Learn · Signal Graph ·
Integrate** — enough to aim, not a list of URLs to reproduce.
