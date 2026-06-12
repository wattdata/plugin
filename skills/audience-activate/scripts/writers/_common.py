#!/usr/bin/env python3
"""Shared infrastructure for the per-platform writer scripts.

This module holds **only** the parts that carry *no platform semantics* and so
are byte-identical wherever they appear — the things that genuinely cannot
differ between platforms:

  * primitives — ``sha256_hex`` (SHA-256 is SHA-256), ``_csv_field`` (RFC 4180
    escaping is universal);
  * input parsing — ``read_watt_csv``, ``parse_address``, ``split_name`` parse
    *Watt's* materialization schemas (the flat ``entity_find`` columns from the
    composition path **and** the nested ``entity_enrich`` columns from the roster
    path), normalizing both to the same flat row the writers read — the same for
    every platform;
  * presence checks — ``any_email`` / ``any_phone`` / ``any_maid`` over the
    fixed ``<type><1..MAX_PER_TYPE>`` columns;
  * ``MAX_PER_TYPE`` — the entity_find materialization count, a cross-writer
    invariant (frozen at 3; bumping it requires a sweep of every writer).

**What deliberately stays in each writer** — the match-rate-critical surface,
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
import re

# Number of identifier values per type to materialize (entity_find's
# max_identifiers parameter). Frozen at 3; bumping it requires a sweep of
# every writer.
MAX_PER_TYPE = 3


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
    """Read a Watt CSV into flat column->value dicts.

    Accepts both materialization schemas and normalizes to the flat
    ``<type><1..3>`` / ``name1`` / ``address1`` row the writers read: the
    ``entity_find`` CSV (composition export) as-is, the ``entity_enrich`` CSV
    (roster export) flattened. Detected by header, per row.
    """
    with open(path, "r", encoding="utf-8", newline="") as f:
        raw = list(_csv.reader(f))
    if not raw:
        return []
    header = raw[0]
    rows = [{nm: (cells[i] if i < len(cells) else "") for i, nm in enumerate(header)} for cells in raw[1:]]
    if any(_ENRICH_COL.match(h) for h in header):
        rows = [_flatten_enrich_row(r) for r in rows]
    return rows


def _csv_field(v):
    v = "" if v is None else str(v)
    if any(c in v for c in ('"', ",", "\r", "\n")):
        return '"' + v.replace('"', '""') + '"'
    return v
