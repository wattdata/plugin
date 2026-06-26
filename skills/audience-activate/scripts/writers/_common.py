#!/usr/bin/env python3
"""Shared infrastructure for the per-platform writer scripts.

This module holds **only** the parts that carry *no platform semantics* and so
are byte-identical wherever they appear — the things that genuinely cannot
differ between platforms:

  * primitives — ``sha256_hex`` (SHA-256 is SHA-256), ``_csv_field`` (RFC 4180
    escaping is universal), ``csv_line`` (escape + join + CRLF — the one-line
    assembly every writer streams a row through, equally universal);
  * input parsing — ``read_watt_csv``, ``parse_address``, ``split_name`` parse
    *Watt's* materialization schemas (the flat ``entity_find`` columns from the
    composition path **and** the nested ``entity_enrich`` columns from the roster
    path), normalizing both to the same flat row the writers read — the same for
    every platform. ``read_watt_csv`` **streams** — it yields one normalized row
    at a time off the open file, so a writer holds a single row, never the whole
    audience. Memory stays flat across the largest file a writer reads — a contact
    export concatenated from ``contact_window_cap``-sized batches (below) — which
    is what keeps a writer inside a bounded sandbox's memory. ``read_watt_csv_with_maid``
    holds the same flat-memory line when it joins the two lanes, via a bounded
    external merge sort rather than buffering either lane (see its note);
  * presence checks — ``any_email`` / ``any_phone`` / ``any_maid`` over the
    fixed ``<type><1..MAX_PER_TYPE>`` columns;
  * ``MAX_PER_TYPE`` — the entity_find materialization count, a cross-writer
    invariant (frozen at 3; bumping it requires a sweep of every writer).

**What deliberately stays in each writer** — the audience-size-critical surface,
where one file must tell the whole story:

  * normalization *policy* — ``email_lower_trim``, the phone normalizer
    (Meta strips the leading ``+``, Google keeps it) — these encode a platform
    choice and have already diverged, so each writer owns its own;
  * ``has_required`` — which identifier makes a row matchable differs (Google
    counts a device ID; Meta does not);
  * the column layout and hash-vs-raw transform (``write_*``, the CSV-shape
    writer) and the platform's ``IDENTIFIERS`` declaration;
  * the CLI runner (``main`` / ``USAGE``) — left inline so each writer runs and
    reads as one self-contained executable.

So a platform's *transform* is still auditable in its own file with nothing to
diff against a sibling; only the can't-vary plumbing is shared. The cost of that
share: a writer is no longer a single portable file — this module must sit
beside it in ``scripts/writers/``. Filenames beginning with ``_`` are shared
helpers, **not** platforms — the platform menu is the ``<platform>.py`` files.

Python-only, stdlib-only, zero-dep. No I/O beyond the CSV read; no network.
"""
import csv as _csv
import hashlib
import heapq
import itertools
import json
import os
import re
import shutil

# Number of identifier values per type to materialize (entity_find's
# max_identifiers parameter). Frozen at 3; bumping it requires a sweep of
# every writer.
MAX_PER_TYPE = 3

# Server export cost budget — the envelope a single export batch must stay
# within. The Signal Graph refuses an export pre-flight when a call's cost
# exceeds this; for an export every materialized domain is a contact/identifier
# domain worth one unit per person, so a batch's cost is its row count times its
# domain count. This is an **optimistic mirror** used only to *size the batch
# window conservatively* (below) — it is not a load-bearing assertion. The server
# is authoritative: a batch over the real budget is rejected at pre-flight with a
# concrete smaller ``audience_limit`` that fits, which the activator surfaces for
# re-confirmation — never silently shrinking the run or shipping a partial file.
# So if this number ever drifts above the server's, the failure is loud and
# actionable, never a silently-wrong file. Calibrated for ~750k x 4 contact
# domains; mirror of the server's MAX_EXPORT_COST_UNITS.
MAX_EXPORT_COST_UNITS = 3_000_000

# Fraction of the budget a single contact batch is allowed to claim, so a batch
# never rides the edge of the envelope. Two-thirds keeps real headroom.
_EXPORT_COST_SAFETY_NUM, _EXPORT_COST_SAFETY_DEN = 2, 3

# Operational ceiling on a single contact batch — the most people one export
# call pulls regardless of how cheap its domains are. Caps download size and
# call time, and keeps the batch window flat and predictable across platforms
# (every shipped writer lands here today). The cost-derived bound below only
# pulls the window *under* this ceiling, never above it.
CONTACT_WINDOW_CEILING = 400_000


