#!/usr/bin/env python3
"""group_score.py — the deterministic ranking kernel for the `group` strategy.

The `strategy-group` worker (agents/strategy-group.md) partitions an
entity set into disjoint cells across one or more caller-named partition-type axes,
measures each cell's size and lift, and hands the cells here for the ranking math.
This script owns that math so it is auditable and identical across runs; the worker
never hand-computes a cell score or a rank. (Discovering *which* dimension separates
an audience is audience-analyze's read, not this kernel's job — so there is no
discovery mode here.)

Pure deterministic, stdlib-only, no MCP, no network, writes nothing to disk.

IO: reads one JSON object from stdin (or --input <file>), writes one JSON object
to stdout. Exit 0 on success, 2 on bad input, 1 on internal error.

stdin:
  { "min_cell_size": 1000, "top_k": 10,
    "cells": [ { "group_label": "TX · 25-34", "cell_size": 41000, "cell_lift": 2.6 } ] }
(coverage/set-size is the worker's to compute — the kernel only gates, scores, and ranks.)
stdout:
  { "cells": [ {group_label, cell_size, cell_lift, rank} … top_k ],
    "pruned": { "cells_below_floor": <int>, "people_in_pruned": <int> } }

The cell composite is concentration weighted by reach: score = cell_lift * ln(cell_size).
Lift leads (the "best-concentrated cell" objective); the log-size factor keeps a barely-
above-floor cell with freak lift from automatically outranking a far larger, still-distinctive
cell. The min_cell_size gate runs first, so freak-tiny cells never reach the scorer. The
composite is not emitted: rank carries the order, and cell_lift + cell_size (both in the
roster) plus this documented formula make "why A over B" answerable without a redundant column.
"""

import json
import math
import sys

DEFAULT_MIN_CELL_SIZE = 1000
DEFAULT_TOP_K = 10


def die(code, msg):
    sys.stderr.write("group_score: %s\n" % msg)
    sys.exit(code)


def to_num(x):
    """Coerce to a finite float, else None (bools are not numbers here)."""
    if x is None or isinstance(x, bool):
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def to_int(x):
    v = to_num(x)
    return None if v is None else int(v)


def read_input():
    args = sys.argv[1:]
    if "--input" in args:
        with open(args[args.index("--input") + 1], "r", encoding="utf-8") as fh:
            return fh.read()
    return sys.stdin.read()


def rank_cells(data):
    cells_in = data.get("cells")
    if not isinstance(cells_in, list):
        die(2, "input.cells must be an array")
    floor = to_int(data.get("min_cell_size"))
    if floor is None:
        floor = DEFAULT_MIN_CELL_SIZE
    top_k = to_int(data.get("top_k"))
    if top_k is None:
        top_k = DEFAULT_TOP_K

    survivors = []
    pruned_count = 0
    pruned_people = 0
    for c in cells_in:
        if not isinstance(c, dict):
            die(2, "each cell must be an object")
        size = to_int(c.get("cell_size"))
        lift = to_num(c.get("cell_lift"))
        if size is None or lift is None:
            die(2, "each cell needs numeric cell_size and cell_lift")
        if size < floor:
            pruned_count += 1
            pruned_people += size
            continue
        # composite documented in the module docstring; not emitted
        score = lift * math.log(size) if size > 0 else 0.0
        survivors.append({
            "group_label": c.get("group_label"),
            "cell_size": size,
            "cell_lift": round(lift, 2),
            "_score": score,
        })

    # rank: composite desc, then lift desc, then label asc — fully deterministic
    survivors.sort(key=lambda r: (-r["_score"], -r["cell_lift"], str(r["group_label"])))
    kept = survivors[:top_k]
    for i, r in enumerate(kept):
        r["rank"] = i + 1
        del r["_score"]

    return {
        "cells": kept,
        "pruned": {"cells_below_floor": pruned_count, "people_in_pruned": pruned_people},
    }


def main():
    try:
        raw = read_input()
    except OSError as e:
        die(2, "cannot read input: %s" % e)
    try:
        data = json.loads(raw)
    except ValueError as e:
        die(2, "input is not valid JSON: %s" % e)

    if not isinstance(data, dict):
        die(2, "input must be a JSON object")

    sys.stdout.write(json.dumps(rank_cells(data), indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 — top-level guard, mirrors signal_profile.py
        die(1, str(e))
