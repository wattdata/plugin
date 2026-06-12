#!/usr/bin/env python3
# Build the shareable two-section signal membership report for audience-analyze.
#
# Two sections: a SPECIFIED read (per-signal prevalence + a coverage
# distribution) and a DISCOVERED read (lift-scored defining traits + optional
# per-domain breakdown), with deterministic filters (negation, prevalence-noise,
# over/under split, coverage). This script consumes the structured read the
# audience-profiler advisor already produced. The profiler does the sampling and
# aggregation against the graph
# (it has the MCP access and the sample); this script does the deterministic
# shaping + HTML emission the model must not improvise. The SPECIFIED arrays are
# empty for a discovered-only read (the -list flavor, where no signals are
# supplied) — pass --no-specified to drop Section 1 entirely.
#
# Rendering is pure HTML + CSS — NO JavaScript, NO external fetch, NO CDN, NO
# Chart.js. Every "chart" is a CSS bar table: the label, a proportional bar, and
# the numeric value, all as real DOM text. This renders in any viewer, including
# ones with no internet and ones that block external scripts — a viewer where a
# Chart.js/CDN-based dashboard renders blank. The report is a client deliverable, so the styling is
# neutral and print-friendly — the Watt brand palette governs in-pane visuals,
# not this file.
#
# The two sections in detail:
#
#   SECTION 1 — YOUR SIGNALS (specified)
#     How the people in the audience express the signals it was composed from.
#       * per-signal prevalence within the audience (precomputed by the profiler)
#       * coverage distribution: how many specified signals each person hits
#       * customer-friendly quality chips per signal (reach / actively-searching /
#         match-to-brief / concentration), shown when present
#
#   SECTION 2 — DISCOVERED (net-new)
#     What stands out that was NOT specified.
#       * lift table — over-represented traits vs the average American
#       * optional segmentation panels by domain
#     DEDUPE: any discovered/breakdown row whose trait_hash matches a specified
#     signal is dropped, so Discovered is genuinely net-new (belt-and-suspenders —
#     the profiler is asked to dedupe upstream too).
#     NEGATION FILTER: rows whose value is "false"/"no"/"0" are inverse noise, dropped.
#
# No MCP calls. No randomness. Pure data-shaping + HTML emission. Deterministic:
# same profile + same meta → same report.
#
# Input: a single --profile JSON file with this shape (all arrays optional). The
# field names are the audience-profiler read's own, so the analyze
# skill passes the profiler arrays under these top-level keys with no per-field
# renaming — prevalence reads either `prevalence` or `audience_prevalence`, and a
# trait label reads either `trait_name` or `name`:
#
#   {
#     "specified":  [ { name, value?, domain?, trait_hash?, audience_prevalence,
#                       reach?, match_to_brief?, concentration?, actively_searching? } ],
#     "coverage":   [ { signals_hit, people } ],
#     "discovered": [ { name|trait_name, trait_value?, domain?, trait_hash?,
#                       audience_prevalence, world_prevalence, lift, under_represented? } ],
#     "breakdown":  [ { domain, title?, items: [ { name|trait_name, trait_value?,
#                       audience_prevalence, audience_count? } ] } ]
#   }
#
# Usage:
#   python3 build_report_membership.py --profile profile.json \
#     --title "In-market auto buyers" \
#     --location-label "Within 60 mi of Nashville, TN" \
#     --expression "(<hash> OR …) AND … AND NOT …" \
#     --headcount 240000 --sample 5000 --workflow-id W \
#     --gates '{"must_have":["Colorado resident"],"exclusion":["Gear resellers"]}' \
#     --summary "There are 240,000 in-market people within …" \
#     --out-html report.html --out-json report.json
#   python3 build_report_membership.py --help
import json
import math
import sys

