#!/usr/bin/env python3
"""Reddit audience writer — turns a materialized Watt audience CSV
into a Reddit upload file.

Owns its audience-size-critical transform in this one file — the column layout,
the hash-vs-raw decisions, and the CLI runner. The can't-vary plumbing
(SHA-256, RFC 4180 escaping, the Watt CSV reader, presence checks) is imported
from ``_common`` — see that module's header for why the line falls where it does.

Audience-size-critical, so keep the hashing and column layout stable: Reddit's
customer-list upload takes one combined CSV with the template's three-column
header — ``Emails (hashed)``, ``Emails (unhashed)``, ``Mobile Ad IDs
(unhashed)`` — and one identifier per row. Emails are SHA-256-hashed
(lowercased, trimmed) into the hashed column, leaving the unhashed-email column
empty. Mobile-ad IDs ride raw in their own column — Reddit's upload takes the
device ID unhashed (unlike the email). Reddit matches on email or device ID; it
takes no phone. Deterministic — the same input always produces the same output.

Writes ``reddit_audience.csv``. Requires ``_common.py`` beside it in
``scripts/writers/``.
"""
import os
import sys

from _common import (
    MAX_PER_TYPE,
    sha256_hex,
    any_email,
    any_maid,
    read_watt_csv,
    _csv_field,
)

# entity_find `domains` the Reddit export needs materialized.
IDENTIFIERS = ["email", "maid"]

# Reddit's customer-list template header — one combined file, exactly these
# columns in this order. Reddit rejects an upload whose headers are changed or
# removed, so keep this row verbatim.
HEADER = ["Emails (hashed)", "Emails (unhashed)", "Mobile Ad IDs (unhashed)"]


# ----- Reddit normalization policy -----

def email_lower_trim(e):
    return e.strip().lower() if e else ""


def maid_raw(m):
    """Lowercase and trim, but do NOT hash — Reddit's upload takes the device ID
    raw (the ``Mobile Ad IDs (unhashed)`` column), unlike the email."""
    return m.strip().lower() if m else ""


def has_required(row):
    """True if Reddit can match the row. Reddit matches on email or device ID,
    so a maid-only person is still reachable."""
    return any_email(row) or any_maid(row)


def write_rows(path, header_row, rows):
    """Write positional rows (lists of cells) as RFC 4180 CSV — CRLF line
    endings, minimal quoting. The header row is mandatory — Reddit keys the
    upload on its exact column names."""
    lines = [",".join(_csv_field(h) for h in header_row)]
    for cells in rows:
        lines.append(",".join(_csv_field(c) for c in cells))
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write("\r\n".join(lines) + "\r\n")


def write_reddit(rows, out_dir):
    """Write ``reddit_audience.csv`` — one combined file, the template header,
    one identifier per row.

    Emails explode one row per email per person, SHA-256-hashed into the hashed
    column; the unhashed-email column stays empty. The device ID rides raw in
    its own column — the top-quality device ID per person. A person with no
    identifier Reddit can match is skipped, so the write path can never emit an
    all-empty row.
    """
    rows = [r for r in rows if has_required(r)]
    out = []
    for r in rows:
        for i in range(1, MAX_PER_TYPE + 1):
            e = r.get(f"email{i}") or ""
            if e:
                out.append([sha256_hex(email_lower_trim(e)), "", ""])
        m = r.get("maid1") or ""
        if m:
            out.append(["", "", maid_raw(m)])
    write_rows(os.path.join(out_dir, "reddit_audience.csv"), HEADER, out)


USAGE = """usage: reddit.py [--help] [--list-identifiers]
                 [--input CSV --out-dir DIR]

  --list-identifiers  Print the entity_find domains this writer needs and exit.
  --input CSV         Materialized audience CSV (Watt v2 entity_find schema).
  --out-dir DIR       Output directory for the platform file(s).

  A person with no identifier Reddit can match produces no row. The reported
  count is the people actually written.

  Exit codes: 0 success · 2 bad arguments."""


def main(argv):
    args = {"list_identifiers": False, "input": "", "out_dir": ""}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--help", "-h"):
            print(USAGE)
            return 0
        elif a == "--list-identifiers":
            args["list_identifiers"] = True
        elif a == "--input":
            i += 1
            args["input"] = argv[i] if i < len(argv) else ""
        elif a == "--out-dir":
            i += 1
            args["out_dir"] = argv[i] if i < len(argv) else ""
        else:
            print(f"Unknown argument: {a}\n{USAGE}", file=sys.stderr)
            return 2
        i += 1

    if args["list_identifiers"]:
        print(",".join(IDENTIFIERS))
        return 0

    if not (args["input"] and args["out_dir"]):
        print(f"Provide either --list-identifiers, or both --input and --out-dir.\n{USAGE}", file=sys.stderr)
        return 2

    os.makedirs(args["out_dir"], exist_ok=True)
    rows = read_watt_csv(args["input"])
    written = sum(1 for r in rows if has_required(r))
    write_reddit(rows, args["out_dir"])
    skipped = len(rows) - written
    note = f"; {skipped} skipped with no identifier Reddit can match" if skipped else ""
    print(f"OK: wrote {written} of {len(rows)} persons to {args['out_dir']}{note}")
    return 0


sys.exit(main(sys.argv[1:]))
