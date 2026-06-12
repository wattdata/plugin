# Signal metrics

The fields a Watt **signal** (trait) carries — **raw** from the graph and
**computed** by the scoring model — and the project-wide **default parameters**.
This doc defines the fields and the defaults; it says nothing about how they're
weighted, grounded, or ranked — that's the `signal-profiler` agent's job, and the
math runtime is [`scripts/signal_profile.py`](../scripts/signal_profile.py).
Edit this doc and that script together.

Every metric is oriented so **higher = "more of the thing it names"** — whether
that's *desirable* is a ranking's opinion, never the metric's.

## Raw fields

What Watt hands back per signal. Nothing else feeds the model — no extra calls,
no external baselines (which is why **lift is absent**: it needs a world baseline
that isn't here).

| Field | Source | Meaning |
|---|---|---|
| `similarity_score` | `trait_search` **only** | Semantic closeness to the *search phrase*. Query-time — relative to the phrase that surfaced it, not comparable across searches, not cacheable per trait. |
| `domain` | both | The trait's domain (`interest`, `intent`, `demographic`, …). |
| `size` | both | How many entities carry the trait (raw count). |
| `prevalence` | both | `size / universe` — the trait's share of the population it was measured against. |
| `skew` | `trait_get` **only** | Ratio of what Watt observes to what its ground-truth model expects. `1.0` = perfectly calibrated; `>1` over-counts, `<1` under-counts. Search results don't carry it. |

## Computed metrics

All derived from the raw fields above — no new inputs.

**Derived population.** Recover the size of the population a signal lives in by
algebra, never hardcode it:

```
universe = size / prevalence
```

| Metric | Equation | Range | Meaning |
|---|---|---|---|
| `relevance` | `1 / (1 + e^(−k·(similarity_score − s0)))` | [0, 1] | Match closeness, with the compressed similarity band (~0.6–0.85) stretched to fill [0,1]. The one query-time metric — `null` when no `similarity_score` is present. |
| `freshness` | `age = 1 if domain=="intent" else 30` → `f_min + (1−f_min)·2^(−age/H)` | [f_min, 1] | Recency proxy. Watt exposes no per-trait recency, so `intent` is treated as fresh, everything else as standing. Half-life form is ready for a real `age` field. |
| `rarity` | `−ln(prevalence)` | [0, ln(universe)] | How niche — surprisal in nats (raw, unbounded). |
| `specificity` | `−ln(prevalence) / ln(universe)` | [0, 1] | `rarity` normalized to [0,1] against the universe. |
| `breadth` | `clip( (ln(size) − ln(N_min)) / (ln(universe) − ln(N_min)), 0, 1 )` | [0, 1] | How big, normalized to [0,1]. |
| `size` | `size` (raw) | [0, universe] | How big, raw — also the value for reach ceilings and "drop signals under N" filters. |
| `coverage` | `e^(−λ·|ln(skew)|)` | (0, 1] | Calibration: `1.0` = on the money; falls off as `skew` departs from 1 in either direction. Direction is discarded (it's `ln(skew)` if ever needed). |

**Two pairs name one fact.** `rarity`/`specificity` are the same concept (how
niche), raw vs normalized; `breadth`/`size` likewise (how big). And when
`size / prevalence` clusters at one number across traits (≈ US adult population),
all four of `rarity`, `specificity`, `breadth`, `size` collapse to functions of
the same two inputs — `specificity = 1 − breadth` exactly. Keep them as named
views, but a single blended score must weight **at most one** of them.

## Default parameters

Project-wide defaults, tuned to person traits. **Baked into
[`signal_profile.py`](../scripts/signal_profile.py) and applied every run** — not
a per-call input; tuning is author-time (edit the script and this table together).
Revisit after a collinearity check (above) and a few real runs.

| Param | Shapes | Default | Direction |
|---|---|---|---|
| `s0` | `relevance` pivot — the `similarity_score` mapping to 0.5 | `0.73` | ↑ stricter · ↓ lenient |
| `k` | `relevance` gain — sigmoid sharpness around `s0` | `25` | ↑ more separation · ↓ near-linear |
| `H` | `freshness` half-life (days) | `30` | ↑ standing decays slower · ↓ harsher on non-intent |
| `f_min` | `freshness` floor — stalest signal's minimum | `0.25` | ↑ axis flattens · ↓ stale → 0 |
| `N_min` | `breadth` floor (people) — size that maps to breadth 0 | `100` | ↑ niche → 0 sooner · ↓ full size range |
| `λ` | `coverage` penalty — how hard miscalibration is punished | `1.0` | ↑ only well-calibrated score · ↓ tolerant |