HELP = """build_report_membership.py — build the shareable two-section signal membership report.

Reads a structured profile (--profile JSON: specified[], coverage[], discovered[],
breakdown[]) produced from the audience-profiler read, plus meta flags,
and writes a self-contained HTML report (no JavaScript, no CDN) + a JSON audit.
Section 1 (your signals): per-signal prevalence + coverage. Section 2 (discovered):
over-indexing lift table + optional segmentation panels, with the composition's own
signals and inverse ("=false") rows dropped.

Flags:
  --profile FILE          structured profile JSON (required)
  --title TEXT            report title (required)
  --location-label TEXT   human geo, e.g. "Within 60 mi of Nashville, TN" (required)
  --expression TEXT       human-readable composition (optional)
  --headcount N           full in-market headcount (required)
  --sample N              profiling sample size the stats were computed on (optional)
  --workflow-id TEXT      workflow id, shown in the footer (optional)
  --gates JSON            {"must_have":[...],"exclusion":[...]} of gate labels (optional)
  --summary TEXT          executive-summary prose (optional)
  --no-specified          drop Section 1 entirely (the -list discovered-only read:
                          no signals were supplied, so there is no your-signals half)
  --out-html FILE         output HTML path (required)
  --out-json FILE         output JSON audit path (required)
Exit codes: 0 ok · 1 invalid input.
"""

# Prevalence filters for the segmentation panels.
HIGH_PREVALENCE_DROP = 0.95
LONGTAIL_DOMAINS = {"intent", "interest", "affinity", "purchase", "content"}
LONGTAIL_MIN_PREVALENCE = 0.05

# Domains rendered as Section-2 segmentation panels, in display order: [domain, title, topN].
PANEL_DOMAINS = [
    ["intent", "Top intents by reach", 10],
    ["interest", "Engaged interests", 12],
    ["purchase", "Recent purchase categories", 10],
    ["affinity", "Brand affinities", 10],
    ["demographic", "Demographics", 14],
    ["household", "Household", 14],
    ["financial", "Financial", 12],
    ["lifestyle", "Lifestyle", 10],
    ["employment", "Employment", 10],
]

INK = "#1f2937"
MUTED = "#6b7280"
LINE = "#e5e7eb"
ACCENT = "#2563eb"
BAR_BG = "#eef2ff"


def fail(message):
    sys.stderr.write(f"build_report_membership: {message}\n")
    sys.stderr.write("Try --help.\n")
    sys.exit(1)


def num(x, default=0):
    """Mirror JS Number(x || default): falsy -> default; non-numeric -> default."""
    if x is None or x == "" or x is False:
        return default
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


# Valueless boolean flags — present → True, absent → False.
BOOLEAN_FLAGS = {"no-specified"}


def parse_args(args):
    if "--help" in args or "-h" in args:
        sys.stdout.write(HELP)
        sys.exit(0)
    out = {}
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--"):
            key = a[2:]
            if key in BOOLEAN_FLAGS:
                out[key] = True
                i += 1
                continue
            nxt = args[i + 1] if i + 1 < len(args) else None
            if nxt is None or nxt.startswith("--"):
                fail(f"flag --{key} expects a value")
            out[key] = nxt
            i += 1
        i += 1
    return out


def esc(x):
    s = "" if x is None else str(x)
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def pct(x):
    return f"{100.0 * num(x):.1f}%"


def is_negation(value):
    return str("" if value is None else value).strip().lower() in ("false", "no", "0")


def commas(n):
    v = num(n)
    return f"{int(v):,}" if float(v).is_integer() else f"{v:,}"


def fixed(x, digits):
    return f"{x:.{digits}f}"


# ---------------------------------------------------------------------------
# Section 1 — your signals (specified)
# ---------------------------------------------------------------------------
def build_specified(profile):
    specified = profile.get("specified") if isinstance(profile.get("specified"), list) else []
    per_signal = []
    for s in specified:
        per_signal.append({
            "name": s.get("name") or s.get("trait_name") or "",
            "value": s.get("value") or s.get("trait_value") or "",
            "domain": s.get("domain") or "",
            "trait_hash": s.get("trait_hash") or "",
            "prevalence": num(s.get("prevalence") if s.get("prevalence") is not None else s.get("audience_prevalence")),
            "reach": num(s.get("reach")),
            "actively_searching": s.get("actively_searching") is True or s.get("domain") == "intent",
            "match_to_brief": None if s.get("match_to_brief") is None else num(s.get("match_to_brief")),
            "concentration": None if s.get("concentration") is None else abs(num(s.get("concentration"))),
        })
    per_signal.sort(key=lambda a: a["prevalence"], reverse=True)

    coverage_in = profile.get("coverage") if isinstance(profile.get("coverage"), list) else []
    coverage = [
        {"signals_hit": num(c.get("signals_hit")), "people": num(c.get("people"))}
        for c in coverage_in
    ]
    coverage = [c for c in coverage if c["signals_hit"] >= 1]
    coverage.sort(key=lambda c: c["signals_hit"])
    return {"per_signal": per_signal, "coverage": coverage}


