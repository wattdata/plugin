# Watt record contract

Every composition you build — a **signal pool**, a **signal stack**, or a
**roster** — is saved to a **CSV file** in the working directory, named for the
audience (e.g. `watt-audience-weekend-hikers.csv`; a refresh overwrites it).
Re-write it on every change to the composition, so the saved state stays current.
CSV because the state is structured and re-parsed downstream: it round-trips
cleanly, opens in any spreadsheet, and a roster's rows are the same shape as the
`roster.csv` the graph returns.

A record file is two parts:

- **A metadata header** — lines beginning with `#`, one labeled fact each: the
  `kind` (pool / stack / roster), the audience name, the measured `reach` with
  its target or band, the `location` (always written — `none (national)` when no
  filter rode along, never dropped), the `entity_type`, the `workflow` id, and
  the `angles:` map (open / covered / set-aside per angle) — the convergence
  state that must survive compaction. A refresh re-writes the file with today's
  reach and a `· refreshed` suffix on the reach line.
- **A typed table** — a column-header row, then one row per item: each **signal**
  for a pool or stack (its `role`, name, the graph facts, and `trait_hash`); the
  **entity-ID sample** with its classification columns for a roster (whose full
  set lives behind its `roster_uri` — itself a CSV of those per-entity columns).
  A *grouped* roster is the one two-tier case: its in-file rows are the per-group
  cells (each with its own `entity_ids_uri`), while `roster_uri` holds the
  per-entity assignment.

The `role` column carries the boolean structure, so a downstream step rebuilds
the expression exactly as composed without an operator ever seeing a boolean:
`defining` = any-of (OR), `must-have` = all-of (AND), `exclusion` = none-of
(AND-NOT). Names ride beside the hashes so a re-supplied record stays readable.

Hold it to valid CSV: quote any field that contains a comma, a quote, or a
newline, and double an internal quote — a trait name with a comma is the common
case. The file holds signals and entity IDs only, **never PII**.

The rendered visual is what the user reads; the saved file is what they keep —
name it in one quiet line. Where a visual can't render, give the facts in plain
labeled lines. Each skill supplies its own record's shape; this contract owns the
rule. Rendering itself is the render contract, `context/visuals.md`.
