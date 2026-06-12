"""
Score an owned entity set against a signal pool and write the strategy-overlay
roster CSV (entity_id, overlay_score, signals_matched, rank) deterministically,
so the model never hand-computes the weighted sum, hand-ranks, or hand-writes the
CSV (all of which drift and can't be audited).

strategy-overlay runs entity_traits with format='csv' over the source set's
entity-ID URI, the signal pool as the `expressions` list (≤100 per call), and
downloads the per-entity match matrix: one row per source entity, an entity_id
column plus one 0/1 column per pool signal (column header = the signal's label).
A pool over 100 signals arrives as several matrix CSVs, each covering a subset of
the signal columns for the SAME source entities; this script joins them on
entity_id (a column missing for an entity is treated as 0 — unmatched).

    python3 scripts/overlay_score.py \
        --matrix matrix1.csv matrix2.csv … \
        --out roster.csv
      < config.json          # {"weights": {"<label>": <weight>}, "workflow_id": "…"}

  --matrix   one or more entity_traits format='csv' match-matrix exports. Every
             column other than entity_id is a signal column; its value is matched
             when truthy (1/true/yes or any non-zero number), else unmatched.
  --out      roster CSV path (columns entity_id, overlay_score, signals_matched,
             rank; header included).
  stdin      JSON config. `weights` maps a signal-column label → its weight; any
             column absent from the map (or an absent/empty map) defaults to
             weight 1, so the default overlay_score is a plain count of matched
             signals. `workflow_id` is echoed through, not used in the math.

overlay_score = Σ (weightᵢ × matchᵢ) over the pool; signals_matched = Σ matchᵢ
(the unweighted count). The whole source set is ranked descending by
overlay_score, ties broken by entity_id ascending so the rank is fully
deterministic; an entity matching zero signals scores 0 and STAYS in the roster.

Emits (stdout) a JSON summary the agent reports verbatim:
  { "source_size": N, "scored": N, "scored_zero": Z, "out": "<path>" }

source_size = scored = distinct source entities in the matrix; scored_zero =
those matching no pool signal. No MCP calls, stdlib only, deterministic: same
matrices + same weights → same CSV.
"""

import argparse
import csv
import json
import sys

ENTITY_COL = "entity_id"
_TRUE = {"1", "true", "t", "yes", "y"}


def die(code, msg):
    sys.stderr.write("overlay_score: %s\n" % msg)
    sys.exit(code)


def is_matched(raw):
    """A matrix cell is a match when truthy: 1/true/yes, or any non-zero number."""
    if raw is None:
        return False
    s = str(raw).strip().lower()
    if s == "":
        return False
    if s in _TRUE:
        return True
    try:
        return float(s) != 0.0
    except ValueError:
        return False


def read_config():
    """Read {weights, workflow_id} JSON from stdin; empty stdin → defaults."""
    raw = sys.stdin.read().strip()
    if not raw:
        return {}, None
    try:
        cfg = json.loads(raw)
    except ValueError as e:
        die(2, "stdin is not valid JSON: %s" % e)
    if not isinstance(cfg, dict):
        die(2, "stdin config must be a JSON object")
    weights = cfg.get("weights") or {}
    if not isinstance(weights, dict):
        die(2, "config.weights must be an object")
    return weights, cfg.get("workflow_id")


def weight_for(label, weights):
    """Weight for a signal column; absent → 1 (uniform default)."""
    if label not in weights:
        return 1.0
    try:
        return float(weights[label])
    except (TypeError, ValueError):
        die(2, "weight for %r is not a number" % label)


def as_number(score):
    """Emit an integral score as an int (clean CSV), else a rounded float."""
    r = round(score, 6)
    return int(r) if r == int(r) else r


def main(argv=None):
    p = argparse.ArgumentParser(
        description="score an entity_traits match matrix -> overlay roster CSV")
    p.add_argument("--matrix", nargs="+", required=True,
                   help="entity_traits format='csv' match-matrix export(s).")
    p.add_argument("--out", required=True, help="roster CSV path to write.")
    args = p.parse_args(argv)

    weights, _workflow_id = read_config()

    # entity_id -> [accumulated overlay_score, accumulated signals_matched].
    # Joining several matrices on entity_id unions their signal columns; the same
    # entity_id legitimately recurs across files, each carrying a disjoint subset
    # of the pool's signals.
    score = {}
    matched = {}
    order = []  # first-seen order, only to seed a stable set of ids before sort

    for path in args.matrix:
        try:
            fh = open(path, newline="", encoding="utf-8")
        except OSError as e:
            die(2, "cannot read matrix %r: %s" % (path, e))
        with fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None or ENTITY_COL not in reader.fieldnames:
                die(2, "matrix %r has no %s column" % (path, ENTITY_COL))
            signal_cols = [c for c in reader.fieldnames if c != ENTITY_COL]
            for row in reader:
                eid = (row.get(ENTITY_COL) or "").strip()
                if eid == "":
                    continue
                if eid not in score:
                    score[eid] = 0.0
                    matched[eid] = 0
                    order.append(eid)
                for col in signal_cols:
                    if is_matched(row.get(col)):
                        score[eid] += weight_for(col, weights)
                        matched[eid] += 1

    if not order:
        die(2, "no source entities found in the matrix")

    # Rank: overlay_score desc, then entity_id asc — fully deterministic, ties
    # get distinct sequential ranks ordered by entity_id.
    ranked = sorted(score, key=lambda e: (-score[e], e))

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["entity_id", "overlay_score", "signals_matched", "rank"])
        for i, eid in enumerate(ranked):
            w.writerow([eid, as_number(score[eid]), matched[eid], i + 1])

    json.dump({
        "source_size": len(ranked),
        "scored": len(ranked),
        "scored_zero": sum(1 for e in ranked if matched[e] == 0),
        "out": args.out,
    }, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