# ---------------------------------------------------------------------------
# Section 2 — discovered (net-new), deduped vs specified + negation-filtered
# ---------------------------------------------------------------------------
def build_discovered(profile, specified_hashes):
    over = []
    under = []
    discovered_in = profile.get("discovered") if isinstance(profile.get("discovered"), list) else []
    for row in discovered_in:
        if row.get("trait_hash") and row["trait_hash"] in specified_hashes:
            continue
        if is_negation(row.get("trait_value")):
            continue
        rec = {
            "trait_name": row.get("trait_name") or row.get("name") or "",
            "trait_value": row.get("trait_value") or "",
            "domain": row.get("domain") or "",
            "audience_prevalence": num(row.get("audience_prevalence")),
            "world_prevalence": num(row.get("world_prevalence")),
            "lift": num(row.get("lift")),
        }
        (under if row.get("under_represented") else over).append(rec)
    over.sort(key=lambda r: r["lift"], reverse=True)
    under.sort(key=lambda r: r["lift"])

    # Optional per-domain breakdown panels (segmentation), noise-filtered.
    by_domain = {}
    breakdown_in = profile.get("breakdown") if isinstance(profile.get("breakdown"), list) else []
    for panel in breakdown_in:
        items = panel.get("items") if isinstance(panel.get("items"), list) else []
        for it in items:
            dom = panel.get("domain") or ""
            if it.get("trait_hash") and it["trait_hash"] in specified_hashes:
                continue
            if is_negation(it.get("trait_value")):
                continue
            prev = num(it.get("audience_prevalence"))
            if prev > HIGH_PREVALENCE_DROP:
                continue
            if dom in LONGTAIL_DOMAINS and prev < LONGTAIL_MIN_PREVALENCE:
                continue
            by_domain.setdefault(dom, []).append({
                "trait_name": it.get("trait_name") or it.get("name") or "",
                "trait_value": it.get("trait_value") or "",
                "audience_prevalence": prev,
                "audience_count": num(it.get("audience_count")),
            })
    panels = []
    for dom, title, top_n in PANEL_DOMAINS:
        items = by_domain.get(dom)
        if not items:
            continue
        items.sort(key=lambda a: a["audience_prevalence"], reverse=True)
        panels.append({"domain": dom, "title": title, "items": items[:top_n]})

    return {"lift_over": over, "lift_under": under, "panels": panels}


# ---------------------------------------------------------------------------
# Pure-CSS bar table (no JS)
# ---------------------------------------------------------------------------
def bar_table(rows, value_max):
    # rows: [label, sublabel|None, barValue, valueText]
    vmax = value_max if value_max and value_max > 0 else 1.0
    out = ["<table class='bar'>"]
    for label, sub, bar_val, val_text in rows:
        width = max(0.0, min(100.0, (100.0 * num(bar_val)) / vmax))
        sub_html = f"<div class='val'>{esc(sub)}</div>" if sub else ""
        out.append(
            f"<tr><td class='lab'>{esc(label)}{sub_html}</td>"
            f"<td class='track'><div class='fill' style='width:{fixed(width, 1)}%'></div></td>"
            f"<td class='num'>{val_text}</td></tr>"
        )
    out.append("</table>")
    return "\n".join(out)


