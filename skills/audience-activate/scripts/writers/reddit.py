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
    read_watt_csv_with_maid,
    csv_line,
    contact_window_cap,
    MAID_WINDOW_CAP,
)

# The contact-lane domains the Reddit export materializes — email only. ``maid``
# is the heavy domain, so it is NOT pulled here: it rides its own lane and is
# merged back by entity_id, where write_reddit emits it raw on its own row in the
# combined file (a device-ID-only person becomes a maid-only row). The two lanes
# reunite into one flat row, so the transform below is unchanged.
IDENTIFIERS = ["email"]
USES_MAID = True

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


def write_reddit(rows, out_dir):
    """Stream ``reddit_audience.csv`` — one combined file, the template header,
    one identifier per row — returning ``(total, written)`` — persons seen and
    persons with a matchable identifier.

    Emails explode one row per email per person, SHA-256-hashed into the hashed
    column; the unhashed-email column stays empty. The device ID rides raw in
    its own column — the top-quality device ID per person. A person with no
    identifier Reddit can match is skipped, so the write path can never emit an
    all-empty row.

    Rows are written as the input streams through — the writer holds one person
    at a time, never the whole audience. The header is mandatory; Reddit keys the
    upload on its exact column names.
    """
    path = os.path.join(out_dir, "reddit_audience.csv")
    total = written = 0
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(csv_line(HEADER))
        for r in rows:
            total += 1
            if not has_required(r):
                continue
            written += 1
            for i in range(1, MAX_PER_TYPE + 1):
                e = r.get(f"email{i}") or ""
                if e:
                    f.write(csv_line([sha256_hex(email_lower_trim(e)), "", ""]))
            m = r.get("maid1") or ""
            if m:
                f.write(csv_line(["", "", maid_raw(m)]))
    return total, written


USAGE = """usage: reddit.py [--help] [--list-identifiers] [--export-cap]
                 [--uses-maid] [--maid-cap]
                 [--input CSV [--maid-input CSV] --out-dir DIR]

  --list-identifiers  Print the contact-lane entity_find domains this writer
                      needs and exit (the mobile-ad ID rides its own lane).
  --export-cap        Print the contact-lane batch window — the export pages
                      the full audience this many people at a time — and exit.
  --uses-maid         Print "true"/"false" — whether a mobile-ad-ID lane applies.
  --maid-cap          Print the maid lane's per-window ceiling, and exit.
  --input CSV         Materialized contact-lane CSV (Watt entity_find schema).
  --maid-input CSV    Optional maid-lane CSV; merged onto --input by entity_id.
  --out-dir DIR       Output directory for the platform file(s).

  A person with no identifier Reddit can match produces no row. The reported
  count is the people actually written.

  Exit codes: 0 success · 2 bad arguments."""


def main(argv):
    args = {"list_identifiers": False, "export_cap": False, "uses_maid": False,
            "maid_cap": False, "input": "", "maid_input": "", "out_dir": ""}
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--help", "-h"):
            print(USAGE)
            return 0
        elif a == "--list-identifiers":
            args["list_identifiers"] = True
        elif a == "--export-cap":
            args["export_cap"] = True
        elif a == "--uses-maid":
            args["uses_maid"] = True
        elif a == "--maid-cap":
            args["maid_cap"] = True
        elif a == "--input":
            i += 1
            args["input"] = argv[i] if i < len(argv) else ""
        elif a == "--maid-input":
            i += 1
            args["maid_input"] = argv[i] if i < len(argv) else ""
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

    if args["export_cap"]:
        print(contact_window_cap(len(IDENTIFIERS)))
        return 0

    if args["uses_maid"]:
        print("true" if USES_MAID else "false")
        return 0

    if args["maid_cap"]:
        print(MAID_WINDOW_CAP)
        return 0

    if not (args["input"] and args["out_dir"]):
        print(f"Provide either --list-identifiers, or both --input and --out-dir.\n{USAGE}", file=sys.stderr)
        return 2

    os.makedirs(args["out_dir"], exist_ok=True)
    rows = (read_watt_csv_with_maid(args["input"], args["maid_input"])
            if args["maid_input"] else read_watt_csv(args["input"]))
    total, written = write_reddit(rows, args["out_dir"])
    skipped = total - written
    note = f"; {skipped} skipped with no identifier Reddit can match" if skipped else ""
    print(f"OK: wrote {written} of {total} persons to {args['out_dir']}{note}")
    return 0


sys.exit(main(sys.argv[1:]))