def contact_window_cap(num_contact_domains):
    """The contact-lane batch window for a writer of ``num_contact_domains``
    domains — how many people each batch pulls while paging the full confirmed
    audience one batch after the next (concatenated into one file) so an audience
    of any size exports whole, never truncated to a single call.

    Derived, not hard-coded, so it can't silently outgrow the budget: it's the
    smaller of the operational ceiling and the largest window whose worst-case
    cost (window x domain count) stays within the safety fraction of
    ``MAX_EXPORT_COST_UNITS``. With today's writers it lands at the 400,000
    ceiling on every shipped platform (4 domains -> cost bound 500,000,
    ceilinged to 400,000; 1 domain -> ceilinged); add enough domains and the
    cost bound drops the window below the ceiling automatically (6 domains ->
    333,333) instead of quietly overshooting. Should the server's
    real budget be lower still, an over-budget batch is rejected at pre-flight
    with a concrete smaller limit the activator surfaces (see
    ``MAX_EXPORT_COST_UNITS``) — a loud re-confirmation, never a silent shortfall.
    """
    n = max(1, int(num_contact_domains))
    cost_safe = (MAX_EXPORT_COST_UNITS * _EXPORT_COST_SAFETY_NUM
                 // _EXPORT_COST_SAFETY_DEN) // n
    return max(1, min(CONTACT_WINDOW_CEILING, cost_safe))


# Window size for the mobile-ad-ID lane, pulled on its own as an after-export
# second pass. A maid projection is far heavier per row than a contact domain — a
# large export carrying maid fails well below the cost budget above and can drop
# the connection mid-stream — so neither the cost-unit math nor the contact batch
# size governs it. The maid lane is pulled separately, one identifier (``maid``),
# in windows of this fixed, conservatively-small size, then merged back onto the
# contact rows by entity_id. Empirically calibrated to stay inside the safe
# envelope with headroom; independent of both the cost budget and the contact
# window. (As with the contact lane, an over-budget window is rejected at
# pre-flight with a concrete smaller limit the activator surfaces — never a
# silent shortfall.)
MAID_WINDOW_CAP = 100_000


def sha256_hex(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest() if s else ""


def parse_address(cell):
    """Split Watt's comma-joined address: ``street, city, state, zip5, zip4``."""
    if not cell:
        return {"street": "", "city": "", "state": "", "zip5": "", "zip4": ""}
    parts = [x.strip() for x in cell.split(",")]
    while len(parts) < 5:
        parts.append("")
    return {"street": parts[0], "city": parts[1], "state": parts[2], "zip5": parts[3], "zip4": parts[4]}


def split_name(cell):
    """Return ``[first, rest]`` — first whitespace-delimited token, then the rest."""
    if not cell:
        return ["", ""]
    m = re.match(r"^(\S+)\s+([\s\S]*)$", cell.strip())
    return [m.group(1), m.group(2)] if m else [cell.strip(), ""]


def any_email(row):
    return any((row.get(f"email{i}", "") or "").strip() for i in range(1, MAX_PER_TYPE + 1))


def any_phone(row):
    return any((row.get(f"phone{i}", "") or "").strip() for i in range(1, MAX_PER_TYPE + 1))


def any_maid(row):
    return any((row.get(f"maid{i}", "") or "").strip() for i in range(1, MAX_PER_TYPE + 1))


# entity_enrich's nested CSV columns: ``domains_<type>_<index>_<field>``
# (e.g. ``domains_emails_0_email``, ``domains_names_0_first_name``,
# ``domains_addresses_0_address``, ``domains_maids_0_device_id``). The roster
# export path materializes with entity_enrich, so its CSV arrives in this shape
# rather than entity_find's flat ``<type><1..3>`` columns.
_ENRICH_COL = re.compile(r"^domains_(emails|phones|names|addresses|maids)_(\d+)_(.+)$")


def _flatten_enrich_row(row):
    """Map one entity_enrich nested row to the flat entity_find shape the writers read.

    ``domains_emails_{i}_email`` -> ``email{i+1}``, phones/maids likewise;
    ``domains_names_0_*`` -> ``name1`` ("First Last"); ``domains_addresses_0_*``
    -> ``address1`` (the comma-joined cell parse_address expects, or its
    street/city/state/zip subfields joined). Only the first MAX_PER_TYPE of each
    multi-valued type are kept — the writers read no further.
    """
    out = {"entity_id": row.get("entity_id", "")}
    emails, phones, maids, names, addrs = {}, {}, {}, {}, {}
    for col, val in row.items():
        m = _ENRICH_COL.match(col)
        if not m or not (val or "").strip():
            continue
        typ, idx, field = m.group(1), int(m.group(2)), m.group(3)
        if typ == "emails" and field == "email":
            emails[idx] = val
        elif typ == "phones" and field == "phone":
            phones[idx] = val
        elif typ == "maids" and field == "device_id":
            maids[idx] = val
        elif typ == "names":
            names.setdefault(idx, {})[field] = val
        elif typ == "addresses":
            addrs.setdefault(idx, {})[field] = val
    for i in range(MAX_PER_TYPE):
        if i in emails:
            out["email%d" % (i + 1)] = emails[i]
        if i in phones:
            out["phone%d" % (i + 1)] = phones[i]
        if i in maids:
            out["maid%d" % (i + 1)] = maids[i]
    if 0 in names:
        n = names[0]
        full = " ".join(p for p in (n.get("first_name", ""), n.get("last_name", "")) if p).strip()
        if full:
            out["name1"] = full
    if 0 in addrs:
        a = addrs[0]
        # entity_enrich gives the street line in ``address`` (or ``street``) with
        # city / state / zip5 / zip4 as SEPARATE subfields — so always join them
        # into the comma cell parse_address reads ("street, city, state, zip5, zip4").
        # Only when there are no structured subfields (e.g. ``address`` already
        # carries a full comma-joined value) is ``address`` used as-is — never take
        # the street line alone, which would silently drop zip (a plaintext match key).
        street = (a.get("address") or a.get("street") or "")
        if any((a.get(k) or "").strip() for k in ("city", "state", "zip5", "zip", "zip4")):
            joined = ", ".join([street, a.get("city", ""), a.get("state", ""),
                                a.get("zip5", a.get("zip", "")), a.get("zip4", "")])
        else:
            joined = street
        if joined.strip(", "):
            out["address1"] = joined
    return out


def read_watt_csv(path):
    """Stream a Watt CSV as flat column->value dicts — one row at a time.

    A **generator**: it reads the header, then yields each data row off the open
    file as it goes, never materializing the whole audience. So a writer's memory
    stays flat across the full export budget — the input never lives in RAM as a
    list. The file is held open for the life of the iteration; consume it to
    completion (every writer does).

    Accepts both materialization schemas and normalizes to the flat
    ``<type><1..3>`` / ``name1`` / ``address1`` row the writers read: the
    ``entity_find`` CSV (composition export) as-is, the ``entity_enrich`` CSV
    (roster export) flattened. The schema is detected once from the header — both
    materializations write a uniform header — so the per-row branch is a constant.
    """
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = _csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            return
        is_enrich = any(_ENRICH_COL.match(h) for h in header)
        for cells in reader:
            row = {nm: (cells[i] if i < len(cells) else "") for i, nm in enumerate(header)}
            yield _flatten_enrich_row(row) if is_enrich else row


def _maid_cols(row):
    """The non-empty ``maid<1..MAX_PER_TYPE>`` values on a row, as a dict."""
    out = {}
    for i in range(1, MAX_PER_TYPE + 1):
        v = (row.get("maid%d" % i) or "").strip()
        if v:
            out["maid%d" % i] = v
    return out


def _entity_id(row):
    return (row.get("entity_id") or "").strip()


def _eid_sort_key(row):
    """Total order on ``entity_id`` shared by the sort and the merge below. Watt
    entity_ids are Int64, so numeric ones sort numerically — Python ints are exact
    at any width, so an Int64 past 2^53 still orders correctly (a string sort would
    put "1000" before "999"). Anything non-numeric sorts after, by string, so a
    stray blank/odd id can't crash the merge. The key is 1:1 with the canonical
    entity_id (Int64 has no leading-zero forms), so key-equality == id-equality."""
    eid = _entity_id(row)
    return (0, int(eid)) if eid.isdigit() else (1, eid)


# Rows held in memory per sort chunk before spilling a sorted run to disk. The
# in-memory sort of one chunk is the merge's memory high-water mark, so this caps
# peak RAM at ~this many rows regardless of total export size — the whole audience
# never lives in memory at once.
_MERGE_CHUNK_ROWS = 100_000

# Max run files merged (and held open) at once. Beyond this, runs are merged in
# grouped passes, so both memory and open file descriptors stay bounded no matter
# how many runs the spill produced — a huge export can't exhaust the fd limit.
_MERGE_FANIN = 16


def _spill_sorted_runs(rows, run_dir):
    """Read ``rows`` in ``_MERGE_CHUNK_ROWS`` chunks, sort each by entity_id, and
    write each as a JSONL run file. Returns the run-file paths. Memory is bounded
    by one chunk; the number of runs grows with total size, not memory."""
    runs = []
    it = iter(rows)
    while True:
        chunk = list(itertools.islice(it, _MERGE_CHUNK_ROWS))
        if not chunk:
            break
        chunk.sort(key=_eid_sort_key)
        run_path = os.path.join(run_dir, "run_%05d.jsonl" % len(runs))
        with open(run_path, "w", encoding="utf-8") as f:
            for r in chunk:
                f.write(json.dumps(r) + "\n")
        runs.append(run_path)
    return runs


def _read_run(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)


def _merge_runs(runs, run_dir):
    """K-way merge of sorted run files with a bounded fan-in. While there are more
    than ``_MERGE_FANIN`` runs, merge them in groups into fewer, longer runs
    (reclaiming each consumed run's disk); then return the final merge iterator
    over the survivors. Open files and resident rows never exceed the fan-in, so
    peak memory tracks the chunk size, not the run count."""
    gen = 0
    while len(runs) > _MERGE_FANIN:
        nxt = []
        for i in range(0, len(runs), _MERGE_FANIN):
            group = runs[i:i + _MERGE_FANIN]
            out_path = os.path.join(run_dir, "merge_%d_%05d.jsonl" % (gen, len(nxt)))
            with open(out_path, "w", encoding="utf-8") as f:
                for r in heapq.merge(*(_read_run(p) for p in group), key=_eid_sort_key):
                    f.write(json.dumps(r) + "\n")
            for p in group:
                os.remove(p)
            nxt.append(out_path)
        runs = nxt
        gen += 1
    return heapq.merge(*(_read_run(p) for p in runs), key=_eid_sort_key)


def _sorted_by_eid(path, run_dir):
    """Yield ``path``'s rows in entity_id order via a bounded-memory external merge
    sort: spill sorted chunks, then merge them with a capped fan-in. Flat memory
    no matter how large the file — the export's own streaming discipline, extended
    across a sort the source doesn't give us."""
    os.makedirs(run_dir, exist_ok=True)
    return _merge_runs(_spill_sorted_runs(read_watt_csv(path), run_dir), run_dir)


def read_watt_csv_with_maid(contact_path, maid_path):
    """Stream the contact lane with mobile-ad IDs merged in by ``entity_id`` — a
    flat-memory **external-sort merge-join** of the two lanes.

    The two lanes arrive as separate exports — a big contact-domain window
    (``contact_path``) and the maid lane (``maid_path``), pulled on its own in
    smaller windows because maid is the heavy domain. This rejoins them into the
    one flat row every writer reads, so the writers stay unchanged: each yielded
    row carries its contact columns **and** that person's ``maid<n>`` columns,
    matched on ``entity_id``. A maid-bearing person absent from the contact lane
    (a device-ID-only record) rides as a maid-only row — never dropped, since Meta
    matches a madid-only record and Google's device file and Reddit's maid rows
    take them too.

    Why an external sort and not a dict: the ``entity_find`` export applies no
    ``ORDER BY``, so the two lanes don't share a row order. A hash-join would hold
    the whole maid set resident (memory scaling with maid coverage). Instead each
    lane is sorted by entity_id through a bounded external merge sort (chunks
    spilled as run files under the maid file's directory, then merged), and the two
    sorted streams are walked in lockstep — so memory stays flat at any audience
    size, the same discipline as ``read_watt_csv``. Output is entity_id-ordered and
    deterministic. Run files are scratch and are removed when iteration completes.
    """
    base = os.path.dirname(os.path.abspath(maid_path)) or "."
    run_dir = os.path.join(base, ".maid_merge")
    try:
        contacts = _sorted_by_eid(contact_path, os.path.join(run_dir, "contact"))
        maids = (
            m for m in _sorted_by_eid(maid_path, os.path.join(run_dir, "maid"))
            if _entity_id(m) and _maid_cols(m)
        )
        c = next(contacts, None)
        m = next(maids, None)
        while c is not None and m is not None:
            kc, km = _eid_sort_key(c), _eid_sort_key(m)
            if kc == km:  # same entity (key is 1:1 with entity_id) — merge
                c.update(_maid_cols(m))
                yield c
                c = next(contacts, None)
                m = next(maids, None)
            elif kc < km:  # contact-only person (or a blank-id contact row)
                yield c
                c = next(contacts, None)
            else:  # device-ID-only person, in entity_id order
                row = {"entity_id": _entity_id(m)}
                row.update(_maid_cols(m))
                yield row
                m = next(maids, None)
        while c is not None:
            yield c
            c = next(contacts, None)
        while m is not None:
            row = {"entity_id": _entity_id(m)}
            row.update(_maid_cols(m))
            yield row
            m = next(maids, None)
    finally:
        shutil.rmtree(run_dir, ignore_errors=True)


def _csv_field(v):
    v = "" if v is None else str(v)
    if any(c in v for c in ('"', ",", "\r", "\n")):
        return '"' + v.replace('"', '""') + '"'
    return v


def csv_line(cells):
    """Assemble one RFC 4180 record: escape each cell, join on commas, terminate
    with CRLF. The single row-assembly primitive every writer streams through, so
    escaping and line endings can't drift between platforms."""
    return ",".join(_csv_field(c) for c in cells) + "\r\n"