def render_html(meta, specified, discovered, discovered_only=False):
    # Section 1: specified signals quality table + coverage bars
    sig_rows = []
    for s in specified["per_signal"]:
        chips = [f"<span class='chip'>Reach {commas(s['reach'])}</span>"]
        if s["actively_searching"]:
            chips.append("<span class='chip chip-live'>Actively searching now</span>")
        if s["match_to_brief"] is not None:
            chips.append(f"<span class='chip'>Match {fixed(s['match_to_brief'], 2)}</span>")
        if s["concentration"] is not None:
            chips.append(f"<span class='chip'>Concentration {fixed(s['concentration'], 2)}</span>")
        prev_w = 100.0 * s["prevalence"]
        sig_rows.append(
            f"<tr><td class='lab'>{esc(s['name'])}<div class='val'>{esc(s['value'])}</div></td>"
            f"<td class='track'><div class='fill' style='width:{fixed(prev_w, 1)}%'></div></td>"
            f"<td class='num'>{pct(s['prevalence'])}</td>"
            f"<td class='chips'>{''.join(chips)}</td></tr>"
        )
    if specified["per_signal"]:
        specified_table = (
            "<table class='bar wide'><thead><tr><th>Signal</th><th>% of audience</th>"
            "<th class='num'>&nbsp;</th><th>Signal quality</th></tr></thead><tbody>"
            + "\n".join(sig_rows) + "</tbody></table>"
        )
    else:
        specified_table = "<p class='empty'>No specified signals supplied.</p>"

    cov = specified["coverage"]
    cov_max = max((c["people"] for c in cov), default=1) if cov else 1
    cov_rows = [
        [f"{int(c['signals_hit'])} signal{'s' if c['signals_hit'] != 1 else ''}", None, c["people"], commas(c["people"])]
        for c in cov
    ]
    coverage_table = bar_table(cov_rows, cov_max) if cov else "<p class='empty'>No coverage distribution supplied.</p>"

    # Section 2: lift table
    over = discovered["lift_over"][:15]
    lift_max = max((r["lift"] for r in over), default=1.0) if over else 1.0
    lift_rows = []
    for r in over:
        w = (100.0 * r["lift"]) / lift_max
        lift_rows.append(
            f"<tr><td class='lab'>{esc(r['trait_name'])}<div class='val'>{esc(r['trait_value'])}</div></td>"
            f"<td class='track'><div class='fill' style='width:{fixed(w, 1)}%'></div></td>"
            f"<td class='num accent'>{fixed(r['lift'], 1)}x</td>"
            f"<td class='num'>{pct(r['audience_prevalence'])}</td>"
            f"<td class='num muted'>{pct(r['world_prevalence'])}</td></tr>"
        )
    if lift_rows:
        lift_table = (
            "<table class='bar wide'><thead><tr><th>Trait</th><th>Over-index</th>"
            "<th class='num'>Lift</th><th class='num'>Audience</th><th class='num'>Avg. American</th>"
            "</tr></thead><tbody>" + "\n".join(lift_rows) + "</tbody></table>"
        )
    else:
        lift_table = "<p class='empty'>No over-indexing traits surfaced.</p>"

    # Section 2: segmentation panels. The intent panel renders on its own, above
    # the grid and surfaced by reach (intent over-indexes weakly, so it earns a
    # by-size read with the standing sparse-intent caveat — not a lift framing);
    # every other domain renders in the grid.
    def panel_html(p):
        pmax = max((it["audience_prevalence"] for it in p["items"]), default=1.0) if p["items"] else 1.0
        prows = [[it["trait_name"], it["trait_value"], it["audience_prevalence"], pct(it["audience_prevalence"])] for it in p["items"]]
        return (
            f"<div class='panel'><h3>{esc(p['title'])} <span class='dom'>{esc(p['domain'])}</span></h3>"
            + bar_table(prows, pmax) + "</div>"
        )

    intent_panel = next((p for p in discovered["panels"] if p["domain"] == "intent"), None)
    other_panels = [p for p in discovered["panels"] if p["domain"] != "intent"]
    panels_html = "\n".join(panel_html(p) for p in other_panels) if other_panels else "<p class='empty'>No segmentation panels supplied.</p>"

    gates = meta.get("gates") or {}
    and_list = ", ".join(esc(g) for g in (gates.get("must_have") or [])) or "none"
    andnot_list = ", ".join(esc(g) for g in (gates.get("exclusion") or [])) or "none"

    caveat = (
        "Lift compares this audience to the <b>average American</b>, not to your neighbors. "
        "A national baseline can't separate what's distinctive about <i>buyers</i> from what's "
        "distinctive about this <i>region</i> &mdash; regional over-indexing can show as lift. "
        "Read these as \"vs. the average American.\""
    )
    intent_note = (
        "Topic-level intent is sparse in the graph: individual intent topics rarely exceed a few "
        "percent prevalence, so the breakdown shows the rollups people hit most. The lift table is "
        "where low-prevalence-but-distinctive intents surface &mdash; read it for what over-indexes, "
        "not just what's common."
    )

    headcount = commas(meta["headcount"])
    sample = commas(meta.get("sample") or 0)

    css = (
        f"\n  :root{{--ink:{INK};--muted:{MUTED};--line:{LINE};--accent:{ACCENT};--bar:{BAR_BG};}}"
        + """
  *{box-sizing:border-box;}
  body{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
       color:var(--ink);background:#fff;margin:0;padding:0 24px 64px;line-height:1.5;}
  .wrap{max-width:1040px;margin:0 auto;}
  header{padding:32px 0 16px;border-bottom:2px solid var(--ink);}
  h1{font-size:24px;margin:0 0 4px;}
  .sub{color:var(--muted);font-size:14px;}
  .meta{display:flex;flex-wrap:wrap;gap:28px;margin:18px 0;font-size:13px;color:var(--muted);}
  .meta b{color:var(--ink);font-size:22px;display:block;line-height:1.2;}
  .summary{background:#f9fafb;border:1px solid var(--line);border-radius:8px;padding:16px 20px;margin:20px 0;}
  h2{font-size:18px;margin:40px 0 4px;padding-top:16px;border-top:1px solid var(--line);}
  .secsub{color:var(--muted);font-size:13px;margin:0 0 14px;}
  h3{font-size:15px;margin:22px 0 8px;}
  .dom{color:var(--muted);font-weight:400;font-size:11px;text-transform:uppercase;letter-spacing:.04em;margin-left:6px;}
  table.bar{width:100%;border-collapse:collapse;font-size:13px;margin:6px 0 14px;}
  table.bar th{text-align:left;color:var(--muted);font-weight:600;font-size:11px;text-transform:uppercase;
       letter-spacing:.03em;border-bottom:1px solid var(--line);padding:6px 8px;}
  table.bar td{padding:5px 8px;border-bottom:1px solid #f1f3f5;vertical-align:middle;}
  td.lab{font-weight:600;width:34%;}
  td.lab .val{color:var(--muted);font-weight:400;font-size:11.5px;}
  td.track{width:auto;}
  td.track .fill{background:var(--accent);height:14px;border-radius:3px;min-width:2px;}
  table.bar:not(.wide) td.lab{width:42%;}
  td.num{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums;width:1%;}
  td.num.accent{color:var(--accent);font-weight:700;}
  td.num.muted{color:var(--muted);}
  td.chips{width:38%;}
  .chip{display:inline-block;background:var(--bar);color:#3730a3;border-radius:12px;padding:2px 9px;
        margin:2px 4px 2px 0;font-size:11px;white-space:nowrap;}
  .chip-live{background:#dcfce7;color:#166534;}
  .grid{display:grid;grid-template-columns:1fr 1fr;gap:8px 32px;}
  .panel{min-width:0;}
  .note{background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:10px 14px;margin:12px 0;font-size:12.5px;color:#1e40af;}
  .caveat{background:#fffbeb;border:1px solid #fde68a;border-radius:8px;padding:12px 16px;margin:14px 0;font-size:12.5px;color:#92400e;}
  .empty{color:var(--muted);font-style:italic;font-size:13px;}
  footer{margin-top:48px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:12px;word-break:break-word;}
  footer b{color:var(--ink);}
  code{background:#f3f4f6;padding:1px 5px;border-radius:4px;font-size:12px;}"""
    )

    summary_html = f'<div class="summary">{esc(meta["summary"])}</div>' if meta.get("summary") else ""
    workflow_note = f' workflow_id <code>{esc(meta["workflow_id"])}</code>.' if meta.get("workflow_id") else ""

    # Section 1 (your signals) is present only when signals were supplied. The
    # -list flavor is discovered-only, so it omits Section 1, drops the specified
    # count from the header, and renumbers Discovered to section 1.
    if discovered_only:
        meta_specified_div = ""
        section1_html = ""
        disc_num = "1"
        disc_excl = "inverse (&ldquo;= false&rdquo;) traits are dropped."
    else:
        meta_specified_div = f'  <div><b>{len(specified["per_signal"])}</b>specified signals</div>\n'
        section1_html = (
            "<h2>1 &nbsp;Your signals</h2>\n"
            '<p class="secsub">How the people in this market express the signals you composed the audience from.</p>\n'
            f"{specified_table}\n"
            "<h3>Signal coverage &mdash; how many specified signals each person hits</h3>\n"
            f"{coverage_table}\n\n"
        )
        disc_num = "2"
        disc_excl = "Signals already in section 1 are excluded; inverse (&ldquo;= false&rdquo;) traits are dropped."

    # The intent panel renders distinctly, above the grid, with its caveat.
    if intent_panel and intent_panel["items"]:
        intent_block = (
            f'<h3 style="margin-top:28px;">{esc(intent_panel["title"])} '
            f'<span class="dom">intent</span></h3>\n'
            f'<div class="note">{intent_note}</div>\n'
            f"{panel_html(intent_panel)}"
        )
    else:
        intent_block = f'<div class="note">{intent_note}</div>'

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(meta["title"])}</title>
<style>{css}</style></head>
<body><div class="wrap">
<header>
  <h1>{esc(meta["title"])}</h1>
  <div class="sub">{esc(meta["location_label"])}</div>
