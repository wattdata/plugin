#!/usr/bin/env python3
"""signal_profile.py — the runtime of the Watt signal scoring model.

Fields & defaults: context/signal-metrics.md (defines the metrics
and the parameter defaults — keep them in sync with this runtime). This script
owns the math. Pure deterministic, stdlib-only, no MCP, no network. The
signal-profiler agent enriches signals (trait_get / grounding trait_search) and
feeds the result here; this script never fetches anything.

IO: reads one JSON object from stdin (or --input <file>), writes one JSON object
to stdout. Exit 0 on success, 2 on bad input, 1 on internal error.

Profile vs. score: every signal always gets its full axis vector (the profile).
A ranking method is OPTIONAL — supply one of weights / sort_by / score_by and the
signals are scored, ranked, and truncated to `limit`; supply none and they come
back in input order, unranked.

Input shape:
{
  "weights":  { "relevance":1, "specificity":1, "breadth":-1, "coverage":0.5 },  # normalized weighted mean
  "sort_by":  ["specificity","coverage"],          # lexicographic, descending
  "score_by": "relevance + specificity - breadth",  # arbitrary arithmetic over axis names
  "filters":  [ { "axis":"size", "op":">=", "value":5000 } ],  # optional hard cutoffs
  "limit":    null | <int>,                         # truncate ranked output
  "signals":  [ { "trait_hash","name","domain","size","prevalence","skew","similarity_score"? }, ... ]
}
At most ONE of weights / sort_by / score_by. None -> profile only.
The six model parameters are baked in (see PARAMS) per signal-metrics.md — not
an input; tuning is author-time (edit this script and the doc together).
"""

import json
import math
import re
import sys

# Baked-in model parameters — the project-wide defaults from signal-metrics.md.
PARAMS = {"s0": 0.73, "k": 25, "H": 30, "f_min": 0.25, "N_min": 100, "lambda": 1.0}

AXES = ["relevance", "freshness", "rarity", "specificity", "breadth", "size", "coverage"]
# Axes that all collapse to one fact when every trait shares a denominator.
SIZE_FAMILY = ["rarity", "specificity", "breadth", "size"]
RANKERS = ["weights", "sort_by", "score_by"]

_EXPR_OK = re.compile(r"^[-+*/().\d\seE]*$")


def die(code, msg):
    sys.stderr.write("signal_profile: %s\n" % msg)
    sys.exit(code)


def clip(x, lo, hi):
    return max(lo, min(hi, x))


def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))


def to_num(x):
    """Coerce to a finite float, else None (mirrors JS Number()/isFinite guards)."""
    if x is None or isinstance(x, bool):
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def relevance(s):
    # global sigmoid only: stretch the compressed similarity band with the fixed
    # pivot/gain. No similarity -> None (NOT 0); unmeasured, dropped from any score.
    v = to_num(s)
    return None if v is None else sigmoid(PARAMS["k"] * (v - PARAMS["s0"]))


def query_independent_axes(sig):
    out = {}
    notes = []
    size = to_num(sig.get("size"))
    prev = to_num(sig.get("prevalence"))
    skew = to_num(sig.get("skew"))

    # freshness — binary intent proxy
    age = 1 if sig.get("domain") == "intent" else 30
    out["freshness"] = PARAMS["f_min"] + (1 - PARAMS["f_min"]) * (2 ** (-age / PARAMS["H"]))

    # universe by algebra
    universe = None
    if size is not None and prev is not None and prev > 0:
        universe = size / prev
    else:
        notes.append("size/prevalence missing or zero — rarity/specificity/breadth not computed")

    # size (raw, neutral)
    out["size"] = size

    if universe is not None and universe > 0 and prev is not None and 0 < prev <= 1:
        ln_u = math.log(universe)
        out["rarity"] = -math.log(prev)                                   # [0, ln(universe)]
        out["specificity"] = clip(out["rarity"] / ln_u, 0, 1) if ln_u > 0 else None  # [0,1]
        ln_nmin = math.log(PARAMS["N_min"])
        out["breadth"] = (
            clip((math.log(size) - ln_nmin) / (ln_u - ln_nmin), 0, 1)
            if (ln_u - ln_nmin) != 0 else None
        )                                                                 # [0,1]
    else:
        out["rarity"] = out["specificity"] = out["breadth"] = None

    # coverage — folded skew (direction discarded)
    if skew is not None and skew > 0:
        out["coverage"] = math.exp(-PARAMS["lambda"] * abs(math.log(skew)))   # (0,1]
    else:
        out["coverage"] = None
        notes.append("skew missing — coverage not computed")

    return out, universe, notes


def passes_filters(axes, filters):
    for f in filters:
        v = axes.get(f.get("axis"))
        if v is None:
            return False                 # can't satisfy a cutoff on an unmeasured axis
        t = to_num(f.get("value"))
        op = f.get("op")
        ok = (
            v >= t if op == ">=" else
            v <= t if op == "<=" else
            v > t if op == ">" else
            v < t if op == "<" else
            v == t if op == "==" else
            v != t if op == "!=" else
            False
        )
        if not ok:
            return False
    return True


def weighted_mean(axes, weights):
    num = 0.0
    den = 0.0
    for axis, w in weights.items():
        if not w:
            continue
        v = axes.get(axis)
        if v is None:
            continue                     # null axis dropped; denominator renormalizes
        num += w * v
        den += abs(w)
    return None if den == 0 else num / den


