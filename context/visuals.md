# Watt render contract — the operative visual rules

The rules a Watt render obeys. This file is delivered into context right after
the host visualize tool's own guidance (`read_me`) lands, and the `show_widget`
gate holds renders to it. The host's guidance and this contract divide cleanly:
**sandbox and pipeline facts are the host's — obey them verbatim. Styling is
Watt's — this contract overrides the host's styling guidance wherever the two
touch.** A render that adopts the host theme, leans on host CSS variables, or
comes out rounded is a brand regression, not a pass.

Scope: these rules dress **Watt's own renders only** — signals, signal pools
and stacks, audiences, profiles. A render unrelated to Watt work uses the host defaults;
mark its root element `data-non-watt` so the brand gate passes it through.

## Brand — the Watt override

Watt's renders sit on **one dark surface**, flat (no rounded corners), **two
tones per application — never three.** Lime earns attention; neutrals do the
work — so **lime appears in exactly two slots per render: the bolt mark and the
one hero figure.** Dense per-row data stays quiet (taupe / sand on faint tracks).

- **The surface lives on one *inner* wrapper with `background:#222222`** — the
  true root stays transparent (the host's transparency rule binds the *outer*
  container only), the tokens below scoped to that wrapper. The render is then
  **identical in the host's light and dark mode**.
- **No `--color-*` / `--border-radius-*` host variable is referenced.** Copy
  these tokens in:

```css
:root{
  --surface:#222222; --ink:#FFFFFF; --ink-quiet:#A29A7E;
  --lime:#D1FF01;          /* reserved — the mark + ONE hero figure only */
  --sage:#B8C3AE; --lavender:#D7D0F2;   /* pick ONE supporting accent */
  --alert:#FF6200;         /* rare */
  --track:rgba(255,255,255,.08);        /* faint size-bar track */
}
```

- **Lime grounds: the dark surface, taupe, or sand.** Size bars are a neutral
  fill (taupe/sand) on a faint track; disclose any nonlinear scale in the
  caption. Accents pair only with the surface, taupe, or sand. Orange is the
  rare alert. Color never carries meaning on its own.
- **Geist, two weights.** `font-family:'Geist'` on the wrapper (the loaded
  stylesheet ships only weights 400 and 500, so 500 is the heaviest there is);
  figures and labels in `'Geist Mono', ui-monospace, monospace` with
  `tabular-nums`. Scale does the work of weight; short mono-caps labels stay at
  the smallest mono size.
- **Flat form** — `border-radius:0` on every surface, badge, and bar. One
  exception: a decision-visual option control uses a lime fill and a small
  rounded corner.

## The pipeline

- **`read_me` once per session, before the first render** — `modules:
  ["data_viz","interactive"]`, `platform` from context (omit / `unknown` when
  unsure). Silent — never narrated (the one exception to narrating MCP calls).
  Call again only for a genuinely different module.
- **`show_widget` per render** — a `widget_code` HTML fragment; a **snake_case**
  `title`, specific and disambiguating (it's also the download filename:
  `trail_running_candidates`, not `widget`); **1–4 short (~5-word) factual**
  `loading_messages` in the user's language, in Watt's voice ("Sizing 12
  trail-running signals…").

## Render facts (obey verbatim — sandbox, not style)

- Fragment only — no `DOCTYPE`/`<html>`/`<head>`/`<body>`. No comments
  (`<!-- -->`, `/* */`). Order: short `<style>` → content → `<script>` last.
- First element: a visually-hidden one-line summary `<h2 class="sr-only">`.
  No emoji. Font floor 11px. Round every figure (417K, 1.4M).
- No `position:fixed`, no nested scrolling, no `display:none` during streaming.
  Desktop container is 680px — the wrapper spans 100%; assume no more.
- **One external resource only** — the Geist stylesheet, first in the fragment:
  `https://fonts.googleapis.com/css2?family=Geist:wght@400;500&family=Geist+Mono&display=swap`.
  No libraries — bars and lists are plain HTML/CSS.

## Behavior

- **Render on every beat that has signals to show.** Never substitute a prose
  list, a markdown table, or a raw fenced block as the thing the user reads.
- **Data visuals carry no controls and no `<script>`** — they explain and set
  up the ask; ordering and emphasis are decided before the render.
- **The decision lands in the one answerable decision visual**: each of its
  2–4 option controls fires `sendPrompt('<the answer in plain words>')`, so the
  pick arrives as the user's next message and *is* the answer — append a `↗`
  glyph to a control that sends. This `sendPrompt` wiring is the **only**
  script in any render. The host guidance also documents an elicitation form
  module (`class="elicit"` …) — a Watt decision is sendPrompt option controls,
  not that form. Where the visual can't return a pick, the structured question
  tool lands the decision; where there's neither, a formatted decision block
  does — a `→ your call:` line, then numbered options.
- **Same structure every render. Verified figures only — nothing speculative.**
  Ranked items carry the ranking's inputs, so *why X sits above Y* is
  answerable from the render.
- **The record rides beneath.** The fenced plain-text record (with
  `trait_hash`es) follows the visual in the message — quietly, never as the
  headline. It survives compaction, seeds `/watt:audience`, and is the full
  fallback wherever a visual can't render. The visual is never a fact's only
  home.
