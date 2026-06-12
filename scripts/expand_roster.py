"""
Build the strategy-expand roster from entity_resolve exports — dedupe across
exports, apply the quality floor, and write the roster CSV
(entity_id, match_confidence, match_criteria_count) deterministically, so the
model never hand-dedupes or hand-counts corroboration (that drifts and can't be
audited).

strategy-expand runs ONE entity_resolve call with format='csv' (the inline
format='none' path caps at the top 100 entities — unusable for a real list) and
downloads the export(s). Each export row is one matched entity: columns
`entity_id`, `overall_quality_score`, `matches_json`, `identifier_*`. Across
multiple exports — input batches, paginated csv_resource_uri pages, or several
identifier groups — the same entity_id legitimately recurs, each occurrence
carrying its own Noisy-OR overall_quality_score and its own matched criteria.
This script reads every export, keeps the HIGHEST score per entity_id, unions the
distinct criteria that matched it across all occurrences (the corroboration
count), drops anything below the floor, and writes the survivors.

    python3 scripts/expand_roster.py \
        --exports export1.csv export2.csv … \
        --quality-floor 0 \
        --out roster.csv

  --exports        one or more entity_resolve exports. CSV (format='csv', the
                   default path) read by column; .json/.jsonl (a saved
                   format='none'/'jsonl' response or bare entity array) also
                   accepted. Each entity needs an entity_id and
                   overall_quality_score; matches drive the criteria count.
  --quality-floor  minimum overall_quality_score to keep (default 0 — keep every
                   match; the whole point of expand is the widest net).
  --out            roster CSV path (columns entity_id, match_confidence,
                   match_criteria_count; header included).

Emits (stdout) a JSON summary the agent reports verbatim:
  { "resolved_count": N, "below_floor_count": M, "quality_floor": F, "out": "<path>" }

resolved_count = distinct entities kept (≥ floor); below_floor_count = distinct
entities whose best score was under the floor. No MCP calls, stdlib only,
deterministic: same inputs + same floor → same CSV (entity_ids sorted).
"""

import argparse
import csv
import json
import sys


def _criteria_keys(matches):
    """Distinct criterion keys from a matches value (the corroboration count).

    Each match entry identifies which submitted criterion matched this entity.
    entity_resolve's export names them `criterion_type` + `criterion_value`; key
    on that pair so two distinct submitted values count as two even when they
    share a type, and the same matched value across exports counts once. Older
    `id_type`/`criterion`/`type`/`field` shapes are accepted as fallbacks, and a
    wholly unknown shape still counts as one distinct criterion (stable
    serialization) rather than collapsing to zero.
    """
    keys = set()
    if isinstance(matches, str):
        try:
            matches = json.loads(matches)
        except (json.JSONDecodeError, TypeError):
            return keys
    if isinstance(matches, dict):
        matches = [matches]
    if not isinstance(matches, list):
        return keys
    for m in matches:
        if isinstance(m, dict):
            ctype = m.get("criterion_type") or m.get("id_type") or m.get("type") or m.get("field")
            cval = m.get("criterion_value") or m.get("criterion") or m.get("value")
            if ctype is not None or cval is not None:
                keys.add(f"{ctype}\x1f{cval}")
            else:
                keys.add(json.dumps(m, sort_keys=True))
        else:
            keys.add(str(m))
    return keys


def rows_from_csv(path):
    """Yield (entity_id, score, matches_raw) from a format='csv' resolve export."""
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            yield row.get("entity_id"), row.get("overall_quality_score", 0.0), row.get("matches_json")


def rows_from_json(path):
    """Yield (entity_id, score, matches) from a format='none'/'jsonl' response or array."""
    with open(path) as f:
        text = f.read().strip()
    docs = []
    try:
        docs = [json.loads(text)]
    except json.JSONDecodeError:
        docs = [json.loads(line) for line in text.splitlines() if line.strip()]
    for doc in docs:
        entities = doc.get("entities", []) if isinstance(doc, dict) else (doc if isinstance(doc, list) else [doc])
        for e in entities:
            yield e.get("entity_id"), e.get("overall_quality_score", 0.0), e.get("matches")


def main(argv=None):
    p = argparse.ArgumentParser(description="dedupe entity_resolve exports -> expand roster CSV")
    p.add_argument("--exports", nargs="+", required=True,
                   help="entity_resolve exports: CSV (format='csv') or JSON/JSONL.")
    p.add_argument("--quality-floor", type=float, default=0.0)
    p.add_argument("--out", required=True, help="roster CSV path to write.")
    args = p.parse_args(argv)

    best = {}      # entity_id -> max overall_quality_score seen
    criteria = {}  # entity_id -> set of distinct matched-criterion keys (union across exports)
    no_id = 0
    for path in args.exports:
        reader = rows_from_csv(path) if path.lower().endswith(".csv") else rows_from_json(path)
        for eid, raw_score, matches in reader:
            if eid is None or eid == "":
                no_id += 1
                continue
            eid = str(eid)
            try:
                score = float(raw_score)
            except (TypeError, ValueError):
                score = 0.0
            if eid not in best or score > best[eid]:
                best[eid] = score
            criteria.setdefault(eid, set()).update(_criteria_keys(matches))

    kept = sorted((eid for eid, s in best.items() if s >= args.quality_floor),
                  key=lambda x: (len(x), x))
    below = sum(1 for s in best.values() if s < args.quality_floor)

    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["entity_id", "match_confidence", "match_criteria_count"])
        for eid in kept:
            w.writerow([eid, best[eid], len(criteria.get(eid, ()))])

    json.dump({
        "resolved_count": len(kept),
        "below_floor_count": below,
        "quality_floor": args.quality_floor,
        "out": args.out,
    }, sys.stdout, indent=2)
    sys.stdout.write("\n")
    if no_id:
        print(f"expand_roster: skipped {no_id} rows with no entity_id", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