def expression_score(axes, expr):
    """Restricted arithmetic eval: axis identifiers, numbers, + - * / ( ) only."""
    e = expr
    for a in AXES:
        v = axes.get(a)
        e = re.sub(r"\b%s\b" % a, "0" if v is None else "(%r)" % v, e)
    if not _EXPR_OK.match(e):
        raise ValueError("score_by contains unsupported tokens after axis substitution: %s" % expr)
    val = eval(e, {"__builtins__": {}}, {})  # noqa: S307 — whitelisted to arithmetic only
    return val if isinstance(val, (int, float)) and math.isfinite(val) else None


def collinearity_warning(by, spec):
    referenced = set()
    if by == "weights":
        for a, w in spec.items():
            if w and a in SIZE_FAMILY:
                referenced.add(a)
    elif by == "sort_by":
        for a in spec:
            if a in SIZE_FAMILY:
                referenced.add(a)
    elif by == "score_by":
        for a in SIZE_FAMILY:
            if re.search(r"\b%s\b" % a, spec):
                referenced.add(a)
    if len(referenced) > 1:
        return (
            "ranking references %d size-family axes (%s); "
            "if size/prevalence shares one denominator across traits these are the same fact — double-counted. "
            "Run the collinearity test (signal-metrics.md) and weight at most one."
            % (len(referenced), ", ".join(sorted(referenced)))
        )
    return None


def read_input():
    args = sys.argv[1:]
    if "--input" in args:
        with open(args[args.index("--input") + 1], "r", encoding="utf-8") as fh:
            return fh.read()
    return sys.stdin.read()


def main():
    try:
        raw = read_input()
    except OSError as e:
        die(2, "cannot read input: %s" % e)
    try:
        data = json.loads(raw)
    except ValueError as e:
        die(2, "input is not valid JSON: %s" % e)

    if not isinstance(data, dict) or not isinstance(data.get("signals"), list):
        die(2, "input.signals must be an array")

    filters = data["filters"] if isinstance(data.get("filters"), list) else []
    lim = data.get("limit")
    limit = lim if isinstance(lim, int) and not isinstance(lim, bool) else None

    # exactly-one-or-none ranking method
    present = [r for r in RANKERS if data.get(r) is not None]
    if len(present) > 1:
        die(2, "at most one ranking method allowed; got: %s" % ", ".join(present))
    by = present[0] if present else None
    spec = data[by] if by else None

    # per-signal axes (relevance is global; None when no similarity_score)
    rel_measured = 0
    rel_null = 0
    rows = []
    for sig in data["signals"]:
        axes, universe, notes = query_independent_axes(sig)
        axes["relevance"] = relevance(sig.get("similarity_score"))
        if axes["relevance"] is None:
            rel_null += 1
        else:
            rel_measured += 1
        rows.append({
            "trait_hash": sig.get("trait_hash"),
            "name": sig.get("name"),
            "axes": axes,
            "raw": {
                "domain": sig.get("domain"),
                "size": sig.get("size"),
                "prevalence": sig.get("prevalence"),
                "skew": sig.get("skew"),
                "similarity_score": sig.get("similarity_score"),
                "universe": universe,
            },
            "_notes": notes,
        })

    filtered_out = len([r for r in rows if not passes_filters(r["axes"], filters)]) if filters else 0
    if filters:
        rows = [r for r in rows if passes_filters(r["axes"], filters)]

    warning = None
    if by:
        warning = collinearity_warning(by, spec)
        if by == "weights":
            for r in rows:
                r["score"] = weighted_mean(r["axes"], spec)
            rows.sort(key=lambda r: (r["score"] if r["score"] is not None else -math.inf), reverse=True)
        elif by == "score_by":
            for r in rows:
                r["score"] = expression_score(r["axes"], spec)
            rows.sort(key=lambda r: (r["score"] if r["score"] is not None else -math.inf), reverse=True)
        elif by == "sort_by":
            def sort_key(r):
                return tuple((r["axes"].get(a) if r["axes"].get(a) is not None else -math.inf) for a in spec)
            rows.sort(key=sort_key, reverse=True)
        for i, r in enumerate(rows):
            r["rank"] = i + 1
        if limit is not None:
            rows = rows[:limit]

    signals = []
    for r in rows:
        o = {"trait_hash": r["trait_hash"], "name": r["name"]}
        if "rank" in r:
            o["rank"] = r["rank"]
        if "score" in r:
            o["score"] = r["score"]
        o["axes"] = r["axes"]
        o["raw"] = r["raw"]
        if r["_notes"]:
            o["notes"] = r["_notes"]
        signals.append(o)

    out = {
        "model": "signal-scoring/v1",
        "params": PARAMS,                                  # baked-in, echoed for self-description
        "relevance": {"measured": rel_measured, "unmeasured": rel_null},
        "ranked_by": by,                                   # None when profile-only
        "ranking_spec": spec,
        "collinearity_warning": warning,
        "filtered_out": filtered_out,
        "count": len(rows),
        "signals": signals,
    }
    sys.stdout.write(json.dumps(out, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 — top-level guard mirrors the .mjs
        die(1, str(e))