</header>

<div class="meta">
  <div><b>{headcount}</b>people in market</div>
{meta_specified_div}  <div><b>{len(discovered["lift_over"])}</b>discovered over-indexing traits</div>
</div>

{summary_html}

{section1_html}<h2>{disc_num} &nbsp;Discovered signals</h2>
<p class="secsub">What stands out about these people that you did <em>not</em> specify. {disc_excl}</p>
<div class="caveat">{caveat}</div>
<h3>Most over-represented traits vs. the average American</h3>
{lift_table}
{intent_block}
<h3 style="margin-top:28px;">Audience breakdown</h3>
<div class="grid">{panels_html}</div>

<footer>
  <div><b>Signal stack.</b> <code>{esc(meta.get("expression") or "")}</code></div>
  <div><b>Structural gates (must-have).</b> {and_list} &nbsp;|&nbsp; <b>Exclusions.</b> {andnot_list}</div>
  <div>Gates aren't shown as stat panels: by construction ~100% of the audience passes every must-have and ~0% hits any exclusion.</div>
  <div><b>Method.</b> Both sections are computed on a deterministic <b>{sample}-person</b> profiling sample; the {headcount} headcount is the full in-market population. Lift is vs. a national baseline (geographic traits excluded).{workflow_note}</div>
</footer>
</div>
</body></html>"""


def main():
    args = parse_args(sys.argv[1:])
    for req in ["profile", "title", "location-label", "headcount", "out-html", "out-json"]:
        if req not in args:
            fail(f"missing required flag --{req}")
    try:
        if not math.isfinite(float(args["headcount"])):
            raise ValueError()
    except (TypeError, ValueError):
        fail(f"--headcount must be a number, got {json.dumps(args['headcount'])}")

    try:
        with open(args["profile"], "r", encoding="utf-8") as f:
            profile = json.load(f)
    except Exception as e:
        fail(f"could not read --profile {args['profile']} ({e})")
    gates = {}
    if args.get("gates"):
        try:
            gates = json.loads(args["gates"])
        except json.JSONDecodeError as e:
            fail(f"--gates is not valid JSON ({e})")

    specified_in = profile.get("specified") if isinstance(profile.get("specified"), list) else []
    specified_hashes = {s.get("trait_hash") for s in specified_in if s.get("trait_hash")}

    specified = build_specified(profile)
    discovered = build_discovered(profile, specified_hashes)
    # Discovered-only when asked (-list) or when the read carried no signals.
    discovered_only = bool(args.get("no-specified")) or not specified["per_signal"]

    meta = {
        "title": args["title"],
        "location_label": args["location-label"],
        "expression": args.get("expression") or "",
        "headcount": num(args["headcount"]),
        "sample": num(args.get("sample") or 0),
        "workflow_id": args.get("workflow-id") or "",
        "gates": gates,
        "summary": args.get("summary") or "",
    }

    meta["discovered_only"] = discovered_only
    with open(args["out-json"], "w", encoding="utf-8") as f:
        f.write(json.dumps({"meta": meta, "specified": specified, "discovered": discovered}, indent=2, ensure_ascii=False))
    with open(args["out-html"], "w", encoding="utf-8") as f:
        f.write(render_html(meta, specified, discovered, discovered_only=discovered_only))

    sys.stdout.write(f"OK: {args['out-html']}\n")
    sys.stdout.write(f"  specified signals: {len(specified['per_signal'])}\n")
    sys.stdout.write(
        f"  discovered over-index: {len(discovered['lift_over'])}, under-index: {len(discovered['lift_under'])}, panels: {len(discovered['panels'])}\n"
    )


main()
