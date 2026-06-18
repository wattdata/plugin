#!/usr/bin/env python3
"""Reddit audience writer — turns a materialized Watt audience CSV
into Reddit upload files.

Owns its audience-size-critical transform in this one file — the column layout,
the hash-vs-raw decisions, and the CLI runner. The can't-vary plumbing
(SHA-256, the Watt CSV reader, presence checks) is imported from ``_common`` —
see that module's header for why the line falls where it does.

Audience-size-critical, so keep the hashing and column layout stable: Reddit takes
two match keys, each in its own single-column file — emails SHA-256-hashed
(lowercased, trimmed), and mobile-ad IDs SHA-256-hashed (lowercased). Unlike
Meta and Google, Reddit hashes the device ID rather than sending it raw. The
files carry no header row — one hex digest per line. Deterministic — the same
input always produces the same output.

Writes ``reddit_email.csv`` and ``reddit_maid.csv``. Requires ``_common.py``
beside it in ``scripts/writers/``.
"""
import os
import sys

from _common import (
    MAX_PER_TYPE,
    sha256_hex,
    any_email,
    any_maid,
    read_watt_csv,
)

# entity_find `domains` the Reddit export needs materialized.
IDENTIFIERS = ["email", "maid"]


# ----- Reddit normalization policy -----

def email_lower_trim(e):
    return e.strip().lower() if e else ""


def maid_lower(m):
    """Lowercase the device ID before hashing — Reddit hashes the MAID (unlike
    Meta and Google, which send the device ID raw)."""
    return m.strip().lower() if m else ""


def has_required(row):
    """True if Reddit can match the row. Reddit matches on email or device ID,
    so a maid-only person is still reachable."""
    return any_email(row) or any_maid(row)


def write_lines(path, lines):
    """Write one value per line — Reddit's single-column files carry no header,
    and a SHA-256 hex digest never needs RFC 4180 escaping."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        for v in lines:
            f.write(v + "\n")


def write_reddit(rows, out_dir):
    """Write ``reddit_email.csv`` and ``reddit_maid.csv``.

    Both keys are SHA-256-hashed, each to its own single-column, header-less
    file (Reddit's email and device-ID lists are separate match paths). Emails
    explode one digest per email per person; the device file carries the
    top-quality device ID per person.
    """
    rows = list(rows)

    email_digests = []
    for r in rows:
        for i in range(1, MAX_PER_TYPE + 1):
            e = r.get(f"email{i}") or ""
            if e:
                email_digests.append(sha256_hex(email_lower_trim(e)))
    write_lines(os.path.join(out_dir, "reddit_email.csv"), email_digests)

    maid_digests = [sha256_hex(maid_lower(r.get("maid1") or "")) for r in rows if (r.get("maid1") or "")]
    write_lines(os.path.join(out_dir, "reddit_maid.csv"), maid_digests)


USAGE = """usage: reddit.py [--help] [--list-identifiers]
                 [--input CSV --out-dir DIR] [--prune-missing]

  --list-identifiers  Print the entity_find domains this writer needs and exit.
  --input CSV         Materialized audience CSV (Watt v2 entity_find schema).
  --out-dir DIR       Output directory for the platform file(s).
  --prune-missing     Drop persons with no usable identifier before writing.
                      Default: pass them through.

  Exit codes: 0 success · 2 bad arguments."""


def main(argv):
    args = {"list_identifiers": False, "input": "", "out_dir": "", "prune_missing": False}
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
        elif a == "--prune-missing":
            args["prune_missing"] = True
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
    total_in = len(rows)

    if args["prune_missing"]:
        rows = [r for r in rows if has_required(r)]
        print(f"Prune: dropped {total_in - len(rows)} of {total_in} persons missing required identifiers for platform 'reddit'.")
    else:
        missing = sum(1 for r in rows if not has_required(r))
        if missing:
            print(f"NOTE: {missing} of {total_in} persons have no required identifier for platform 'reddit' (not pruned; pass --prune-missing to drop them).")

    write_reddit(rows, args["out_dir"])
    print(f"OK: wrote reddit output to {args['out_dir']} (persons in: {len(rows)})")
    return 0


sys.exit(main(sys.argv[1:]))
